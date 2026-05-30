"""
ChristianMind AI - Anthropic Client Module
==========================================
SINGLE SOURCE OF TRUTH for all LLM calls in this project.
Every module imports from here. Never instantiate Anthropic() elsewhere.
"""

import anthropic
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Custom Anthropic proxy configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
MODEL_NAME = "claude-opus-4-7"

# Singleton client instance
client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    base_url=ANTHROPIC_BASE_URL
)


def call_llm(system_prompt: str, user_message: str,
             max_tokens: int = 1024) -> str:
    """
    Single unified function for all LLM calls in this project.
    """
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return _extract_text(response)


def call_llm_with_history(system_prompt: str,
                           messages: list,
                           max_tokens: int = 1024) -> str:
    """
    For chat with conversation history.
    """
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages
    )
    return _extract_text(response)


def _extract_text(response) -> str:
    """Extract text from response, handling various block types."""
    text_parts = []

    for block in response.content:
        # Handle text blocks
        if hasattr(block, 'type') and block.type == "text":
            text_parts.append(block.text)
        # Handle thinking blocks (skip them)
        elif hasattr(block, 'type') and block.type == "thinking":
            continue
        # Handle other block types with text attribute
        elif hasattr(block, 'text'):
            text_parts.append(block.text)

    result = " ".join(text_parts)

    # Try to extract JSON if the response looks like it contains JSON
    if result.strip().startswith('{') or result.strip().startswith('['):
        try:
            # Try to find and parse JSON in the response
            json_match = None
            for start_char in ['{', '[']:
                idx = result.find(start_char)
                if idx != -1:
                    json_str = result[idx:]
                    try:
                        json.loads(json_str)
                        return json_str
                    except json.JSONDecodeError:
                        continue
        except:
            pass

    return result if result else ""