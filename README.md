# ChristianMind AI

A production-grade Christian AI Assistant built with FastAPI and React, featuring Bible-grounded responses, hallucination prevention, and theological accuracy verification.

![ChristianMind AI](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## Features

- **Bible-Grounded Responses** - All answers cite verified Scripture from the King James Version
- **Hallucination Prevention** - Two-layer strategy: RAG retrieval + citation validation against ground truth
- **Voice Input** - Speak your questions using voice recognition (continuous listening mode)
- **Text-to-Speech** - Listen to AI responses read aloud
- **Image Generation** - Create reverent Christian imagery with LLM-powered prompt sanitization
- **LLM-as-Judge** - Independent evaluation of response quality, safety, and accuracy
- **Full Pipeline Transparency** - See exactly which verses were retrieved, verified, and flagged
- **Modern Dark UI** - Beautiful glassmorphism design with smooth animations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ChristianMind Pipeline                 │
├─────────────────────────────────────────────────────────┤
│  Input → Safety → Intent → RAG → Generate →           │
│  Citation Validate → Judge → Output Safety              │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd christianmind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (Bible data downloads automatically on first run)
python backend/main.py
```

The backend will:
1. Download all 66 Bible books (~31,000 verses)
2. Build the verse index (bible_index.json)
3. Initialize ChromaDB with embeddings
4. Start serving on http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

### Chat Features

- **Type your question** and press Enter to send
- **Shift+Enter** for new line in message
- **Voice Input** - Click the microphone button to speak your question
- **Listen** - Click the "Listen" button on any response to hear it read aloud
- **Quick Actions** - Use preset questions on the welcome screen

### Image Generation

Simply ask to generate an image:
- "create image of jesus and mary"
- "show me the nativity scene"
- "generate image of jesus on the cross"

Images are automatically reviewed for theological appropriateness using LLM-powered prompt sanitization.

## API Endpoints

### Chat

```bash
POST /chat

{
  "message": "What does John 3:16 mean?",
  "session_id": "uuid-string"
}
```

Response:
```json
{
  "response": "John 3:16 is one of the most famous verses...",
  "verified_citations": [{"reference": "John 3:16", "text": "...", "status": "verified"}],
  "hallucinated_citations": [],
  "judge_scores": {"accuracy_score": 0.95, ...},
  "judge_verdict": "PASS",
  "retrieved_verses": [...],
  "is_image_request": false,
  "image_result": null
}
```

### Image Generation

```bash
POST /image

{
  "prompt": "Generate an image of the Good Samaritan parable",
  "session_id": "uuid-string"
}
```

Response:
```json
{
  "success": true,
  "image_url": "data:image/jpeg;base64,...",
  "sanitized_prompt": "A reverent artistic depiction of the Good Samaritan...",
  "original_prompt": "Generate an image of the Good Samaritan parable"
}
```

### Health Check

```bash
GET /health

{
  "status": "ok",
  "bible_verses_indexed": 31102,
  "chroma_collection_size": 31102
}
```

## Project Structure

```
christianmind/
├── backend/
│   ├── main.py                    # FastAPI app, startup Bible setup
│   ├── requirements.txt
│   ├── core/
│   │   ├── client.py              # Single Anthropic client
│   │   ├── safety.py              # Input safety classification
│   │   ├── intent.py              # Intent detection
│   │   ├── rag.py                 # ChromaDB retrieval
│   │   ├── citation_validator.py  # Verse validation
│   │   ├── judge.py               # LLM-as-Judge evaluation
│   │   ├── generator.py           # Response generation
│   │   └── image_pipeline.py      # LLM-powered image prompts
│   ├── routes/
│   │   ├── chat.py                # Chat API endpoint
│   │   ├── image.py               # Image API endpoint
│   │   └── health.py             # Health check endpoint
│   ├── data/
│   │   ├── bible/                 # Downloaded Bible JSON files
│   │   ├── bible_index.json       # Verse lookup index
│   │   └── chroma_db/             # ChromaDB persistence
│   └── evaluation/
│       ├── test_cases.json        # 42 evaluation test cases
│       └── run_eval.py            # Evaluation runner
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── api/
│       │   └── client.js          # API client functions
│       └── components/
│           ├── ChatWindow.jsx      # Main chat interface
│           ├── MessageBubble.jsx   # Chat message bubbles
│           ├── ImagePanel.jsx      # Generated image display
│           ├── GroundingPanel.jsx  # Scripture citations panel
│           ├── VoiceInput.jsx      # Voice recognition
│           └── TextToSpeech.jsx    # Text-to-speech
├── architecture.md                # Detailed architecture docs
└── README.md                     # This file
```

## Configuration

### Anthropic Client

The Anthropic client is configured in `backend/core/client.py`:

```python
ANTHROPIC_API_KEY = "sk-ant-opm-..."      # Your API key
ANTHROPIC_BASE_URL = "https://api.opusmax.pro"  # Custom proxy
MODEL_NAME = "claude-opus-4-7"
```

### Bible Data Source

Bible data is downloaded from: https://github.com/aruljohn/Bible-kjv

## Key Design Decisions

### Why KJV?
- Public domain, freely redistributable
- Well-structured JSON available
- Standard verse numbering across translations
- High familiarity in English-speaking Christian contexts

### Why ChromaDB + Bible Index?
ChromaDB provides semantic search for relevant verses. The bible_index.json provides factual verification of citations. Together they prevent both missing relevant context and accepting fabricated references.

### Why LLM-as-Judge?
Independent evaluation by a second LLM call catches nuanced issues that rule-based validation misses: contextual appropriateness, theological harmonization claims, and pastoral tone.

### Why LLM for Image Prompts?
Using an LLM to generate image prompts allows for intelligent, context-aware prompt creation that adapts to the user's request while maintaining theological appropriateness.

## Running Evaluation

```bash
# Ensure backend is running
cd backend
python main.py

# Wait for Bible data to finish downloading and indexing

# In another terminal
python evaluation/run_eval.py
```

The evaluation runner tests all 42 cases across 5 categories:
- Hallucination Tests (10 cases)
- Adversarial/Manipulation (10 cases)
- Edge Cases (8 cases)
- Difficult Theology (8 cases)
- Normal Function (6 cases)

Results are saved to `eval_results/run_{timestamp}.json`.

## Limitations

- **Single translation** - Currently only KJV supported
- **No cross-session memory** - Conversation history resets per session
- **No patristic sources** - Only Scripture is ground truth

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: React 18, Vite
- **LLM**: Claude (via Anthropic API)
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers
- **Image Gen**: Pollinations.ai

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [aruljohn/Bible-kjv](https://github.com/aruljohn/Bible-kjv) - KJV Bible JSON data
- [Pollinations.ai](https://pollinations.ai) - Free image generation
- [Anthropic](https://anthropic.com) - Claude language model
- [ChromaDB](https://www.trychroma.com) - Vector database
- [sentence-transformers](https://www.sbert.net) - Embedding model
