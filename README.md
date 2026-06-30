# DevMatch-A

Resume matching backend for DevMatch-A. This Phase 1 service exposes a FastAPI endpoint that accepts a resume PDF and a job description, extracts the resume text, sends both inputs to Gemini, and returns structured JSON analysis.

## What it does

- Accepts PDF resume uploads through Swagger or direct API calls.
- Extracts and cleans resume text before sending it to the model.
- Returns a typed JSON payload with score, recommendation, strengths, weaknesses, missing skills, suggestions, and interview probability.
- Logs the request lifecycle for debugging.
- Runs with Docker Compose.

## API

- `POST /analyze` with multipart form fields:
	- `resume`: PDF file
	- `job_description`: pasted job description text
- `GET /health` for a simple readiness check.

## Local setup

1. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
2. Start the service with `docker compose up --build`.
3. Open `http://localhost:8000/docs` and call `POST /analyze`.

## Environment variables

- `GEMINI_API_KEY`
- `MODEL_NAME`
- `LOG_LEVEL`
- `GEMINI_TIMEOUT_SECONDS`

## Notes

- The backend currently supports PDF resumes only.
- Future extension, web, and mobile clients can all reuse this same API.
