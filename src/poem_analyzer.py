#!/usr/bin/env python3
"""
Poem Analyzer for Daily Culture Bot

This module analyzes poems to extract themes and subjects, then maps them
to Wikidata entity IDs for complementary artwork matching.
"""

import re
import json
import os
from typing import List, Dict, Tuple, Set, Optional
from collections import Counter

# OpenAI integration
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class PoemAnalyzer:
    def __init__(self):
        """Initialize the poem analyzer with theme mappings and OpenAI client."""
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if OpenAI and os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                print("✅ OpenAI API initialized for enhanced poem analysis")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            print("ℹ️ OpenAI API key not found, using keyword-based analysis only")
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
        
        # Emotion-aware mappings for better artwork matching
        self.emotion_mappings = {
            "grief": {
                "q_codes": ["Q4", "Q203", "Q2912397", "Q3305213"],  # death, mourning, memorial, painting
                "genres": ["Q134307", "Q2839016"],  # portrait, religious painting
                "keywords": ["mourning", "memorial", "sorrow", "loss", "burial", "pietà", "funeral", "grave"]
            },
            "melancholy": {
                "q_codes": ["Q183", "Q8886", "Q35127"],  # night, loneliness, solitude
                "genres": ["Q191163", "Q40446"],  # landscape, nocturne
                "keywords": ["solitary", "twilight", "contemplative", "pensive", "sad", "blue", "lonely"]
            },
            "joy": {
                "q_codes": ["Q2385804", "Q8274", "Q1068639"],  # celebration, dance, festival
                "genres": ["Q16875712", "Q1640824"],  # genre painting, floral painting
                "keywords": ["celebration", "dance", "festive", "bright", "colorful", "happy", "merry"]
            },
            "peace": {
                "q_codes": ["Q23397", "Q35127", "Q483130"],  # landscape, solitude, pastoral
                "genres": ["Q191163", "Q1640824"],  # landscape, still life
                "keywords": ["pastoral", "serene", "calm", "quiet", "peaceful", "tranquil", "gentle"]
            },
            "love": {
                "q_codes": ["Q316", "Q16538", "Q506"],  # love, romantic, flower
                "genres": ["Q134307", "Q1640824"],  # portrait, floral painting
                "keywords": ["romance", "passion", "tender", "sweet", "beloved", "heart", "kiss"]
            },
            "hope": {
                "q_codes": ["Q111", "Q525", "Q12133"],  # day, sun, light
                "genres": ["Q191163", "Q1640824"],  # landscape, floral painting
                "keywords": ["dawn", "morning", "bright", "promise", "future", "renewal", "spring"]
            },
            "despair": {
                "q_codes": ["Q183", "Q4", "Q8886"],  # night, death, loneliness
                "genres": ["Q191163", "Q134307"],  # landscape, portrait
                "keywords": ["dark", "hopeless", "empty", "void", "end", "nothing", "lost"]
            },
            "nostalgia": {
                "q_codes": ["Q23397", "Q35127", "Q395"],  # landscape, solitude, building
                "genres": ["Q191163", "Q134307"],  # landscape, portrait
                "keywords": ["memory", "past", "old", "remember", "childhood", "home", "familiar"]
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
        Analyze a poem to extract themes and emotions, then map them to Wikidata Q-codes.
        Uses OpenAI API if available, falls back to keyword-based analysis.
        
        Args:
            poem: Dictionary containing poem data with 'title' and 'text' keys
            
        Returns:
            Dictionary with analysis results including themes, emotions, q_codes, and confidence scores
        """
        if not poem or not isinstance(poem, dict):
            return self._empty_analysis()
        
        title = poem.get('title', '')
        text = poem.get('text', '')
        
        if not title and not text:
            return self._empty_analysis()
        
        # Try OpenAI analysis first if available
        ai_analysis = None
        if self.openai_client:
            try:
                ai_analysis = self.analyze_poem_with_ai(poem)
                print(f"🤖 AI analysis completed for: {title}")
            except Exception as e:
                print(f"⚠️ OpenAI analysis failed: {e}, falling back to keyword analysis")
                ai_analysis = None
        
        # Always do keyword-based analysis as fallback or supplement
        keyword_analysis = self._analyze_with_keywords(poem)
        
        # Combine results
        if ai_analysis:
            # Use AI analysis as primary, supplement with keywords
            combined_themes = list(set(ai_analysis.get("themes", []) + keyword_analysis.get("themes", [])))
            combined_q_codes = list(set(ai_analysis.get("q_codes", []) + keyword_analysis.get("q_codes", [])))
            
            return {
                "primary_emotions": ai_analysis.get("primary_emotions", []),
                "secondary_emotions": ai_analysis.get("secondary_emotions", []),
                "emotional_tone": ai_analysis.get("emotional_tone", "unknown"),
                "themes": combined_themes,
                "imagery_type": ai_analysis.get("imagery_type", "concrete"),
                "visual_aesthetic": ai_analysis.get("visual_aesthetic", {}),
                "subject_suggestions": ai_analysis.get("subject_suggestions", []),
                "intensity": ai_analysis.get("intensity", 5),
                "avoid_subjects": ai_analysis.get("avoid_subjects", []),
                "q_codes": combined_q_codes,
                "theme_scores": keyword_analysis.get("theme_scores", {}),
                "confidence_scores": keyword_analysis.get("confidence_scores", {}),
                "total_matches": keyword_analysis.get("total_matches", 0),
                "has_themes": len(combined_themes) > 0,
                "analysis_method": "ai_enhanced"
            }
        else:
            # Use keyword analysis only
            keyword_analysis["analysis_method"] = "keyword_only"
            return keyword_analysis
    
    def analyze_poem_with_ai(self, poem: Dict) -> Dict:
        """
        Analyze poem using OpenAI API to extract emotions, themes, and visual suggestions.
        
        Args:
            poem: Dictionary containing poem data with 'title' and 'text' keys
            
        Returns:
            Dictionary with AI analysis results
        """
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        title = poem.get('title', '')
        text = poem.get('text', '')
        full_text = f"{title}\n\n{text}".strip()
        
        prompt = f"""You are an expert in analyzing poetry for visual art pairing. Analyze this poem and return ONLY a JSON object with the following structure:

{{
  "primary_emotions": ["emotion1", "emotion2"],  // Top 2-3 dominant emotions
  "secondary_emotions": ["emotion3"],  // Supporting emotions
  "emotional_tone": "playful|serious|ironic|melancholic|celebratory|contemplative",
  "themes": ["theme1", "theme2"],  // Core subjects
  "imagery_type": "concrete|abstract|symbolic|literal",
  "visual_aesthetic": {{
    "mood": "light|dark|dramatic|serene|turbulent",
    "color_palette": "warm|cool|muted|vibrant|monochrome",
    "composition": "intimate|expansive|chaotic|ordered"
  }},
  "subject_suggestions": ["specific artwork subjects that match the poem's feeling and content"],
  "intensity": 1-10,
  "avoid_subjects": ["subjects that would clash with the poem's tone"]
}}

Poem:
{full_text}

Return ONLY valid JSON with no additional text."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert poetry analyst. Analyze poems for emotions, themes, and visual art suggestions. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                ai_result = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    ai_result = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from OpenAI response")
            
            # Map emotions and themes to Q-codes
            primary_emotions = ai_result.get("primary_emotions", [])
            secondary_emotions = ai_result.get("secondary_emotions", [])
            themes = ai_result.get("themes", [])
            
            q_codes = []
            
            # Add Q-codes for primary emotions (higher weight)
            for emotion in primary_emotions:
                if emotion.lower() in self.emotion_mappings:
                    q_codes.extend(self.emotion_mappings[emotion.lower()]["q_codes"])
            
            # Add Q-codes for secondary emotions (lower weight)
            for emotion in secondary_emotions:
                if emotion.lower() in self.emotion_mappings:
                    q_codes.extend(self.emotion_mappings[emotion.lower()]["q_codes"])
            
            # Add Q-codes for themes
            for theme in themes:
                if theme.lower() in self.theme_mappings:
                    q_codes.extend(self.theme_mappings[theme.lower()]["q_codes"])
            
            # Remove duplicates
            q_codes = list(set(q_codes))
            
            return {
                "primary_emotions": primary_emotions,
                "secondary_emotions": secondary_emotions,
                "emotional_tone": ai_result.get("emotional_tone", "unknown"),
                "themes": themes,
                "imagery_type": ai_result.get("imagery_type", "concrete"),
                "visual_aesthetic": ai_result.get("visual_aesthetic", {}),
                "subject_suggestions": ai_result.get("subject_suggestions", []),
                "intensity": ai_result.get("intensity", 5),
                "avoid_subjects": ai_result.get("avoid_subjects", []),
                "q_codes": q_codes
            }
            
        except Exception as e:
            raise ValueError(f"OpenAI API error: {e}")
    
    def _analyze_with_keywords(self, poem: Dict) -> Dict:
        """
        Analyze poem using keyword-based approach (original method).
        
        Args:
            poem: Dictionary containing poem data with 'title' and 'text' keys
            
        Returns:
            Dictionary with keyword analysis results
        """
        title = poem.get('title', '')
        text = poem.get('text', '')
        
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
    
    def get_emotion_q_codes(self, emotions: List[str]) -> List[str]:
        """Get Wikidata Q-codes for detected emotions."""
        q_codes = []
        
        for emotion in emotions:
            emotion_lower = emotion.lower()
            if emotion_lower in self.emotion_mappings:
                q_codes.extend(self.emotion_mappings[emotion_lower]["q_codes"])
        
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
            "primary_emotions": [],
            "secondary_emotions": [],
            "emotional_tone": "unknown",
            "themes": [],
            "imagery_type": "concrete",
            "visual_aesthetic": {},
            "subject_suggestions": [],
            "intensity": 5,
            "avoid_subjects": [],
            "q_codes": [],
            "theme_scores": {},
            "confidence_scores": {},
            "total_matches": 0,
            "has_themes": False,
            "analysis_method": "none"
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
        """Get combined Q-codes from multiple poem analyses, optimized for performance."""
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
        
        # Limit to 8 Q-codes maximum for query performance
        if len(unique_q_codes) > 8:
            print(f"⚠️ Limiting Q-codes from {len(unique_q_codes)} to 8 for performance")
            unique_q_codes = unique_q_codes[:8]
        
        return unique_q_codes
    
    def score_artwork_match(self, poem_analysis: Dict, artwork_q_codes: List[str], artwork_genres: List[str]) -> float:
        """
        Score how well an artwork matches a poem's emotional and thematic profile.
        Returns score from 0.0 (poor match) to 1.0 (excellent match).
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_q_codes: List of Q-codes associated with the artwork
            artwork_genres: List of genre Q-codes for the artwork
            
        Returns:
            Float score between 0.0 and 1.0
        """
        if not poem_analysis or not artwork_q_codes:
            return 0.0
        
        score = 0.0
        
        # 1. Primary emotion match (40% weight)
        primary_emotions = poem_analysis.get("primary_emotions", [])
        secondary_emotions = poem_analysis.get("secondary_emotions", [])
        
        primary_emotion_q_codes = []
        secondary_emotion_q_codes = []
        
        for emotion in primary_emotions:
            if emotion.lower() in self.emotion_mappings:
                primary_emotion_q_codes.extend(self.emotion_mappings[emotion.lower()]["q_codes"])
        
        for emotion in secondary_emotions:
            if emotion.lower() in self.emotion_mappings:
                secondary_emotion_q_codes.extend(self.emotion_mappings[emotion.lower()]["q_codes"])
        
        # Check for primary emotion matches
        primary_matches = len(set(artwork_q_codes) & set(primary_emotion_q_codes))
        secondary_matches = len(set(artwork_q_codes) & set(secondary_emotion_q_codes))
        
        if primary_matches > 0:
            score += 0.4  # Full weight for primary emotion match
        elif secondary_matches > 0:
            score += 0.2  # Half weight for secondary emotion match
        
        # 2. Theme/subject match (30% weight)
        themes = poem_analysis.get("themes", [])
        theme_q_codes = []
        
        for theme in themes:
            if theme.lower() in self.theme_mappings:
                theme_q_codes.extend(self.theme_mappings[theme.lower()]["q_codes"])
        
        theme_matches = len(set(artwork_q_codes) & set(theme_q_codes))
        if theme_matches > 0:
            score += 0.3
        
        # 3. Genre alignment (20% weight)
        emotional_tone = poem_analysis.get("emotional_tone", "unknown")
        visual_aesthetic = poem_analysis.get("visual_aesthetic", {})
        
        # Map emotional tone to appropriate genres
        tone_genre_mapping = {
            "playful": ["Q16875712", "Q1640824"],  # genre painting, floral painting
            "serious": ["Q134307", "Q2839016"],     # portrait, religious painting
            "melancholic": ["Q191163", "Q40446"],   # landscape, nocturne
            "celebratory": ["Q16875712", "Q1640824"], # genre painting, floral painting
            "contemplative": ["Q191163", "Q134307"], # landscape, portrait
            "ironic": ["Q16875712", "Q134307"]      # genre painting, portrait
        }
        
        appropriate_genres = tone_genre_mapping.get(emotional_tone, [])
        genre_matches = len(set(artwork_genres) & set(appropriate_genres))
        
        if genre_matches > 0:
            score += 0.2
        elif artwork_genres:  # Has genres but not matching
            score += 0.1  # Neutral genre
        
        # 4. Intensity alignment (10% weight)
        poem_intensity = poem_analysis.get("intensity", 5)
        
        # Simple intensity scoring based on artwork complexity
        # More complex subjects (multiple Q-codes) suggest higher intensity
        artwork_complexity = len(artwork_q_codes)
        
        # Normalize complexity to 1-10 scale
        normalized_complexity = min(artwork_complexity * 2, 10)
        
        # Score based on how close artwork complexity matches poem intensity
        intensity_diff = abs(poem_intensity - normalized_complexity)
        intensity_score = max(0, (10 - intensity_diff) / 10)
        
        score += intensity_score * 0.1
        
        # Check for avoid_subjects conflicts
        avoid_subjects = poem_analysis.get("avoid_subjects", [])
        avoid_q_codes = []
        
        for subject in avoid_subjects:
            if subject.lower() in self.theme_mappings:
                avoid_q_codes.extend(self.theme_mappings[subject.lower()]["q_codes"])
        
        avoid_conflicts = len(set(artwork_q_codes) & set(avoid_q_codes))
        if avoid_conflicts > 0:
            score *= 0.5  # Halve the score if there are conflicts
        
        return min(score, 1.0)  # Cap at 1.0


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
