"""
ChristianMind AI - Denomination Detector
=========================================
Detects and manages denominational context for theological responses.
Supports Catholic, Protestant, Orthodox, Evangelical, and Non-denominational.
"""

import json
from typing import Optional
from backend.core.client import call_llm


# Available denominations
DENOMINATIONS = [
    "CATHOLIC", "PROTESTANT", "ORTHODOX",
    "EVANGELICAL", "NONDENOMINATIONAL"
]

DEFAULT_DENOMINATION = "NONDENOMINATIONAL"

# System prompt for denomination detection - defined as constant at module level
DENOMINATION_DETECTOR_SYSTEM = """You are a denominational context detector for a Christian AI assistant.
Based on the user's message, determine if they have a denominational context.

Look for:
- Explicit denominational references (Catholic, Protestant, Orthodox, etc.)
- Theological positions that suggest a tradition (sacramental vs. symbolic baptism, etc.)
- Questions about specific denominational practices
- Neutral/general Christian questions

Return ONLY valid JSON:
{
  "detected_denomination": "CATHOLIC|PROTESTANT|ORTHODOX|EVANGELICAL|NONDENOMINATIONAL",
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}

If no specific denomination is indicated, default to NONDENOMINATIONAL."""


# Session storage: maps session_id -> denomination
_session_denominations: dict[str, str] = {}


def detect_denomination(user_message: str) -> tuple[str, float]:
    """
    Detect the denominational context from user message.

    This helps provide more tailored theological responses.
    For example, a Catholic asking about saints gets a different
    answer than a Protestant asking the same question.

    Args:
        user_message: The user's message

    Returns:
        Tuple of (denomination: str, confidence: float)
    """
    result = call_llm(DENOMINATION_DETECTOR_SYSTEM, user_message, max_tokens=200)

    try:
        detection = json.loads(result)
        denom = detection.get("detected_denomination", DEFAULT_DENOMINATION)

        # Validate denomination
        if denom not in DENOMINATIONS:
            denom = DEFAULT_DENOMINATION

        confidence = detection.get("confidence", 0.5)
        return denom, confidence

    except json.JSONDecodeError:
        return DEFAULT_DENOMINATION, 0.0


def get_denomination(session_id: str, user_message: str,
                     explicit_denomination: Optional[str] = None) -> str:
    """
    Get the denominational context for a session.

    Priority:
    1. Explicitly provided denomination (from UI selector)
    2. Detected from message context
    3. Stored session preference
    4. Default: NONDENOMINATIONAL

    Args:
        session_id: The current session UUID
        user_message: The user's message
        explicit_denomination: Optional override from UI

    Returns:
        The determined denomination string
    """
    # Priority 1: Explicit override
    if explicit_denomination and explicit_denomination in DENOMINATIONS:
        _session_denominations[session_id] = explicit_denomination
        return explicit_denomination

    # Priority 2: Detection from message
    detected, confidence = detect_denomination(user_message)
    if confidence > 0.6:
        _session_denominations[session_id] = detected
        return detected

    # Priority 3: Stored session preference
    if session_id in _session_denominations:
        return _session_denominations[session_id]

    # Priority 4: Default
    _session_denominations[session_id] = DEFAULT_DENOMINATION
    return DEFAULT_DENOMINATION


def set_denomination(session_id: str, denomination: str) -> bool:
    """
    Set a session's denominational preference.

    Args:
        session_id: The session UUID
        denomination: One of the valid denominations

    Returns:
        True if successfully set, False if invalid denomination
    """
    if denomination not in DENOMINATIONS:
        return False

    _session_denominations[session_id] = denomination
    return True


def get_denomination_info(denomination: str) -> dict:
    """
    Get metadata about a denomination for UI display.

    Args:
        denomination: The denomination string

    Returns:
        Dict with display name, description, and key characteristics
    """
    info = {
        "CATHOLIC": {
            "display_name": "Catholic",
            "description": "Roman Catholic Church - sacramental theology, Mary and saints, papal authority",
            "key_traits": ["Sacramental grace", "Communion of Saints", "Magisterial authority"]
        },
        "PROTESTANT": {
            "display_name": "Protestant",
            "description": "Reformation traditions - sola scriptura, justification by faith",
            "key_traits": ["Scripture alone", "Faith alone", "Grace alone"]
        },
        "ORTHODOX": {
            "display_name": "Eastern Orthodox",
            "description": "Byzantine tradition - apostolic succession, icons, theosis",
            "key_traits": ["Theosis (divinization)", "Patrearchal authority", "Icons as sacred"]
        },
        "EVANGELICAL": {
            "display_name": "Evangelical",
            "description": "Bible-focused, salvation-focused - personal faith, missions",
            "key_traits": ["Inerrancy", "Personal conversion", "Biblical authority"]
        },
        "NONDENOMINATIONAL": {
            "display_name": "Non-denominational",
            "description": "Independent churches without specific denominational affiliation",
            "key_traits": ["Flexibility", "Biblical focus", "Independence"]
        }
    }

    return info.get(denomination, info["NONDENOMINATIONAL"])
