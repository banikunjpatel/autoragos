import os
from typing import Dict, Any

import requests

OPUS_API_KEY = os.getenv("OPUS_API_KEY", "")
OPUS_WORKFLOW_ID = os.getenv("OPUS_WORKFLOW_ID", "")
OPUS_RUN_URL = os.getenv("OPUS_RUN_URL", "https://api.opus.ai/workflow/run")


def run_review_workflow(question: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal use of Opus: send question + base RAG answer for lightweight review.
    If Opus is not configured or fails, return {} and let backend proceed.
    """
    if not (OPUS_API_KEY and OPUS_WORKFLOW_ID):
        return {}

    payload = {
        "workflow_id": OPUS_WORKFLOW_ID,
        "input": {
            "question": question,
            "answer": base_result.get("answer", ""),
            "confidence": base_result.get("confidence", 0.0),
            "citations": base_result.get("citations", []),
        },
    }

    headers = {
        "Authorization": f"Bearer {OPUS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(OPUS_RUN_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        # If anything goes wrong with Opus, just skip review.
        return {}

    # Match your Output node system names:
    approved_answer = data.get("approved_answer") or base_result.get("answer", "")
    needs_human_review = data.get("needs_human_review", False)
    review_comment = data.get("review_comment", "")
    citations = data.get("citations") or base_result.get("citations", [])

    return {
        "approved_answer": approved_answer,
        "needs_human_review": needs_human_review,
        "review_comment": review_comment,
        "citations": citations,
    }
