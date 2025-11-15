import os
from typing import List, Dict, Any
from uuid import uuid4

from qdrant_client import QdrantClient, models

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "rag_chunks")

VECTOR_SIZE = 768

_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def ensure_collection() -> None:
    try:
        _client.get_collection(QDRANT_COLLECTION)
    except Exception:
        _client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def upsert_chunk(workspace_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
    ensure_collection()

    payload = dict(payload)
    payload["workspace_id"] = workspace_id

    _client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            models.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload=payload,
            )
        ],
    )


def search_chunks(
    workspace_id: str, query_vector: List[float], limit: int = 5
) -> List[Dict[str, Any]]:
    ensure_collection()

    results = _client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="workspace_id", match=models.MatchValue(value=workspace_id))]
        ),
        limit=limit,
    )

    return [hit.payload for hit in results]
