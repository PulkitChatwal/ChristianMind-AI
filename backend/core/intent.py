"""
ChristianMind AI - Intent Classifier
=====================================
Classifies user message intent to route through appropriate pipeline.
Determines whether this is a question, devotional request, image generation, etc.
"""

import json
from backend.core.client import call_llm


# System prompt for intent classification
INTENT_CLASSIFIER_SYSTEM = """Classify this message. Return JSON only:
{"intent": "QUESTION", "confidence": 0.8, "reason": "ok"}

IMAGE_REQUEST if: asks for image, picture, generate image, visualize.
QUESTION if: asks what, who, how, why about Bible/topics.
OTHER for everything else."""


INTENT_CLASSES = [
    "QUESTION", "DEVOTIONAL", "IMAGE_REQUEST", "DEBATE",
    "EXPLANATION", "PRAYER_REQUEST", "SCRIPTURE_LOOKUP",
    "COMPARATIVE", "OTHER"
]


def classify_intent(user_message: str) -> dict:
    """Classify message intent."""
    result = call_llm(INTENT_CLASSIFIER_SYSTEM, user_message, max_tokens=100)

    # Check for image request keywords first
    message_lower = user_message.lower()
    image_keywords = ['image', 'picture', 'generate', 'visualize', 'draw', 'create image']
    if any(kw in message_lower for kw in image_keywords):
        return {
            "intent": "IMAGE_REQUEST",
            "confidence": 0.9,
            "reason": "contains image request keywords"
        }

    import re
    try:
        classification = json.loads(result.strip())
        if classification.get("intent") in INTENT_CLASSES:
            return classification
    except json.JSONDecodeError:
        pass

    # Try to find JSON in response
    match = re.search(r'\{[^}]+\}', result)
    if match:
        try:
            classification = json.loads(match.group(0))
            if classification.get("intent") in INTENT_CLASSES:
                return classification
        except json.JSONDecodeError:
            pass

    # Default to QUESTION
    return {
        "intent": "QUESTION",
        "confidence": 0.5,
        "reason": "default"
    }


def is_image_request(user_message: str) -> bool:
    """
    Quick check if message is an image request.

    Args:
        user_message: The user's message

    Returns:
        True if intent is IMAGE_REQUEST
    """
    result = classify_intent(user_message)
    return result.get("intent") == "IMAGE_REQUEST"
