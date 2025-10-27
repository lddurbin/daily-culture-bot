<!-- 86237248-f95f-48ff-974d-53052a878331 e728e645-e67c-400f-9f3a-2a1f4ec243a4 -->
# Improve Artwork-Poem Matching with Emotional Analysis

## Overview

Enhance the existing complementary mode to use OpenAI API for emotional and thematic poem analysis, then improve Q-code mappings to be emotion-aware for better artwork matching. Focus on email delivery as the primary output mechanism, simplifying or removing less critical features like HTML gallery generation and local file saving.

## Implementation Strategy

### 1. Add OpenAI Integration (`poem_analyzer.py`)

**Install OpenAI SDK:**

- Add `openai` to `requirements.txt`
- Add `python-dotenv` if not already present (for API key management)

**Create OpenAI Analyzer Method:**

- Add `analyze_poem_with_ai()` method that uses GPT-4 or GPT-3.5-turbo
- Prompt design: Ask OpenAI to identify:
  - **Primary emotions**: grief, joy, melancholy, peace, anger, love, hope, despair, nostalgia, etc.
  - **Themes**: death, loss, nature, love, war, childhood, memory, etc.
  - **Mood/Tone**: somber, celebratory, contemplative, energetic, peaceful, turbulent, etc.
  - **Visual suggestions**: color palette, scene types (solitary figures, landscapes, abstract, symbolic)
- Return structured JSON response with confidence scores
- Add fallback to keyword-based analysis if API fails or key is missing

**Example API prompt:**

```
Analyze this poem and return a JSON object with:
- emotions: array of primary emotions (grief, joy, melancholy, peace, etc.)
- themes: array of thematic elements (death, nature, love, war, etc.)
- mood: overall mood descriptor (somber, joyful, contemplative, etc.)
- visual_suggestions: types of artwork that would pair well (e.g., "mourning scenes", "solitary figures", "abstract representations of loss")
- intensity: emotional intensity on scale 1-10

Poem:
[poem text here]
```

### 2. Expand Emotion-Aware Q-Code Mappings (`poem_analyzer.py`)

**Create Emotion-Based Mappings:**

Add new mappings that connect emotions to appropriate Wikidata Q-codes for artwork subjects and genres:

```python
EMOTION_MAPPINGS = {
    "grief": {
        "q_codes": ["Q4", "Q203", "Q2912397", "Q3305213"],  # death, mourning, memorial, painting
        "genres": ["Q134307", "Q2839016"],  # portrait, religious painting
        "keywords": ["mourning", "memorial", "sorrow", "loss", "burial", "pietà"]
    },
    "melancholy": {
        "q_codes": ["Q183", "Q8886", "Q35127"],  # night, loneliness, solitude
        "genres": ["Q191163", "Q40446"],  # landscape, nocturne
        "keywords": ["solitary", "twilight", "contemplative", "pensive"]
    },
    "joy": {
        "q_codes": ["Q2385804", "Q8274", "Q1068639"],  # celebration, dance, festival
        "genres": ["Q16875712", "Q1640824"],  # genre painting, floral painting
        "keywords": ["celebration", "dance", "festive", "bright", "colorful"]
    },
    "peace": {
        "q_codes": ["Q23397", "Q35127", "Q483130"],  # landscape, solitude, pastoral
        "genres": ["Q191163", "Q1640824"],  # landscape, still life
        "keywords": ["pastoral", "serene", "calm", "quiet", "peaceful"]
    }
    # ... more emotions
}
```

**Enhance Existing Theme Mappings:**

- Update existing theme mappings (death, love, nature, etc.) with more specific Q-codes
- Add emotional context to each theme (e.g., "death" can be peaceful or tragic)
- Include genre-specific Q-codes (portrait, landscape, religious art, abstract)

### 3. Improve Subject-Based Query (`datacreator.py`)

**Enhance `query_paintings_by_subject()`:**

- Accept both subject Q-codes and genre Q-codes
- Add genre filtering to SPARQL query using P136 (genre) property
- Prioritize paintings that match multiple criteria (subject + genre + depicts)
- Add option to filter by color palette or style when emotional tone is provided

**Updated SPARQL query structure:**

```sparql
SELECT ?painting ?image WHERE {
  ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
  ?painting wdt:P18 ?image .        # Has image
  
  # Match by subject/depicts/genre
  {
    ?painting wdt:P180 ?subject .    # depicts
    FILTER(?subject IN (wd:Q4, wd:Q203, ...))
  } UNION {
    ?painting wdt:P921 ?subject .    # main subject
    FILTER(?subject IN (wd:Q4, wd:Q203, ...))
  } UNION {
    ?painting wdt:P136 ?genre .      # genre
    FILTER(?genre IN (wd:Q134307, wd:Q2839016, ...))
  }
}
ORDER BY RAND()
LIMIT 50
```

### 4. Update Orchestration Logic (`daily_paintings.py`)

**Modify complementary mode workflow:**

1. Fetch poems first
2. For each poem:

   - Try OpenAI analysis first (if API key present)
   - Fall back to keyword analysis if OpenAI fails
   - Combine results from both analyzers for better coverage

3. Use emotional analysis results to build comprehensive Q-code list
4. Query Wikidata with emotion-aware Q-codes
5. Track whether match used AI analysis or keyword fallback

**Add environment variable handling:**

- Check for `OPENAI_API_KEY` in environment
- Gracefully degrade to keyword-only mode if not present
- Print informative message about analysis method being used

### 5. Update Configuration Files

**Update `requirements.txt`:**

```
requests
pytest>=7.4.0
pytest-cov>=4.1.0
poetpy
python-dotenv
openai>=1.0.0
```

**Update README.md:**

- Add section on OpenAI API setup
- Document emotion-aware matching feature
- Provide examples of emotional poem-artwork pairs
- Add environment variable documentation

**Create/Update `.env.example`:**

```
OPENAI_API_KEY=sk-...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
```

### 6. Enhance Email Display

**Update email content to show emotion-based match indicators:**

- Add "AI-Matched" badge for OpenAI-analyzed matches
- Add "Emotion-Matched" indicator showing which emotions were matched
- Display detected emotions and mood in poem cards
- Show visual matching explanation (e.g., "Matched: grief → mourning scene")

**Add emotion visualization:**

- Color-code emotion tags (grief=dark blue, joy=yellow, peace=green, etc.)
- Show confidence scores for detected emotions
- Display whether match used AI or keyword analysis

### 7. Testing Strategy

**Update `test_poem_analyzer.py`:**

- Test OpenAI integration with mocked API responses
- Test emotion detection accuracy with sample poems
- Test fallback to keyword analysis when API unavailable
- Test combined AI + keyword analysis
- Test emotion-to-Q-code mapping logic

**Add integration tests:**

- Test end-to-end workflow with grief poem (like the example)
- Verify appropriate artwork is matched (mourning scenes, solitary figures, etc.)
- Test fallback behavior when no emotion-matched artwork is found
- Test with various emotional poems (joy, melancholy, peace, anger, etc.)

### 8. Performance & Cost Considerations

**OpenAI API Usage:**

- Use GPT-3.5-turbo for cost efficiency (~$0.002 per poem analysis)
- Cache analysis results to avoid repeated API calls
- Set reasonable token limits (max 1000 tokens per request)
- Implement retry logic with exponential backoff for API errors

**Fallback Strategy:**

- Always have keyword-based analysis as fallback
- Don't block execution if OpenAI API fails
- Print clear messages about analysis method being used

## Files to Modify

**Modified files:**

- `src/poem_analyzer.py` - Add OpenAI integration, expand emotion-aware mappings
- `src/datacreator.py` - Enhance subject-based queries with genre filtering
- `src/daily_paintings.py` - Update workflow to use AI analysis, add env var handling
- `requirements.txt` - Add openai and python-dotenv
- `README.md` - Document OpenAI setup and emotion-aware matching
- `tests/test_poem_analyzer.py` - Add tests for OpenAI integration and emotion detection

**New files:**

- `.env.example` - Template for environment variables

## Example Usage

```bash
# With OpenAI API key set
export OPENAI_API_KEY="sk-..."
python daily_culture_bot.py --complementary --output --html

# Without OpenAI (fallback to keywords)
python daily_culture_bot.py --complementary --output --html

# Email with emotion-matched content
python daily_culture_bot.py --complementary --email user@example.com
```

## Success Criteria

1. OpenAI integration works for poem emotional analysis with structured JSON output
2. Emotion-aware Q-code mappings significantly improve artwork matching (grief poems → somber/memorial artwork)
3. Fallback to keyword analysis works seamlessly when API unavailable
4. No breaking changes to existing functionality
5. Clear visual indicators in HTML gallery show emotion-based matches
6. API costs remain reasonable (<$0.01 per run for typical usage)

### To-dos

- [ ] Add openai and python-dotenv to requirements.txt
- [ ] Create .env.example with OPENAI_API_KEY template
- [ ] Add analyze_poem_with_ai() method to poem_analyzer.py using OpenAI API
- [ ] Add comprehensive emotion-aware Q-code mappings (grief, melancholy, joy, peace, etc.)
- [ ] Update existing theme mappings with more specific emotion-aware Q-codes
- [ ] Update analyze_poem() to use OpenAI analysis with keyword fallback
- [ ] Enhance query_paintings_by_subject() to include genre filtering
- [ ] Update complementary mode in daily_paintings.py to use emotion-aware analysis
- [ ] Add OPENAI_API_KEY environment variable handling with graceful degradation
- [ ] Update email content to show emotion-based match indicators and AI analysis status
- [ ] Add tests for OpenAI integration, emotion detection, and emotion-aware matching
- [ ] Document OpenAI setup, emotion-aware matching, and provide examples