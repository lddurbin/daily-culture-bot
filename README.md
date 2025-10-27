# Daily Culture Bot 🎨📝

Fetches famous paintings and poems, delivering them via email. Combines visual art with poetry for a complete cultural experience.

## ✨ Features

- **🎨 Artwork**: Fetch 1-10+ paintings from Wikidata with rich metadata
- **📝 Poetry**: Random public domain poems from PoetryDB
- **🎯 Smart Matching**: AI-powered artwork-poem pairing for complementary mode
- **📧 Email Delivery**: Beautiful HTML/text emails with embedded images
- **💾 Local Storage**: Save data and high-quality images locally
- **⚡ Fast Mode**: Sample data for testing without API calls

## 🏗️ Architecture

**Modular Design** - Refactored into focused modules (200-400 lines each):

```
src/
├── daily_paintings.py         # Main orchestration (395 lines)
├── datacreator.py             # Artwork orchestration (858 lines)  
├── poem_analyzer.py           # Poem analysis (470 lines)
├── poem_fetcher.py            # Poetry API (582 lines)
├── email_sender.py            # Email delivery (541 lines)
├── wikidata_queries.py        # SPARQL queries (308 lines)
├── artwork_processor.py       # Data processing (271 lines)
├── poem_themes.py             # Theme mappings (144 lines)
├── openai_analyzer.py         # AI integration (134 lines)
└── wikidata_config.py         # Configuration (52 lines)
```

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/ugurelveren/daily-painting-bot.git
cd daily-painting-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Get artwork and save locally
python daily_culture_bot.py --output --save-image

# Send via email (requires .env setup)
python daily_culture_bot.py --email user@example.com

# Smart matching mode
python daily_culture_bot.py --complementary --email user@example.com
```

## 🤖 OpenAI Integration (Optional)

**Enhanced AI Analysis** - Better artwork-poem matching with emotion detection:

```bash
# Setup OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Use AI-enhanced matching
python daily_culture_bot.py --complementary --email user@example.com
```

**Benefits:**
- **Emotion Detection**: grief, joy, melancholy, peace, hope, despair, nostalgia
- **Mood Analysis**: somber, celebratory, contemplative, playful
- **Visual Suggestions**: specific artwork recommendations
- **Intensity Scoring**: 1-10 emotional intensity scale
- **Cost**: ~$0.002 per poem analysis

## 🎯 Usage Examples

**Basic Commands:**
```bash
# Get artwork and save locally
python daily_culture_bot.py --output --save-image

# Multiple artworks
python daily_culture_bot.py --count 5 --output --save-image

# Fast mode (sample data)
python daily_culture_bot.py --fast --count 3
```

**Poetry Integration:**
```bash
# Artwork + poems
python daily_culture_bot.py --poems --poem-count 2 --output

# Poems only
python daily_culture_bot.py --poems-only --poem-count 3 --output
```

**Smart Matching (Complementary Mode):**
```bash
# AI-powered artwork-poem matching
python daily_culture_bot.py --complementary --email user@example.com

# Custom matching thresholds
python daily_culture_bot.py --complementary --min-match-score 0.6 --max-fame-level 15
```

**Email Delivery:**
```bash
# Send via email
python daily_culture_bot.py --email user@example.com

# HTML only
python daily_culture_bot.py --email user@example.com --email-format html
```

**Key Options:**
- `--count N` - Number of artworks (default: 1)
- `--output` - Save data to JSON
- `--save-image` - Download images
- `--fast` - Use sample data
- `--complementary` - Smart artwork-poem matching
- `--email ADDRESS` - Send via email

## 📧 Email Setup

**Configure SMTP** - Copy `.env.example` to `.env` and add your email settings:

```bash
# Gmail example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Gmail Setup:**
1. Enable 2-Factor Authentication
2. Generate App Password for "Mail"
3. Use App Password (not regular password)

**Email Features:**
- 📧 HTML + plain text formats
- 🖼️ Embedded artwork images
- 🎯 Match status indicators
- 📱 Responsive design
- 🔒 TLS/SSL encryption

## 🤖 Automation

**GitHub Actions** - Automated daily email delivery:

1. **Configure Secrets** in repository settings:
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
   - `SMTP_FROM_EMAIL`, `EMAIL_RECIPIENT`

2. **Workflow Features:**
   - Daily emails at 9:00 AM UTC
   - Complementary artwork-poem matching
   - HTML + text formats
   - 7-day artifact retention

## 🛠️ Development

**Testing:**
```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific tests
pytest test_daily_paintings.py -v
```

**Test Coverage:** 182 tests covering CLI parsing, API integration, email delivery, error handling, and edge cases.

## 📚 Data Sources

- **[Wikidata](https://www.wikidata.org/)** - Artwork metadata
- **[Wikimedia Commons](https://commons.wikimedia.org/)** - High-res images  
- **[PoetryDB](https://poetrydb.org/)** - Public domain poems
- **[Wikipedia](https://en.wikipedia.org/)** - Artwork facts

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

*Bringing art to your data, one painting at a time* 🎨✨
