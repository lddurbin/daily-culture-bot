#!/bin/bash

# Daily Artwork Bot - Simple Script
# This script activates the virtual environment and runs the artwork fetcher

# Change to the script directory and go up to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run the artwork fetcher with both output and image download
python daily_culture_bot.py --output --save-image

echo "✅ Artwork and image saved successfully!"
