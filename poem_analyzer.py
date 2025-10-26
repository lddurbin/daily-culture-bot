#!/usr/bin/env python3
"""
Poem Analyzer for Daily Culture Bot

This module analyzes poems to extract themes and subjects, then maps them
to Wikidata entity IDs for complementary artwork matching.
"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter


class PoemAnalyzer:
    def __init__(self):
        """Initialize the poem analyzer with theme mappings."""
        # Theme keywords and their corresponding Wikidata Q-codes
        self.theme_mappings = {
            "nature": {
                "keywords": [
                    "nature", "natural", "wild", "wilderness", "forest", "wood", "woods",
                    "tree", "trees", "leaf", "leaves", "green", "earth", "ground", "land",
                    "countryside", "country", "rural", "pastoral", "meadow", "field", "fields"
                ],
                "q_codes": ["Q7860", "Q23397", "Q1640824"]  # nature, landscape, floral painting
            },
            "flowers": {
                "keywords": [
                    "flower", "flowers", "bloom", "blooms", "blossom", "blossoms", "petal", "petals",
                    "rose", "roses", "daffodil", "daffodils", "lily", "lilies", "tulip", "tulips",
                    "garden", "gardens", "floral", "botanical", "spring", "springtime"
                ],
                "q_codes": ["Q506", "Q1640824", "Q16538"]  # flower, floral painting, romantic
            },
            "water": {
                "keywords": [
                    "water", "sea", "ocean", "lake", "river", "stream", "brook", "pond", "pool",
                    "wave", "waves", "tide", "tides", "rain", "rainy", "storm", "storms",
                    "sail", "sailing", "boat", "boats", "ship", "ships", "fishing", "fisherman"
                ],
                "q_codes": ["Q283", "Q16970", "Q131681", "Q18811"]  # water, sea, seascape, battle
            },
            "love": {
                "keywords": [
                    "love", "loved", "loving", "beloved", "heart", "hearts", "romance", "romantic",
                    "kiss", "kisses", "embrace", "embraces", "passion", "passionate", "desire",
                    "affection", "tender", "sweet", "dear", "darling", "lover", "lovers"
                ],
                "q_codes": ["Q316", "Q16538", "Q506"]  # love, romantic, flower
            },
            "death": {
                "keywords": [
                    "death", "die", "dies", "died", "dying", "dead", "grave", "graves", "burial",
                    "funeral", "mourning", "grief", "sorrow", "sad", "sadness", "tears", "weep",
                    "weeping", "memorial", "remembrance", "ghost", "ghosts", "spirit", "spirits"
                ],
                "q_codes": ["Q4", "Q198", "Q18811"]  # death, war, battle
            },
            "war": {
                "keywords": [
                    "war", "wars", "warfare", "battle", "battles", "fight", "fighting", "soldier",
                    "soldiers", "army", "armies", "weapon", "weapons", "sword", "swords", "gun",
                    "guns", "bomb", "bombs", "conflict", "conflicts", "struggle", "struggles"
                ],
                "q_codes": ["Q198", "Q18811", "Q4"]  # war, battle, death
            },
            "night": {
                "keywords": [
                    "night", "nights", "dark", "darkness", "midnight", "evening", "evenings",
                    "dusk", "twilight", "moon", "moonlight", "stars", "starry", "sleep", "sleeping",
                    "dream", "dreams", "dreaming", "shadow", "shadows", "black"
                ],
                "q_codes": ["Q183", "Q111", "Q12133"]  # night, darkness, sleep
            },
            "day": {
                "keywords": [
                    "day", "days", "morning", "mornings", "dawn", "sunrise", "sun", "sunny",
                    "bright", "light", "lightness", "daylight", "noon", "afternoon", "golden",
                    "yellow", "warm", "warmth", "clear", "blue", "sky", "skies"
                ],
                "q_codes": ["Q111", "Q525", "Q12133"]  # day, sun, light
            },
            "city": {
                "keywords": [
                    "city", "cities", "urban", "town", "towns", "street", "streets", "road", "roads",
                    "building", "buildings", "house", "houses", "home", "homes", "window", "windows",
                    "door", "doors", "wall", "walls", "roof", "roofs", "crowd", "crowds", "people"
                ],
                "q_codes": ["Q515", "Q395", "Q18811"]  # city, building, battle
            },
            "animals": {
                "keywords": [
                    "animal", "animals", "bird", "birds", "dog", "dogs", "cat", "cats", "horse",
                    "horses", "cow", "cows", "sheep", "lamb", "lambs", "wolf", "wolves", "lion",
                    "lions", "eagle", "eagles", "swan", "swans", "butterfly", "butterflies"
                ],
                "q_codes": ["Q729", "Q5113", "Q1640824"]  # animal, bird, floral painting
            },
            "seasons": {
                "keywords": [
                    "spring", "summer", "autumn", "fall", "winter", "season", "seasons", "year",
                    "years", "time", "times", "change", "changes", "new", "old", "young", "age"
                ],
                "q_codes": ["Q395", "Q12133", "Q23397"]  # building, light, landscape
            }
        }
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for theme detection."""
        self.patterns = {}
        for theme, data in self.theme_mappings.items():
            # Create case-insensitive pattern that matches whole words
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in data["keywords"]) + r')\b'
            self.patterns[theme] = re.compile(pattern, re.IGNORECASE)
    
    def analyze_poem(self, poem: Dict) -> Dict:
        """
        Analyze a poem to extract themes and map them to Wikidata Q-codes.
        
        Args:
            poem: Dictionary containing poem data with 'title' and 'text' keys
            
        Returns:
            Dictionary with analysis results including themes, q_codes, and confidence scores
        """
        if not poem or not isinstance(poem, dict):
            return self._empty_analysis()
        
        title = poem.get('title', '')
        text = poem.get('text', '')
        
        if not title and not text:
            return self._empty_analysis()
        
        # Combine title and text for analysis
        full_text = f"{title} {text}".strip()
        
        # Find theme matches
        theme_scores = self._find_theme_matches(full_text)
        
        # Get Q-codes for detected themes
        q_codes = self._get_q_codes_for_themes(theme_scores)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence(theme_scores, full_text)
        
        return {
            "themes": list(theme_scores.keys()),
            "q_codes": q_codes,
            "theme_scores": theme_scores,
            "confidence_scores": confidence_scores,
            "total_matches": sum(theme_scores.values()),
            "has_themes": len(theme_scores) > 0
        }
    
    def _find_theme_matches(self, text: str) -> Dict[str, int]:
        """Find theme matches in the given text."""
        theme_scores = {}
        
        for theme, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                theme_scores[theme] = len(matches)
        
        return theme_scores
    
    def _get_q_codes_for_themes(self, theme_scores: Dict[str, int]) -> List[str]:
        """Get Wikidata Q-codes for detected themes."""
        q_codes = []
        
        for theme in theme_scores.keys():
            if theme in self.theme_mappings:
                q_codes.extend(self.theme_mappings[theme]["q_codes"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_q_codes = []
        for q_code in q_codes:
            if q_code not in seen:
                seen.add(q_code)
                unique_q_codes.append(q_code)
        
        return unique_q_codes
    
    def _calculate_confidence(self, theme_scores: Dict[str, int], text: str) -> Dict[str, float]:
        """Calculate confidence scores for detected themes."""
        confidence_scores = {}
        total_words = len(text.split())
        
        for theme, count in theme_scores.items():
            # Confidence based on frequency and text length
            frequency = count / max(total_words, 1)
            confidence = min(frequency * 10, 1.0)  # Cap at 1.0
            confidence_scores[theme] = round(confidence, 3)
        
        return confidence_scores
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis result."""
        return {
            "themes": [],
            "q_codes": [],
            "theme_scores": {},
            "confidence_scores": {},
            "total_matches": 0,
            "has_themes": False
        }
    
    def get_primary_theme(self, analysis: Dict) -> str:
        """Get the primary (most confident) theme from analysis results."""
        if not analysis.get("theme_scores"):
            return None
        
        # Return theme with highest score
        return max(analysis["theme_scores"].items(), key=lambda x: x[1])[0]
    
    def get_theme_summary(self, analysis: Dict) -> str:
        """Get a human-readable summary of detected themes."""
        if not analysis.get("has_themes"):
            return "No themes detected"
        
        themes = analysis["themes"]
        if len(themes) == 1:
            return f"Primary theme: {themes[0]}"
        elif len(themes) == 2:
            return f"Themes: {themes[0]} and {themes[1]}"
        else:
            return f"Themes: {', '.join(themes[:-1])}, and {themes[-1]}"
    
    def analyze_multiple_poems(self, poems: List[Dict]) -> List[Dict]:
        """Analyze multiple poems and return list of analysis results."""
        return [self.analyze_poem(poem) for poem in poems]
    
    def get_combined_q_codes(self, analyses: List[Dict]) -> List[str]:
        """Get combined Q-codes from multiple poem analyses."""
        all_q_codes = []
        for analysis in analyses:
            all_q_codes.extend(analysis.get("q_codes", []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_q_codes = []
        for q_code in all_q_codes:
            if q_code not in seen:
                seen.add(q_code)
                unique_q_codes.append(q_code)
        
        return unique_q_codes


def main():
    """Demonstrate the poem analyzer functionality."""
    analyzer = PoemAnalyzer()
    
    # Sample poems for testing
    sample_poems = [
        {
            "title": "I Wandered Lonely as a Cloud",
            "text": "I wandered lonely as a cloud\nThat floats on high o'er vales and hills,\nWhen all at once I saw a crowd,\nA host, of golden daffodils;\nBeside the lake, beneath the trees,\nFluttering and dancing in the breeze."
        },
        {
            "title": "The Road Not Taken",
            "text": "Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could\nTo where it bent in the undergrowth;"
        },
        {
            "title": "Sonnet 18",
            "text": "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer's lease hath all too short a date;"
        }
    ]
    
    print("Poem Analyzer - Theme Detection Demo")
    print("=" * 50)
    
    for i, poem in enumerate(sample_poems, 1):
        print(f"\nPoem {i}: {poem['title']}")
        analysis = analyzer.analyze_poem(poem)
        
        print(f"Themes detected: {analysis['themes']}")
        print(f"Q-codes: {analysis['q_codes']}")
        print(f"Summary: {analyzer.get_theme_summary(analysis)}")
        print(f"Primary theme: {analyzer.get_primary_theme(analysis)}")


if __name__ == "__main__":
    main()
