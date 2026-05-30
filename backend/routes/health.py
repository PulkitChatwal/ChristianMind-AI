"""
ChristianMind AI - Health Route
==============================
API endpoint for system health and status checks.
"""

from fastapi import APIRouter
import os
import json

from backend.core.citation_validator import get_bible_index_size
from backend.core.rag import get_collection_size


router = APIRouter()


@router.get("")
async def health_check():
    """
    Get system health status.

    Returns:
        Health status including Bible verse counts and ChromaDB size
    """
    bible_size = get_bible_index_size()
    chroma_size = get_collection_size()

    return {
        "status": "ok",
        "service": "ChristianMind AI",
        "version": "1.0.0",
        "bible_verses_indexed": bible_size,
        "chroma_collection_size": chroma_size
    }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe.

    Returns 200 if the service is ready to handle requests.
    """
    bible_size = get_bible_index_size()

    # Service is ready if Bible is indexed
    if bible_size > 0:
        return {"ready": True}
    else:
        return {"ready": False, "reason": "Bible not yet indexed"}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.

    Returns 200 if the service is alive.
    """
    return {"alive": True}
