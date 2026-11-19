
"""
Large Language Model (LLM) Integration Service
Supports Google Gemini and OpenAI.
Includes retry handling for temporary Gemini API failures.
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, Optional

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings
from app.core.logging import logger


class LLMService:
    """Unified async LLM service."""

    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None):
        self.provider = provider.lower()

        if self.provider not in ("gemini", "openai"):
            raise ValueError(
                "Unsupported provider. Use 'gemini' or 'openai'."
            )

        self.api_key = api_key or (
            settings.GEMINI_API_KEY
            if self.provider == "gemini"
            else settings.OPENAI_API_KEY
        )

        if not self.api_key:
            raise ValueError(
                f"Missing API key for provider: {self.provider}"
            )

        if self.provider == "gemini":
            from google import genai

            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-3.5-flash-lite"

        else:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"

        logger.info(f"LLMService initialized using {self.provider}")

    async def _generate_gemini_with_retry(self, contents, config):
        """
        Generate Gemini response with retry handling for temporary errors.
        Retries up to 3 attempts with exponential backoff.
        """

        max_attempts = 3

        retryable_errors = (
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "500",
            "INTERNAL",
            "504",
            "TIMEOUT",
        )

        for attempt in range(max_attempts):
            try:
                return await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

            except Exception as e:
                error_message = str(e).upper()

                is_retryable = any(
                    error in error_message
                    for error in retryable_errors
                )

                # Stop immediately for non-retryable errors
                if not is_retryable:
                    raise

                # Stop after the last attempt
                if attempt == max_attempts - 1:
                    raise

                wait_time = 2 ** (attempt + 1)

                logger.warning(
                    f"Gemini temporary error. "
                    f"Attempt {attempt + 1}/{max_attempts}. "
                    f"Retrying in {wait_time} seconds. "
                    f"Error: {e}"
                )

                await asyncio.sleep(wait_time)

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """Generate a normal text response from the LLM."""

        try:
            logger.info(f"Generating completion using {self.provider}")

            if self.provider == "gemini":
                from google.genai import types

                response = await self._generate_gemini_with_retry(
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )

                return response.text or ""

            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                return response.choices[0].message.content or ""

        except Exception as e:
            logger.exception("LLM completion failed")

            raise RuntimeError(
                f"LLM generation failed ({self.provider}): {e}"
            ) from e

    async def generate_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_model: Any = None,
    ) -> Dict[str, Any]:
        """
        Generate JSON and optionally validate it against a Pydantic model.
        """

        try:
            logger.info(
                f"Generating structured JSON using {self.provider}"
            )

            json_instruction = (
                "\nReturn ONLY valid JSON. Do not include markdown fences "
                "or additional explanations."
            )

            if self.provider == "gemini":
                from google.genai import types

                response = await self._generate_gemini_with_retry(
                    contents=user_prompt + json_instruction,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                        response_mime_type="application/json",
                    ),
                )

                raw_text = response.text or ""

            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content:": system_prompt + json_instruction,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )

                raw_text = response.choices[0].message.content or ""

            # Parse JSON response
            data = json.loads(raw_text)

            # Validate using Pydantic if schema is provided
            if schema_model is not None:

                if hasattr(schema_model, "model_validate"):
                    data = schema_model.model_validate(data)
                    return data.model_dump()

                elif hasattr(schema_model, "parse_obj"):
                    data = schema_model.parse_obj(data)
                    return data.dict()

            # Ensure response is a dictionary
            if not isinstance(data, dict):
                raise ValueError(
                    "LLM response must be a JSON object."
                )

            return data

        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON returned by LLM")

            raise RuntimeError(
                "LLM returned invalid JSON."
            ) from e

        except Exception as e:
            logger.exception("Structured LLM generation failed")

            raise RuntimeError(
                f"Structured generation failed ({self.provider}): {e}"
            ) from e


if __name__ == "__main__":
    service = LLMService(provider="gemini")
    print(
        "LLMService initialized successfully:",
        service.provider
    )
