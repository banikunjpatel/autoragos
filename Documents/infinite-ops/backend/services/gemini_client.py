import json
import os
from typing import List, Dict, Any

import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiClient:
    def __init__(self):
        self.text_model_name = "gemini-1.5-pro"
        self.embed_model_name = "models/text-embedding-004"

    def extract_text_from_file(self, file_obj: Dict[str, Any]) -> str:
        if not GEMINI_API_KEY:
            return ""

        data = file_obj["data"]
        mime_type = file_obj.get("content_type") or "application/octet-stream"

        model = genai.GenerativeModel(self.text_model_name)

        prompt = (
            "You are a document text extractor. "
            "Read the content of the attached file and return ONLY the plain text content, "
            "with no formatting, explanations, or extra commentary."
        )

        resp = model.generate_content(
            contents=[
                {"mime_type": mime_type, "data": data},
                {"text": prompt},
            ]
        )

        return (resp.text or "").strip()

    def chunk_text_for_rag(self, text: str, max_chars: int = 800) -> List[Dict[str, str]]:
        chunks = []
        current = []
        current_len = 0

        for paragraph in text.split("\n"):
            p = paragraph.strip()
            if not p:
                continue
            if current_len + len(p) + 1 > max_chars and current:
                chunks.append({"text": "\n".join(current)})
                current = [p]
                current_len = len(p)
            else:
                current.append(p)
                current_len += len(p) + 1

        if current:
            chunks.append({"text": "\n".join(current)})

        return chunks

    def embed_text(self, text: str) -> List[float]:
        if not GEMINI_API_KEY:
            return []

        res = genai.embed_content(
            model=self.embed_model_name,
            content=text,
        )
        return res["embedding"]
