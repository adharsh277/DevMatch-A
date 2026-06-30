ANALYSIS_JSON_SCHEMA = """{
  "score": 0,
  "recommendation": "Apply",
  "strengths": ["Strong AWS knowledge"],
  "weaknesses": ["Limited Kubernetes experience"],
  "missing_skills": ["Terraform", "Helm"],
  "suggestions": ["Mention AWS projects", "Highlight Linux troubleshooting"],
  "interview_probability": 0
}"""


def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    return (
        "You are an ATS-focused recruiter assistant for DevMatch-A. "
        "Compare the resume to the job description and return only valid JSON. "
        "Do not use markdown, backticks, or commentary. "
        "All arrays must contain short, specific, actionable strings. "
        "The recommendation must be one of: Apply, Consider, Do Not Apply. "
        "Scores and probabilities must be integers from 0 to 100.\n\n"
        "JSON schema:\n"
        f"{ANALYSIS_JSON_SCHEMA}\n\n"
        "Resume:\n"
        f"{resume_text.strip()}\n\n"
        "Job Description:\n"
        f"{job_description.strip()}\n"
    )