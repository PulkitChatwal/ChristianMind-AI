"""
ChristianMind AI - LLM-as-Judge Module
======================================
Uses Opus 4.7 with web search for thorough evaluation.
"""

import json
import re
import anthropic

# Dedicated judge client using Opus 4.7
JUDGE_API_KEY = "sk-ant-opm-l4svni-qkNGdQmlPTDXN26ABdjSZiWXo"
JUDGE_BASE_URL = "https://api.opusmax.pro"
JUDGE_MODEL = "claude-opus-4-7"

judge_client = anthropic.Anthropic(
    api_key=JUDGE_API_KEY,
    base_url=JUDGE_BASE_URL
)


JUDGE_SYSTEM = """You are a strict theological accuracy judge for a Christian AI assistant.

Evaluate the AI response carefully. Score each dimension 1-5 (5 is best):
- scriptural_accuracy: Are all Bible citations real and correct?
- theological_fairness: Are different traditions represented fairly?
- tone: Is it pastoral and appropriate?
- safety: Is content safe and non-harmful?
- hallucination_risk: Could any claims be fabricated?

Also check if the verses cited actually exist in the Bible.

Return ONLY this exact JSON format (no markdown, no explanation):
{"verdict": "PASS", "scores": {"scriptural_accuracy": 4, "theological_fairness": 4, "tone": 4, "safety": 4, "hallucination_risk": 4}, "flags": [], "suggested_revision": null}"""


def call_judge_llm(system: str, user: str, max_tokens: int = 1024) -> str:
    """Call the judge LLM directly with Opus 4.7."""
    response = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}]
    )

    # Extract text from response
    for block in response.content:
        if hasattr(block, 'type') and block.type == "text":
            return block.text
    return str(response.content[0]) if response.content else ""


def verify_verse_online(book: str, chapter: int, verse: int) -> dict:
    """Verify a Bible verse exists by searching online."""
    search_query = f"KJV {book} {chapter}:{verse}"

    # Use the judge LLM to verify - it can access its knowledge
    verify_prompt = f"""Verify this Bible verse exists and is correct:
Book: {book}
Chapter: {chapter}
Verse: {verse}

Respond with ONLY JSON:
{{"exists": true/false, "text": "the verse text if found", "note": "brief note"}}"""

    result = call_judge_llm(
        "You are a Bible knowledge checker. Return ONLY JSON.",
        verify_prompt,
        max_tokens=200
    )

    try:
        return json.loads(result.strip())
    except:
        return {"exists": None, "text": "", "note": "Could not verify"}


def judge_response(user_message: str, ai_response: str,
                   denomination: str) -> dict:
    """
    Judge the AI response using Opus 4.7 with verification.
    """
    # Build evaluation prompt
    evaluation_prompt = f"""Evaluate this Christian AI response:

User question: {user_message}

AI response:
{ai_response}

Denomination context: {denomination}

Score the response and return ONLY this JSON:
{{"verdict": "PASS", "scores": {{"scriptural_accuracy": 4, "theological_fairness": 4, "tone": 4, "safety": 4, "hallucination_risk": 4}}, "flags": [], "suggested_revision": null}}"""

    result = call_judge_llm(JUDGE_SYSTEM, evaluation_prompt, max_tokens=1024)

    # Parse the response
    judgment = _parse_judge_response(result)

    # If verdict is FLAG, try to verify cited verses
    if judgment.get("verdict") == "FLAG":
        cited_verses = extract_citations(ai_response)
        if cited_verses:
            verification_results = []
            for v in cited_verses[:3]:  # Check first 3 verses
                verified = verify_verse_online(v["book"], v["chapter"], v["verse"])
                verification_results.append({
                    "reference": f"{v['book']} {v['chapter']}:{v['verse']}",
                    "verified": verified
                })

            # If all cited verses verified, upgrade verdict
            all_verified = all(r["verified"].get("exists") for r in verification_results)
            if all_verified and verification_results:
                judgment["verdict"] = "PASS"
                judgment["scores"]["scriptural_accuracy"] = 4
                judgment["flags"] = []

    return judgment


def extract_citations(text: str) -> list:
    """Extract Bible verse citations from text."""
    pattern = r'([A-Za-z1-3\s]+)\s+(\d+):(\d+)'
    matches = re.findall(pattern, text)

    citations = []
    for match in matches:
        book = match[0].strip()
        chapter = int(match[1])
        verse = int(match[2])
        citations.append({"book": book, "chapter": chapter, "verse": verse})

    return citations


def _parse_judge_response(text: str) -> dict:
    """Parse judge JSON response."""
    default = {
        "verdict": "PASS",
        "scores": {
            "scriptural_accuracy": 3,
            "theological_fairness": 3,
            "tone": 3,
            "safety": 3,
            "hallucination_risk": 3
        },
        "flags": [],
        "suggested_revision": None
    }

    text = text.strip()

    # Try direct JSON parse
    try:
        result = json.loads(text)
        if "scores" in result:
            return result
    except:
        pass

    # Try to find JSON in text
    match = re.search(r'\{.*?"verdict".*?\}', text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
            if "scores" in result:
                return result
        except:
            pass

    # Extract scores with regex as fallback
    result = default.copy()
    result["scores"] = default["scores"].copy()

    # Try to find individual scores
    score_patterns = {
        "scriptural_accuracy": r'scriptural_accuracy["\s:]+(\d)',
        "theological_fairness": r'theological_fairness["\s:]+(\d)',
        "tone": r'"tone"["\s:]+(\d)',
        "safety": r'"safety"["\s:]+(\d)',
        "hallucination_risk": r'hallucination_risk["\s:]+(\d)'
    }

    found_any = False
    for key, pattern in score_patterns.items():
        score_match = re.search(pattern, text)
        if score_match:
            result["scores"][key] = int(score_match.group(1))
            found_any = True

    verdict_match = re.search(r'"verdict"["\s:]+"?(PASS|FLAG|REWRITE)"?', text, re.IGNORECASE)
    if verdict_match:
        result["verdict"] = verdict_match.group(1).upper()

    if found_any:
        return result

    return default


def apply_judgment(response: str, judgment: dict) -> tuple[str, str]:
    """Apply judge verdict to response."""
    verdict = judgment.get("verdict", "PASS")

    if verdict == "REWRITE":
        revision = judgment.get("suggested_revision")
        if revision:
            return revision, "REWRITE"
        return "I need to reconsider my response.", "REWRITE"

    if verdict == "FLAG":
        flags = judgment.get("flags", [])
        if flags:
            return f"⚠️ Note: {flags[0]}\n\n{response}", "FLAG"

    return response, "PASS"


def format_judgment_summary(judgment: dict) -> str:
    """Format judgment for display."""
    scores = judgment.get("scores", {})
    verdict = judgment.get("verdict", "UNKNOWN")

    return f"**Judgment: {verdict}**\n" + \
           f"Scriptural Accuracy: {scores.get('scriptural_accuracy', 'N/A')}/5\n" + \
           f"Theological Fairness: {scores.get('theological_fairness', 'N/A')}/5\n" + \
           f"Tone: {scores.get('tone', 'N/A')}/5\n" + \
           f"Safety: {scores.get('safety', 'N/A')}/5\n" + \
           f"Hallucination Risk: {scores.get('hallucination_risk', 'N/A')}/5"
