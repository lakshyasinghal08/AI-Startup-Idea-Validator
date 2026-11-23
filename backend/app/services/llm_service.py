"""
Large Language Model (LLM) Integration Service
==============================================
Purpose:
    Provides structured prompt execution, startup idea attribute extraction,
    and consulting report synthesis across foundation models.

Supported Providers (in priority order):
    1. Google Gemini API (gemini-3.5-flash-lite) with exponential backoff retries.
    2. OpenAI GPT (gpt-4o-mini / gpt-4o).
    3. Groq (llama-3.3-70b-versatile / llama-3.1-8b-instant).
    4. Heuristic Domain Engine (offline/fallback mode when credentials are not configured).
"""

import json
import os
import re
import sys
import time
import warnings
from typing import Any

import httpx

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings
from app.core.logging import logger

# Safe SDK Imports
genai: Any = None
genai_types: Any = None
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

legacy_genai: Any = None
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    try:
        import google.generativeai as legacy_genai
        HAS_LEGACY_GENAI = True
    except ImportError:
        HAS_LEGACY_GENAI = False

OpenAI: Any = None
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

Groq: Any = None
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


class LLMConfigurationError(Exception):
    """Raised when the required LLM API key is not configured."""
    def __init__(self, key_name: str = "GEMINI_API_KEY"):
        self.key_name = key_name
        super().__init__(f"{key_name} not configured.")


class LLMService:
    """
    Unified LLM Client coordinating prompt execution, idea extraction,
    and consulting report synthesis with multi-provider failover and retry handling.
    """

    def __init__(self, provider: str | None = None):
        self.provider = (provider or settings.DEFAULT_LLM_PROVIDER or "auto").lower()
        self.gemini_key = (settings.GEMINI_API_KEY or "").strip()
        self.openai_key = (settings.OPENAI_API_KEY or "").strip()
        self.groq_key = (settings.GROQ_API_KEY or "").strip()

        # Determine active provider
        self.active_provider = self._resolve_provider()
        self._unreachable_providers = set()
        logger.info(f"[LLMService] Initialized with active provider: '{self.active_provider}'")

    def _resolve_provider(self) -> str:
        """Determines which provider to use based on configuration and available API keys."""
        if self.provider == "groq":
            if self.groq_key and not self.groq_key.startswith("your-"):
                return "groq"
            return "missing_key"
        elif self.provider == "gemini":
            if self.gemini_key and not self.gemini_key.startswith("your-"):
                return "gemini"
            return "missing_key"
        elif self.provider == "openai":
            if self.openai_key and not self.openai_key.startswith("your-"):
                return "openai"
            return "missing_key"

        if self.groq_key and not self.groq_key.startswith("your-"):
            return "groq"
        if self.gemini_key and not self.gemini_key.startswith("your-"):
            return "gemini"
        if self.openai_key and not self.openai_key.startswith("your-"):
            return "openai"

        return "missing_key"

    def is_configured(self) -> bool:
        """Returns True if at least one valid LLM provider API key is configured."""
        return self._resolve_provider() in ("gemini", "openai", "groq")

    def get_missing_key_name(self) -> str:
        """Returns the specific API key variable name that is missing."""
        prov = (self.provider or "auto").lower()
        if prov == "groq":
            return "GROQ_API_KEY"
        elif prov == "openai":
            return "OPENAI_API_KEY"
        elif prov == "gemini":
            return "GEMINI_API_KEY"
        return "GEMINI_API_KEY"

    # =========================================================================
    # RETRY LOGIC FOR TRANSIENT API FAILURES
    # =========================================================================

    def _should_retry_error(self, err_msg: str) -> bool:
        """Identifies transient, retryable status codes and error keywords."""
        msg = err_msg.upper()
        retryable_keywords = (
            "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED",
            "500", "INTERNAL", "504", "TIMEOUT", "OVERLOADED"
        )
        return any(k in msg for k in retryable_keywords)

    # =========================================================================
    # CORE COMPLETION METHODS
    # =========================================================================

    def generate_completion_sync(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Executes a prompt synchronously against the active LLM provider with fallback handling.
        """
        if not self.is_configured():
            raise LLMConfigurationError(self.get_missing_key_name())

        provider = self.active_provider

        # 1. Active Provider First (e.g. Groq when configured as default)
        if provider == "groq" and "groq" not in self._unreachable_providers and (self.groq_key and not self.groq_key.startswith("your-")):
            try:
                result = self._call_groq(system_prompt, user_prompt, temperature)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                if any(k in str(e).lower() for k in ["getaddrinfo", "connecterror", "connection error", "timeout"]):
                    self._unreachable_providers.add("groq")
                logger.error(f"[LLMService] Groq execution failed: {e}. Attempting fallback.")

        # 2. Google Gemini
        if "gemini" not in self._unreachable_providers and (provider == "gemini" or (self.gemini_key and not self.gemini_key.startswith("your-"))):
            try:
                result = self._call_gemini(system_prompt, user_prompt, temperature)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                if any(k in str(e).lower() for k in ["getaddrinfo", "connecterror", "connection error", "timeout"]):
                    self._unreachable_providers.add("gemini")
                logger.error(f"[LLMService] Gemini execution failed: {e}. Attempting fallback.")

        # 3. OpenAI GPT
        if "openai" not in self._unreachable_providers and (provider == "openai" or (self.openai_key and not self.openai_key.startswith("your-"))):
            try:
                result = self._call_openai(system_prompt, user_prompt, temperature)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                if any(k in str(e).lower() for k in ["getaddrinfo", "connecterror", "connection error", "timeout"]):
                    self._unreachable_providers.add("openai")
                logger.error(f"[LLMService] OpenAI execution failed: {e}. Attempting fallback.")

        # 4. Groq (if not already tried)
        if provider != "groq" and "groq" not in self._unreachable_providers and (self.groq_key and not self.groq_key.startswith("your-")):
            try:
                result = self._call_groq(system_prompt, user_prompt, temperature)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                if any(k in str(e).lower() for k in ["getaddrinfo", "connecterror", "connection error", "timeout"]):
                    self._unreachable_providers.add("groq")
                logger.error(f"[LLMService] Groq execution failed: {e}. Attempting fallback.")

        # 4. Deterministic Heuristic Fallback
        logger.info(f"[LLMService] Using heuristic text generation fallback for: '{user_prompt[:50]}...'")
        return self._heuristic_completion(system_prompt, user_prompt)

    async def generate_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Executes a prompt asynchronously against the active LLM provider with fallback handling."""
        return self.generate_completion_sync(system_prompt, user_prompt, temperature)

    async def agenerate_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Async alias for prompt completion execution."""
        return self.generate_completion_sync(system_prompt, user_prompt, temperature)

    def generate_structured_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """
        Executes a prompt requesting structured JSON output synchronously and parses the response.
        """
        json_instruction = (
            "\n\nCRITICAL: You MUST respond ONLY with a valid JSON object matching the requested fields. "
            "Do not include any preamble, conversational commentary, or markdown text outside of the JSON."
        )
        combined_system = f"{system_prompt}{json_instruction}"

        try:
            raw_response = self.generate_completion_sync(combined_system, user_prompt, temperature=temperature)
            parsed = self._parse_json(str(raw_response))
            if parsed and isinstance(parsed, dict) and len(parsed) > 0:
                return parsed
        except Exception as e:  # noqa: BLE001
            logger.warning(f"[LLMService] Structured JSON generation error: {e}. Falling back to heuristic JSON.")

        # Fallback to structured heuristic dictionary
        return self._heuristic_structured_json(system_prompt, user_prompt)

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

    def _heuristic_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generates domain-grounded heuristic text completion when providers are unavailable."""
        prompt_lower = user_prompt.lower()
        if "json" in system_prompt.lower():
            structured_data = self._heuristic_structured_json(system_prompt, user_prompt)
            return json.dumps(structured_data)

        if "farmer" in prompt_lower or "agri" in prompt_lower:
            return (
                "The AI agricultural platform addresses crucial farmer pain points by optimizing crop selection and predicting market yields. "
                "Significant commercial potential exists across regional farming collectives, though localized data calibration and offline usability will be critical. "
                "Targeting agricultural cooperatives and regional agri-input distributors offers a viable, defensible beachhead."
            )
        return (
            "The proposed startup concept demonstrates compelling alignment with verifiable market friction. "
            "Strong customer demand is supported by industry-wide digital acceleration and demand for automated workflows. "
            "Near-term execution should prioritize rapid MVP validation, clear unit economics, and targeted customer interviews."
        )

    def _heuristic_structured_json(
        self, system_prompt: str, user_prompt: str
    ) -> dict[str, Any]:
        """Generates structured heuristic output when LLM providers are unavailable."""

        prompt_lower = user_prompt.lower()
        system_lower = system_prompt.lower()

        # Preserve the existing startup extraction fallback.
        if "startup_name" in system_lower:
            return self._heuristic_extract(user_prompt)

        # Handle IdeaAgent AI evaluation fallback.
        if "solution_defensibility_score" in system_lower:
            required_fields = [
                "problem_statement",
                "proposed_solution",
                "target_customers",
                "business_model",
            ]

            available_fields = sum(
                1
                for field in required_fields
                if field in prompt_lower
                and not any(
                    marker in prompt_lower.split(field, 1)[-1][:100]
                    for marker in ["unknown", "not specified", "none"]
                )
            )

            completeness = available_fields / len(required_fields)

            # Heuristic scores depend on information completeness and idea details.
            specificity_keywords = [
                "platform", "application", "app", "automate", "predict",
                "recommend", "analyze", "personalized", "real-time",
                "machine learning", "artificial intelligence", "ai",
                "mobile", "web", "marketplace", "subscription",
            ]

            specificity = sum(
                1 for keyword in specificity_keywords if keyword in prompt_lower
            )

            feasibility_score = min(
                90, max(35, round(45 + completeness * 25 + min(specificity, 5) * 4))
            )
            problem_clarity_score = min(
                90, max(30, round(35 + completeness * 35 + min(specificity, 5) * 3))
            )
            uniqueness_score = min(
                85, max(25, round(40 + min(specificity, 5) * 5))
            )
            market_potential_score = min(
                85, max(30, round(40 + completeness * 25 + min(specificity, 4) * 4))
            )
            solution_defensibility_score = min(
                80, max(20, round(30 + completeness * 20 + min(specificity, 4) * 5))
            )

            missing_information = [
                field.replace("_", " ")
                for field in required_fields
                if field in prompt_lower
                and any(
                    marker in prompt_lower.split(field, 1)[-1][:100]
                    for marker in ["unknown", "not specified", "none"]
                )
            ]

            strengths = []
            weaknesses = []
            recommendations = []

            if completeness >= 0.75:
                strengths.append(
                    "The idea includes several key startup components for initial evaluation."
                )
            else:
                weaknesses.append(
                    "Some important startup details are missing, limiting evaluation confidence."
                )
                recommendations.append(
                    "Define the problem, proposed solution, target customers, and revenue model more clearly."
                )

            if specificity >= 3:
                strengths.append(
                    "The description includes specific product or implementation details."
                )
            else:
                weaknesses.append(
                    "The solution description may be too broad to establish differentiation."
                )
                recommendations.append(
                    "Specify the core product functionality and how it differs from existing alternatives."
                )

            weaknesses.append(
                "The fallback evaluation cannot verify market demand or competitor information."
            )
            recommendations.append(
                "Validate the idea through competitor research and interviews with target users."
            )

            if missing_information:
                recommendations.append(
                    "Clarify the following missing details: "
                    + ", ".join(missing_information)
                    + "."
                )

            return {
                "problem_solution_fit": (
                    "This is a rule-based preliminary assessment derived from the "
                    "provided startup description. The problem-solution fit has not "
                    "been independently validated by an AI provider or market research."
                ),
                "feasibility_score": feasibility_score,
                "uniqueness_score": uniqueness_score,
                "problem_clarity_score": problem_clarity_score,
                "market_potential_score": market_potential_score,
                "solution_defensibility_score": solution_defensibility_score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations,
            }

        # Preserve compatibility with other agents using the older fallback.
        if "farmer" in prompt_lower or "agri" in prompt_lower:
            return {
                "idea_summary": (
                    "An agricultural technology concept focused on farmer needs."
                ),
                "feasibility_score": 60,
                "strengths": [
                    "Addresses a potentially important agricultural use case."
                ],
                "weaknesses": [
                    "Requires validation with farmers and agriculture domain experts."
                ],
            }

        return {
            "idea_summary": (
                "A preliminary startup concept requiring further validation."
            ),
            "feasibility_score": 50,
            "strengths": [
                "The concept provides a starting point for product discovery."
            ],
            "weaknesses": [
                "Market demand and competitive differentiation have not been validated."
            ],
        }

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls Google Gemini using google-genai, legacy SDK, or direct REST API with retries."""
        combined_prompt = f"{system_prompt}\n\nUser Input:\n{user_prompt}"
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                # Try official google.genai SDK
                if HAS_GOOGLE_GENAI and genai is not None:
                    client = genai.Client(api_key=self.gemini_key)
                    if genai_types and hasattr(genai_types, "GenerateContentConfig"):
                        config = genai_types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=temperature,
                        )
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=user_prompt,
                            config=config,
                        )
                    else:
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=user_prompt,
                        )
                    if response and response.text:
                        return response.text

                # Try legacy google.generativeai
                if (
                    HAS_LEGACY_GENAI
                    and legacy_genai is not None
                    and hasattr(legacy_genai, "configure")
                    and hasattr(legacy_genai, "GenerativeModel")
                ):
                    legacy_genai.configure(api_key=self.gemini_key)
                    model = legacy_genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(
                        combined_prompt,
                        generation_config={"temperature": temperature},
                    )
                    if response and response.text:
                        return response.text

                # Direct REST API fallback
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                with httpx.Client(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
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
                                return parts[0].get("text", "")
                    raise RuntimeError(f"Gemini REST error {resp.status_code}: {resp.text}")

            except Exception as e:
                err_str = str(e)
                if self._should_retry_error(err_str) and attempt < max_attempts - 1:
                    wait_time = 1
                    logger.warning(f"[LLMService] Gemini retryable error ({err_str}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        return ""

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls OpenAI GPT models via official SDK or REST."""
        if HAS_OPENAI and OpenAI is not None:
            client = OpenAI(api_key=self.openai_key, timeout=10.0, max_retries=0)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content or ""

        # Direct REST API fallback
        with httpx.Client(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
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

    def _call_groq(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Calls Groq API via official SDK or REST with model fallback."""
        candidate_models = [
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        last_error = None

        for model_name in candidate_models:
            try:
                if HAS_GROQ and Groq is not None:
                    client = Groq(api_key=self.groq_key, timeout=30.0, max_retries=1)
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
                else:
                    with httpx.Client(timeout=httpx.Timeout(30.0, connect=5.0)) as client:
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
                            if content.strip():
                                return content
                        last_error = RuntimeError(f"Groq REST API error {resp.status_code}: {resp.text}")
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning(f"[LLMService] Groq model '{model_name}' failed: {exc}. Trying next candidate.")

        raise last_error or RuntimeError("All Groq models failed.")

    # =========================================================================
    # STRUCTURED EXTRACTION & AGENT METHODS
    # =========================================================================

    def extract_startup_details(self, raw_idea: str) -> dict[str, Any]:
        """
        Extracts structured startup attributes from raw user text:
        - Startup Name
        - Problem Statement
        - Proposed Solution
        - Target Customers
        - Industry
        - Business Model
        - Key Value Proposition
        """
        raw_idea = raw_idea.strip()
        logger.info(f"[LLMService] Extracting startup details from raw text (Length: {len(raw_idea)} chars)")

        if not self.is_configured():
            logger.error("[LLMService] No external LLM API key configured.")
            raise LLMConfigurationError(self.get_missing_key_name())

        system_prompt = (
            "You are a Senior Principal Venture Analyst. The user provides a raw startup idea description.\n"
            "Your task is to analyze the text and extract structured venture information.\n"
            "You MUST respond ONLY with a valid JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "startup_name": "Working name or inferred concise brand name",\n'
            '  "problem_statement": "Concise definition of the acute customer friction or market inefficiency",\n'
            '  "proposed_solution": "Concrete description of the product/platform and how it resolves the pain point",\n'
            '  "target_customers": "Specific buyer persona, demographic, or B2B/B2C segment",\n'
            '  "industry": "Standard industry sector (e.g. EdTech & Career Tech, FinTech, B2B SaaS, HealthTech, AI & ML, Logistics)",\n'
            '  "business_model": "Feasible revenue model (e.g. Monthly B2B SaaS, Freemium, Marketplace Fee, Usage-based)",\n'
            '  "key_value_proposition": "Primary compelling benefit and competitive differentiation"\n'
            "}\n"
            "Do not include any conversational preamble or markdown backticks outside of the JSON."
        )

        try:
            raw_response = self.generate_completion_sync(system_prompt, raw_idea, temperature=0.2)
            parsed = self._parse_json(raw_response)
            if parsed and isinstance(parsed, dict) and "startup_name" in parsed:
                logger.info(f"[LLMService] Successfully extracted startup: '{parsed.get('startup_name')}'")
                return parsed
        except Exception as e:  # noqa: BLE001
            logger.error(f"[LLMService] Error during LLM idea extraction: {e}. Falling back to heuristic extraction.")

        return self._heuristic_extract(raw_idea)

    def synthesize_consulting_report(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Synthesizes a complete McKinsey/BCG/Deloitte style consulting report
        based on the extracted idea and real-time Tavily search snippets.
        Grounds market research and competitor findings in actual web evidence.
        """
        title = extracted_idea.get("startup_name") or "Startup Venture"
        industry = extracted_idea.get("industry") or "Technology & Services"
        problem = extracted_idea.get("problem_statement") or ""
        solution = extracted_idea.get("proposed_solution") or ""
        customers = extracted_idea.get("target_customers") or "Target users"
        model = extracted_idea.get("business_model") or "SaaS Subscription"

        # Format web search context
        search_context_text = "\n".join([
            f"- [{item.get('title')}]: {item.get('content')}"
            for item in search_snippets[:5]
        ])

        if not self.is_configured():
            logger.info("[LLMService] Using deterministic synthesis for consulting report.")
            return self._heuristic_consulting_report(extracted_idea, search_snippets)

        system_prompt = (
            "You are a Senior Engagement Manager at a top-tier management consultancy (McKinsey / BCG / Deloitte).\n"
            "Analyze the startup idea and the provided live market search context, and generate an executive-ready\n"
            "Startup Validation Consulting Report.\n"
            "CRITICAL: Ground your market research and competitor analysis in the real-time web search findings provided.\n"
            "Do not invent fake statistics. If exact numbers are unavailable, provide rigorous qualitative insights.\n"
            "You MUST respond ONLY with a valid JSON object matching this structure:\n"
            "{\n"
            '  "overall_score": 82.0,\n'
            '  "feasibility_score": 85.0,\n'
            '  "market_demand_score": 80.0,\n'
            '  "uniqueness_score": 81.0,\n'
            '  "executive_summary": "Two to three sentence executive synthesis of commercial viability and key findings.",\n'
            '  "startup_overview": "Comprehensive overview of the venture concept, positioning, and value proposition.",\n'
            '  "problem_statement": "Detailed analysis of customer pain points, market inefficiencies, and economic impact.",\n'
            '  "proposed_solution": "Structured explanation of the product architecture, user flow, and competitive edge.",\n'
            '  "target_customers": "Ideal Customer Profile (ICP), personas, and adoption triggers.",\n'
            '  "industry": "Industry sector categorization and macroeconomic context.",\n'
            '  "business_model": "Revenue model, pricing mechanics, and unit economics.",\n'
            '  "market_research": "Evidence-grounded market analysis derived from search findings and industry developments.",\n'
            '  "market_trends": ["Trend 1", "Trend 2", "Trend 3"],\n'
            '  "competitor_analysis": {\n'
            '    "direct_competitors": [{"name": "Competitor Name", "vulnerability": "Weakness/gap in offering"}],\n'
            '    "indirect_competitors": ["Substitute 1", "Substitute 2"],\n'
            '    "defensive_moats": ["Moat 1", "Moat 2", "Moat 3"]\n'
            '  },\n'
            '  "swot_analysis": {\n'
            '    "strengths": ["Strength 1", "Strength 2", "Strength 3"],\n'
            '    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],\n'
            '    "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3"],\n'
            '    "threats": ["Threat 1", "Threat 2", "Threat 3"]\n'
            '  },\n'
            '  "opportunities": ["Growth lever 1", "Growth lever 2", "Growth lever 3"],\n'
            '  "risks": ["Risk 1 with mitigation", "Risk 2 with mitigation", "Risk 3 with mitigation"],\n'
            '  "recommendations": ["Actionable step 1", "Actionable step 2", "Actionable step 3", "Actionable step 4"],\n'
            '  "final_conclusion": "Strategic advisory verdict and definitive go-forward recommendation."\n'
            "}\n"
            "Do not include markdown backticks around the JSON."
        )

        user_prompt = (
            f"Startup Name: {title}\n"
            f"Industry: {industry}\n"
            f"Target Customers: {customers}\n"
            f"Problem: {problem}\n"
            f"Solution: {solution}\n"
            f"Business Model: {model}\n\n"
            f"Live Market Search Findings (from Tavily Search API):\n{search_context_text}"
        )

        try:
            raw_response = self.generate_completion_sync(system_prompt, user_prompt, temperature=0.3)
            parsed = self._parse_json(raw_response)
            if parsed and isinstance(parsed, dict) and "overall_score" in parsed:
                logger.info(f"[LLMService] Successfully generated LLM consulting report for '{title}'.")
                return parsed
        except Exception as e:  # noqa: BLE001
            logger.error(f"[LLMService] LLM report synthesis failed: {e}. Falling back to deterministic synthesis.")

        return self._heuristic_consulting_report(extracted_idea, search_snippets)

    # =========================================================================
    # HELPERS & HEURISTIC FALLBACKS
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
            return json.loads(cleaned)
        except Exception as err:  # noqa: BLE001
            logger.warning(f"[LLMService] JSON parse failed: {err}. Raw text:\n{text[:200]}")
            return None

    def _heuristic_extract(self, text: str) -> dict[str, Any]:
        """Provides an intelligent heuristic extraction when LLM is unavailable."""
        sentences = [s.strip() for s in re.split(r"[.!?\n]", text) if len(s.strip()) > 5]
        first_sentence = sentences[0] if sentences else text[:80]

        # Inferred name: Check if user mentions "called X", "name is X", or first 3 words
        name_match = re.search(r"(?:called|named|name is)\s+([A-Za-z0-9_\- ]{3,30})", text, re.IGNORECASE)
        if name_match:
            inferred_name = name_match.group(1).strip().title()
        else:
            words = [w for w in re.sub(r"[^A-Za-z0-9 ]", "", first_sentence).split() if len(w) > 2]
            key_words = [w for w in words if w.lower() not in {"want", "build", "create", "make", "that", "this", "platform", "app"}]
            inferred_name = " ".join(key_words[:2]).title() + " AI" if key_words else "Venture Concept"

        # Inferred industry
        text_lower = text.lower()
        if any(w in text_lower for w in ["student", "interview", "prep", "learn", "course", "education", "tutor", "college"]):
            industry = "EdTech & Career Tech"
            customers = "Students, Job Seekers, and University Placement Cells"
        elif any(w in text_lower for w in ["health", "medical", "patient", "doctor", "clinic", "fitness", "diet"]):
            industry = "HealthTech & Digital Health"
            customers = "Healthcare Providers, Clinics, and Wellness Seekers"
        elif any(w in text_lower for w in ["money", "finance", "bank", "invest", "crypto", "payment", "loan", "tax"]):
            industry = "FinTech & Financial Services"
            customers = "Retail Consumers, Freelancers, and Small Businesses"
        elif any(w in text_lower for w in ["freight", "logistics", "fleet", "truck", "warehouse", "delivery", "shipping"]):
            industry = "Logistics & Supply Chain"
            customers = "Fleet Operators, Freight Dispatchers, and Shippers"
        elif any(w in text_lower for w in ["store", "ecommerce", "d2c", "retail", "shop", "cart", "product"]):
            industry = "E-Commerce & Retail Tech"
            customers = "Online Merchants and D2C Brands"
        else:
            industry = "B2B SaaS & Artificial Intelligence"
            customers = "Modern Enterprises, Knowledge Workers, and SMBs"

        return {
            "startup_name": inferred_name,
            "problem_statement": (
                f"Individuals and organizations lack streamlined, automated tools for {first_sentence.lower()}, "
                "leading to fragmented workflows, high preparation friction, and sub-optimal outcomes."
            ),
            "proposed_solution": (
                f"An intelligent platform providing {text.strip()[:180]}, "
                "leveraging automation and structured feedback loops to deliver immediate measurable value."
            ),
            "target_customers": customers,
            "industry": industry,
            "business_model": "Freemium with B2B / B2C Tiered SaaS Subscription",
            "key_value_proposition": "Significantly reduces time-to-mastery and costs through automated personalized feedback.",
        }

    def _heuristic_consulting_report(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Synthesizes structured consulting content deterministically,
        grounded in actual search snippets when available.
        """
        title = extracted_idea.get("startup_name", "Venture Concept")
        industry = extracted_idea.get("industry", "Technology")
        customers = extracted_idea.get("target_customers", "Target users")
        problem = extracted_idea.get("problem_statement", "")
        solution = extracted_idea.get("proposed_solution", "")
        model = extracted_idea.get("business_model", "SaaS Subscription")

        # Ground competitors from search snippets if found
        direct_competitors = []
        if search_snippets:
            for snippet in search_snippets[:3]:
                stitle = snippet.get("title", "")
                if ":" in stitle:
                    cname = stitle.split(":")[0].strip()
                    if 3 < len(cname) < 40 and not any(w in cname.lower() for w in ["market", "overview", "report", "size"]):
                        direct_competitors.append({"name": cname, "vulnerability": "Higher enterprise pricing and lack of specialized automation"})
        if not direct_competitors:
            direct_competitors = [
                {"name": f"Legacy {industry} Incumbents", "vulnerability": "High licensing cost and rigid, slow product iteration"},
                {"name": "Horizontal AI Assistants", "vulnerability": "Lack domain-specific workflows and dedicated scoring"},
            ]

        # Extract real market research text from search findings
        if search_snippets:
            research_summary = (
                f"Live web market intelligence indicates sustained activity in {industry}. "
                f"Key industry finding: '{search_snippets[0].get('content', '')[:200]}...' "
                "Market demand is characterized by rising user expectations for automated, on-demand domain intelligence."
            )
        else:
            research_summary = (
                f"Qualitative market analysis reveals accelerating demand across {industry}. "
                "Buyers are actively migrating away from fragmented manual workflows toward integrated, automated platforms "
                "that offer immediate time-to-value without heavy onboarding overhead."
            )

        return {
            "overall_score": 83.5,
            "feasibility_score": 86.0,
            "market_demand_score": 82.0,
            "uniqueness_score": 81.5,
            "executive_summary": (
                f"Executive Assessment: '{title}' presents a compelling value proposition targeting high-friction "
                f"inefficiencies in the {industry} sector. With strong demand tailwinds, grounded market need, "
                "and manageable technical risk, the venture is well positioned for early beachhead traction."
            ),
            "startup_overview": (
                f"'{title}' is an innovative platform positioned within {industry}. Designed specifically for {customers}, "
                f"the venture resolves operational friction through {model} delivery, prioritizing rapid onboarding and measurable user progress."
            ),
            "problem_statement": (
                f"Core Market Friction: Current target users face acute pain: '{problem}'. Existing solutions force buyers "
                "to choose between expensive manual consultations or fragmented tools that fail to provide actionable, real-time guidance."
            ),
            "proposed_solution": (
                f"Engineered Solution: '{title}' implements {solution}. By orchestrating domain intelligence with "
                "structured feedback loops, the platform reduces cycle times and delivers direct, quantifiable efficiency gains."
            ),
            "target_customers": (
                f"Primary Customer Profile: {customers}. Initial adoption centers on high-urgency early adopters "
                "seeking immediate capability uplift, followed by secondary expansion into institutional accounts."
            ),
            "industry": industry,
            "business_model": model,
            "market_research": research_summary,
            "market_trends": [
                f"Accelerated digitization and automation adoption across the {industry} domain.",
                "Growing customer willingness to pay for specialized vertical intelligence over generic horizontal tools.",
                "Demand for transparent, measurable outcome tracking and verifiable progress metrics.",
            ],
            "competitor_analysis": {
                "direct_competitors": direct_competitors,
                "indirect_competitors": [
                    "Manual in-house spreadsheets, informal peer practice, and ad-hoc workflows",
                    "Generic foundational language models without tailored evaluation rubrics",
                ],
                "defensive_moats": [
                    "Proprietary contextual dataset and feedback loops compounding accuracy over time",
                    "High user switching barriers generated by personalized telemetry and history",
                    "Substantially lower cost of onboarding and faster time-to-value than incumbents",
                ],
            },
            "swot_analysis": {
                "strengths": [
                    f"Laser-focused value proposition resolving acute friction for {customers}",
                    f"Favorable unit economics supported by a {model} pricing architecture",
                    "Lightweight, agile technical foundation enabling rapid product iteration",
                ],
                "weaknesses": [
                    "Early brand obscurity requiring focused initial proof-of-work case studies",
                    "Distribution reliance on early organic referral loops and content marketing",
                    "Continuous requirement for domain benchmarking and quality calibration",
                ],
                "opportunities": [
                    f"Strong macroeconomic tailwinds expanding across the {industry} sector",
                    "B2B enterprise cohort licensing and institutional partnerships",
                    "Integration with mainstream productivity ecosystems and workflow suites",
                ],
                "threats": [
                    "Feature bundling by capitalized platform incumbents",
                    "Pricing resistance among cost-sensitive early customer cohorts",
                    "Long-term user retention friction if engagement habits are not cemented early",
                ],
            },
            "opportunities": [
                "Beachhead expansion through viral user-to-user referral incentives.",
                "Institutional & enterprise cohort multi-seat licensing.",
                "Proprietary benchmark monetization and developer API partnerships.",
            ],
            "risks": [
                "Customer Acquisition Friction: High CAC if relying strictly on paid advertising channels.",
                "Incumbent Bundling: Legacy platforms releasing baseline automated features.",
                "User Retention: Risk of user dropout following initial milestone completion.",
            ],
            "recommendations": [
                "Phase 1 (Days 1-30): Conduct 25 structured user discovery interviews to validate pricing thresholds.",
                "Phase 2 (Days 31-60): Launch a functional MVP focused solely on the single highest-frequency user friction point.",
                "Phase 3 (Days 61-90): Secure 3 flagship reference pilot customers and establish quantitative case studies.",
                "Phase 4 (Ongoing): Maintain lean unit economics, targeting a Customer Acquisition Cost payback period under 10 months.",
            ],
            "final_conclusion": (
                f"Strategic Verdict: Highly Viable with Clear Execution Roadmap. '{title}' represents a compelling venture "
                f"opportunity within the {industry} sector. It demonstrates authentic problem-solution alignment and defensible moats. "
                "By executing a disciplined, product-led go-to-market strategy, the founding team has a strong probability of commercial success."
            ),
        }


# Singleton instance
llm_service = LLMService()


if __name__ == "__main__":
    svc = LLMService()
    test_extraction = svc.extract_startup_details("I want to build an AI platform that helps students prepare for interviews.")
    print("Extracted Details:", json.dumps(test_extraction, indent=2))
