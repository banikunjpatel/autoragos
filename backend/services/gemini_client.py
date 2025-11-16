import json
import os
from typing import List, Dict, Any

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
        self.text_model_name = "gemini-2.5-flash"
        self.embed_model_name = "text-embedding-004"

    def _ensure_client(self) -> bool:
        return self.client is not None

    def extract_text_from_file(self, file_obj: Dict[str, Any]) -> str:
        if not self._ensure_client():
            return ""

        data = file_obj["data"]
        mime_type = file_obj.get("content_type") or "application/octet-stream"

        prompt = (
            "You are a document text extractor. "
            "Read the content of the attached file and return ONLY the plain text content, "
            "with no formatting, explanations, or extra commentary."
        )

        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": data,
                        }
                    },
                    {"text": prompt},
                ],
            }
        ]

        response = self.client.models.generate_content(
            model=self.text_model_name,
            contents=contents,
        )

        return (getattr(response, "text", "") or "").strip()

    def chunk_text_for_rag(self, text: str, max_chars: int = 800) -> List[Dict[str, str]]:
        chunks: List[Dict[str, str]] = []
        current: List[str] = []
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
        if not self._ensure_client():
            return []

        resp = self.client.models.embed_content(
            model=self.embed_model_name,
            contents=[text],
        )

        # Adapt to common response shape: embeddings[0].values
        try:
            return list(resp.embeddings[0].values)
        except Exception:
            return []

    def answer_with_context(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not self._ensure_client():
            return {
                "answer": "",
                "confidence": 0.0,
                "citations": [],
                "error": "GEMINI_API_KEY not configured",
            }

        context_lines: List[str] = []
        for i, ch in enumerate(context_chunks):
            # ContextChunk may be a Pydantic model; normalize to dict-like access.
            if hasattr(ch, "dict"):
                ch_data = ch.dict()
            elif isinstance(ch, dict):
                ch_data = ch
            else:
                ch_data = {
                    "source": getattr(ch, "source", ""),
                    "chunk_index": getattr(ch, "chunk_index", -1),
                    "text": getattr(ch, "text", ""),
                }

            context_lines.append(
                f"[{i}] source={ch_data.get('source','')}, chunk_index={ch_data.get('chunk_index', -1)}\n{ch_data.get('text','')}\n"
            )
        context_text = "\n\n".join(context_lines)

        system_prompt = """
You are an answer-generation agent for a Retrieval-Augmented Generation (RAG) system.

You are given:
- a user's question
- a set of context chunks extracted from the user's private documents

Rules:
1. Use ONLY the provided context to answer. Do NOT use outside knowledge.
2. If the answer is not clearly supported by the context, say:
   "I cannot answer this based on the provided context."
3. Be concise and factual.
4. Provide a confidence score between 0.0 and 1.0 that reflects how well the context supports your answer.
5. Provide citations: a list of objects { "source": string, "chunk_index": number } corresponding to the chunks you used.

Return ONLY valid JSON in this exact format:

{
  "answer": "<string>",
  "confidence": <float between 0 and 1>,
  "citations": [
    { "source": "<string>", "chunk_index": <number> }
  ]
}
"""

        prompt_text = (
            system_prompt
            + "\n\nQuestion:\n"
            + question
            + "\n\nContext Chunks:\n"
            + context_text
        )

        response = self.client.models.generate_content(
            model=self.text_model_name,
            contents=prompt_text,
        )

        raw = (getattr(response, "text", "") or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```", 1)[-1].strip()
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {
                "answer": raw,
                "confidence": 0.5,
                "citations": [],
            }

        answer = parsed.get("answer", "")
        confidence = float(parsed.get("confidence", 0.0) or 0.0)
        citations = parsed.get("citations", [])

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
        }
