#!/bin/bash

# Test script to verify CI/CD setup
# This script can be run locally to simulate CI environment

echo "🧪 Testing CI/CD Setup"
echo "====================="

# Check Python version
echo "🐍 Python version:"
python3 --version

# Check if we're in the right directory
if [ ! -f "daily_culture_bot.py" ]; then
    echo "❌ Error: Not in project root directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run syntax check
echo "🔍 Running syntax check..."
python3 -m py_compile src/*.py
echo "✅ Syntax check passed"

# Run tests
echo "🧪 Running test suite..."
pytest -v --tb=short --maxfail=3

# Test basic functionality
echo "⚡ Testing basic functionality..."
python3 daily_culture_bot.py --fast --count 1 --output
echo "✅ Basic functionality test passed"

# Test complementary mode
echo "🎯 Testing complementary mode..."
python3 daily_culture_bot.py --complementary --fast --count 1
echo "✅ Complementary mode test passed"

echo ""
echo "🎉 All CI tests passed! Ready for GitHub Actions."
