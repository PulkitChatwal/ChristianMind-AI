"""
ChristianMind AI - Response Generator Module
=============================================
Main LLM call for generating contextual, grounded responses.
Uses conversation history for multi-turn dialogue.
"""

from typing import Optional
import re
from backend.core.client import call_llm_with_history
from backend.core.rag import format_verses_for_context, retrieve_similar_verses
from backend.core.citation_validator import lookup_verse, load_bible_index


# System prompt for the generator - defined as constant at module level
GENERATOR_SYSTEM_TEMPLATE = """You are ChristianMind, a knowledgeable and
compassionate Christian AI assistant grounded in Biblical truth.
You speak with warmth, humility, and theological accuracy.

RULES YOU MUST FOLLOW:
1. Only cite Bible verses from the GROUNDING CONTEXT below, or
   use [VERIFY:BookName:Chapter:Verse] tags for lookup.
2. Never invent verse text. If asked about a specific verse,
   look it up in the context or use [VERIFY:...] tag.
3. Cite format: BookName Chapter:Verse (KJV)
4. For theologically disputed topics, present each tradition's view.
5. For genuinely difficult questions, present multiple serious
   theological positions with the scriptures each tradition uses.
6. Maintain tone: pastoral warmth + intellectual honesty +
   epistemic humility.
7. Never claim certainty where scripture is genuinely ambiguous.

Current denomination context: {denomination}

GROUNDING CONTEXT (verified verse lookups — cite from these):
{retrieved_verses}
"""


def extract_verse_reference(text: str) -> list:
    """Extract verse references like 'John 1:45' from text."""
    pattern = r'([A-Za-z1-3\s]+)\s+(\d+):(\d+)'
    matches = re.findall(pattern, text)

    references = []
    for match in matches:
        book = match[0].strip()
        chapter = int(match[1])
        verse = int(match[2])
        references.append({"book": book, "chapter": chapter, "verse": verse})

    return references


def lookup_verses_for_question(question: str) -> list[dict]:
    """
    Look up specific verse references mentioned in the question.
    This ensures accurate answers for specific verse queries.
    """
    # Ensure bible index is loaded
    load_bible_index()

    refs = extract_verse_reference(question)

    if not refs:
        # No specific verses mentioned, use RAG
        return retrieve_similar_verses(question, top_k=7)

    # Look up each mentioned verse
    looked_up = []
    for ref in refs:
        text = lookup_verse(ref["book"], ref["chapter"], ref["verse"])
        if text:
            looked_up.append({
                "reference": f"{ref['book']} {ref['chapter']}:{ref['verse']}",
                "text": text,
                "book": ref["book"],
                "chapter": ref["chapter"],
                "verse_num": ref["verse"]
            })

    # If we found the verses, use them
    if looked_up:
        # Also get semantic matches for context
        semantic = retrieve_similar_verses(question, top_k=5)
        # Combine, preferring exact lookups
        combined = looked_up + [v for v in semantic if v not in looked_up]
        return combined[:7]

    # Fall back to RAG
    return retrieve_similar_verses(question, top_k=7)


def build_generator_system_prompt(denomination: str,
                                   retrieved_verses: list[dict]) -> str:
    """Build the system prompt for the generator with current context."""
    verses_context = format_verses_for_context(retrieved_verses)

    return GENERATOR_SYSTEM_TEMPLATE.format(
        denomination=denomination,
        retrieved_verses=verses_context
    )


def generate_response(
    user_message: str,
    conversation_history: list[dict],
    denomination: str,
    retrieved_verses: list[dict],
    max_tokens: int = 1024
) -> str:
    """Generate a contextual response using the LLM."""
    # Build system prompt with denomination context and retrieved verses
    system_prompt = build_generator_system_prompt(denomination, retrieved_verses)

    # Build messages list
    messages = []
    for hist in conversation_history:
        role = hist.get("role", "user")
        content = hist.get("content", "")
        messages.append({"role": role, "content": content})

    # Add current message
    messages.append({"role": "user", "content": user_message})

    # Generate response
    response = call_llm_with_history(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=max_tokens
    )

    return response


def generate_simple_response(
    user_message: str,
    denomination: str,
    retrieved_verses: list[dict],
    max_tokens: int = 1024
) -> str:
    """Generate a response without conversation history."""
    return generate_response(
        user_message=user_message,
        conversation_history=[],
        denomination=denomination,
        retrieved_verses=retrieved_verses,
        max_tokens=max_tokens
    )
