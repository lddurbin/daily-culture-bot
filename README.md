# Daily Painting Bot 🎨

A dynamic Mastodon bot that posts a different famous painting every day by fetching live data from Wikidata and Wikimedia Commons. Built with Python and designed for automated scheduling via GitHub Actions.

## 🌟 Features

- **🔍 Live Data Fetching**: Pulls fresh painting data from Wikidata using SPARQL queries
- **⚖️ License Safe**: Only uses public domain artworks and Creative Commons licensed images
- **🎲 Random Selection**: Different painting every day - never repeats content
- **🛡️ Robust Fallback**: Works even when APIs are down using sample data
- **🧪 Testing Mode**: Dry-run functionality for development and testing
- **📦 Self-Contained**: No manual data curation or JSON file maintenance needed

## 🏗️ Architecture

### Core Components

- **`daily_paintings.py`** - Main bot script that posts to Mastodon
- **`datacreator.py`** - Data fetcher that queries Wikidata for paintings
- **`requirements.txt`** - Python dependencies

### How It Works

1. **Data Discovery**: `datacreator.py` queries Wikidata for paintings using combined license+age filtering
2. **Random Selection**: Gets a random painting with full metadata (title, artist, year, style, museum, etc.)
3. **Image Download**: Fetches high-resolution images from Wikimedia Commons
4. **Social Posting**: Formats and posts to Mastodon with beautiful captions

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Mastodon account and access token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ugurelveren/daily-painting-bot.git
   cd daily-painting-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export MASTODON_ACCESS_TOKEN="your_access_token_here"
   export MASTODON_BASE_URL="https://your.mastodon.instance"
   ```

## 🎯 Usage

### Post Today's Painting
```bash
python daily_paintings.py
```

### Test Mode (Dry Run)
```bash
python daily_paintings.py --dry-run
```

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

## 🔧 Configuration

### Filter Types
The bot uses a "both" filter by default, which includes:
- **License-based**: Paintings with explicit Creative Commons or public domain licenses
- **Age-based**: Historical paintings (artist died before 1953, created before 1900)

### Supported Licenses
- Public Domain (various types)
- CC0 (Public Domain Dedication)
- CC BY (Attribution)
- CC BY-SA (Attribution-ShareAlike)

## 📊 Sample Output

```
🎨 The Great Wave off Kanagawa by Katsushika Hokusai (1831)
Style: Ukiyo-e
Medium: Polychrome woodblock print
Museum: Metropolitan Museum of Art, New York
Fun fact: One of the most recognizable works of Japanese art in the world.
#Art #Painting #DailyArt
```

## 🤖 Automation

### GitHub Actions Setup

Create `.github/workflows/daily-painting.yml`:

```yaml
name: Daily Painting Post
on:
  schedule:
    - cron: '0 12 * * *'  # Daily at 12:00 UTC
  workflow_dispatch:  # Manual trigger

jobs:
  post-painting:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Post daily painting
        env:
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
          MASTODON_BASE_URL: ${{ secrets.MASTODON_BASE_URL }}
        run: python daily_paintings.py
```

## 🛠️ Development

### Testing
```bash
# Test with dry run
python daily_paintings.py --dry-run

# Test data creator
python -c "
import datacreator
creator = datacreator.PaintingDataCreator()
painting = creator.get_daily_painting()
print(f'Test painting: {painting[\"title\"] if painting else \"None\"}')
"
```

### Adding New Features
The modular architecture makes it easy to extend:
- Modify SPARQL queries in `datacreator.py` for different art selections
- Customize caption formatting in `daily_paintings.py`
- Add new social media platforms by extending the posting logic

## 📚 Data Sources

- **[Wikidata](https://www.wikidata.org/)** - Painting metadata, artists, museums, dates
- **[Wikimedia Commons](https://commons.wikimedia.org/)** - High-resolution artwork images
- **[Wikipedia](https://en.wikipedia.org/)** - Interesting facts about artworks

## ⚖️ Legal & Ethics

- All paintings are verified as public domain or CC-licensed
- Respects Wikimedia API usage policies
- Includes proper attribution in posts
- No copyrighted contemporary artworks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Wikimedia Foundation](https://wikimedia.org/) for providing free access to art data
- [Mastodon](https://joinmastodon.org/) for the decentralized social platform
- Art museums worldwide for digitizing and sharing their collections

---

*Bringing art to your timeline, one painting at a time* 🎨✨
