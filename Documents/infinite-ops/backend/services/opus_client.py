import os
from typing import Dict, Any, List

import requests

OPUS_API_KEY = os.getenv("OPUS_API_KEY", "")
OPUS_WORKFLOW_ID = os.getenv("OPUS_WORKFLOW_ID", "")
OPUS_RUN_URL = os.getenv("OPUS_RUN_URL", "https://api.opus.ai/workflow/run")


def run_rag_workflow(question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not (OPUS_API_KEY and OPUS_WORKFLOW_ID):
        return {
            "error": "OPUS_API_KEY or OPUS_WORKFLOW_ID not configured",
            "answer": "",
            "confidence": 0.0,
            "citations": [],
            "needs_human_review": False,
        }

    payload = {
        "workflow_id": OPUS_WORKFLOW_ID,
        "input": {
            "question": question,
            "context_chunks": context_chunks,
        },
    }

    headers = {
        "Authorization": f"Bearer {OPUS_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(OPUS_RUN_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()
