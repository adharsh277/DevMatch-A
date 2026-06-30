from __future__ import annotations

import json
import logging
import re
from typing import Any

import google.generativeai as genai
from pydantic import ValidationError

from prompt import build_analysis_prompt
from response_model import AnalysisResponse


class GeminiService:
    def __init__(self, api_key: str | None, model_name: str, timeout_seconds: int) -> None:
        self._logger = logging.getLogger(__name__)
        self._timeout_seconds = timeout_seconds
        self._model = None

        if api_key:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(model_name)

    def analyze(self, resume_text: str, job_description: str) -> AnalysisResponse:
        if self._model is None:
            raise RuntimeError("AI temporarily unavailable")

        prompt = build_analysis_prompt(resume_text, job_description)

        try:
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                },
                request_options={"timeout": self._timeout_seconds},
            )
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            self._logger.exception("Gemini request failed")
            raise RuntimeError("AI temporarily unavailable") from exc

        payload = self._parse_response_payload(self._extract_text(response))
        return self._validate_payload(payload)

    def _extract_text(self, response: Any) -> str:
        response_text = getattr(response, "text", None)
        if response_text:
            return str(response_text)

        candidates = getattr(response, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []
            text_parts = [getattr(part, "text", "") for part in parts if getattr(part, "text", "")]
            if text_parts:
                return "".join(text_parts)

        raise RuntimeError("AI temporarily unavailable")

    def _parse_response_payload(self, raw_text: str) -> dict[str, Any]:
        cleaned_text = raw_text.strip()
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        json_match = re.search(r"\{.*\}", cleaned_text, flags=re.DOTALL)
        if json_match:
            cleaned_text = json_match.group(0)

        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("AI temporarily unavailable") from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("AI temporarily unavailable")

        return parsed

    def _validate_payload(self, payload: dict[str, Any]) -> AnalysisResponse:
        normalized = {
            "score": self._coerce_int(payload.get("score"), "score"),
            "recommendation": self._coerce_recommendation(payload.get("recommendation")),
            "strengths": self._coerce_string_list(payload.get("strengths")),
            "weaknesses": self._coerce_string_list(payload.get("weaknesses")),
            "missing_skills": self._coerce_string_list(payload.get("missing_skills")),
            "suggestions": self._coerce_string_list(payload.get("suggestions")),
            "interview_probability": self._coerce_int(payload.get("interview_probability"), "interview_probability"),
        }

        try:
            return AnalysisResponse.model_validate(normalized)
        except ValidationError as exc:
            raise RuntimeError("AI temporarily unavailable") from exc

    @staticmethod
    def _coerce_int(value: Any, field_name: str) -> int:
        if isinstance(value, bool) or value is None:
            raise RuntimeError(f"Invalid {field_name}")

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        match = re.search(r"-?\d+", str(value))
        if not match:
            raise RuntimeError(f"Invalid {field_name}")

        return int(match.group(0))

    @staticmethod
    def _coerce_recommendation(value: Any) -> str:
        normalized = str(value or "").strip().title()
        allowed = {"Apply", "Consider", "Do Not Apply"}
        if normalized not in allowed:
            raise RuntimeError("Invalid recommendation")
        return normalized

    @staticmethod
    def _coerce_string_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []

        return [str(value).strip()]