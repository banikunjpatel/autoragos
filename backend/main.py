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


class Citation(BaseModel):
    source: str
    chunk_index: int


class RagResult(BaseModel):
    answer: str
    confidence: float
    citations: List[Citation]
    needs_human_review: bool
    review_comment: str


class ContextChunk(BaseModel):
    text: str
    source: str
    chunk_index: int


class AskResponse(BaseModel):
    workspace_id: str
    question: str
    context_chunks: List[ContextChunk]
    rag_result: RagResult


class UploadResponse(BaseModel):
    workspace_id: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str


gemini_client = GeminiClient()


async def _read_files(files: List[UploadFile]) -> List[Dict[str, Any]]:
    file_objs = []
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


async def _extract_text_for_rag(file_obj: Dict[str, Any]) -> str:
    text = gemini_client.extract_text_from_file(file_obj)
    return text or ""


@app.get("/health")
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/api/workspaces/{workspace_id}/upload")
async def upload_workspace_data(
    workspace_id: str = Path(...),
    files: List[UploadFile] = File(...),
) -> UploadResponse:
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
                chunk_text = chunk.get("text", "").strip()
                if not chunk_text:
                    continue

                vector = gemini_client.embed_text(chunk_text)

                payload = {
                    "workspace_id": workspace_id,
                    "filename": file_obj["filename"],
                    "chunk_index": idx,
                    "text": chunk_text,
                }

                upsert_chunk(workspace_id, vector, payload)
                total_chunks += 1

        return UploadResponse(workspace_id=workspace_id, chunks_indexed=total_chunks)

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
) -> AskResponse:
    if body is None or not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required.",
        )

    question = body.question.strip()

    try:
        # 1) Embed question and retrieve chunks from Qdrant
        q_vector = gemini_client.embed_text(question)
        retrieved = search_chunks(workspace_id, q_vector, limit=5)

        context_chunks = []
        for hit in retrieved:
            context_chunks.append(
                ContextChunk(
                    text=hit.get("text", ""),
                    source=hit.get("filename", ""),
                    chunk_index=hit.get("chunk_index", -1),
                )
            )

        # 2) Local RAG answer with Gemini
        base_result = gemini_client.answer_with_context(question, context_chunks)
        # base_result = { "answer", "confidence", "citations" }

        # 3) Minimal review with Opus (optional governance layer)
        review_result = run_review_workflow(question, base_result)

        final_answer = review_result.get("approved_answer") or base_result.get("answer", "")
        needs_human_review = review_result.get("needs_human_review", False)
        review_comment = (
            review_result.get("review_comment")
            or review_result.get("explanation")
            or ""
        )
        # Allow Opus to override citations if it wants, else keep base
        final_citations = review_result.get("citations") or base_result.get("citations", [])
        final_confidence = base_result.get("confidence", 0.0)

        rag_result = RagResult(
            answer=final_answer,
            confidence=final_confidence,
            citations=[Citation(source=c.get("source", ""), chunk_index=c.get("chunk_index", -1)) for c in final_citations],
            needs_human_review=needs_human_review,
            review_comment=review_comment,
        )

        return AskResponse(
            workspace_id=workspace_id,
            question=question,
            context_chunks=context_chunks,
            rag_result=rag_result,
        )

    except Exception as exc:
        logger.exception("Failed to process ask request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
