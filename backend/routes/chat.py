"""
ChristianMind AI - Chat Route
=============================
Main API endpoint for chat interactions.
Implements the full pipeline: safety → intent → denomination → RAG → generate → validate → judge.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import time

from backend.core.safety import classify_input, is_blocked, get_safe_response
from backend.core.intent import classify_intent, is_image_request
from backend.core.denomination import get_denomination
from backend.core.generator import lookup_verses_for_question
from backend.core.generator import generate_response
from backend.core.citation_validator import validate_response, load_bible_index
from backend.core.judge import judge_response, apply_judgment
from backend.core.image_pipeline import generate_christian_image


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The user's message")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()),
                            description="Unique session identifier")
    denomination: Optional[str] = Field(None,
                                        description="Optional denomination override")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    verified_citations: list
    hallucinated_citations: list
    judge_scores: dict
    judge_verdict: str
    retrieved_verses: list
    session_id: str
    is_image_request: bool = False
    image_result: Optional[dict] = None


# Session storage for conversation history
session_histories: dict[str, list[dict]] = {}


def get_conversation_history(session_id: str) -> list[dict]:
    """Get or create conversation history for a session."""
    if session_id not in session_histories:
        session_histories[session_id] = []
    return session_histories[session_id]


def add_to_history(session_id: str, role: str, content: str):
    """Add a message to session history."""
    history = get_conversation_history(session_id)
    history.append({"role": role, "content": content})


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message through the full pipeline.

    Pipeline steps:
    1. Safety check - block inappropriate requests
    2. Intent classification - detect IMAGE_REQUEST
    3. Denomination detection
    4. RAG retrieval - get relevant verses
    5. Response generation
    6. Citation validation
    7. LLM-as-judge evaluation
    8. Return response with metadata
    """
    start_time = time.time()

    # Ensure bible index is loaded
    load_bible_index()

    # Step 1: Safety check
    safety_result = classify_input(request.message)

    if safety_result.get("classification") == "BLOCK":
        return ChatResponse(
            response=get_safe_response(),
            verified_citations=[],
            hallucinated_citations=[],
            judge_scores={},
            judge_verdict="PASS",
            retrieved_verses=[],
            session_id=request.session_id
        )

    # Step 2: Intent classification
    intent_result = classify_intent(request.message)

    # Step 3: Get denominational context
    denomination = get_denomination(
        request.session_id,
        request.message,
        request.denomination
    )

    # Handle image requests specially
    if intent_result.get("intent") == "IMAGE_REQUEST":
        image_result = generate_christian_image(request.message)
        return ChatResponse(
            response=f"I'd be happy to generate an image for you! "
                     f"Prompt: {request.message}",
            verified_citations=[],
            hallucinated_citations=[],
            judge_scores={},
            judge_verdict="PASS",
            retrieved_verses=[],
            session_id=request.session_id,
            is_image_request=True,
            image_result=image_result
        )

    # Step 4: RAG retrieval with verse lookup for specific verse questions
    retrieved_verses = lookup_verses_for_question(request.message)

    # Step 5: Generate response
    history = get_conversation_history(request.session_id)
    generated_response = generate_response(
        user_message=request.message,
        conversation_history=history,
        denomination=denomination,
        retrieved_verses=retrieved_verses
    )

    # Step 6: Validate citations
    validation = validate_response(generated_response)

    # Step 7: Judge evaluation
    judgment = judge_response(
        user_message=request.message,
        ai_response=validation["validated_response"],
        denomination=denomination
    )

    # Apply judgment
    final_response, verdict = apply_judgment(
        validation["validated_response"],
        judgment
    )

    # Step 8: Update history
    add_to_history(request.session_id, "user", request.message)
    add_to_history(request.session_id, "assistant", final_response)

    # Limit history size
    history = get_conversation_history(request.session_id)
    if len(history) > 50:
        session_histories[request.session_id] = history[-50:]

    elapsed = time.time() - start_time
    print(f"Chat request processed in {elapsed:.2f}s")

    return ChatResponse(
        response=final_response,
        verified_citations=validation.get("verified", []),
        hallucinated_citations=validation.get("hallucinated", []),
        judge_scores=judgment.get("scores", {}),
        judge_verdict=verdict,
        retrieved_verses=retrieved_verses,
        session_id=request.session_id
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session's conversation history."""
    if session_id in session_histories:
        del session_histories[session_id]
    return {"status": "cleared", "session_id": session_id}


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get info about a session."""
    history = get_conversation_history(session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": history
    }
