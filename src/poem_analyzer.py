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

# Import theme mappings
try:
    from . import poem_themes
except ImportError:
    # Fallback for when running as standalone module
    try:
        import poem_themes
    except ImportError:
        poem_themes = None

# Import OpenAI analyzer
try:
    from . import openai_analyzer
except ImportError:
    # Fallback for when running as standalone module
    try:
        import openai_analyzer
    except ImportError:
        openai_analyzer = None


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
        
        # Import theme mappings from separate module
        if poem_themes:
            self.theme_mappings = poem_themes.THEME_MAPPINGS
            self.emotion_mappings = poem_themes.EMOTION_MAPPINGS
        else:
            # Fallback if module not available
            self.theme_mappings = {}
            self.emotion_mappings = {}
            print("⚠️ Warning: poem_themes module not available, theme analysis disabled")
        
        # Initialize OpenAI analyzer if available
        if openai_analyzer and self.openai_client:
            self.openai_analyzer = openai_analyzer.OpenAIAnalyzer(
                self.openai_client, self.theme_mappings, self.emotion_mappings
            )
        else:
            self.openai_analyzer = None
            if not openai_analyzer:
                print("⚠️ Warning: openai_analyzer module not available")
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _reinitialize_openai_analyzer(self):
        """Reinitialize the OpenAI analyzer when client is set in tests."""
        if openai_analyzer and self.openai_client:
            self.openai_analyzer = openai_analyzer.OpenAIAnalyzer(
                self.openai_client, self.theme_mappings, self.emotion_mappings
            )
    
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
            
            # Combine all emotions
            all_emotions = ai_analysis.get("primary_emotions", []) + ai_analysis.get("secondary_emotions", [])
            
            return {
                "primary_emotions": ai_analysis.get("primary_emotions", []),
                "secondary_emotions": ai_analysis.get("secondary_emotions", []),
                "emotions": all_emotions,  # Combined emotions for backward compatibility
                "emotional_tone": ai_analysis.get("emotional_tone", "unknown"),
                "themes": combined_themes,
                "narrative_elements": ai_analysis.get("narrative_elements", {}),
                "concrete_elements": ai_analysis.get("concrete_elements", {}),
                "symbolic_objects": ai_analysis.get("symbolic_objects", []),
                "spatial_qualities": ai_analysis.get("spatial_qualities", "unknown"),
                "movement_energy": ai_analysis.get("movement_energy", "unknown"),
                "color_references": ai_analysis.get("color_references", []),
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
        """Delegate to openai_analyzer module."""
        if self.openai_analyzer:
            return self.openai_analyzer.analyze_poem_with_ai(poem)
        else:
            raise ValueError("OpenAI analyzer not available")
    
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
            "narrative_elements": {},
            "concrete_elements": {},
            "symbolic_objects": [],
            "spatial_qualities": "unknown",
            "movement_energy": "unknown",
            "color_references": [],
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
    
    def calculate_era_score(self, poet_birth_year: Optional[int], poet_death_year: Optional[int], 
                           artwork_year: Optional[int]) -> Optional[float]:
        """
        Calculate era score based on temporal distance between poet's lifetime and artwork.
        Returns 0.0-1.0 score or None if dates are unavailable.
        
        Args:
            poet_birth_year: Year poet was born
            poet_death_year: Year poet died
            artwork_year: Year artwork was created
            
        Returns:
            Float score 0.0-1.0 or None if dates unavailable
        """
        # Return None if any dates are missing
        if any(x is None for x in [poet_birth_year, poet_death_year, artwork_year]):
            return None
        
        buffer_years = 50
        
        # Perfect match: artwork created during poet's lifetime
        if poet_birth_year <= artwork_year <= poet_death_year:
            return 1.0
        
        # Calculate distance from nearest lifetime boundary
        if artwork_year < poet_birth_year:
            distance = poet_birth_year - artwork_year
        else:  # artwork_year > poet_death_year
            distance = artwork_year - poet_death_year
        
        # Linear decay within buffer zone
        if distance <= buffer_years:
            # Linear decay from 1.0 to 0.5 within buffer
            return 1.0 - (distance / buffer_years) * 0.5
        
        # Outside buffer zone
        return 0.0
    
    def estimate_poet_era(self, poem: Dict) -> Optional[Dict[str, int]]:
        """
        Estimate poet's era based on poem characteristics.
        For now, returns None as this is a placeholder for future enhancement.
        
        Args:
            poem: Poem dictionary
            
        Returns:
            Dictionary with 'birth_year' and 'death_year' or None
        """
        # TODO: Implement estimation based on language patterns, themes, etc.
        # For now, return None to gracefully fall back to visual-only matching
        return None
    
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
    
    def score_artwork_match(self, poem_analysis: Dict, artwork_q_codes: List[str], 
                           artwork_genres: List[str], artwork_year: Optional[int] = None,
                           poet_birth_year: Optional[int] = None, poet_death_year: Optional[int] = None) -> float:
        """
        Score how well an artwork matches a poem's emotional and thematic profile.
        Returns score from 0.0 (poor match) to 1.0 (excellent match).
        
        New scoring weights (as per user requirements):
        - Concrete Elements: 35% (setting, objects, composition)
        - Theme/Subject: 30% (keep this)
        - Emotional Tone: 25% (reduce from 40%)
        - Genre: 10% (reduce from 20%)
        - Intensity: 5% (reduce from 10%)
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_q_codes: List of Q-codes associated with the artwork
            artwork_genres: List of genre Q-codes for the artwork
            artwork_year: Optional year artwork was created
            poet_birth_year: Optional year poet was born
            poet_death_year: Optional year poet died
            
        Returns:
            Float score between 0.0 and 1.0
        """
        if not poem_analysis:
            return 0.0
        
        score = 0.0
        
        # 1. Concrete Elements Match (35% weight) - NEW PRIORITY
        concrete_score = self._score_concrete_elements(poem_analysis, artwork_q_codes)
        score += concrete_score * 0.35
        
        # 2. Theme/subject match (30% weight) - KEPT SAME
        themes = poem_analysis.get("themes", [])
        theme_q_codes = []
        
        for theme in themes:
            if theme.lower() in self.theme_mappings:
                theme_q_codes.extend(self.theme_mappings[theme.lower()]["q_codes"])
        
        theme_matches = len(set(artwork_q_codes) & set(theme_q_codes))
        if theme_matches > 0:
            score += 0.3
        
        # 3. Emotional Tone Match (25% weight) - REDUCED FROM 40%
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
            score += 0.25  # Reduced from 0.4 to 0.25
        elif secondary_matches > 0:
            score += 0.125  # Reduced from 0.2 to 0.125
        
        # 4. Genre alignment (10% weight) - REDUCED FROM 20%
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
            score += 0.1  # Reduced from 0.2 to 0.1
        elif artwork_genres:  # Has genres but not matching
            score += 0.05  # Reduced from 0.1 to 0.05
        
        # 5. Intensity alignment (5% weight) - REDUCED FROM 10%
        poem_intensity = poem_analysis.get("intensity", 5)
        
        # Simple intensity scoring based on artwork complexity
        # More complex subjects (multiple Q-codes) suggest higher intensity
        artwork_complexity = len(artwork_q_codes)
        
        # Normalize complexity to 1-10 scale
        normalized_complexity = min(artwork_complexity * 2, 10)
        
        # Score based on how close artwork complexity matches poem intensity
        intensity_diff = abs(poem_intensity - normalized_complexity)
        intensity_score = max(0, (10 - intensity_diff) / 10)
        
        score += intensity_score * 0.05  # Reduced from 0.1 to 0.05
        
        # Check for avoid_subjects conflicts
        avoid_subjects = poem_analysis.get("avoid_subjects", [])
        avoid_q_codes = []
        
        for subject in avoid_subjects:
            if subject.lower() in self.theme_mappings:
                avoid_q_codes.extend(self.theme_mappings[subject.lower()]["q_codes"])
        
        avoid_conflicts = len(set(artwork_q_codes) & set(avoid_q_codes))
        if avoid_conflicts > 0:
            score *= 0.5  # Halve the score if there are conflicts
        
        # Calculate era score if dates are available
        era_score = self.calculate_era_score(poet_birth_year, poet_death_year, artwork_year)
        
        if era_score is not None:
            # Combine visual/thematic score (80% weight) with era score (20% weight)
            # era_score is already 0.0-1.0, so we just combine
            final_score = (score * 0.8) + (era_score * 0.2)
            return min(final_score, 1.0)  # Cap at 1.0
        else:
            # No era data available, return visual/thematic score only
            return min(score, 1.0)  # Cap at 1.0
    
    def _score_concrete_elements(self, poem_analysis: Dict, artwork_q_codes: List[str]) -> float:
        """
        Score concrete elements match between poem and artwork.
        Returns score from 0.0 to 1.0 based on concrete element alignment.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_q_codes: List of Q-codes associated with the artwork
            
        Returns:
            Float score between 0.0 and 1.0
        """
        concrete_score = 0.0
        
        # 1. Score concrete objects (natural, man-made, living beings)
        concrete_elements = poem_analysis.get("concrete_elements", {})
        if concrete_elements:
            # Get Q-codes for concrete objects mentioned in poem
            poem_object_q_codes = []
            
            # Natural objects
            natural_objects = concrete_elements.get("natural_objects", [])
            for obj in natural_objects:
                if obj.lower() in poem_themes.OBJECT_MAPPINGS:
                    poem_object_q_codes.extend(poem_themes.OBJECT_MAPPINGS[obj.lower()]["q_codes"])
            
            # Man-made objects
            man_made_objects = concrete_elements.get("man_made_objects", [])
            for obj in man_made_objects:
                if obj.lower() in poem_themes.OBJECT_MAPPINGS:
                    poem_object_q_codes.extend(poem_themes.OBJECT_MAPPINGS[obj.lower()]["q_codes"])
            
            # Living beings
            living_beings = concrete_elements.get("living_beings", [])
            for obj in living_beings:
                if obj.lower() in poem_themes.OBJECT_MAPPINGS:
                    poem_object_q_codes.extend(poem_themes.OBJECT_MAPPINGS[obj.lower()]["q_codes"])
            
            # Calculate object matches
            if poem_object_q_codes:
                object_matches = len(set(artwork_q_codes) & set(poem_object_q_codes))
                total_objects = len(set(poem_object_q_codes))
                concrete_score += (object_matches / max(total_objects, 1)) * 0.4  # 40% of concrete score
        
        # 2. Score setting alignment
        narrative_elements = poem_analysis.get("narrative_elements", {})
        if narrative_elements:
            poem_setting = narrative_elements.get("setting", "unknown")
            
            # Map settings to Q-codes
            setting_mappings = {
                "outdoor": ["Q7860", "Q191163"],  # nature, landscape
                "indoor": ["Q134307", "Q16875712"],  # portrait, genre painting
                "urban": ["Q515", "Q134307"],  # city, portrait
                "rural": ["Q7860", "Q191163"],  # nature, landscape
                "seascape": ["Q9430", "Q191163"],  # ocean, landscape
                "celestial": ["Q183", "Q40446"],  # night, nocturne
                "abstract": ["Q40446", "Q16875712"]  # nocturne, genre painting
            }
            
            setting_q_codes = setting_mappings.get(poem_setting, [])
            if setting_q_codes:
                setting_matches = len(set(artwork_q_codes) & set(setting_q_codes))
                if setting_matches > 0:
                    concrete_score += 0.3  # 30% of concrete score
        
        # 3. Score spatial qualities alignment
        spatial_qualities = poem_analysis.get("spatial_qualities", "unknown")
        if spatial_qualities != "unknown":
            # Map spatial qualities to artwork characteristics
            spatial_mappings = {
                "enclosed": ["Q134307", "Q16875712"],  # portrait, genre painting
                "open": ["Q191163", "Q7860"],  # landscape, nature
                "vertical": ["Q134307", "Q2839016"],  # portrait, religious painting
                "horizontal": ["Q191163", "Q7860"],  # landscape, nature
                "centered": ["Q134307", "Q16875712"],  # portrait, genre painting
                "dispersed": ["Q191163", "Q7860"]  # landscape, nature
            }
            
            spatial_q_codes = spatial_mappings.get(spatial_qualities, [])
            if spatial_q_codes:
                spatial_matches = len(set(artwork_q_codes) & set(spatial_q_codes))
                if spatial_matches > 0:
                    concrete_score += 0.2  # 20% of concrete score
        
        # 4. Score movement energy alignment
        movement_energy = poem_analysis.get("movement_energy", "unknown")
        if movement_energy != "unknown":
            # Map movement energy to artwork characteristics
            movement_mappings = {
                "static": ["Q134307", "Q191163"],  # portrait, landscape
                "flowing": ["Q191163", "Q7860"],  # landscape, nature
                "explosive": ["Q16875712", "Q2839016"],  # genre painting, religious painting
                "rhythmic": ["Q16875712", "Q1640824"],  # genre painting, floral painting
                "stagnant": ["Q134307", "Q191163"]  # portrait, landscape
            }
            
            movement_q_codes = movement_mappings.get(movement_energy, [])
            if movement_q_codes:
                movement_matches = len(set(artwork_q_codes) & set(movement_q_codes))
                if movement_matches > 0:
                    concrete_score += 0.1  # 10% of concrete score
        
        # 5. Add specificity bonuses for highly specific matches
        specificity_bonus = self._calculate_specificity_bonus(poem_analysis, artwork_q_codes)
        concrete_score += specificity_bonus
        
        return min(concrete_score, 1.0)  # Cap at 1.0
    
    def _calculate_specificity_bonus(self, poem_analysis: Dict, artwork_q_codes: List[str]) -> float:
        """
        Calculate specificity bonuses for highly specific matches.
        Returns bonus score from 0.0 to 0.2 for specific matches.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_q_codes: List of Q-codes associated with the artwork
            
        Returns:
            Float bonus score between 0.0 and 0.2
        """
        bonus = 0.0
        
        # 1. Direct noun matches (highest specificity)
        concrete_elements = poem_analysis.get("concrete_elements", {})
        if concrete_elements:
            poem_object_q_codes = []
            
            # Collect all concrete object Q-codes from poem
            for category in ["natural_objects", "man_made_objects", "living_beings"]:
                objects = concrete_elements.get(category, [])
                for obj in objects:
                    if obj.lower() in poem_themes.OBJECT_MAPPINGS:
                        poem_object_q_codes.extend(poem_themes.OBJECT_MAPPINGS[obj.lower()]["q_codes"])
            
            # Calculate direct matches
            if poem_object_q_codes:
                direct_matches = len(set(artwork_q_codes) & set(poem_object_q_codes))
                total_objects = len(set(poem_object_q_codes))
                match_ratio = direct_matches / max(total_objects, 1)
                
                # High bonus for direct object matches
                if match_ratio >= 0.5:  # 50% or more objects match
                    bonus += 0.15  # Significant bonus
                elif match_ratio >= 0.25:  # 25% or more objects match
                    bonus += 0.1   # Moderate bonus
                elif match_ratio > 0:  # Any objects match
                    bonus += 0.05  # Small bonus
        
        # 2. Temporal alignment (time of day, season)
        narrative_elements = poem_analysis.get("narrative_elements", {})
        if narrative_elements:
            poem_time = narrative_elements.get("time_of_day", "unknown")
            poem_season = narrative_elements.get("season", "timeless")
            
            # Map temporal elements to Q-codes
            temporal_mappings = {
                "dawn": ["Q183", "Q40446"],  # night, nocturne (dawn is transitional)
                "day": ["Q7860", "Q191163"],  # nature, landscape
                "dusk": ["Q183", "Q40446"],  # night, nocturne
                "night": ["Q183", "Q40446"], # night, nocturne
                "spring": ["Q11427", "Q7860"], # flower, nature
                "summer": ["Q7860", "Q191163"], # nature, landscape
                "autumn": ["Q11427", "Q7860"], # flower, nature (autumn colors)
                "winter": ["Q183", "Q40446"]  # night, nocturne (winter darkness)
            }
            
            # Check time of day alignment
            if poem_time != "unknown":
                time_q_codes = temporal_mappings.get(poem_time, [])
                if time_q_codes:
                    time_matches = len(set(artwork_q_codes) & set(time_q_codes))
                    if time_matches > 0:
                        bonus += 0.05  # Temporal alignment bonus
            
            # Check season alignment
            if poem_season != "timeless":
                season_q_codes = temporal_mappings.get(poem_season, [])
                if season_q_codes:
                    season_matches = len(set(artwork_q_codes) & set(season_q_codes))
                    if season_matches > 0:
                        bonus += 0.05  # Seasonal alignment bonus
        
        # 3. Color alignment bonus
        color_references = poem_analysis.get("color_references", [])
        if color_references:
            # Map colors to Q-codes (simplified mapping)
            color_mappings = {
                "red": ["Q11427", "Q16875712"],  # flower, genre painting
                "blue": ["Q9430", "Q191163"],    # ocean, landscape
                "green": ["Q7860", "Q191163"],   # nature, landscape
                "yellow": ["Q11427", "Q7860"],   # flower, nature
                "white": ["Q183", "Q40446"],     # night, nocturne
                "black": ["Q183", "Q40446"],     # night, nocturne
                "gold": ["Q11427", "Q16875712"], # flower, genre painting
                "silver": ["Q183", "Q40446"]     # night, nocturne
            }
            
            poem_color_q_codes = []
            for color in color_references:
                color_lower = color.lower()
                if color_lower in color_mappings:
                    poem_color_q_codes.extend(color_mappings[color_lower])
            
            if poem_color_q_codes:
                color_matches = len(set(artwork_q_codes) & set(poem_color_q_codes))
                if color_matches > 0:
                    bonus += 0.03  # Color alignment bonus
        
        # 4. Human presence alignment
        if narrative_elements:
            human_presence = narrative_elements.get("human_presence", "absent")
            
            if human_presence in ["central", "peripheral"]:
                # Artwork should have human subjects
                human_q_codes = ["Q134307", "Q16875712"]  # portrait, genre painting
                human_matches = len(set(artwork_q_codes) & set(human_q_codes))
                if human_matches > 0:
                    bonus += 0.02  # Human presence bonus
            elif human_presence == "absent":
                # Artwork should not have human subjects
                non_human_q_codes = ["Q191163", "Q7860", "Q11427"]  # landscape, nature, flower
                non_human_matches = len(set(artwork_q_codes) & set(non_human_q_codes))
                if non_human_matches > 0:
                    bonus += 0.02  # Absence of humans bonus
        
        return min(bonus, 0.2)  # Cap bonus at 0.2 (20% of total score)


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
