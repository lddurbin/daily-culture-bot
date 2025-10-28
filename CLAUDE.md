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
```

Coverage requirement: 70% minimum (enforced in CI)

### Running the Application
```bash
# Basic run with sample data (fast mode)
python daily_culture_bot.py --fast --count 1 --output

# Fetch artwork with images
python daily_culture_bot.py --output --save-image

# Complementary mode (AI-powered artwork-poem matching)
python daily_culture_bot.py --complementary --email user@example.com

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

### Complementary Matching Flow

When `--complementary` flag is used:
1. Fetch poems from PoetryDB
2. Analyze poems → extract themes/emotions → map to Q-codes
3. Combine all Q-codes from all poems
4. Query Wikidata for artwork matching ANY of these Q-codes
5. Calculate match scores based on overlap percentage
6. Filter by minimum match score (default: 0.4) and fame level (default: 20)
7. Return best matches, fall back to random artwork if no matches found

Match status tracked for each artwork: "Matched" vs "Fallback (Random)"

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

The test suite (182 tests) covers:
- CLI argument parsing and validation
- API integration with mocking
- Email delivery (HTML/text formats)
- Complementary matching algorithm
- Error handling and edge cases
- Word count filtering for poems
- Fast mode sample data generation

Test files use pytest fixtures and mocking extensively. Key test patterns:
- Mock external API calls (`@patch('requests.get')`, `@patch('requests.post')`)
- Mock OpenAI client for deterministic testing
- Test both success and failure paths
- Validate data structure and content

## CI/CD Pipeline

`.github/workflows/ci.yml` runs on push/PR to main/dev:
1. **Test matrix**: Python 3.8-3.12
2. **Unit tests**: Full test suite with coverage reporting
3. **Integration tests**: Email and OpenAI integration (if secrets configured)
4. **Security scan**: safety + bandit checks
5. **Build verification**: Module import checks and entry point validation

Functional smoke tests:
```bash
python daily_culture_bot.py --fast --count 1 --output
python daily_culture_bot.py --complementary --fast --count 1
```

## Data Sources

- **Wikidata SPARQL endpoint**: Artwork metadata and Q-code mappings
- **Wikimedia Commons API**: High-resolution images
- **Wikipedia REST API**: Artwork descriptions and interesting facts
- **PoetryDB API**: Public domain poems

## Common Development Patterns

### Adding New Poem Themes

Edit `src/poem_themes.py`:
1. Add theme to `THEME_MAPPINGS` with keywords and Q-codes
2. Recompile patterns automatically handled by `PoemAnalyzer._compile_patterns()`

### Modifying Email Templates

Email HTML generation in `src/email_sender.py`:
- `_create_html_body()` - main HTML structure
- Inline CSS for email client compatibility
- Responsive design for mobile

### Adjusting Matching Algorithm

Match scoring logic in `src/datacreator.py`:
- `_calculate_match_score()` - computes overlap percentage
- `_filter_artworks_by_match_score()` - applies threshold and fame level filters
- Tune via CLI: `--min-match-score` and `--max-fame-level`

## Known Constraints

- **Wikidata query timeout**: Default 60s, configurable via `--query-timeout`
- **PoetryDB rate limits**: No explicit rate limiting, but retries on failure
- **Email word count**: 300-word max per poem for optimal email length
- **OpenAI cost**: ~$0.002/poem (GPT-4 mini model)
- **Image downloads**: Only downloads on explicit `--save-image` flag

## Troubleshooting

**Tests failing with Wikidata timeout**: Use `--query-timeout 120` or enable `--no-poet-dates` flag

**OpenAI analysis not working**: Verify `OPENAI_API_KEY` is set and valid; system falls back to keyword analysis automatically

**Email delivery fails**: Check `.env` SMTP configuration; Gmail requires app-specific password with 2FA enabled

**Complementary mode returns no matches**: Lower `--min-match-score` (default 0.4) or increase `--max-fame-level` (default 20)
