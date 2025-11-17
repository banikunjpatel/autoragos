import logging
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette import status
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

from services.gemini_client import GeminiClient
from services.qdrant_client import upsert_chunk, search_chunks
from services.opus_client import run_review_workflow


app = FastAPI(title="AutoRAG OS Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


gemini_client = GeminiClient()


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)


async def _read_files(files: List[UploadFile]) -> List[Dict[str, Any]]:
    file_objs: List[Dict[str, Any]] = []
    for f in files:
        data = await f.read()
        file_objs.append(
            {
                "filename": f.filename,
                "content_type": f.content_type,
                "data": data,
            }
        )
    return file_objs


@app.post("/api/workspaces/{workspace_id}/upload")
async def upload_workspace_data(
    workspace_id: str = Path(...),
    files: List[UploadFile] = File(...),
) -> Dict[str, Any]:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file must be provided.",
        )

    try:
        file_objs = await _read_files(files)
        total_chunks = 0

        for file_obj in file_objs:
            text = await _extract_text_for_rag(file_obj)
            if not text:
                continue

            chunks = gemini_client.chunk_text_for_rag(text)
            for idx, chunk in enumerate(chunks):
                chunk_text = (chunk.get("text") or "").strip()
                if not chunk_text:
                    continue

                vector = gemini_client.embed_text(chunk_text)
                if not vector:
                    continue

                payload = {
                    "workspace_id": workspace_id,
                    "filename": file_obj["filename"],
                    "chunk_index": idx,
                    "text": chunk_text,
                }

                upsert_chunk(workspace_id, vector, payload)
                total_chunks += 1

        return {"workspace_id": workspace_id, "chunks_indexed": total_chunks}

    except Exception as exc:
        logger.exception("Failed to process workspace upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@app.post("/api/workspaces/{workspace_id}/ask")
async def ask_workspace(
    workspace_id: str = Path(...),
    body: AskRequest = None,
) -> Dict[str, Any]:
    if body is None or not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required.",
        )

    question = body.question.strip()

    try:
        q_vector = gemini_client.embed_text(question)
        if not q_vector:
            raise RuntimeError("Failed to embed question")

        retrieved = search_chunks(workspace_id, q_vector, limit=5)

        context_chunks: List[Dict[str, Any]] = []
        for hit in retrieved:
            context_chunks.append(
                {
                    "text": hit.get("text", ""),
                    "source": hit.get("filename", ""),
                    "chunk_index": hit.get("chunk_index", -1),
                }
            )

        rag_result = gemini_client.answer_with_context(
            question=question, context_chunks=context_chunks,
        )

        return {
            "workspace_id": workspace_id,
            "question": question,
            "context_chunks": context_chunks,
            "rag_result": rag_result,
        }

    except Exception as exc:
        logger.exception("Failed to process ask request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


async def _extract_text_for_rag(file_obj: Dict[str, Any]) -> str:
    text = gemini_client.extract_text_from_file(file_obj)
    return text or ""
