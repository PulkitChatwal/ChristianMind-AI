"""
ChristianMind AI - Citation Validator
======================================
Validates Bible verse references against the ground truth index.
Detects hallucinated verses and corrects invalid references.
"""

import re
import json
import os
from typing import Optional

# Global bible index loaded at startup
_bible_index: dict[str, str] = {}
_index_loaded = False


# Book name normalization map - handles abbreviations and aliases
BOOK_ALIASES = {
    # Old Testament
    "gen": "Genesis", "genesis": "Genesis",
    "ex": "Exodus", "exod": "Exodus", "exodus": "Exodus",
    "lev": "Leviticus", "leviticus": "Leviticus",
    "num": "Numbers", "numbers": "Numbers",
    "deut": "Deuteronomy", "deuteronomy": "Deuteronomy",
    "josh": "Joshua", "joshua": "Joshua",
    "judg": "Judges", "judges": "Judges",
    "ruth": "Ruth",
    "1sam": "1Samuel", "1 samuel": "1Samuel", "i samuel": "1Samuel",
    "2sam": "2Samuel", "2 samuel": "2Samuel", "ii samuel": "2Samuel",
    "1ki": "1Kings", "1 kings": "1Kings", "i kings": "1Kings",
    "2ki": "2Kings", "2 kings": "2Kings", "ii kings": "2Kings",
    "1chr": "1Chronicles", "1 chronicles": "1Chronicles", "i chronicles": "1Chronicles",
    "2chr": "2Chronicles", "2 chronicles": "2Chronicles", "ii chronicles": "2Chronicles",
    "ezr": "Ezra", "ezra": "Ezra",
    "neh": "Nehemiah", "nehemiah": "Nehemiah",
    "esth": "Esther", "esther": "Esther",
    "job": "Job",
    "ps": "Psalms", "psa": "Psalms", "pss": "Psalms", "psalm": "Psalms", "psalms": "Psalms",
    "prov": "Proverbs", "proverbs": "Proverbs",
    "eccl": "Ecclesiastes", "ecclesiastes": "Ecclesiastes",
    "song": "SongofSolomon", "sos": "SongofSolomon",
    "song of solomon": "SongofSolomon", "canticles": "SongofSolomon",
    "isa": "Isaiah", "isaiah": "Isaiah",
    "jer": "Jeremiah", "jeremiah": "Jeremiah",
    "lam": "Lamentations", "lamentations": "Lamentations",
    "ezek": "Ezekiel", "ezekiel": "Ezekiel",
    "dan": "Daniel", "daniel": "Daniel",
    "hos": "Hosea", "hosea": "Hosea",
    "joe": "Joel", "joel": "Joel",
    "amos": "Amos",
    "obad": "Obadiah", "obadiah": "Obadiah",
    "jon": "Jonah", "jonah": "Jonah",
    "mic": "Micah", "micah": "Micah",
    "nah": "Nahum", "nahum": "Nahum",
    "hab": "Habakkuk", "habakkuk": "Habakkuk",
    "zeph": "Zephaniah", "zephaniah": "Zephaniah",
    "hag": "Haggai", "haggai": "Haggai",
    "zech": "Zechariah", "zechariah": "Zechariah",
    "mal": "Malachi", "malachi": "Malachi",

    # New Testament
    "matt": "Matthew", "matthew": "Matthew",
    "mk": "Mark", "mark": "Mark",
    "lk": "Luke", "luke": "Luke",
    "jn": "John", "joh": "John", "john": "John",
    "acts": "Acts",
    "rom": "Romans", "romans": "Romans",
    "1cor": "1Corinthians", "1 corinthians": "1Corinthians", "i corinthians": "1Corinthians",
    "2cor": "2Corinthians", "2 corinthians": "2Corinthians", "ii corinthians": "2Corinthians",
    "gal": "Galatians", "galatians": "Galatians",
    "eph": "Ephesians", "ephesians": "Ephesians",
    "phil": "Philippians", "philippians": "Philippians",
    "col": "Colossians", "colossians": "Colossians",
    "1thess": "1Thessalonians", "1 thessalonians": "1Thessalonians",
    "2thess": "2Thessalonians", "2 thessalonians": "2Thessalonians",
    "1tim": "1Timothy", "1 timothy": "1Timothy", "i timothy": "1Timothy",
    "2tim": "2Timothy", "2 timothy": "2Timothy", "ii timothy": "2Timothy",
    "tit": "Titus", "titus": "Titus",
    "phlm": "Philemon", "philemon": "Philemon",
    "heb": "Hebrews", "hebrews": "Hebrews",
    "jas": "James", "james": "James",
    "1pet": "1Peter", "1 peter": "1Peter", "i peter": "1Peter",
    "2pet": "2Peter", "2 peter": "2Peter", "ii peter": "2Peter",
    "1jn": "1John", "1 john": "1John", "i john": "1John",
    "2jn": "2John", "2 john": "2John", "ii john": "2John",
    "3jn": "3John", "3 john": "3John", "iii john": "3John",
    "jude": "Jude",
    "rev": "Revelation", "revelation": "Revelation",

    # Common misspellings
    "genesis": "Genesis", "genesis": "Genesis",
    "judges": "Judges", "judge": "Judges",
    "samuel": None,  # Ambiguous - requires chapter number to disambiguate
    "kings": None,   # Ambiguous
}


def normalize_book_name(book_input: str) -> Optional[str]:
    """
    Normalize a book name using aliases.

    Converts abbreviated or alternative names to canonical form.
    Returns None if book is ambiguous or unknown.

    Args:
        book_input: The book name as it appears in the citation

    Returns:
        Normalized book name or None if invalid
    """
    book_lower = book_input.lower().strip()

    # Direct lookup in aliases
    if book_lower in BOOK_ALIASES:
        return BOOK_ALIASES[book_lower]

    # Try with spaces removed
    book_no_space = book_lower.replace(" ", "")
    if book_no_space in BOOK_ALIASES:
        return BOOK_ALIASES[book_no_space]

    # Try title case
    return None


def load_bible_index():
    """
    Load the bible_index.json file into memory.

    Should be called once at startup. Populates the global
    _bible_index dict with all verse lookups.
    """
    global _bible_index, _index_loaded

    if _index_loaded:
        return

    index_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "bible_index.json"
    )

    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            _bible_index = json.load(f)
    else:
        print(f"Warning: bible_index.json not found at {index_path}")
        _bible_index = {}

    _index_loaded = True


def lookup_verse(book: str, chapter: int, verse: int) -> Optional[str]:
    """
    Look up a specific verse in the bible index.

    Args:
        book: Book name (will be normalized)
        chapter: Chapter number
        verse: Verse number

    Returns:
        Verse text if found, None otherwise
    """
    if not _index_loaded:
        load_bible_index()

    normalized = normalize_book_name(book)
    if not normalized:
        return None

    key = f"{normalized}:{chapter}:{verse}"
    return _bible_index.get(key)


def lookup_verse_range(book: str, chapter: int,
                       start_verse: int, end_verse: int) -> list[tuple[int, str]]:
    """
    Look up a range of verses.

    Args:
        book: Book name
        chapter: Chapter number
        start_verse: Starting verse
        end_verse: Ending verse

    Returns:
        List of (verse_num, text) tuples
    """
    verses = []
    for v in range(start_verse, end_verse + 1):
        text = lookup_verse(book, chapter, v)
        if text:
            verses.append((v, text))
    return verses


def validate_reference(ref_text: str) -> tuple[bool, str, Optional[str]]:
    """
    Validate a single Bible reference.

    Args:
        ref_text: Reference text like "John 3:16" or "Romans 8:28"

    Returns:
        Tuple of (is_valid, full_reference, verse_text)
    """
    # Parse reference pattern: Book Chapter:Verse or Book Chapter:Verse-Verse
    pattern = r"([A-Za-z\s]+)\s+(\d+):(\d+)(?:-(\d+))?"
    match = re.match(pattern, ref_text.strip())

    if not match:
        return False, ref_text, None

    book_raw = match.group(1).strip()
    chapter = int(match.group(2))
    verse_start = int(match.group(3))
    verse_end = match.group(4)  # Optional range end

    normalized = normalize_book_name(book_raw)
    if not normalized:
        return False, ref_text, None

    full_ref = f"{normalized} {chapter}:{verse_start}"
    if verse_end:
        full_ref += f"-{verse_end}"

    # Single verse lookup
    if not verse_end:
        text = lookup_verse(normalized, chapter, verse_start)
        return (text is not None), full_ref, text

    # Range lookup
    verse_texts = lookup_verse_range(normalized, chapter, verse_start, int(verse_end))
    if len(verse_texts) == (int(verse_end) - verse_start + 1):
        combined = " ".join([v[1] for v in verse_texts])
        return True, full_ref, combined

    return False, full_ref, None


def extract_citations(text: str) -> list[str]:
    """
    Extract all Bible citations from text.

    Finds patterns like "John 3:16", "Romans 8:28-30", etc.

    Args:
        text: The text to search

    Returns:
        List of citation strings found
    """
    # Pattern: Book name (may have numbers) followed by chapter:verse
    pattern = r'\b([1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+):(\d+)(?:-(\d+))?'
    matches = re.findall(pattern, text)

    citations = []
    for match in matches:
        book = match[0].strip()
        chapter = match[1]
        verse = match[2]
        verse_range = f"-{match[3]}" if match[3] else ""
        citations.append(f"{book} {chapter}:{verse}{verse_range}")

    return citations


def parse_verify_tags(text: str) -> list[str]:
    """
    Extract [VERIFY:BookName:Chapter:Verse] tags from text.

    Args:
        text: Text containing VERIFY tags

    Returns:
        List of tag strings found
    """
    pattern = r'\[VERIFY:([A-Za-z]+):(\d+):(\d+)\]'
    matches = re.findall(pattern, text)
    return [f"{m[0]}:{m[1]}:{m[2]}" for m in matches]


def validate_response(response: str) -> dict:
    """
    Validate all Bible citations in a response.

    This is the main entry point for citation validation.
    It extracts all citations, looks them up, and returns
    validation results.

    Args:
        response: The generated response text

    Returns:
        Dict with validated_response, verified, hallucinated, corrected lists
    """
    if not _index_loaded:
        load_bible_index()

    verified = []
    hallucinated = []
    corrected = []
    validated_response = response

    # Extract inline citations
    citations = extract_citations(response)

    for cite in citations:
        is_valid, full_ref, verse_text = validate_reference(cite)

        if is_valid:
            verified.append({
                "reference": full_ref,
                "text": verse_text,
                "status": "verified"
            })
            # Add checkmark to the response
            validated_response = validated_response.replace(
                cite, f"{cite} ✓"
            )
        else:
            hallucinated.append({
                "reference": cite,
                "status": "not_found"
            })
            # Replace with warning
            warning = f"⚠️ [{cite} — could not be verified in scripture]"
            validated_response = validated_response.replace(cite, warning)

    # Handle [VERIFY:...] tags
    verify_tags = parse_verify_tags(response)
    for tag in verify_tags:
        parts = tag.split(":")
        if len(parts) == 3:
            book, chapter, verse = parts
            text = lookup_verse(book, int(chapter), int(verse))

            if text:
                verified.append({
                    "reference": f"{book} {chapter}:{verse}",
                    "text": text,
                    "status": "verified"
                })
                replacement = f"[✓ {book} {chapter}:{verse} — {text}]"
                validated_response = validated_response.replace(
                    f"[VERIFY:{book}:{chapter}:{verse}]",
                    replacement
                )
            else:
                hallucinated.append({
                    "reference": f"{book} {chapter}:{verse}",
                    "status": "not_found"
                })
                validated_response = validated_response.replace(
                    f"[VERIFY:{book}:{chapter}:{verse}]",
                    f"⚠️ [{book} {chapter}:{verse} — could not be verified]"
                )

    return {
        "validated_response": validated_response,
        "verified": verified,
        "hallucinated": hallucinated,
        "corrected": corrected,
        "verified_count": len(verified),
        "hallucinated_count": len(hallucinated)
    }


def get_bible_index_size() -> int:
    """
    Get the number of verses in the loaded bible index.

    Returns:
        Total count of verses indexed
    """
    if not _index_loaded:
        load_bible_index()

    return len(_bible_index)
