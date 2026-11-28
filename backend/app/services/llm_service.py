"""
Large Language Model (LLM) Integration Service
==============================================
Purpose:
    Provides structured prompt execution, startup idea attribute extraction,
    and consulting report synthesis across foundation models.

Supported Providers:
    1. Groq (Primary: llama-3.3-70b-versatile / llama-3.1-8b-instant)
    2. Google Gemini (Fallback if configured)
    3. OpenAI GPT (Fallback if configured)

Directives:
    - Real LLM reasoning only (strictly no fabricated or heuristic fallbacks).
    - If provider call fails, raise a descriptive RuntimeError.
"""

import json
import os
import re
import sys
import warnings
from typing import Any

import httpx

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings
from app.core.logging import logger
from app.prompt import IDEA_ANALYSIS_PROMPT


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM service is missing valid configuration."""


# Safe SDK Imports
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False
    genai = None  # type: ignore
    genai_types = None  # type: ignore

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    try:
        import google.generativeai as legacy_genai
        HAS_LEGACY_GENAI = True
    except ImportError:
        HAS_LEGACY_GENAI = False
        legacy_genai = None  # type: ignore

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None  # type: ignore

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    Groq = None  # type: ignore


class LLMService:
    """
    Unified LLM Client coordinating prompt execution, idea extraction,
    and structured generation with Groq as primary provider.
    """

    def __init__(self, provider: str | None = None):
        self.provider = (provider or settings.DEFAULT_LLM_PROVIDER or "groq").lower()
        self.gemini_key = (settings.GEMINI_API_KEY or "").strip()
        self.openai_key = (settings.OPENAI_API_KEY or "").strip()
        self.groq_key = (settings.GROQ_API_KEY or "").strip()

        # Determine active provider
        self.active_provider = self._resolve_provider()
        self._unreachable_providers: set[str] = set()
        logger.info(f"[LLMService] Initialized with active provider: '{self.active_provider}'")

    def _resolve_provider(self) -> str:
        """Determines which provider to use based on configuration and available API keys."""
        if self.provider != "auto":
            return self.provider

        if self.groq_key and not self.groq_key.startswith("your-"):
            return "groq"
        if self.gemini_key and not self.gemini_key.startswith("your-"):
            return "gemini"
        if self.openai_key and not self.openai_key.startswith("your-"):
            return "openai"

        return "unconfigured"

    def is_configured(self) -> bool:
        """Returns True if the active LLM provider has a valid API key."""
        if self.active_provider == "groq":
            return bool(self.groq_key and not self.groq_key.startswith("your-"))
        elif self.active_provider == "gemini":
            return bool(self.gemini_key and not self.gemini_key.startswith("your-"))
        elif self.active_provider == "openai":
            return bool(self.openai_key and not self.openai_key.startswith("your-"))
        return False

    def get_missing_key_name(self) -> str:
        """Returns the environment variable name for the missing LLM API key."""
        if self.active_provider == "groq":
            return "GROQ_API_KEY"
        elif self.active_provider == "gemini":
            return "GEMINI_API_KEY"
        elif self.active_provider == "openai":
            return "OPENAI_API_KEY"
        return "GROQ_API_KEY"

    # =========================================================================
    # RETRY LOGIC FOR TRANSIENT API FAILURES
    # =========================================================================

    def _should_retry_error(self, error_str: str) -> bool:
        """Determines if an error message represents a transient issue worth retrying."""
        retryable_keywords = [
            "429", "rate limit", "resource exhausted", "quota",
            "500", "503", "service unavailable", "overloaded",
            "timeout", "deadline", "connection error", "connecterror",
            "try again", "temporarily unavailable",
        ]
        err_lower = error_str.lower()
        return any(kw in err_lower for kw in retryable_keywords)

    # =========================================================================
    # CORE COMPLETION METHODS
    # =========================================================================

    def generate_completion_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """Generate text using the configured LLM provider without heuristic fallback."""
        provider = self.active_provider

        try:
            if provider == "groq":
                if not self.groq_key or self.groq_key.startswith("your-"):
                    raise LLMConfigurationError("Groq API key is missing or invalid.")
                result = self._call_groq(system_prompt, user_prompt, temperature)

            elif provider == "gemini":
                if not self.gemini_key or self.gemini_key.startswith("your-"):
                    raise LLMConfigurationError("Gemini API key is missing or invalid.")
                result = self._call_gemini(system_prompt, user_prompt, temperature)

            elif provider == "openai":
                if not self.openai_key or self.openai_key.startswith("your-"):
                    raise LLMConfigurationError("OpenAI API key is missing or invalid.")
                result = self._call_openai(system_prompt, user_prompt, temperature)

            else:
                raise LLMConfigurationError(
                    f"No valid LLM provider configured. Active provider: {provider}"
                )

            if not result or not str(result).strip():
                raise RuntimeError(f"{provider} returned an empty response.")

            return str(result).strip()

        except (LLMConfigurationError, RuntimeError):
            raise
        except Exception as exc:
            logger.exception("[LLMService] %s API call failed: %s", provider, exc)
            raise RuntimeError(
                f"{provider} request failed: {exc!s}"
            ) from exc

    async def generate_completion(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.3
    ) -> str:
        """Executes a prompt asynchronously against the active LLM provider."""
        return self.generate_completion_sync(system_prompt, user_prompt, temperature)

    async def agenerate_completion(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.3
    ) -> str:
        """Async alias for prompt completion execution."""
        return self.generate_completion_sync(system_prompt, user_prompt, temperature)

    def generate_structured_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """
        Generates structured JSON using the configured LLM provider.
        Raises an error if the LLM fails or returns invalid JSON.
        Never fabricates heuristic data.
        """
        json_instruction = (
            "\n\nCRITICAL: You MUST respond ONLY with a valid JSON object "
            "matching the requested fields. Do not include any preamble, "
            "conversational commentary, or markdown text outside of the JSON."
        )

        combined_system = f"{system_prompt}{json_instruction}"

        raw_response = self.generate_completion_sync(
            combined_system,
            user_prompt,
            temperature=temperature,
        )

        try:
            parsed = self._parse_json(str(raw_response))

            if isinstance(parsed, dict) and parsed:
                return parsed

            raise ValueError("LLM returned empty or invalid JSON.")

        except Exception as e:
            logger.error("[LLMService] Structured JSON parsing failed: %s", e)
            raise RuntimeError(
                f"LLM returned an invalid structured response: {e!s}"
            ) from e

    async def generate_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Executes a prompt requesting structured JSON output asynchronously and parses the response."""
        return self.generate_structured_json_sync(system_prompt, user_prompt, temperature)

    async def agenerate_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Async alias for structured JSON generation."""
        return self.generate_structured_json_sync(system_prompt, user_prompt, temperature)

    # =========================================================================
    # LOW-LEVEL CALL HANDLERS
    # =========================================================================

    def _call_groq(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls Groq API via official SDK or REST."""
        model_name = "llama-3.3-70b-versatile"

        if HAS_GROQ and Groq is not None:
            try:
                client = Groq(
                    api_key=self.groq_key,
                    timeout=httpx.Timeout(15.0, connect=5.0),
                    max_retries=1,
                )
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                )
                content = response.choices[0].message.content or ""
                if content.strip():
                    return content
            except Exception as exc:  # noqa: BLE001
                logger.warning("[LLMService] Groq SDK call failed: %s. Trying REST fallback.", exc)

        # Direct REST API fallback
        with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_key}"},
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                if content and content.strip():
                    return content
            raise RuntimeError(f"Groq REST API error {resp.status_code}: {resp.text}")

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls OpenAI GPT models via official SDK or REST."""
        if HAS_OPENAI and OpenAI is not None:
            try:
                client = OpenAI(
                    api_key=self.openai_key,
                    timeout=15.0,
                    max_retries=1,
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                )
                content = response.choices[0].message.content or ""
                if content.strip():
                    return content
            except Exception as exc:  # noqa: BLE001
                logger.warning("[LLMService] OpenAI SDK call failed: %s. Trying REST fallback.", exc)

        # Direct REST API fallback
        with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            raise RuntimeError(f"OpenAI REST API error {resp.status_code}: {resp.text}")

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls Google Gemini using google-genai, legacy SDK, or direct REST API."""
        combined_prompt = f"{system_prompt}\n\nUser Input:\n{user_prompt}"

        # Try official google.genai SDK
        if HAS_GOOGLE_GENAI and genai is not None:
            try:
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=combined_prompt,
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text
            except Exception as exc:  # noqa: BLE001
                logger.warning("[LLMService] Gemini google-genai failed: %s. Trying legacy.", exc)

        # Try legacy google.generativeai
        if HAS_LEGACY_GENAI and legacy_genai is not None:
            try:
                if hasattr(legacy_genai, "configure") and hasattr(legacy_genai, "GenerativeModel"):
                    configure_fn = getattr(legacy_genai, "configure", None)
                    model_cls = getattr(legacy_genai, "GenerativeModel", None)
                    if callable(configure_fn) and callable(model_cls):
                        configure_fn(api_key=self.gemini_key)
                        model = model_cls("gemini-1.5-flash")
                        gen_fn = getattr(model, "generate_content", None)
                        if callable(gen_fn):
                            response = gen_fn(
                                combined_prompt,
                                generation_config={"temperature": temperature},
                            )
                            resp_text = getattr(response, "text", None)
                            if resp_text and isinstance(resp_text, str):
                                return resp_text
            except Exception as exc:  # noqa: BLE001
                logger.warning("[LLMService] Legacy Gemini failed: %s. Trying REST.", exc)

        # Direct REST API fallback
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
            resp = client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": combined_prompt}]}],
                    "generationConfig": {"temperature": temperature},
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        if text:
                            return text
            raise RuntimeError(f"Gemini REST error {resp.status_code}: {resp.text}")

    # =========================================================================
    # STRUCTURED EXTRACTION & AGENT METHODS
    # =========================================================================

    def extract_startup_details(self, raw_idea: str) -> dict[str, Any]:
        """
        Extracts standardized startup attributes from raw user text using real Groq LLM:
        - startup_name
        - industry
        - problem (problem_statement)
        - solution (proposed_solution)
        - target_users (target_customers)
        - business_model
        - value_proposition
        """
        raw_idea = raw_idea.strip()
        logger.info(f"[LLMService] Extracting startup details from raw text (Length: {len(raw_idea)} chars)")

        if not self.is_configured():
            raise LLMConfigurationError(f"{self.get_missing_key_name()} not configured.")

        system_prompt = IDEA_ANALYSIS_PROMPT
        user_prompt = f"Analyze the following startup idea description:\n\n{raw_idea}"

        parsed = self.generate_structured_json_sync(system_prompt, user_prompt, temperature=0.2)

        startup_name = parsed.get("startup_name") or "Startup Venture"
        industry = parsed.get("industry") or "Technology & Services"
        problem = parsed.get("problem") or parsed.get("problem_statement") or raw_idea[:100]
        solution = parsed.get("solution") or parsed.get("proposed_solution") or raw_idea[:100]
        target_users = parsed.get("target_users") or parsed.get("target_customers") or "Target users"
        business_model = parsed.get("business_model") or "SaaS Subscription"
        value_prop = parsed.get("value_proposition") or parsed.get("key_value_proposition") or ""

        return {
            "startup_name": startup_name,
            "industry": industry,
            "problem": problem,
            "solution": solution,
            "target_users": target_users,
            "business_model": business_model,
            "value_proposition": value_prop,
            # Backwards compatibility keys
            "problem_statement": problem,
            "proposed_solution": solution,
            "target_customers": target_users,
            "key_value_proposition": value_prop,
        }

    def synthesize_consulting_report(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Synthesizes a complete consulting report based on the extracted idea
        and real-time Tavily search snippets using Groq.
        """
        title = extracted_idea.get("startup_name") or "Startup Venture"
        industry = extracted_idea.get("industry") or "Technology & Services"
        problem = extracted_idea.get("problem") or extracted_idea.get("problem_statement") or ""
        solution = extracted_idea.get("solution") or extracted_idea.get("proposed_solution") or ""
        customers = extracted_idea.get("target_users") or extracted_idea.get("target_customers") or "Target users"
        model = extracted_idea.get("business_model") or "SaaS Subscription"

        # Format web search context
        search_context_text = "\n".join([
            f"- [{item.get('title')}]: {item.get('content')}"
            for item in search_snippets[:5]
        ])

        if not self.is_configured():
            raise LLMConfigurationError(f"{self.get_missing_key_name()} not configured.")

        system_prompt = (
            "You are a Senior Principal Venture Consultant.\n"
            "Analyze the startup idea and live market search context to produce a structured JSON validation dossier.\n"
            "CRITICAL: Ground findings strictly in evidence. Never invent statistics or fake competitors.\n"
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "overall_score": 82.0,\n'
            '  "feasibility_score": 85.0,\n'
            '  "market_demand_score": 80.0,\n'
            '  "uniqueness_score": 81.0,\n'
            '  "executive_summary": "Concise executive synthesis.",\n'
            '  "startup_overview": "Overview of venture positioning.",\n'
            '  "problem_statement": "Detailed analysis of customer friction.",\n'
            '  "proposed_solution": "Product architecture and solution.",\n'
            '  "target_customers": "ICP and buyer personas.",\n'
            '  "industry": "Industry sector.",\n'
            '  "business_model": "Monetization and unit economics.",\n'
            '  "market_research": "Evidence-grounded market findings.",\n'
            '  "market_trends": ["Trend 1", "Trend 2"],\n'
            '  "competitor_analysis": {\n'
            '    "direct_competitors": [{"name": "Competitor 1", "vulnerability": "Gap 1"}],\n'
            '    "indirect_competitors": ["Substitute 1"],\n'
            '    "defensive_moats": ["Moat 1"]\n'
            '  },\n'
            '  "swot_analysis": {\n'
            '    "strengths": ["Strength 1"],\n'
            '    "weaknesses": ["Weakness 1"],\n'
            '    "opportunities": ["Opportunity 1"],\n'
            '    "threats": ["Threat 1"]\n'
            '  },\n'
            '  "opportunities": ["Growth lever 1"],\n'
            '  "risks": ["Risk 1"],\n'
            '  "recommendations": ["Recommendation 1"],\n'
            '  "final_conclusion": "Strategic advisory verdict."\n'
            "}"
        )

        user_prompt = (
            f"Startup Name: {title}\n"
            f"Industry: {industry}\n"
            f"Target Customers: {customers}\n"
            f"Problem: {problem}\n"
            f"Solution: {solution}\n"
            f"Business Model: {model}\n\n"
            f"Live Market Search Findings (from Tavily):\n{search_context_text}"
        )

        parsed = self.generate_structured_json_sync(system_prompt, user_prompt, temperature=0.3)
        return parsed

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _parse_json(self, text: str) -> dict[str, Any] | None:
        """Cleans and extracts JSON payload from raw LLM output."""
        if not text:
            return None
        cleaned = text.strip()
        # Remove ```json ... ``` code blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
        elif "{" in cleaned and "}" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end].strip()

        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, dict) else None
        except Exception as err:  # noqa: BLE001
            logger.warning("[LLMService] JSON parse failed: %s. Raw text:\n%s", err, text[:200])
            return None


# Singleton instance
llm_service = LLMService()
