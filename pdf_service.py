from __future__ import annotations

import re
from io import BytesIO

from pypdf import PdfReader


class PDFService:
    def extract_text(self, pdf_bytes: bytes) -> str:
        if not pdf_bytes:
            raise ValueError("Could not extract text")

        try:
            reader = PdfReader(BytesIO(pdf_bytes))
        except Exception as exc:  # pragma: no cover - defensive path
            raise ValueError("Could not extract text") from exc

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:  # pragma: no cover - defensive path
                raise ValueError("Could not extract text") from exc

        pages: list[str] = []
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            if page_text.strip():
                pages.append(page_text)

        text = self._clean_text(" ".join(pages))
        if not text:
            raise ValueError("Could not extract text")

        return text

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()