from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from analyze import ResumeAnalyzer
from config import get_settings
from gemini_service import GeminiService
from pdf_service import PDFService
from response_model import AnalysisResponse, ErrorResponse

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("devmatch")
pdf_service = PDFService()
gemini_service = GeminiService(
    api_key=settings.gemini_api_key,
    model_name=settings.model_name,
    timeout_seconds=settings.gemini_timeout_seconds,
)
analyzer = ResumeAnalyzer(pdf_service=pdf_service, gemini_service=gemini_service, logger=logger)

app = FastAPI(title="DevMatch-A Resume Analyzer API", version="1.0.0")


def get_analyzer() -> ResumeAnalyzer:
    return analyzer


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    message = "Invalid request"
    if exc.errors():
        first_error = exc.errors()[0]
        message = first_error.get("msg", message)
    return JSONResponse(status_code=422, content={"error": message})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def analyze(
    resume: UploadFile | None = File(default=None),
    job_description: str | None = Form(default=None),
    analyzer_service: ResumeAnalyzer = Depends(get_analyzer),
) -> AnalysisResponse:
    return await analyzer_service.analyze(resume=resume, job_description=job_description)