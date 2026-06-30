from __future__ import annotations

import logging

from fastapi import HTTPException, UploadFile

from gemini_service import GeminiService
from pdf_service import PDFService
from response_model import AnalysisResponse


class ResumeAnalyzer:
    def __init__(self, pdf_service: PDFService, gemini_service: GeminiService, logger: logging.Logger) -> None:
        self._pdf_service = pdf_service
        self._gemini_service = gemini_service
        self._logger = logger

    async def analyze(self, resume: UploadFile | None, job_description: str | None) -> AnalysisResponse:
        if resume is None or not resume.filename:
            raise HTTPException(status_code=400, detail="Resume missing")

        if not self._is_pdf(resume):
            raise HTTPException(status_code=400, detail="Resume must be a PDF")

        if job_description is None or not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description required")

        self._logger.info("Resume Uploaded")

        resume_bytes = await resume.read()
        if not resume_bytes:
            raise HTTPException(status_code=400, detail="Resume missing")

        try:
            resume_text = self._pdf_service.extract_text(resume_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Could not extract text") from exc

        self._logger.info("Resume Parsed")
        self._logger.info("Gemini Started")

        try:
            analysis = self._gemini_service.analyze(resume_text, job_description.strip())
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail="AI temporarily unavailable") from exc

        self._logger.info("Gemini Finished")
        self._logger.info("JSON Returned")
        return analysis

    @staticmethod
    def _is_pdf(resume: UploadFile) -> bool:
        filename = (resume.filename or "").lower()
        content_type = (resume.content_type or "").lower()
        return filename.endswith(".pdf") or content_type == "application/pdf"