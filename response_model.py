from typing import Literal

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    recommendation: Literal["Apply", "Consider", "Do Not Apply"]
    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    interview_probability: int = Field(ge=0, le=100)


class ErrorResponse(BaseModel):
    error: str