"""
ChristianMind AI - RAG (Retrieval-Augmented Generation) Module
==============================================================
Retrieves semantically similar Bible verses from ChromaDB to ground responses.
"""

import chromadb
from chromadb.config import Settings
from typing import Optional
import os

# Global ChromaDB client and collection
_chroma_client: Optional[chromadb.PersistentClient] = None
_kjv_collection = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Get or create the ChromaDB persistent client.

    ChromaDB is persisted to disk in backend/data/chroma_db/
    This ensures the index survives restarts.

    Returns:
        ChromaDB PersistentClient instance
    """
    global _chroma_client

    if _chroma_client is None:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "chroma_db"
        )
        os.makedirs(db_path, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

    return _chroma_client


def get_kjv_collection():
    """
    Get the KJV verses collection from ChromaDB.

    Returns the collection object, initializing it if necessary.
    The collection contains verse-level documents with metadata.

    Returns:
        ChromaDB collection object for kjv_verses
    """
    global _kjv_collection

    if _kjv_collection is None:
        client = get_chroma_client()
        _kjv_collection = client.get_or_create_collection(
            name="kjv_verses",
            metadata={"description": "King James Version Bible verses"}
        )

    return _kjv_collection


def retrieve_similar_verses(query: str, top_k: int = 7) -> list[dict]:
    """
    Retrieve semantically similar Bible verses for a query.

    Uses sentence-transformers (all-MiniLM-L6-v2) embeddings
    to find verses relevant to the user's question.

    Args:
        query: The user's question or topic
        top_k: Number of verses to retrieve (default 7)

    Returns:
        List of verse dicts with text and metadata:
        [{"text": "...", "book": "...", "chapter": int, "verse": int}, ...]
    """
    collection = get_kjv_collection()

    try:
        # Query ChromaDB for similar verses
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        verses = []
        if results and results.get("documents"):
            documents = results["documents"][0]
            metadatas = results.get("metadatas", [[]])[0]
            ids = results.get("ids", [[]])[0]

            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}

                verse_info = {
                    "id": ids[i] if i < len(ids) else None,
                    "text": doc,
                    "book": metadata.get("book", ""),
                    "chapter": metadata.get("chapter", 0),
                    "verse_num": metadata.get("verse", 0),
                    "testament": metadata.get("testament", "UNKNOWN"),
                    "reference": f"{metadata.get('book', '')} {metadata.get('chapter', 0)}:{metadata.get('verse', 0)}"
                }
                verses.append(verse_info)

        return verses

    except Exception as e:
        print(f"Error retrieving verses: {e}")
        return []


def format_verses_for_context(verses: list[dict]) -> str:
    """
    Format retrieved verses for injection into LLM context.

    Creates a clean, readable format that the LLM can cite from.

    Args:
        verses: List of verse dicts from retrieve_similar_verses

    Returns:
        Formatted string for context injection
    """
    if not verses:
        return "No relevant verses found."

    formatted = []
    for v in verses:
        ref = v.get("reference", f"{v.get('book', '')} {v.get('chapter', 0)}:{v.get('verse_num', 0)}")
        text = v.get("text", "")
        formatted.append(f"- {ref} — {text}")

    return "\n".join(formatted)


def get_collection_size() -> int:
    """
    Get the number of verses in the ChromaDB collection.

    Returns:
        Total count of verses indexed
    """
    collection = get_kjv_collection()
    try:
        return collection.count()
    except:
        return 0


def check_collection_exists() -> bool:
    """
    Check if the KJV collection already exists.

    Returns:
        True if collection exists with data, False otherwise
    """
    try:
        collection = get_kjv_collection()
        return collection.count() > 0
    except:
        return False
