# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Culture Bot is a Python application that fetches famous paintings from Wikidata and poems from PoetryDB, then delivers them via email. The bot features AI-powered artwork-poem matching using OpenAI's API for complementary content pairing.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy English model (required for concrete element extraction)
python -m spacy download en_core_web_sm
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_daily_paintings.py -v

# Run single test function
pytest tests/test_poem_analyzer.py::TestPoemAnalyzer::test_analyze_poem -v

# Run with verbose output and show durations
pytest -v --tb=short --durations=10

# Run only fast tests (skips slow tests)
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

Coverage requirement: 50% minimum on fast tests (enforced in CI)

### Running the Application
```bash
# Basic run with sample data (fast mode)
python daily_culture_bot.py --fast --count 1 --output

# Fetch artwork with images
python daily_culture_bot.py --output --save-image

# Complementary mode (AI-powered artwork-poem matching)
python daily_culture_bot.py --complementary --email user@example.com

# Complementary mode with vision analysis and match explanations
python daily_culture_bot.py --complementary --explain-matches --email user@example.com

# Disable vision analysis to save on API costs
python daily_culture_bot.py --complementary --no-vision --email user@example.com

# Multi-pass analysis with custom candidate count
python daily_culture_bot.py --complementary --candidate-count 10 --vision-candidates 5

# Test email integration (requires .env setup)
python daily_culture_bot.py --email user@example.com --fast

# Multiple artworks/poems
python daily_culture_bot.py --count 5 --poems --poem-count 3 --output
```

### Linting and Code Quality
```bash
# Basic syntax check
python -m py_compile src/*.py
```

## Architecture

### Module Structure

The codebase follows a modular design with clear separation of concerns:

**`src/daily_paintings.py`** - Main orchestration layer
- Entry point and CLI argument parsing
- Coordinates between datacreator, poem_fetcher, poem_analyzer, and email_sender
- Handles two primary modes:
  1. **Standard mode**: Fetch artwork → optionally fetch poems
  2. **Complementary mode**: Fetch poems → analyze themes → fetch matching artwork
- Contains email word count optimization (300-word limit for poems in emails)

**`src/datacreator.py`** - Artwork data orchestration
- `PaintingDataCreator` class manages artwork fetching workflow
- Delegates SPARQL queries to `wikidata_queries.py`
- Delegates data processing to `artwork_processor.py`
- Implements query caching (max 50 entries) and connection pooling
- Supports fame-level filtering (sitelinks count) for obscure artwork discovery
- Fast mode uses sample data to avoid API calls

**`src/poem_analyzer.py`** - Poem theme analysis
- Dual analysis strategy:
  1. **OpenAI API** (if `OPENAI_API_KEY` set): Advanced emotion detection, mood analysis, intensity scoring
  2. **Keyword-based fallback**: Pattern matching using `poem_themes.py` mappings
- Maps poem themes/emotions to Wikidata Q-codes for artwork matching
- Delegates OpenAI calls to `openai_analyzer.py`
- Theme detection uses compiled regex patterns for performance

**`src/poem_fetcher.py`** - PoetryDB API integration
- Fetches poems from poetrydb.org
- Implements word count filtering (especially for email: 300-word max)
- Optionally fetches poet biographical data from Wikidata
- Retry logic with fallback to sample data on failure

**`src/email_sender.py`** - Email delivery system
- Sends HTML and/or plain text emails via SMTP
- Handles image attachment/embedding
- Responsive HTML template generation
- TLS/SSL support for various SMTP providers

**`src/wikidata_queries.py`** - SPARQL query builder
- Constructs complex SPARQL queries for Wikidata
- Handles query execution with retry logic and error handling
- Query timeout configurable (default: 60s)

**`src/artwork_processor.py`** - Data processing layer
- Processes raw Wikidata results into structured artwork data
- Enriches with Wikipedia summaries and image metadata
- Extracts interesting facts from Wikipedia content

**`src/poem_themes.py`** - Theme mapping configuration
- Maps poem themes (nature, love, death, etc.) to Wikidata Q-codes
- Maps emotions to Wikidata Q-codes for complementary matching
- Used by both keyword-based and OpenAI analysis

**`src/openai_analyzer.py`** - OpenAI integration
- Encapsulates OpenAI API calls for poem analysis
- Structured JSON output parsing for themes, emotions, moods
- Cost-efficient: ~$0.002 per poem analysis

**`src/vision_analyzer.py`** - GPT-4 Vision integration
- Analyzes artwork images using OpenAI's Vision API
- Extracts visual elements, composition, mood, color palette
- Caches analysis results to avoid redundant API calls
- Supports multi-pass candidate selection workflow

**`src/concrete_element_extractor.py`** - NLP-based concrete element extraction
- Uses spaCy to extract concrete nouns from poems (people, places, objects, nature)
- Maps extracted elements to Wikidata Q-codes for precise matching
- Enables verifiable artwork-poem connections beyond abstract themes
- Requires spaCy model: `python -m spacy download en_core_web_sm`

**`src/two_stage_matcher.py`** - Advanced matching algorithm
- Stage 1: Hard constraints to filter incompatible artwork
  - Exclusions: peaceful poems avoid war/violence subjects
  - Emotional conflicts: joyful poems avoid death/mourning themes
- Stage 2: Weighted scoring across multiple dimensions
  - Theme overlap (40% weight)
  - Emotion alignment (30% weight)
  - Mood consistency (20% weight)
  - Visual element matches (10% weight when vision enabled)
- Soft conflict detection reduces scores (e.g., indoor/outdoor mismatch)

**`src/match_explainer.py`** - Match transparency
- Generates human-readable explanations for artwork-poem pairings
- Details specific connections: shared objects, setting alignment, emotional resonance
- Identifies potential tensions in matches
- Provides overall assessment based on match score

**`src/wikidata_config.py`** - Configuration constants
- API endpoints, User-Agent strings, style mappings

### Import Pattern

All modules use a dual-import pattern to support both package imports and standalone execution:
```python
try:
    from . import module_name  # Package import
except ImportError:
    import module_name  # Standalone import
```

### Key Architectural Patterns

1. **Lazy OpenAI initialization**: OpenAI client only initialized if `OPENAI_API_KEY` is set
2. **Graceful degradation**: Falls back to keyword-based analysis if OpenAI unavailable
3. **Connection pooling**: Uses `requests.Session()` for efficient HTTP requests
4. **Query caching**: Prevents redundant Wikidata queries (50-entry LRU cache)
5. **Retry logic**: API calls retry on failure with exponential backoff
6. **Multi-layered analysis**: Combines multiple analysis techniques:
   - Text-based theme detection (OpenAI + keywords)
   - NLP concrete element extraction (spaCy)
   - Vision-based image analysis (GPT-4 Vision)
7. **Two-stage filtering**: Hard constraints eliminate incompatible matches before weighted scoring
8. **Result caching**: Vision analysis results cached by image URL to avoid redundant API calls

### Complementary Matching Flow

When `--complementary` flag is used:

**Basic Matching (without vision):**
1. Fetch poems from PoetryDB
2. Analyze poems with dual strategy:
   - OpenAI API: emotion detection, mood analysis, intensity scoring
   - spaCy NLP: concrete element extraction (nouns, objects, settings)
3. Map themes, emotions, and concrete elements to Wikidata Q-codes
4. Query Wikidata for artwork matching ANY of these Q-codes
5. Apply two-stage matching:
   - Stage 1: Hard constraints filter (incompatible themes/emotions)
   - Stage 2: Weighted scoring (theme 40%, emotion 30%, mood 20%, visual 10%)
6. Filter by minimum match score (default: 0.4) and fame level (default: 20)
7. Generate match explanations if `--explain-matches` enabled
8. Return best matches, fall back to random artwork if no matches found

**Multi-Pass Analysis (with vision, default):**
1. Steps 1-3 same as above
2. Fetch candidate artworks (default: 6 candidates via `--candidate-count`)
3. Use OpenAI Vision API to analyze artwork images:
   - Extract visual elements, composition, colors
   - Identify mood and setting
   - Cache results for efficiency
4. Apply two-stage matching with vision data incorporated
5. Select best match using combined scores
6. Generate detailed match explanation

**Key Parameters:**
- `--no-vision`: Disable vision analysis (faster, cheaper)
- `--no-multi-pass`: Skip candidate selection, use original algorithm
- `--vision-candidates N`: Analyze top N candidates with vision (0 = all)
- `--candidate-count N`: Number of candidates to fetch initially
- `--min-match-score`: Minimum threshold (0.0-1.0, default: 0.4)
- `--max-fame-level`: Maximum sitelinks (default: 20, lower = more obscure)
- `--explain-matches`: Generate human-readable match explanations

Match status tracked: "Matched" vs "Fallback (Random)"

## Configuration

### Environment Variables (.env file)

Required for email functionality:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

Optional for enhanced poem analysis:
```bash
OPENAI_API_KEY=sk-your-key-here
```

See `.env.example` for multiple SMTP provider examples (Gmail, Outlook, Yahoo, custom).

### GitHub Actions Secrets

For automated daily emails via `.github/workflows/daily-email.yml`:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`
- `EMAIL_RECIPIENT` - destination email address
- `OPENAI_API_KEY` (optional)

## Testing Strategy

The test suite covers:
- CLI argument parsing and validation
- API integration with mocking (Wikidata, PoetryDB, Wikipedia, OpenAI)
- Email delivery (HTML/text formats)
- Complementary matching algorithm and two-stage matcher
- Vision analysis and match explanation generation
- Concrete element extraction with spaCy
- Error handling and edge cases
- Word count filtering for poems
- Fast mode sample data generation
- Multi-pass analysis workflow

Test files use pytest fixtures and mocking extensively. Key test patterns:
- Mock external API calls (`@patch('requests.get')`, `@patch('requests.post')`)
- Mock OpenAI client (text and vision) for deterministic testing
- Mock spaCy NLP pipeline for concrete element extraction
- Test both success and failure paths
- Validate data structure and content
- Integration tests for complete workflows

Test organization:
- `test_daily_paintings.py` - Main CLI and orchestration
- `test_datacreator.py` - Artwork fetching and caching
- `test_poem_analyzer.py` - Theme analysis and emotion detection
- `test_poem_fetcher.py` - Poetry API integration
- `test_email_sender.py` - Email delivery
- `test_vision_analyzer.py` - GPT-4 Vision integration
- `test_two_stage_matcher.py` - Advanced matching algorithm
- `test_match_explainer.py` - Match explanation generation
- `test_concrete_element_extractor.py` - NLP element extraction
- `test_complementary_mode_integration.py` - End-to-end matching tests

## CI/CD Pipeline

`.github/workflows/simple-ci.yml` runs on push/PR to main:
1. **Environment**: Ubuntu latest, Python 3.11
2. **Fast tests**: Runs tests marked as not slow (`pytest -m "not slow"`)
3. **Coverage check**: Minimum 50% coverage on fast tests
4. **Functional smoke tests**:
   ```bash
   python daily_culture_bot.py --fast --count 1 --output
   python daily_culture_bot.py --complementary --fast --count 1
   ```

**Test markers:**
- Use `@pytest.mark.slow` for tests that take >5 seconds
- CI runs fast tests by default
- Run slow tests locally: `pytest -m slow` or `pytest` (all tests)

## Data Sources

- **Wikidata SPARQL endpoint**: Artwork metadata and Q-code mappings
- **Wikimedia Commons API**: High-resolution images
- **Wikipedia REST API**: Artwork descriptions and interesting facts
- **PoetryDB API**: Public domain poems

## Common Development Patterns

### Adding New Poem Themes

Edit `src/poem_themes.py`:
1. Add theme to `THEME_MAPPINGS` with keywords and Q-codes
2. Add to `OBJECT_MAPPINGS` for concrete noun mappings
3. Recompile patterns automatically handled by `PoemAnalyzer._compile_patterns()`

### Modifying Email Templates

Email HTML generation in `src/email_sender.py`:
- `_create_html_body()` - main HTML structure
- Inline CSS for email client compatibility
- Responsive design for mobile
- Match explanation section added if `--explain-matches` enabled

### Adjusting Matching Algorithm

**Basic match scoring** in `src/datacreator.py`:
- `_calculate_match_score()` - computes overlap percentage
- `_filter_artworks_by_match_score()` - applies threshold and fame level filters
- Tune via CLI: `--min-match-score` and `--max-fame-level`

**Two-stage matcher** in `src/two_stage_matcher.py`:
- `apply_hard_constraints()` - Stage 1: filter incompatible matches
- `calculate_weighted_score()` - Stage 2: weighted scoring
- Modify `hard_exclusions` dict to add new constraint rules
- Modify `soft_conflicts` dict for scoring penalties
- Adjust weights in `calculate_weighted_score()`:
  - `theme_weight = 0.4` (40%)
  - `emotion_weight = 0.3` (30%)
  - `mood_weight = 0.2` (20%)
  - `visual_weight = 0.1` (10%)

### Adding Vision Analysis Features

Vision analysis in `src/vision_analyzer.py`:
- `analyze_artwork_image()` - main entry point
- Modify system prompt in `analyze_artwork_image()` for different extraction focus
- Cache managed automatically via `analysis_cache` dict
- Cost optimization: analyze top candidates only (`--vision-candidates`)

### Customizing Match Explanations

Match explanation generation in `src/match_explainer.py`:
- `explain_match()` - generates full explanation
- `_get_overall_assessment()` - score-based quality labels
- `_identify_specific_connections()` - finds concrete shared elements
- `_identify_tensions()` - detects mismatches
- Customize explanation format for different output destinations (console, email, web)

## Known Constraints

- **Wikidata query timeout**: Default 60s, configurable via `--query-timeout`
- **PoetryDB rate limits**: No explicit rate limiting, but retries on failure
- **Email word count**: 300-word max per poem for optimal email length
- **OpenAI costs**:
  - Text analysis: ~$0.002/poem (GPT-4o-mini)
  - Vision analysis: ~$0.01/image (GPT-4o)
  - Multi-pass with 6 candidates + vision: ~$0.06-0.07 per run
- **Image downloads**: Only downloads on explicit `--save-image` flag
- **spaCy requirement**: Must install `en_core_web_sm` model for concrete element extraction
- **Vision caching**: Analysis results cached per image URL to minimize redundant API calls

## Troubleshooting

**Tests failing with Wikidata timeout**: Use `--query-timeout 120` or enable `--no-poet-dates` flag

**OpenAI analysis not working**: Verify `OPENAI_API_KEY` is set and valid; system falls back to keyword analysis automatically

**Vision analysis not working**:
- Check `OPENAI_API_KEY` is set with GPT-4 Vision access
- Artwork must have valid image URL
- Use `--no-vision` to disable if not needed
- Check cache stats for hit/miss rates

**spaCy model not found**: Run `python -m spacy download en_core_web_sm`

**Email delivery fails**: Check `.env` SMTP configuration; Gmail requires app-specific password with 2FA enabled

**Complementary mode returns no matches**:
- Lower `--min-match-score` (default 0.4)
- Increase `--max-fame-level` (default 20)
- Check poem analysis output for extracted Q-codes
- Use `--explain-matches` to see why matches were selected/rejected

**High OpenAI costs**:
- Use `--no-vision` to skip image analysis
- Reduce `--vision-candidates` count
- Use `--no-multi-pass` for basic matching only
- Enable fast mode (`--fast`) for testing
