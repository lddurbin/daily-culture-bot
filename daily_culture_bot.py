#!/usr/bin/env python3
"""
Daily Culture Bot - Main Entry Point

This script provides a convenient way to run the daily culture bot
from the root directory of the project.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daily_paintings import main

if __name__ == "__main__":
    main()
