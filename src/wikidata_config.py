#!/usr/bin/env python3
"""
Wikidata Configuration for Daily Culture Bot

This module contains configuration data for Wikidata queries including
style mappings, medium mappings, and other constants used in artwork
data processing.
"""

# Style mappings for better categorization
STYLE_MAPPINGS = {
    "Q4692": "Renaissance",
    "Q20826540": "Early Renaissance", 
    "Q131808": "High Renaissance",
    "Q37853": "Baroque",
    "Q40415": "Neoclassicism",
    "Q7547": "Romanticism",
    "Q40834": "Realism", 
    "Q40857": "Impressionism",
    "Q42489": "Post-Impressionism",
    "Q9415": "Modernism",
    "Q34636": "Expressionism",
    "Q39428": "Surrealism",
    "Q5090": "Cubism",
    "Q186030": "Abstract Expressionism",
    "Q5415": "Pop art",
    "Q2458": "Fauvism",
    "Q12124693": "Regionalism"
}

# Medium mappings for artwork types
MEDIUM_MAPPINGS = {
    "Q3305213": "Oil on canvas",  # painting
    "Q125191": "Photograph",       # photograph
    "Q860861": "Marble sculpture", # sculpture
    "Q42973": "Pencil on paper",   # drawing
    "Q93184": "Print",            # print
    "Q11661": "Mural",            # mural
    "Q11060274": "Digital art",    # digital art
    "Q1044167": "Illustration"    # illustration
}

# Wikidata endpoints and API URLs
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Default query parameters
DEFAULT_QUERY_TIMEOUT = 60
DEFAULT_CACHE_MAX_SIZE = 50

# Enhanced matching configuration options
ENABLE_VISION_ANALYSIS = True
ENABLE_MULTI_PASS = True
ENABLE_MATCH_EXPLANATIONS = True

# AI Model configuration
GPT4_MODEL = "gpt-4"
VISION_MODEL = "gpt-4o"

# Multi-pass analysis settings
CANDIDATE_COUNT_MULTIPLIER = 3  # Fetch 3x more candidates than needed
MIN_CANDIDATE_COUNT = 20  # Minimum number of candidates to fetch
CANDIDATE_SCORE_THRESHOLD_MULTIPLIER = 0.7  # Lower threshold for candidates

# Specificity bonus weights
SPECIFICITY_BONUS_WEIGHT = 0.2
DIRECT_NOUN_MATCH_BONUS = 0.15
SETTING_MATCH_BONUS = 0.15
TEMPORAL_ALIGNMENT_BONUS = 0.10
SEASON_MATCH_BONUS = 0.10
COLOR_PALETTE_BONUS = 0.05

# Scoring weights (as percentages)
CONCRETE_ELEMENTS_WEIGHT = 0.35
THEME_SUBJECT_WEIGHT = 0.30
EMOTIONAL_TONE_WEIGHT = 0.25
GENRE_ALIGNMENT_WEIGHT = 0.10

# Vision analysis settings
VISION_ANALYSIS_CACHE_SIZE = 100
VISION_ANALYSIS_TIMEOUT = 30
VISION_ANALYSIS_MAX_RETRIES = 2

# Cost tracking settings
ENABLE_COST_TRACKING = True
COST_WARNING_THRESHOLD = 0.05  # Warn if cost per artwork exceeds $0.05
COST_LIMIT_PER_RUN = 1.00  # Maximum cost per run in dollars
DEFAULT_MAX_SITELINKS = 20
DEFAULT_LIMIT = 50
