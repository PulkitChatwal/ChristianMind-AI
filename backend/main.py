"""
ChristianMind AI - Main FastAPI Application
===========================================
Entry point for the backend API.
Handles startup Bible data download and ChromaDB initialization.
"""

import os
import json
import requests
import chromadb
from chromadb.config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.citation_validator import load_bible_index


# All 66 books of the Protestant Bible
BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1Samuel", "2Samuel",
    "1Kings", "2Kings", "1Chronicles", "2Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "SongofSolomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
    "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1Corinthians", "2Corinthians", "Galatians",
    "Ephesians", "Philippians", "Colossians", "1Thessalonians",
    "2Thessalonians", "1Timothy", "2Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1Peter", "2Peter",
    "1John", "2John", "3John", "Jude", "Revelation"
]

# Base URL for Bible JSON files (files are in root, not data/)
BIBLE_BASE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master"


def get_data_dir() -> str:
    """Get the data directory path."""
    return os.path.join(os.path.dirname(__file__), "data")


def get_bible_dir() -> str:
    """Get the Bible data directory path."""
    return os.path.join(get_data_dir(), "bible")


def get_index_path() -> str:
    """Get the bible_index.json path."""
    return os.path.join(get_data_dir(), "bible_index.json")


def get_chroma_dir() -> str:
    """Get the ChromaDB directory path."""
    return os.path.join(get_data_dir(), "chroma_db")


def download_bible_books() -> int:
    """
    Download all 66 Bible JSON files if not already present.

    Downloads from aruljohn/Bible-kjv GitHub repository.
    Only downloads if the directory is empty or missing files.

    Returns:
        Number of books successfully downloaded
    """
    bible_dir = get_bible_dir()
    os.makedirs(bible_dir, exist_ok=True)

    downloaded = 0
    existing = set(f for f in os.listdir(bible_dir) if f.endswith('.json'))

    print(f"Checking Bible books in {bible_dir}...")
    print(f"Existing files: {len(existing)}")

    for book in BIBLE_BOOKS:
        filename = f"{book}.json"
        filepath = os.path.join(bible_dir, filename)

        # Skip if already downloaded
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            continue

        # GitHub uses TitleCase filenames
        url = f"{BIBLE_BASE_URL}/{book}.json"
        print(f"Downloading {book}...")

        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                downloaded += 1
                print(f"  ✓ Downloaded {book}")
            else:
                print(f"  ✗ Failed to download {book}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error downloading {book}: {e}")

    print(f"Downloaded {downloaded} new Bible books")
    return downloaded


def build_bible_index() -> dict:
    """
    Build the flat bible_index.json from downloaded files.

    Key: "BookName:ChapterNumber:VerseNumber" (e.g. "John:3:16")
    Value: verse text string

    Returns:
        The built index dictionary
    """
    bible_dir = get_bible_dir()
    index_path = get_index_path()

    # Check if index already exists
    if os.path.exists(index_path):
        print(f"Bible index already exists at {index_path}")
        with open(index_path, 'r') as f:
            return json.load(f)

    print("Building Bible index...")
    index = {}

    # Map lowercase filenames to proper book names
    lowercase_to_proper = {b.lower(): b for b in BIBLE_BOOKS}

    for book_file in os.listdir(bible_dir):
        if not book_file.endswith('.json'):
            continue

        filepath = os.path.join(bible_dir, book_file)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                book_data = json.load(f)

            # Get proper book name from lowercase filename
            book_name_lower = book_file[:-5].lower()  # Remove .json extension, lowercase
            book_name = lowercase_to_proper.get(book_name_lower, book_file[:-5].title())

            # Handle different JSON structures
            if isinstance(book_data, dict):
                # New structure: {"book": "John", "chapters": [{"chapter": "1", "verses": [...]}, ...]}
                if 'book' in book_data and 'chapters' in book_data:
                    book_name = book_data['book']
                    for chapter_data in book_data['chapters']:
                        chapter_num = chapter_data.get('chapter', '')
                        for verse_data in chapter_data.get('verses', []):
                            verse_num = verse_data.get('verse', '')
                            verse_text = verse_data.get('text', '')
                            if verse_text:
                                key = f"{book_name}:{chapter_num}:{verse_num}"
                                index[key] = verse_text
                    continue
                # Old structure: chapters as dict
                elif 'chapter' in book_data:
                    chapters = book_data['chapter']
                else:
                    chapters = book_data
            elif isinstance(book_data, list):
                # Some files are a list of chapters
                chapters = {i+1: book_data[i] for i in range(len(book_data))}
            else:
                continue

            # Process chapters (old dict structure)
            if isinstance(chapters, dict):
                for chapter_num, verses in chapters.items():
                    if isinstance(verses, dict):
                        for verse_num, verse_text in verses.items():
                            if isinstance(verse_text, str):
                                key = f"{book_name}:{chapter_num}:{verse_num}"
                                index[key] = verse_text
                            elif isinstance(verse_text, dict) and 'text' in verse_text:
                                key = f"{book_name}:{chapter_num}:{verse_num}"
                                index[key] = verse_text['text']

        except Exception as e:
            print(f"  Error processing {book_file}: {e}")

    # Save index
    print(f"Saving index with {len(index)} verses to {index_path}")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


def initialize_chromadb() -> int:
    """
    Initialize ChromaDB with KJV verses.

    Creates the kjv_verses collection with verse-level documents.
    Each document contains the verse text with metadata.
    Skips if collection already exists with data.

    Returns:
        Number of verses indexed
    """
    chroma_dir = get_chroma_dir()
    os.makedirs(chroma_dir, exist_ok=True)

    # Load bible index
    index_path = get_index_path()
    if not os.path.exists(index_path):
        print("Bible index not found. Run download first.")
        return 0

    with open(index_path, 'r') as f:
        bible_index = json.load(f)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    # Check if collection exists with data
    try:
        existing = client.get_collection("kjv_verses")
        if existing.count() > 0:
            print(f"ChromaDB collection already has {existing.count()} verses")
            return existing.count()
        else:
            client.delete_collection("kjv_verses")
    except:
        pass

    print("Creating ChromaDB collection...")

    collection = client.create_collection(
        name="kjv_verses",
        metadata={"description": "King James Version Bible verses"}
    )

    # Prepare documents
    documents = []
    metadatas = []
    ids = []

    for key, text in bible_index.items():
        parts = key.split(':')
        if len(parts) != 3:
            continue

        book, chapter, verse = parts
        testament = "OT" if book in ["Genesis", "Exodus", "Leviticus", "Numbers",
                                      "Deuteronomy", "Joshua", "Judges", "Ruth",
                                      "1Samuel", "2Samuel", "1Kings", "2Kings",
                                      "1Chronicles", "2Chronicles", "Ezra",
                                      "Nehemiah", "Esther", "Job", "Psalms",
                                      "Proverbs", "Ecclesiastes", "SongofSolomon",
                                      "Isaiah", "Jeremiah", "Lamentations",
                                      "Ezekiel", "Daniel", "Hosea", "Joel",
                                      "Amos", "Obadiah", "Jonah", "Micah",
                                      "Nahum", "Habakkuk", "Zephaniah",
                                      "Haggai", "Zechariah", "Malachi"] else "NT"

        # Format: "BookName Chapter:Verse — verse text"
        doc_text = f"{book} {chapter}:{verse} — {text}"

        documents.append(doc_text)
        metadatas.append({
            "book": book,
            "chapter": int(chapter),
            "verse": int(verse),
            "testament": testament
        })
        ids.append(key)

    # Batch add to ChromaDB
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        collection.add(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )
        print(f"  Indexed {min(i+batch_size, len(documents))}/{len(documents)} verses")

    print(f"Indexed {len(documents)} verses into ChromaDB")
    return len(documents)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown handler for FastAPI.

    On startup:
    1. Download Bible books if needed
    2. Build bible_index.json
    3. Initialize ChromaDB collection
    4. Load bible index into citation validator
    """
    print("=" * 60)
    print("ChristianMind AI - Starting up...")
    print("=" * 60)

    # 1. Download Bible books
    print("\n[1/4] Checking Bible data...")
    download_bible_books()

    # 2. Build bible index
    print("\n[2/4] Building Bible index...")
    build_bible_index()

    # 3. Initialize ChromaDB
    print("\n[3/4] Initializing ChromaDB...")
    chroma_count = initialize_chromadb()

    # 4. Load bible index for citation validator
    print("\n[4/4] Loading citation validator...")
    load_bible_index()

    print("\n" + "=" * 60)
    print(f"ChristianMind AI ready!")
    print(f"Bible verses indexed: {len(bible_index) if 'bible_index' in dir() else 'N/A'}")
    print(f"ChromaDB verses: {chroma_count}")
    print("=" * 60)

    yield  # Application runs here

    print("\nChristianMind AI shutting down...")


# Create FastAPI app
app = FastAPI(
    title="ChristianMind AI",
    description="A production-grade Christian AI Assistant with Bible-grounded responses",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from backend.routes import chat, image, health

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(image.router, prefix="/image", tags=["image"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "ChristianMind AI",
        "version": "1.0.0",
        "description": "A production-grade Christian AI Assistant",
        "endpoints": {
            "chat": "/chat",
            "image": "/image",
            "health": "/health"
        }
    }


# Global variables for health check
bible_index = {}
chroma_collection_size = 0


def set_health_stats(index_size: int, chroma_size: int):
    """Set health statistics for the health endpoint."""
    global bible_index, chroma_collection_size
    bible_index = {"size": index_size}
    chroma_collection_size = chroma_size


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
