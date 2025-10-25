# Daily Artwork Bot 🎨

A Python application that fetches and displays famous paintings with detailed information from Wikidata and Wikimedia Commons. Features a modern HTML gallery for browsing multiple artworks with high-quality images.

## 🌟 Features

- **🔍 Live Data Fetching**: Pulls fresh painting data from Wikidata using optimized SPARQL queries
- **🎨 Modern HTML Gallery**: Beautiful, responsive gallery with dark theme and smooth animations
- **📱 Multiple Artworks**: Fetch 1-10+ artworks in a single command
- **💾 Local Storage**: Save artwork data and high-quality images locally
- **⚡ Fast Performance**: Optimized queries and smart caching for quick results
- **🎲 Random Selection**: Different artworks every time with true randomization
- **📊 Rich Metadata**: Style, medium, museum, origin, and more for each artwork

## 🏗️ Architecture

### Core Components

- **`daily_paintings.py`** - Main script that fetches and displays artwork information
- **`datacreator.py`** - Data fetcher that queries Wikidata for paintings
- **`requirements.txt`** - Python dependencies

### How It Works

1. **Data Discovery**: `datacreator.py` queries Wikidata for paintings with images using optimized SPARQL
2. **Random Selection**: Uses random offset to ensure different artworks each time
3. **Image Processing**: Downloads high-resolution images from Wikimedia Commons
4. **Gallery Generation**: Creates modern HTML gallery with responsive design
5. **Data Export**: Saves artwork metadata to JSON and images locally

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

> **Note**: If you get `ModuleNotFoundError: No module named 'requests'`, you need to either:
> - Install requests globally: `pip3 install requests`
> - Or use the virtual environment: `source venv/bin/activate && python daily_paintings.py --output --save-image`

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

### Multiple Artworks with HTML Gallery
```bash
python daily_paintings.py --count 5 --output --save-image --html
```

### Fast Mode (Sample Data Only)
```bash
python daily_paintings.py --count 3 --fast --html
```

### All Options
```bash
python daily_paintings.py --help
```

**Available Options:**
- `--count, -c COUNT` - Number of artworks to fetch (default: 1)
- `--output, -o` - Save artwork data to JSON file
- `--save-image, -i` - Download and save artwork images
- `--html` - Generate modern HTML gallery page
- `--fast` - Skip API calls and use sample data (much faster)

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
🌐 HTML gallery saved to: artwork_gallery.html

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
🌐 Open artwork_gallery.html in your browser to view the gallery!
```

### Generated Files
- **`artwork_gallery.html`** - Modern, responsive gallery with dark theme
- **`artwork_YYYYMMDD.json`** - Complete artwork metadata
- **Individual image files** - High-quality artwork images

### HTML Gallery Features
- **🎨 Modern Design**: Dark theme with gradient accents and smooth animations
- **📱 Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **🖼️ High-Quality Images**: Full-resolution artwork images with hover effects
- **⚡ Fast Loading**: Optimized CSS and lazy image loading
- **🎯 Clean Interface**: Professional gallery layout with card-based design

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
