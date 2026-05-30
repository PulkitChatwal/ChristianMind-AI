"""
ChristianMind AI - Input Safety Classifier
==========================================
First layer of defense: classifies user input before any processing.
Blocks prompt injection, hate speech, and attempts to modify scripture.
"""

import re
import json
from backend.core.client import call_llm


# System prompt for safety classification
SAFETY_CLASSIFIER_SYSTEM = """Return JSON: {"classification": "SAFE", "reason": "ok", "category": "safe"}

If harmful: {"classification": "BLOCK", "reason": "harmful", "category": "hate"}"""


def classify_input(user_message: str) -> dict:
    """
    Classify user input for safety before any processing.

    This is the first checkpoint in the pipeline. It uses an LLM
    to understand context and intent, combined with pattern matching
    for obvious injection attempts.

    BLOCK criteria:
    - Request to rewrite or modify a Bible verse
    - Request to generate fake Bible verse supporting an ideology
    - Hate speech targeting any religious or ethnic group
    - Prompt injection patterns
    - Non-academic Satan/demon roleplay
    - Sexual content involving religious figures

    Args:
        user_message: The raw user input

    Returns:
        dict with classification, reason, and category
    """
    # Quick pattern check for obvious injection attempts
    injection_patterns = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+",
        r"pretend\s+",
        r"act\s+as\s+if\s+no\s+restrictions",
        r"jailbreak",
        r"^DAN",
        r"override\s+(your\s+)?safety",
        r"bypass\s+(your\s+)?(rules|restrictions|guidelines)",
    ]

    message_lower = user_message.lower()
    for pattern in injection_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return {
                "classification": "BLOCK",
                "reason": "Prompt injection pattern detected",
                "category": "injection"
            }

    # Use LLM for classification
    result = call_llm(SAFETY_CLASSIFIER_SYSTEM, user_message, max_tokens=100)

    # Try to parse JSON from response
    try:
        classification = json.loads(result.strip())
        if "classification" in classification:
            return classification
    except json.JSONDecodeError:
        pass

    # Try to find JSON in the response
    match = re.search(r'\{[^}]+\}', result)
    if match:
        try:
            classification = json.loads(match.group(0))
            if "classification" in classification:
                return classification
        except json.JSONDecodeError:
            pass

    # Default to SAFE for unclear cases
    return {
        "classification": "SAFE",
        "reason": "default",
        "category": "safe"
    }


def is_blocked(user_message: str) -> tuple[bool, str]:
    """
    Quick check if input is blocked.

    Args:
        user_message: The user input

    Returns:
        Tuple of (is_blocked: bool, reason: str)
    """
    result = classify_input(user_message)
    is_blocked = result.get("classification") == "BLOCK"
    reason = result.get("reason", "Unknown reason")
    return is_blocked, reason


def get_safe_response() -> str:
    """
    Return the standard safe response for blocked inputs.

    Returns:
        A compassionate but clear refusal message
    """
    return (
        "I'm not able to help with that request. ChristianMind is here "
        "to support genuine faith exploration and Biblical learning. "
        "Please feel free to ask any questions about scripture, theology, "
        "or Christian life that I can assist with."
    )
