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
DEFAULT_MAX_SITELINKS = 20
DEFAULT_LIMIT = 50
