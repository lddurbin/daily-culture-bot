# Daily Artwork Bot 🎨

A Python application that fetches and displays famous paintings with detailed information from Wikidata and Wikimedia Commons. Perfect for art enthusiasts, researchers, and developers who want to access artwork data programmatically.

## 🌟 Features

- **🔍 Live Data Fetching**: Pulls fresh painting data from Wikidata using SPARQL queries
- **⚖️ License Safe**: Only uses public domain artworks and Creative Commons licensed images
- **🎲 Random Selection**: Different painting every time - never repeats content
- **🛡️ Robust Fallback**: Works even when APIs are down using sample data
- **💾 Local Storage**: Save artwork data and images to local files
- **📦 Self-Contained**: No manual data curation or JSON file maintenance needed

## 🏗️ Architecture

### Core Components

- **`daily_paintings.py`** - Main script that fetches and displays artwork information
- **`datacreator.py`** - Data fetcher that queries Wikidata for paintings
- **`requirements.txt`** - Python dependencies

### How It Works

1. **Data Discovery**: `datacreator.py` queries Wikidata for paintings with images and labels
2. **Random Selection**: Uses random offset + client-side selection to ensure different paintings each time
3. **Image Download**: Optionally fetches high-resolution images from Wikimedia Commons
4. **Data Output**: Displays artwork information and optionally saves data and images locally

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Internet connection for API access

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

## 🎯 Usage

### 🚀 Quick Start (Simplest)
If you have `requests` installed globally, you can run directly:
```bash
python3 daily_paintings.py --output --save-image
```

### 💡 Simplified Usage Tips

**Single Command for Everything:**
```bash
python3 daily_paintings.py --output --save-image
```
This one command fetches artwork, saves data to JSON, and downloads the image!

**Create a Shell Script (Even Simpler):**
```bash
# Create get-artwork.sh
echo '#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python daily_paintings.py --output --save-image' > get-artwork.sh
chmod +x get-artwork.sh

# Then just run:
./get-artwork.sh
```

**Add to Your Shell Profile:**
Add this alias to your `~/.zshrc` or `~/.bashrc`:
```bash
alias get-artwork="cd /Users/leedurbin/Code/daily-culture-bot && python3 daily_paintings.py --output --save-image"
```
Then just type `get-artwork` from anywhere!

### Using Virtual Environment (Recommended)
**Important**: Always activate your virtual environment first:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Get Today's Artwork
```bash
python daily_paintings.py
```

### Save Artwork Data to JSON
```bash
python daily_paintings.py --output
```

### Download and Save Image
```bash
python daily_paintings.py --save-image
```

### Both Data and Image
```bash
python daily_paintings.py --output --save-image
```

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

```
============================================================
ARTWORK INFORMATION
============================================================
🎨 Joseph the Carpenter by Georges de La Tour (None)
Style: Classical
Medium: Oil on canvas
Museum: Unknown Location
Origin: Unknown
Dimensions: Unknown dimensions
Fun fact: A classical painting by Georges de La Tour.
Image URL: https://upload.wikimedia.org/wikipedia/commons/thumb/S/Sa/Saint%20Joseph%20Charpentier.jpg/800px-Saint%20Joseph%20Charpentier.jpg
Wikidata: http://www.wikidata.org/entity/Q743643
============================================================
🖼️ Image URL: https://upload.wikimedia.org/wikipedia/commons/thumb/S/Sa/Saint%20Joseph%20Charpentier.jpg/800px-Saint%20Joseph%20Charpentier.jpg
✅ Artwork information retrieved successfully!
```

## 🤖 Automation

### GitHub Actions Setup

Create `.github/workflows/daily-artwork.yml`:

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
        run: python3 daily_paintings.py --output --save-image
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
```bash
# Activate virtual environment first
source venv/bin/activate

# Test basic functionality
python daily_paintings.py

# Test with data output
python daily_paintings.py --output

# Test with image download
python daily_paintings.py --save-image

# Test with real API data
python daily_paintings.py

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
- Customize output formatting in `daily_paintings.py`
- Add new output formats (CSV, XML, etc.) by extending the output logic
- Integrate with other APIs or databases for additional artwork metadata

## 📚 Data Sources

- **[Wikidata](https://www.wikidata.org/)** - Painting metadata, artists, museums, dates
- **[Wikimedia Commons](https://commons.wikimedia.org/)** - High-resolution artwork images
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
