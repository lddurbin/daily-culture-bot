# Daily Culture Bot 🎨📝

A Python application that fetches and displays famous paintings and random public domain poems. Focuses on email delivery as the primary content delivery mechanism, with support for saving data locally.

## 🌟 Features

- **🔍 Live Data Fetching**: Pulls fresh painting data from Wikidata and random poems from PoetryDB
- **📱 Multiple Artworks**: Fetch 1-10+ artworks in a single command
- **📝 Poetry Integration**: Fetch random public domain poems alongside artwork
- **🎯 Complementary Matching**: Match artwork to poem themes for enhanced cultural experience
- **💾 Local Storage**: Save artwork data, poem data, and high-quality images locally
- **⚡ Fast Performance**: Optimized queries and smart caching for quick results
- **🎲 Random Selection**: Different artworks and poems every time with true randomization
- **📊 Rich Metadata**: Style, medium, museum, origin, and more for each artwork
- **🎭 Cultural Experience**: Combine visual art with literary art for a complete cultural experience
- **📧 Email Delivery**: Send artwork and poem content via email with HTML and plain text formats

## 🏗️ Architecture

### Project Structure

The project has been refactored into focused, maintainable modules:

```
daily-culture-bot/
├── src/                           # Source code
│   ├── daily_paintings.py         # Main orchestration script (395 lines)
│   ├── datacreator.py             # High-level artwork orchestration (858 lines)
│   ├── poem_analyzer.py           # Main poem analysis orchestration (470 lines)
│   ├── poem_fetcher.py            # Poetry fetching from PoetryDB (582 lines)
│   ├── email_sender.py            # Email composition and sending (541 lines)
│   ├── wikidata_queries.py        # SPARQL queries to Wikidata (308 lines)
│   ├── artwork_processor.py       # Artwork data processing (271 lines)
│   ├── poem_themes.py             # Theme and emotion mappings (144 lines)
│   ├── openai_analyzer.py         # OpenAI API integration (134 lines)
│   └── wikidata_config.py         # Configuration constants (52 lines)
├── tests/                         # Comprehensive test suites
├── scripts/                       # Utility scripts
├── daily_culture_bot.py           # Entry point script
└── requirements.txt               # Dependencies
```

### Core Components

- **`src/daily_paintings.py`** - Main script that orchestrates the entire process
- **`src/datacreator.py`** - High-level artwork data creation and orchestration
- **`src/poem_analyzer.py`** - Main poem analysis orchestration
- **`src/poem_fetcher.py`** - Fetches poems from PoetryDB API
- **`src/email_sender.py`** - Handles email composition and sending

### Specialized Modules

- **`src/wikidata_queries.py`** - SPARQL queries to Wikidata for artwork data
- **`src/artwork_processor.py`** - Artwork data processing and formatting
- **`src/poem_themes.py`** - Theme and emotion mappings for poem analysis
- **`src/openai_analyzer.py`** - OpenAI API integration for enhanced poem analysis
- **`src/wikidata_config.py`** - Configuration constants and mappings

This modular structure improves maintainability, testability, and code organization while keeping individual files focused and manageable.
- **`src/poem_analyzer.py`** - Theme analysis and artwork matching for complementary mode
- **`src/email_sender.py`** - Email functionality for sending artwork and poem content
- **`daily_culture_bot.py`** - Convenient entry point script

### How It Works

1. **Data Discovery**: `datacreator.py` queries Wikidata for paintings with images using optimized SPARQL
2. **Poetry Fetching**: `poem_fetcher.py` queries PoetryDB for random public domain poems
3. **Random Selection**: Uses random offset to ensure different artworks and poems each time
4. **Image Processing**: Downloads high-resolution images from Wikimedia Commons
5. **Email Delivery**: Sends beautifully formatted emails with artwork and poetry content
6. **Data Export**: Saves artwork metadata, poem data to JSON and images locally

### Complementary Mode

When using the `--complementary` flag, the workflow changes to create meaningful connections between poems and artwork:

1. **Advanced Poem Analysis**: `poem_analyzer.py` analyzes poem content using OpenAI API to detect:
   - **Primary & Secondary Emotions**: grief, joy, melancholy, peace, hope, despair, nostalgia
   - **Emotional Tone**: playful, serious, ironic, melancholic, celebratory, contemplative
   - **Visual Aesthetics**: mood, color palette, composition style
   - **Subject Suggestions**: specific artwork subjects that match the poem's feeling
   - **Avoid Subjects**: subjects that would clash with the poem's tone

2. **Quality Scoring System**: Each potential artwork is scored based on:
   - **Primary emotion match** (40% weight): Direct alignment with poem's dominant emotions
   - **Theme/subject match** (30% weight): Thematic alignment with poem content
   - **Genre alignment** (20% weight): Artwork genre matches emotional tone
   - **Intensity alignment** (10% weight): Artwork complexity matches poem intensity
   - **Conflict detection**: Penalizes artwork that conflicts with "avoid subjects"

3. **Fame Filtering**: Automatically filters out overly famous paintings (like Mona Lisa) using Wikipedia sitelinks count:
   - **Default threshold**: 20 sitelinks (configurable via `--max-fame-level`)
   - **Lower values**: More obscure artwork (10 = very obscure, 30 = moderately known)
   - **Higher values**: More famous artwork (50+ = very famous)

4. **Intelligent Matching**: Only accepts artwork with quality scores above minimum threshold (default: 0.4)
5. **Enhanced Fallback**: If no high-quality matches found, uses random obscure artwork instead of famous pieces
6. **Email Integration**: Sends matched artwork and poems via email with visual indicators

**Supported Themes**: Nature, flowers, water, love, death, war, night, day, city, animals, seasons, and more.

**Example**: A playful poem about "forbidden fruit" will now be matched with light, whimsical artwork rather than somber portraits, thanks to the emotional tone detection and avoid_subjects filtering.

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Internet connection for API access
- OpenAI API key (optional, for enhanced emotion analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ugurelveren/daily-painting-bot.git
   cd daily-painting-bot
   ```

2. **Set up virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key for enhanced emotion analysis
   ```

## 🤖 OpenAI Integration (Optional)

For enhanced emotion analysis and better artwork-poem matching, you can integrate OpenAI's GPT models:

### Setup OpenAI API

1. **Get an OpenAI API key** from [OpenAI Platform](https://platform.openai.com/api-keys)

2. **Add to environment variables**:
   ```bash
   export OPENAI_API_KEY="sk-your-openai-api-key-here"
   ```
   
   Or add to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

### Benefits of OpenAI Integration

- **Emotion Detection**: Identifies grief, joy, melancholy, peace, hope, despair, nostalgia, etc.
- **Mood Analysis**: Determines overall mood (somber, celebratory, contemplative, etc.)
- **Visual Suggestions**: Provides specific artwork recommendations (mourning scenes, solitary figures, etc.)
- **Intensity Scoring**: Rates emotional intensity on a 1-10 scale
- **Better Matching**: More accurate artwork selection based on emotional tone

### Example Analysis

For a grief poem like "Epitaph on her Son H. P." by Katherine Philips:

**Without OpenAI (keyword analysis):**
- Themes: death, loss
- Q-codes: Q4 (death), Q198 (war)

**With OpenAI (enhanced analysis):**
- Emotions: grief, melancholy
- Themes: death, loss, childhood, memory
- Mood: somber
- Intensity: 8/10
- Visual suggestions: mourning scenes, solitary figures, memorial art
- Q-codes: Q4 (death), Q203 (mourning), Q2912397 (memorial), Q134307 (portrait)

### Cost Considerations

- Uses GPT-3.5-turbo for cost efficiency (~$0.002 per poem analysis)
- Typical daily usage costs less than $0.01
- Falls back to keyword analysis if API unavailable

## 🎯 Usage

### 🚀 Quick Start (Simplest)
If you have `requests` installed globally, you can run directly:
```bash
python3 daily_culture_bot.py --output --save-image
```

> **Note**: If you get `ModuleNotFoundError: No module named 'requests'`, you need to either:
> - Install requests globally: `pip3 install requests`
> - Or use the virtual environment: `source venv/bin/activate && python daily_culture_bot.py --output --save-image`

### 💡 Simplified Usage Tips

**Single Command for Everything:**
```bash
python3 daily_culture_bot.py --output --save-image
```
This one command fetches artwork, saves data to JSON, and downloads the image!

**Create a Shell Script (Even Simpler):**
```bash
# Create get-artwork.sh
echo '#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python daily_culture_bot.py --output --save-image' > get-artwork.sh
chmod +x get-artwork.sh

# Then just run:
./get-artwork.sh
```

**Add to Your Shell Profile:**
Add this alias to your `~/.zshrc` or `~/.bashrc`:
```bash
alias get-artwork="cd /Users/leedurbin/Code/daily-culture-bot && python3 daily_culture_bot.py --output --save-image"
```
Then just type `get-artwork` from anywhere!

### Using Virtual Environment (Recommended)
**Important**: Always activate your virtual environment first:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Get Today's Artwork
```bash
python daily_culture_bot.py
```

### Save Artwork Data to JSON
```bash
python daily_culture_bot.py --output
```

### Download and Save Image
```bash
python daily_culture_bot.py --save-image
```

### Both Data and Image
```bash
python daily_culture_bot.py --output --save-image
```

### Multiple Artworks
```bash
python daily_culture_bot.py --count 5 --output --save-image
```

### Fetch Artwork and Poems Together
```bash
python daily_culture_bot.py --poems --poem-count 2 --output
```

### Complementary Mode (Match Artwork to Poems)
```bash
# Basic complementary mode - automatically fetches poems and matches artwork
python daily_culture_bot.py --complementary --output --save-image

# Multiple poems with matched artwork
python daily_culture_bot.py --complementary --poem-count 3

# Fast mode with complementary matching
python daily_culture_bot.py --complementary --fast

# High-quality matching with custom thresholds
python daily_culture_bot.py --complementary --min-match-score 0.6 --max-fame-level 15

# Very obscure artwork only (fame level 10)
python daily_culture_bot.py --complementary --max-fame-level 10

# Relaxed matching (lower quality threshold)
python daily_culture_bot.py --complementary --min-match-score 0.2
```

### Poems Only
```bash
python daily_culture_bot.py --poems-only --poem-count 3 --output
```

### Fast Mode (Sample Data Only)
```bash
python daily_culture_bot.py --count 3 --fast
```

### Disable Poet Date Fetching (Avoid Timeouts)
```bash
# If Wikidata API is slow, disable poet date fetching for faster execution
python daily_culture_bot.py --poems --no-poet-dates
```

### All Options
```bash
python daily_culture_bot.py --help
```

**Available Options:**
- `--count, -c COUNT` - Number of artworks to fetch (default: 1)
- `--output, -o` - Save artwork data to JSON file
- `--save-image, -i` - Download and save artwork images
- `--fast` - Skip API calls and use sample data (much faster)
- `--poems, -p` - Also fetch random poems
- `--poem-count COUNT` - Number of poems to fetch (default: 1)
- `--poems-only` - Fetch only poems, no artwork
- `--complementary` - Match artwork to poem themes (automatically enables --poems)
- `--no-poet-dates` - Disable poet date fetching (faster, avoids Wikidata timeouts)
- `--max-fame-level LEVEL` - Maximum fame level (sitelinks) for artwork (default: 20, lower=more obscure)
- `--min-match-score SCORE` - Minimum match quality score 0.0-1.0 (default: 0.4)
- `--email EMAIL` - Email address to send content to (enables email feature)
- `--email-format FORMAT` - Email format: html, text, or both (default: both)

## ⚠️ Error Handling

**API Failures**: If the Wikidata API is unavailable or times out, the script will fail with a clear error message. This ensures you know when real data isn't available.

**Fallback Options**:
- Use `--fast` flag to skip API calls and use sample data
- Check your internet connection and try again later
- The script will not automatically fall back to sample data

> **Note**: After activating the virtual environment, you can use `python` instead of `python3`. If you prefer not to use a virtual environment, use `python3` directly, but you'll need to install dependencies globally with `pip3 install -r requirements.txt`.


### Generate Painting Data
```bash
# Interactive mode
python datacreator.py

# Get specific number of paintings
python -c "
import datacreator
creator = datacreator.PaintingDataCreator()
paintings = creator.fetch_paintings(count=5)
print(f'Fetched {len(paintings)} paintings')
"
```

## 📧 Email Delivery

The Daily Culture Bot can send artwork and poem content via email with beautiful HTML formatting and plain text alternatives.

### Email Setup

1. **Configure SMTP Settings**: Copy `.env.example` to `.env` and fill in your SMTP details:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your email provider settings:
   ```bash
   # For Siteground (SSL on port 465)
   SMTP_HOST=mail.yourdomain.com
   SMTP_PORT=465
   SMTP_USERNAME=your-email@yourdomain.com
   SMTP_PASSWORD=your-email-password
   SMTP_FROM_EMAIL=your-email@yourdomain.com
   
   # For Gmail (TLS on port 587)
   # SMTP_HOST=smtp.gmail.com
   # SMTP_PORT=587
   # SMTP_USERNAME=your-email@gmail.com
   # SMTP_PASSWORD=your-app-password
   # SMTP_FROM_EMAIL=your-email@gmail.com
   ```

3. **Gmail Setup**: If using Gmail, you'll need an App Password:
   - Go to Google Account settings
   - Enable 2-Factor Authentication
   - Generate an App Password for "Mail"
   - Use the App Password (not your regular password)

### Email Usage Examples

**Basic Email Delivery:**
```bash
# Send artwork via email (HTML + text)
python daily_culture_bot.py --email user@example.com

# Send poems only via email
python daily_culture_bot.py --poems-only --email user@example.com

# Send matched artwork and poems
python daily_culture_bot.py --complementary --email user@example.com

# With OpenAI API for enhanced emotion analysis
export OPENAI_API_KEY="sk-your-key-here"
python daily_culture_bot.py --complementary --email user@example.com
```

**Email Format Options:**
```bash
# HTML only (with embedded images)
python daily_culture_bot.py --email user@example.com --email-format html

# Plain text only (no images)
python daily_culture_bot.py --email user@example.com --email-format text

# Both HTML and text (default)
python daily_culture_bot.py --email user@example.com --email-format both
```

**Advanced Email Examples:**
```bash
# Multiple artworks and poems via email
python daily_culture_bot.py --count 3 --poems --poem-count 2 --email user@example.com

# Fast mode with email (uses sample data)
python daily_culture_bot.py --fast --email user@example.com

# Complementary mode with HTML email
python daily_culture_bot.py --complementary --email user@example.com --email-format html
```

### Email Features

- **📧 Dual Format**: Both HTML and plain text versions for maximum compatibility
- **🖼️ Image Attachments**: High-quality artwork images embedded in HTML emails
- **🎯 Match Status**: Shows whether artwork was matched to poem themes (complementary mode)
- **🎭 Theme Detection**: Displays detected poem themes in email content
- **📱 Responsive Design**: HTML emails work beautifully on desktop and mobile
- **🔒 Secure**: Uses TLS/SSL encryption for email transmission
- **⚡ Smart Fallback**: Continues normal workflow even if email fails

### Email Troubleshooting

**Common Issues:**

1. **"Missing required environment variables"**
   - Check that all SMTP variables are set in your `.env` file
   - Ensure no typos in variable names

2. **"Authentication failed"**
   - Verify your SMTP credentials
   - For Gmail, use App Password (not regular password)
   - Check that 2FA is enabled for Gmail

3. **"Connection refused"**
   - Verify SMTP host and port settings
   - Check firewall settings
   - Try different ports (587 for TLS, 465 for SSL)

4. **"Invalid email address"**
   - Ensure email address format is correct
   - Check for typos in the email address

**Testing Email Setup:**
```bash
# Test with fast mode (uses sample data)
python daily_culture_bot.py --fast --email your-test-email@example.com

# Test with integration tests (requires TEST_EMAIL_INTEGRATION=true)
TEST_EMAIL_INTEGRATION=true pytest test_email_sender.py::TestEmailIntegration
```

## 🔧 Configuration

### API Reliability
The application has been optimized for reliable API access:

- **Optimized Queries**: Simplified SPARQL queries that run much faster
- **Automatic Fallback**: If the API fails, the app automatically uses sample paintings
- **Fast Timeouts**: 15-second timeouts for quick fallback when API is slow
- **True Randomization**: Random offset + client-side selection ensures different paintings each time
- **Connection Pooling**: Reuses connections for better performance

### Data Selection
The bot uses a simple, reliable approach:
- **Basic Filtering**: Only paintings with images and English labels
- **Random Selection**: Random offset + client-side selection for true randomization
- **Public Domain Focus**: Prioritizes historical artworks that are likely public domain

### Supported Licenses
- Public Domain (various types)
- CC0 (Public Domain Dedication)
- CC BY (Attribution)
- CC BY-SA (Attribution-ShareAlike)

## 📊 Sample Output

### Console Output
```
🎨 Fetching 3 paintings...
✅ Selected 3 paintings
📥 Downloading images...
📄 Artwork data saved to: artwork_20251026.json

================================================================================
ARTWORK INFORMATION
================================================================================

1. 🎨 Goethe in the Roman Campagna by Johann Heinrich Wilhelm Tischbein (None)
   Style: Classical | Medium: Oil on canvas
   Museum: Unknown Location | Origin: Unknown
   🖼️ Local image: ./Goethe in the Roman Campagna_None.png

2. 🎨 In the Conservatory by Édouard Manet (None)
   Style: Classical | Medium: Oil on canvas
   Museum: Unknown Location | Origin: Unknown
   🖼️ Local image: ./In the Conservatory_None.jpg

3. 🎨 Adoration of the Magi by Sandro Botticelli (None)
   Style: Classical | Medium: Oil on canvas
   Museum: Unknown Location | Origin: Unknown
   🖼️ Local image: ./Adoration of the Magi_None.jpg

================================================================================
✅ Artwork information retrieved successfully!
```

### Generated Files
- **`artwork_YYYYMMDD.json`** - Complete artwork metadata
- **Individual image files** - High-quality artwork images


## 🤖 Automation

### GitHub Actions Setup

#### Daily Email Delivery

The repository includes a GitHub Action that automatically sends daily emails with artwork and poems. The workflow is already configured in `.github/workflows/daily-email.yml`.

**Setup Instructions:**

1. **Configure GitHub Secrets** in your repository settings:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `SMTP_HOST` - Your SMTP server (e.g., `smtp.gmail.com`)
     - `SMTP_PORT` - SMTP port (e.g., `587` for TLS, `465` for SSL)
     - `SMTP_USERNAME` - Your email username
     - `SMTP_PASSWORD` - Your email password or app password
     - `SMTP_FROM_EMAIL` - Your email address
     - `EMAIL_RECIPIENT` - The email address to send daily emails to

2. **Gmail Setup** (if using Gmail):
   - Enable 2-Factor Authentication in your Google Account
   - Generate an App Password for "Mail"
   - Use the App Password (not your regular password) in `SMTP_PASSWORD`

3. **Schedule**: The workflow runs daily at 9:00 AM UTC by default
   - You can manually trigger it from the Actions tab
   - Modify the cron schedule in the workflow file if needed

**Workflow Features:**
- Sends complementary artwork and poems via email
- Includes both HTML and plain text formats
- Automatically matches artwork to poem themes
- Uploads artifacts for 7 days retention
- Handles errors gracefully

#### Basic Artwork Fetching

For basic artwork fetching without email, create `.github/workflows/daily-artwork.yml`:

```yaml
name: Daily Artwork Fetch
on:
  schedule:
    - cron: '0 12 * * *'  # Daily at 12:00 UTC
  workflow_dispatch:  # Manual trigger

jobs:
  fetch-artwork:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Fetch daily artwork
        run: python3 daily_culture_bot.py --output --save-image
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: daily-artwork
          path: |
            artwork_*.json
            *.jpg
            *.png
```

## 🛠️ Development

### Testing

#### Unit Tests with pytest
```bash
# Activate virtual environment first
source venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_daily_paintings.py
pytest test_datacreator.py

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

#### Manual Testing
```bash
# Test basic functionality
python daily_culture_bot.py

# Test with data output
python daily_culture_bot.py --output

# Test with image download
python daily_culture_bot.py --save-image

# Test with real API data
python daily_culture_bot.py

# Test data creator
python -c "
import datacreator
creator = datacreator.PaintingDataCreator()
painting = creator.get_daily_painting()
print(f'Test painting: {painting[\"title\"] if painting else \"None\"}')
"
```

#### Test Coverage
The test suite includes:
- ✅ Command-line argument parsing
- ✅ Image download functionality
- ✅ HTML gallery generation
- ✅ Sample data creation
- ✅ JSON file operations
- ✅ Data processing and cleaning
- ✅ API integration (with mocking)
- ✅ Error handling
- ✅ Edge cases

### Adding New Features
The modular architecture makes it easy to extend:
- Modify SPARQL queries in `datacreator.py` for different art selections
- Customize output formatting in `daily_paintings.py`
- Add new output formats (CSV, XML, etc.) by extending the output logic
- Integrate with other APIs or databases for additional artwork metadata

## 📚 Data Sources

- **[Wikidata](https://www.wikidata.org/)** - Painting metadata, artists, museums, dates
- **[Wikimedia Commons](https://commons.wikimedia.org/)** - High-resolution artwork images
- **[PoetryDB](https://poetrydb.org/)** - Random public domain poems and poetry metadata
- **[Wikipedia](https://en.wikipedia.org/)** - Interesting facts about artworks

## ⚖️ Legal & Ethics

- All paintings are verified as public domain or CC-licensed
- Respects Wikimedia API usage policies
- Includes proper attribution in data output
- No copyrighted contemporary artworks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Wikimedia Foundation](https://wikimedia.org/) for providing free access to art data
- Art museums worldwide for digitizing and sharing their collections
- The open data community for making cultural heritage accessible

---

*Bringing art to your data, one painting at a time* 🎨✨
