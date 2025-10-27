#!/usr/bin/env python3
"""
Concrete Element Extractor for Daily Culture Bot

This module extracts concrete nouns, objects, and settings from poems using spaCy
to enable more precise artwork matching based on verifiable elements rather than
abstract emotions.
"""

import spacy
from typing import Dict, List, Set, Optional
import re

# Import theme mappings
try:
    from . import poem_themes
except ImportError:
    try:
        import poem_themes
    except ImportError:
        poem_themes = None


class ConcreteElementExtractor:
    """Extracts concrete elements from poems using spaCy NLP."""
    
    def __init__(self):
        """Initialize the extractor with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy English model loaded for concrete element extraction")
        except OSError:
            print("❌ spaCy English model not found. Please run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Import theme mappings for Q-code mapping
        if poem_themes:
            self.theme_mappings = poem_themes.THEME_MAPPINGS
            self.object_mappings = getattr(poem_themes, 'OBJECT_MAPPINGS', {})
        else:
            self.theme_mappings = {}
            self.object_mappings = {}
            print("⚠️ Warning: poem_themes module not available")
    
    def extract_concrete_nouns(self, poem_text: str) -> Dict[str, List[str]]:
        """
        Extract concrete nouns from poem text and categorize them.
        
        Args:
            poem_text: The poem text to analyze
            
        Returns:
            Dictionary with categorized nouns
        """
        if not self.nlp or not poem_text:
            return {
                "natural_objects": [],
                "man_made_objects": [],
                "living_beings": [],
                "abstract_concepts": [],
                "settings": [],
                "all_nouns": []
            }
        
        # Process text with spaCy
        doc = self.nlp(poem_text)
        
        # Extract nouns and categorize them
        natural_objects = []
        man_made_objects = []
        living_beings = []
        abstract_concepts = []
        settings = []
        all_nouns = []
        
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                noun = token.lemma_.lower()
                all_nouns.append(noun)
                
                # Categorize based on semantic knowledge and patterns
                category = self._categorize_noun(noun, token)
                
                if category == "natural":
                    natural_objects.append(noun)
                elif category == "man_made":
                    man_made_objects.append(noun)
                elif category == "living":
                    living_beings.append(noun)
                elif category == "abstract":
                    abstract_concepts.append(noun)
                elif category == "setting":
                    settings.append(noun)
        
        return {
            "natural_objects": list(set(natural_objects)),
            "man_made_objects": list(set(man_made_objects)),
            "living_beings": list(set(living_beings)),
            "abstract_concepts": list(set(abstract_concepts)),
            "settings": list(set(settings)),
            "all_nouns": list(set(all_nouns))
        }
    
    def _categorize_noun(self, noun: str, token) -> str:
        """
        Categorize a noun based on its semantic properties.
        
        Args:
            noun: The noun to categorize
            token: The spaCy token object
            
        Returns:
            Category string: "natural", "man_made", "living", "abstract", "setting"
        """
        # Natural objects patterns
        natural_patterns = [
            r'\b(tree|trees|forest|wood|woods|leaf|leaves|flower|flowers|rose|roses|grass|mountain|mountains|hill|hills|river|rivers|lake|lakes|ocean|oceans|sea|seas|sky|skies|cloud|clouds|star|stars|moon|sun|wind|rain|snow|ice|fire|earth|stone|stones|rock|rocks)\b',
            r'\b(bird|birds|fish|fishes|animal|animals|beast|beasts|creature|creatures)\b'
        ]
        
        # Man-made objects patterns
        man_made_patterns = [
            r'\b(house|houses|building|buildings|church|churches|castle|castles|bridge|bridges|road|roads|street|streets|door|doors|window|windows|wall|walls|roof|roofs|tower|towers|ship|ships|boat|boats|car|cars|train|trains|book|books|table|tables|chair|chairs|bed|beds)\b',
            r'\b(sword|swords|gun|guns|weapon|weapons|tool|tools|machine|machines|engine|engines)\b'
        ]
        
        # Living beings patterns
        living_patterns = [
            r'\b(man|men|woman|women|child|children|boy|boys|girl|girls|person|people|human|humans|soldier|soldiers|king|kings|queen|queens|prince|princess)\b',
            r'\b(dog|dogs|cat|cats|horse|horses|cow|cows|sheep|lamb|lambs|wolf|wolves|lion|lions|eagle|eagles|swan|swans|butterfly|butterflies)\b'
        ]
        
        # Settings patterns
        setting_patterns = [
            r'\b(garden|gardens|field|fields|meadow|meadows|valley|valleys|desert|deserts|city|cities|town|towns|village|villages|home|homes|room|rooms|kitchen|bedroom|parlor|hall|halls)\b',
            r'\b(church|churches|castle|castles|palace|palaces|temple|temples|school|schools|hospital|hospitals|prison|prisons|dungeon|dungeons)\b'
        ]
        
        # Check patterns
        for pattern in natural_patterns:
            if re.search(pattern, noun):
                return "natural"
        
        for pattern in man_made_patterns:
            if re.search(pattern, noun):
                return "man_made"
        
        for pattern in living_patterns:
            if re.search(pattern, noun):
                return "living"
        
        for pattern in setting_patterns:
            if re.search(pattern, noun):
                return "setting"
        
        # Default to abstract for uncategorized nouns
        return "abstract"
    
    def map_nouns_to_q_codes(self, nouns: List[str]) -> List[str]:
        """
        Map extracted nouns to Wikidata Q-codes using theme mappings.
        
        Args:
            nouns: List of nouns to map
            
        Returns:
            List of Wikidata Q-codes
        """
        q_codes = []
        
        for noun in nouns:
            # Check direct mappings first
            if noun in self.object_mappings:
                q_codes.extend(self.object_mappings[noun]["q_codes"])
                continue
            
            # Check theme mappings
            for theme, data in self.theme_mappings.items():
                if noun in data["keywords"]:
                    q_codes.extend(data["q_codes"])
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_q_codes = []
        for q_code in q_codes:
            if q_code not in seen:
                seen.add(q_code)
                unique_q_codes.append(q_code)
        
        return unique_q_codes
    
    def categorize_nouns(self, nouns: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of nouns by type.
        
        Args:
            nouns: List of nouns to categorize
            
        Returns:
            Dictionary with categorized nouns
        """
        categorized = {
            "natural_objects": [],
            "man_made_objects": [],
            "living_beings": [],
            "abstract_concepts": [],
            "settings": []
        }
        
        for noun in nouns:
            # Create a mock token for categorization
            doc = self.nlp(noun) if self.nlp else None
            if doc and len(doc) > 0:
                token = doc[0]
                category = self._categorize_noun(noun, token)
                
                if category == "natural":
                    categorized["natural_objects"].append(noun)
                elif category == "man_made":
                    categorized["man_made_objects"].append(noun)
                elif category == "living":
                    categorized["living_beings"].append(noun)
                elif category == "setting":
                    categorized["settings"].append(noun)
                else:
                    categorized["abstract_concepts"].append(noun)
        
        return categorized
    
    def extract_narrative_elements(self, poem_text: str) -> Dict[str, any]:
        """
        Extract narrative elements from poem text.
        
        Args:
            poem_text: The poem text to analyze
            
        Returns:
            Dictionary with narrative elements
        """
        if not self.nlp or not poem_text:
            return {
                "has_protagonist": False,
                "protagonist_type": "none",
                "setting": "ambiguous",
                "time_of_day": "ambiguous",
                "season": "timeless",
                "human_presence": "absent",
                "weather": "ambiguous"
            }
        
        doc = self.nlp(poem_text)
        
        # Analyze for protagonist
        has_protagonist = False
        protagonist_type = "none"
        
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() in ["i", "me", "my", "myself"]:
                has_protagonist = True
                protagonist_type = "human"
                break
            elif token.pos_ in ["NOUN", "PROPN"] and token.text.lower() in ["man", "woman", "child", "person", "boy", "girl"]:
                has_protagonist = True
                protagonist_type = "human"
                break
        
        # Analyze for setting
        setting = "ambiguous"
        setting_keywords = {
            "indoor": ["room", "house", "home", "kitchen", "bedroom", "hall", "inside", "indoors"],
            "outdoor": ["garden", "field", "forest", "mountain", "outside", "outdoors", "street", "road"],
            "urban": ["city", "town", "street", "building", "crowd", "people"],
            "rural": ["countryside", "village", "farm", "meadow", "pastoral"],
            "seascape": ["ocean", "sea", "shore", "beach", "wave", "sail", "ship"],
            "celestial": ["sky", "star", "moon", "sun", "cloud", "heaven"]
        }
        
        text_lower = poem_text.lower()
        for setting_type, keywords in setting_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                setting = setting_type
                break
        
        # Analyze for time of day
        time_of_day = "ambiguous"
        time_keywords = {
            "dawn": ["dawn", "sunrise", "morning", "early"],
            "day": ["day", "noon", "afternoon", "bright", "sunny"],
            "dusk": ["dusk", "sunset", "evening", "twilight"],
            "night": ["night", "midnight", "dark", "moon", "stars"]
        }
        
        for time_type, keywords in time_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                time_of_day = time_type
                break
        
        # Analyze for season
        season = "timeless"
        season_keywords = {
            "spring": ["spring", "bloom", "flowers", "green", "new"],
            "summer": ["summer", "hot", "warm", "sun", "bright"],
            "autumn": ["autumn", "fall", "leaves", "golden", "harvest"],
            "winter": ["winter", "cold", "snow", "ice", "frost"]
        }
        
        for season_type, keywords in season_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                season = season_type
                break
        
        # Analyze for human presence
        human_presence = "absent"
        human_keywords = ["man", "woman", "child", "people", "person", "human", "i", "me", "we", "us"]
        if any(keyword in text_lower for keyword in human_keywords):
            human_presence = "implied"
            if text_lower.count("i ") > 0 or text_lower.count(" me ") > 0:
                human_presence = "central"
        
        # Analyze for weather
        weather = "ambiguous"
        weather_keywords = {
            "clear": ["clear", "bright", "sunny", "calm"],
            "stormy": ["storm", "stormy", "wind", "windy", "thunder"],
            "rainy": ["rain", "rainy", "wet", "drizzle"],
            "snowy": ["snow", "snowy", "white", "frost"],
            "foggy": ["fog", "foggy", "mist", "misty", "haze"]
        }
        
        for weather_type, keywords in weather_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                weather = weather_type
                break
        
        return {
            "has_protagonist": has_protagonist,
            "protagonist_type": protagonist_type,
            "setting": setting,
            "time_of_day": time_of_day,
            "season": season,
            "human_presence": human_presence,
            "weather": weather
        }


def main():
    """Demonstrate the concrete element extractor functionality."""
    extractor = ConcreteElementExtractor()
    
    # Sample poems for testing
    sample_poems = [
        {
            "title": "I Wandered Lonely as a Cloud",
            "text": "I wandered lonely as a cloud\nThat floats on high o'er vales and hills,\nWhen all at once I saw a crowd,\nA host, of golden daffodils;\nBeside the lake, beneath the trees,\nFluttering and dancing in the breeze."
        },
        {
            "title": "The Road Not Taken",
            "text": "Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could\nTo where it bent in the undergrowth;"
        }
    ]
    
    print("Concrete Element Extractor - Demo")
    print("=" * 50)
    
    for i, poem in enumerate(sample_poems, 1):
        print(f"\nPoem {i}: {poem['title']}")
        
        # Extract concrete nouns
        nouns = extractor.extract_concrete_nouns(poem['text'])
        print(f"Natural objects: {nouns['natural_objects']}")
        print(f"Man-made objects: {nouns['man_made_objects']}")
        print(f"Living beings: {nouns['living_beings']}")
        print(f"Settings: {nouns['settings']}")
        
        # Extract narrative elements
        narrative = extractor.extract_narrative_elements(poem['text'])
        print(f"Setting: {narrative['setting']}")
        print(f"Time of day: {narrative['time_of_day']}")
        print(f"Human presence: {narrative['human_presence']}")


if __name__ == "__main__":
    main()
