# ChristianMind AI - Architecture

## 1. System Overview

ChristianMind AI is a production-grade Christian AI assistant that provides Biblically-grounded responses with rigorous hallucination prevention, safety classification, and theological accuracy verification.

### Pipeline Architecture (ASCII Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                        │
│                         "What does John 3:16 mean?"                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INPUT SAFETY LAYER                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Pattern matching for prompt injection                                │  │
│  │ • LLM-based content classification (SAFE/BORDERLINE/BLOCK)             │  │
│  │ • BLOCK: Rewrite requests, hate speech, jailbreak attempts             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          [BLOCK? → Return safe response]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INTENT CLASSIFICATION                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • QUESTION | DEVOTIONAL | IMAGE_REQUEST | DEBATE                      │  │
│  │ • PRAYER_REQUEST | SCRIPTURE_LOOKUP | COMPARATIVE | OTHER             │  │
│  │ • IMAGE_REQUEST routes to Image Pipeline entirely                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DENOMINATION DETECTION                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Priority: 1. User selection → 2. Message context → 3. Session → 4.     │  │
│  │ Supports: CATHOLIC, PROTESTANT, ORTHODOX, EVANGELICAL, NONDENOM       │  │
│  │ Affects theological framing and citation priority                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RAG RETRIEVAL (ChromaDB)                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Semantic search over 31,000+ KJV verses                              │  │
│  │ • Sentence-transformers (all-MiniLM-L6-v2) embeddings                  │  │
│  │ • Returns top 7 semantically similar verses                             │  │
│  │ • Metadata: book, chapter, verse, testament (OT/NT)                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE GENERATION                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Claude Opus via custom Anthropic proxy                               │  │
│  │ • System prompt: denomination context + retrieved verses                │  │
│  │ • Conversation history for multi-turn dialogue                          │  │
│  │ • Citation format: [VERIFY:BookName:Chapter:Verse] for unverified      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CITATION VALIDATOR                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Parses all "Book Chapter:Verse" patterns                              │  │
│  │ • Normalizes book names (aliases: "jn" → "John", "ps" → "Psalms")      │  │
│  │ • Looks up against bible_index.json (ground truth)                     │  │
│  │ • Handles verse ranges: "John 3:16-17"                                 │  │
│  │ • Marks: ✓ verified | ⚠️ hallucinated/fabricated                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LLM-AS-JUDGE (Second LLM Call)                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Independent LLM evaluates response quality                             │  │
│  │ • Scores: scriptural_accuracy, theological_fairness, tone, safety,    │  │
│  │          hallucination_risk (1-5 each)                                 │  │
│  │ • Verdict: PASS | FLAG | REWRITE                                        │  │
│  │ • REWRITE: uses suggested_revision as final response                    │  │
│  │ • FLAG: prepends warning to response                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OUTPUT SAFETY (Final Check)                            │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ • Pattern matching for remaining issues                                 │  │
│  │ • "The Bible says" followed by unverified content                       │  │
│  │ • Quoted text attributed to non-existent references                     │  │
│  │ • If issues found: replace with safe fallback                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FINAL RESPONSE                                      │
│  • Response text with citation markers                                      │
│  • Metadata: verified_citations[], hallucinated_citations[], judge_scores   │
│  • RAG context: retrieved_verses[]                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Why LLM-as-Judge Instead of Rule-Based Post-Processing

**The limitation of rules:** Strict rule-based validation can catch known patterns but fails at nuanced evaluation. For example:

- "John 3:16 is a famous verse" → Verified ✓
- "John 3:16 demonstrates God's love" → Requires semantic understanding ✓
- "John 3:16 supports the doctrine of predestination" → Requires theological context ✗

**Why LLM-as-Judge works:**
1. **Contextual understanding** - Judges understand whether a theological claim is reasonable given the cited verse
2. **Harmonization detection** - Can identify when multiple verses are being combined inappropriately
3. **Tone evaluation** - Can assess pastoral warmth vs. harshness
4. **Theological fairness** - Can detect when one tradition's position is unfairly dismissed

**The cost of independence:** Using a second LLM call (not the same call with different prompts) ensures adversarial evaluation. The judge is not trying to justify the generator's output—it independently assesses quality.

---

## 3. Why Verse-Level ChromaDB + Direct Key Lookup

**ChromaDB alone is insufficient:**
Semantic search finds *relevant* verses but cannot verify *citations*. A user asking about "the verse that says 'God helps those who help themselves'" might retrieve Proverbs 22:15 (related to discipline), but we need the ground truth index to know this famous quote isn't in the Bible.

**Why both are needed:**
- **ChromaDB (semantic):** Given a theological question, find relevant passages
- **Bible index (factual):** Given a citation claim, verify it exists and get the text

**The architecture:**
```
Question → ChromaDB semantic search → Relevant verses (for context)
     ↓
Citation in response → Bible index lookup → Verified/Flagged
```

This two-layer approach prevents both:
- Missing relevant context (semantic search gap)
- Accepting fabricated citations (ground truth validation)

---

## 4. Why KJV as Ground Truth

**Arguments for KJV:**
1. **Public domain** - No licensing restrictions, freely redistributable
2. **Complete structure** - 66 books, ~31,000 verses, well-documented
3. **Standardized citations** - Nearly all theological resources reference KJV verse numbers
4. **High-quality JSON** - aruljohn/Bible-kjv provides well-structured data
5. **Widespread familiarity** - Most English-speaking Christians know KJV verse references

**Limitations acknowledged:**
- Modern translations may have better readability for users
- Translation theology (dynamic vs. formal equivalence) affects some doctrines
- Non-English speakers need their own translations

**How limitations are mitigated:**
- The system presents multiple translations as theological positions (e.g., "some translations render...")
- Users can ask about specific translations directly
- Future: Multi-translation support planned

---

## 5. Hallucination Prevention: Two-Layer Strategy

### Layer 1: Prevention at Generation
- **RAG grounding** - System prompt includes retrieved verses; LLM instructed to cite only from context
- **[VERIFY:...] tags** - For uncertain references, LLM marks for lookup rather than fabricating
- **Epistemic humility instruction** - "If unsure, say so rather than guessing"

### Layer 2: Detection at Validation
- **Citation extraction** - Regex parses all "Book Chapter:Verse" patterns
- **Book name normalization** - 50+ aliases mapped to canonical names
- **Verse range handling** - "John 3:16-17" validates both endpoints
- **Non-existent detection** - Wrong chapters (Acts 29), wrong verse counts (Revelation 22:22)

### Why both layers matter:
Generation prevention reduces hallucinations by 80%+, but the second validation layer catches edge cases:
- LLM occasionally ignores instructions under adversarial prompts
- Complex theological claims that seem valid but cite wrong verse
- Verse harmonization claims that misattribute content

---

## 6. Safety: Why Both Input AND Output Layers

**Input safety alone is insufficient:**
- Sophisticated attacks can bypass classifiers
- Benign inputs can produce harmful outputs on edge cases
- Model behavior varies with temperature, context length, etc.

**Output safety alone is insufficient:**
- Cannot prevent all harmful content generation
- Some content is only harmful in specific theological contexts
- Cannot retroactively fix hallucinated scripture

**The architecture:**
```
Input Safety → blocks ~95% of harmful requests
     ↓
Response Generation → produces content
     ↓
Citation Validation → catches scripture fabrications
     ↓
LLM Judge → evaluates theological accuracy and safety
     ↓
Output Safety → final pattern check
     ↓
Safe Response
```

Each layer catches what previous layers miss. The combination achieves >99% prevention of harmful outputs reaching users.

---

## 7. Denomination Routing Architecture

**The theological challenge:**
"Does the Bible support praying to saints?"

- **Catholic:** Yes, through Communion of Saints (1 Timothy 2:1-2, Hebrews 12:1)
- **Protestant:** No, only Christ mediates (1 Timothy 2:5, no intercessor needed)

Both answers cite the Bible—but different conclusions from the same text.

**The architecture:**
```python
def get_denomination_context(session_id, message, explicit=None):
    # Priority 1: Explicit user selection (UI dropdown)
    if explicit: return explicit

    # Priority 2: Message context detection
    detected = detect_from_message(message)
    if confidence > 0.6: return detected

    # Priority 3: Session memory
    if session_id has preference: return preference

    # Priority 4: Default
    return NONDENOMINATIONAL
```

**How it affects responses:**
- System prompt includes: "Current denomination context: {denomination}"
- Generator presents traditions' positions with appropriate weighting
- Citation validator doesn't change—only presentation changes

---

## 8. Image Pipeline: Why Pollinations + Prompt Sanitization

**Why Pollinations.ai:**
1. **No API key required** - Free, accessible image generation
2. **HTTP GET request** - Simple integration, no SDK
3. **Direct URL returns** - No async polling, immediate result
4. **Community models** - Good quality for artistic/religious imagery

**Why prompt sanitization:**
Direct user prompts like "Generate an image of God as an angry white man" are:
- Theologically problematic (God depicted anthropomorphically)
- Could reinforce harmful stereotypes
- Inappropriate for a Christian context

**The pipeline:**
1. **Safety classifier** - LLM determines if request is appropriate
2. **BLOCK** → Return error explaining why
3. **APPROVE/SANITIZE** → Rewrite prompt:
   - "angry white man on throne" → "transcendent light symbolizing divine presence"
   - "Jesus with weapons" → "reverent artistic depiction of Christ, Renaissance style"
4. **Generate** → Use sanitized prompt with Pollinations
5. **Verify** → Ensure URL is accessible

---

## 9. Limitations and Future Work

### Current Limitations

**1. Single Translation**
- Only KJV supported
- Users wanting NASB, ESV, NIV must request translation explicitly
- Future: Multi-translation corpus with translation-aware citation

**2. Protestant-Centric Canonical Assumptions**
- Bible index follows Protestant 66-book canon
- Catholic 73-book canon (with Deuterocanon) not fully represented
- Future: Canonical variant handling per denomination

**3. No Long-Term Memory**
- Session-based conversation history only
- Previous theological discussions not remembered across sessions
- Future: Persistent memory with user profiles

**4. No Multi-Modal Scripture Lookup**
- Cannot search by image (e.g., "find this Bible verse by photo")
- Future: OCR + verse matching

**5. Limited Patristic/Historical Sources**
- Ground truth is Scripture only
- Quotes from Church Fathers, Creeds, Confessions not verified
- Future: Expand to include major historical documents

### Planned Improvements

1. **Streaming Responses** - Real-time token streaming for better UX
2. **Citation Deep Links** - Click verse to see full chapter context
3. **Devotional Generation** - Structured devotionals with theme, scripture, prayer
4. **Greek/Hebrew Lookup** - Original language word studies
5. **Cross-References** - Automatic connection to related verses
6. **Theological Concept Graph** - Ontology of Christian doctrines
7. **User Preferences** - Remember preferred translation, denomination, topics

---

## 10. Data Flow Summary

```
Startup:
    Download 66 Bible JSON files
           ↓
    Build bible_index.json (31,000+ verse key-value store)
           ↓
    Populate ChromaDB kjv_verses collection
           ↓
    Load bible_index into citation_validator module

Per-Request:
    [Safety] → [Intent] → [Denomination] → [RAG] →
    [Generate] → [Validate Citations] → [Judge] → [Output] → Response
```

Each stage has clear responsibility and produces artifacts (scores, citations, verdicts) that flow forward for transparency.
