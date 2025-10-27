#!/usr/bin/env python3
"""
Two-Stage Matcher Module for Daily Culture Bot

This module implements a two-stage matching system that first applies hard constraints
to filter out incompatible artwork, then scores the remaining artwork using weighted
criteria for optimal poem-artwork pairing.
"""

from typing import Dict, List, Optional, Tuple
import math


class TwoStageMatcher:
    """Implements two-stage matching: hard constraints + weighted scoring."""
    
    def __init__(self):
        """Initialize the two-stage matcher."""
        # Hard constraint mappings
        self.hard_exclusions = {
            "peaceful": ["Q198", "Q18811", "Q124490"],  # war, battle, violence
            "serene": ["Q198", "Q18811", "Q124490"],    # war, battle, violence
            "joyful": ["Q4", "Q203", "Q2912397"],       # death, mourning, memorial
            "celebratory": ["Q4", "Q203", "Q2912397"],  # death, mourning, memorial
            "intimate": ["Q191163"],                     # vast landscapes for intimate poems
            "bright": ["Q183", "Q111"],                  # darkness for bright poems
            "light": ["Q183", "Q111"]                    # darkness for light poems
        }
        
        # Soft conflict mappings (reduce score by 0.3)
        self.soft_conflicts = {
            "indoor": ["outdoor"],
            "outdoor": ["indoor"],
            "day": ["night"],
            "night": ["day"],
            "urban": ["rural"],
            "rural": ["urban"],
            "warm": ["cool"],
            "cool": ["warm"]
        }
    
    def apply_hard_constraints(self, poem_analysis: Dict, artwork: Dict, 
                            vision_analysis: Optional[Dict] = None) -> bool:
        """
        Stage 1: Check if artwork passes hard constraints.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork: Dictionary containing artwork data
            vision_analysis: Optional vision analysis results
            
        Returns:
            True if artwork is viable, False to exclude
        """
        # Check emotional tone conflicts
        emotional_tone = poem_analysis.get("emotional_tone", "")
        if emotional_tone in self.hard_exclusions:
            artwork_q_codes = artwork.get("subject_q_codes", [])
            artwork_genres = artwork.get("genre_q_codes", [])
            all_artwork_codes = artwork_q_codes + artwork_genres
            
            excluded_codes = self.hard_exclusions[emotional_tone]
            if any(code in all_artwork_codes for code in excluded_codes):
                return False
        
        # Check avoid subjects
        avoid_subjects = poem_analysis.get("avoid_subjects", [])
        if avoid_subjects:
            artwork_q_codes = artwork.get("subject_q_codes", [])
            # This would need mapping from avoid_subjects to Q-codes
            # For now, skip this check
            pass
        
        # Check setting conflicts
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
                if vision_setting and vision_setting != poem_setting:
                    # Check for hard setting conflicts
                    hard_setting_conflicts = {
                        ("indoor", "outdoor"): False,  # Not a hard conflict
                        ("outdoor", "indoor"): False,  # Not a hard conflict
                        ("urban", "rural"): False,     # Not a hard conflict
                        ("rural", "urban"): False      # Not a hard conflict
                    }
                    
                    conflict_key = (poem_setting, vision_setting)
                    if conflict_key in hard_setting_conflicts:
                        return hard_setting_conflicts[conflict_key]
        
        # Check human presence requirements
        poem_human_presence = poem_analysis.get("narrative_elements", {}).get("human_presence", "")
        if poem_human_presence == "central":
            if vision_analysis and vision_analysis.get("success"):
                vision_human_presence = vision_analysis.get("analysis", {}).get("human_presence", "")
                if vision_human_presence == "absent":
                    return False
        
        # Check time of day consistency (if both explicit)
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_time = vision_analysis.get("analysis", {}).get("time_of_day", "")
                if vision_time and vision_time != "ambiguous":
                    # Hard time conflicts (very rare)
                    hard_time_conflicts = {
                        ("dawn", "night"): False,  # Dawn and night are too different
                        ("night", "dawn"): False   # Night and dawn are too different
                    }
                    
                    conflict_key = (poem_time, vision_time)
                    if conflict_key in hard_time_conflicts:
                        return hard_time_conflicts[conflict_key]
        
        return True
    
    def score_artwork(self, poem_analysis: Dict, artwork: Dict, 
                     vision_analysis: Optional[Dict] = None,
                     poet_birth_year: Optional[int] = None,
                     poet_death_year: Optional[int] = None) -> float:
        """
        Stage 2: Score artwork that passed constraints.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork: Dictionary containing artwork data
            vision_analysis: Optional vision analysis results
            poet_birth_year: Optional year poet was born
            poet_death_year: Optional year poet died
            
        Returns:
            Float score between 0.0 and 1.0
        """
        score = 0.0
        
        # 1. Concrete Elements Match (35% weight)
        concrete_score = self._score_concrete_elements(poem_analysis, artwork, vision_analysis)
        score += concrete_score * 0.35
        
        # 2. Theme/Subject Match (30% weight)
        theme_score = self._score_theme_match(poem_analysis, artwork)
        score += theme_score * 0.30
        
        # 3. Emotional Tone Match (25% weight)
        emotion_score = self._score_emotional_tone(poem_analysis, artwork)
        score += emotion_score * 0.25
        
        # 4. Genre Alignment (10% weight)
        genre_score = self._score_genre_alignment(poem_analysis, artwork)
        score += genre_score * 0.10
        
        # Apply specificity bonuses
        specificity_bonus = self._calculate_specificity_bonus(poem_analysis, artwork, vision_analysis)
        score += specificity_bonus
        
        # Apply soft conflicts penalty
        soft_penalty = self._calculate_soft_conflicts_penalty(poem_analysis, artwork, vision_analysis)
        score -= soft_penalty
        
        # Apply era score if dates are available
        era_score = self._calculate_era_score(poem_analysis, artwork, poet_birth_year, poet_death_year)
        if era_score is not None:
            # Combine visual/thematic score (80% weight) with era score (20% weight)
            final_score = (score * 0.8) + (era_score * 0.2)
            return min(final_score, 1.0)
        else:
            return min(score, 1.0)
    
    def _score_concrete_elements(self, poem_analysis: Dict, artwork: Dict, 
                               vision_analysis: Optional[Dict]) -> float:
        """Score concrete elements match (35% weight)."""
        score = 0.0
        
        # Direct noun matches (20% of total weight)
        poem_objects = poem_analysis.get("concrete_elements", {})
        poem_natural = poem_objects.get("natural_objects", [])
        poem_man_made = poem_objects.get("man_made_objects", [])
        poem_living = poem_objects.get("living_beings", [])
        
        all_poem_objects = poem_natural + poem_man_made + poem_living
        
        if vision_analysis and vision_analysis.get("success"):
            vision_objects = vision_analysis.get("analysis", {}).get("detected_objects", [])
            shared_objects = set(all_poem_objects) & set(vision_objects)
            
            if shared_objects:
                # Score based on number of shared objects
                object_score = min(len(shared_objects) / 5.0, 1.0)  # Cap at 5 objects
                score += object_score * 0.20
        
        # Setting/narrative elements (10% of total weight)
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
                if vision_setting == poem_setting:
                    score += 0.10
        
        # Spatial/compositional alignment (5% of total weight)
        poem_spatial = poem_analysis.get("spatial_qualities", "")
        if poem_spatial:
            if vision_analysis and vision_analysis.get("success"):
                vision_composition = vision_analysis.get("analysis", {}).get("composition", "")
                spatial_mappings = {
                    "enclosed": "intimate",
                    "open": "expansive",
                    "centered": "ordered",
                    "dispersed": "chaotic"
                }
                
                if poem_spatial in spatial_mappings:
                    expected_composition = spatial_mappings[poem_spatial]
                    if vision_composition == expected_composition:
                        score += 0.05
        
        return score
    
    def _score_theme_match(self, poem_analysis: Dict, artwork: Dict) -> float:
        """Score theme/subject match (30% weight)."""
        poem_themes = poem_analysis.get("themes", [])
        artwork_q_codes = artwork.get("subject_q_codes", [])
        
        if not poem_themes or not artwork_q_codes:
            return 0.0
        
        # This would need comprehensive theme-to-Q-code mapping
        # For now, return a basic score based on theme presence
        theme_score = 0.0
        for theme in poem_themes:
            # Simple theme matching - would be enhanced with proper mappings
            if theme.lower() in ["nature", "landscape"] and "Q191163" in artwork_q_codes:
                theme_score += 0.3
            elif theme.lower() in ["night", "darkness"] and "Q183" in artwork_q_codes:
                theme_score += 0.3
            elif theme.lower() in ["water", "ocean"] and "Q16970" in artwork_q_codes:
                theme_score += 0.3
        
        return min(theme_score, 1.0)
    
    def _score_emotional_tone(self, poem_analysis: Dict, artwork: Dict) -> float:
        """Score emotional tone match (25% weight)."""
        primary_emotions = poem_analysis.get("primary_emotions", [])
        secondary_emotions = poem_analysis.get("secondary_emotions", [])
        emotional_tone = poem_analysis.get("emotional_tone", "")
        
        artwork_q_codes = artwork.get("subject_q_codes", [])
        artwork_genres = artwork.get("genre_q_codes", [])
        all_artwork_codes = artwork_q_codes + artwork_genres
        
        score = 0.0
        
        # Primary emotions (15% of total weight)
        if primary_emotions:
            emotion_q_codes = self._map_emotions_to_q_codes(primary_emotions)
            primary_matches = len(set(all_artwork_codes) & set(emotion_q_codes))
            if primary_matches > 0:
                score += 0.15
        
        # Secondary emotions (10% of total weight)
        if secondary_emotions:
            emotion_q_codes = self._map_emotions_to_q_codes(secondary_emotions)
            secondary_matches = len(set(all_artwork_codes) & set(emotion_q_codes))
            if secondary_matches > 0:
                score += 0.10
        
        return score
    
    def _score_genre_alignment(self, poem_analysis: Dict, artwork: Dict) -> float:
        """Score genre alignment (10% weight)."""
        emotional_tone = poem_analysis.get("emotional_tone", "")
        artwork_genres = artwork.get("genre_q_codes", [])
        
        if not emotional_tone or not artwork_genres:
            return 0.0
        
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
            return 0.10
        elif artwork_genres:  # Has genres but not matching
            return 0.05  # Neutral genre
        else:
            return 0.0
    
    def _calculate_specificity_bonus(self, poem_analysis: Dict, artwork: Dict, 
                                   vision_analysis: Optional[Dict]) -> float:
        """Calculate specificity bonuses for precise matches."""
        bonus = 0.0
        
        # Direct noun match bonus
        poem_objects = poem_analysis.get("concrete_elements", {})
        poem_natural = poem_objects.get("natural_objects", [])
        poem_man_made = poem_objects.get("man_made_objects", [])
        poem_living = poem_objects.get("living_beings", [])
        
        all_poem_objects = poem_natural + poem_man_made + poem_living
        
        if vision_analysis and vision_analysis.get("success"):
            vision_objects = vision_analysis.get("analysis", {}).get("detected_objects", [])
            shared_objects = set(all_poem_objects) & set(vision_objects)
            
            # Direct noun match bonus
            if shared_objects:
                bonus += min(len(shared_objects) * 0.05, 0.20)  # Max 0.20 bonus
        
        # Setting match bonus
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
                if vision_setting == poem_setting:
                    bonus += 0.15
        
        # Time of day match bonus
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_time = vision_analysis.get("analysis", {}).get("time_of_day", "")
                if vision_time == poem_time:
                    bonus += 0.10
        
        # Season match bonus
        poem_season = poem_analysis.get("narrative_elements", {}).get("season", "")
        if poem_season and poem_season != "timeless":
            if vision_analysis and vision_analysis.get("success"):
                vision_season = vision_analysis.get("analysis", {}).get("season_indicators", "")
                if vision_season == poem_season:
                    bonus += 0.10
        
        # Color palette match bonus
        poem_colors = poem_analysis.get("color_references", [])
        if poem_colors:
            if vision_analysis and vision_analysis.get("success"):
                vision_colors = vision_analysis.get("analysis", {}).get("dominant_colors", [])
                color_overlap = set(poem_colors) & set(vision_colors)
                if color_overlap:
                    bonus += 0.05
        
        return bonus
    
    def _calculate_soft_conflicts_penalty(self, poem_analysis: Dict, artwork: Dict, 
                                        vision_analysis: Optional[Dict]) -> float:
        """Calculate penalty for soft conflicts."""
        penalty = 0.0
        
        # Setting conflicts
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
                if vision_setting and vision_setting != poem_setting:
                    if poem_setting in self.soft_conflicts:
                        if vision_setting in self.soft_conflicts[poem_setting]:
                            penalty += 0.3
        
        # Time conflicts
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_time = vision_analysis.get("analysis", {}).get("time_of_day", "")
                if vision_time and vision_time != "ambiguous":
                    if poem_time in self.soft_conflicts:
                        if vision_time in self.soft_conflicts[poem_time]:
                            penalty += 0.3
        
        return penalty
    
    def _calculate_era_score(self, poem_analysis: Dict, artwork: Dict, 
                           poet_birth_year: Optional[int], poet_death_year: Optional[int]) -> Optional[float]:
        """Calculate era score based on temporal distance."""
        if any(x is None for x in [poet_birth_year, poet_death_year]):
            return None
        
        artwork_year = artwork.get('year')
        if artwork_year is None:
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
    
    def filter_and_score_artwork(self, poem_analysis: Dict, artwork_candidates: List[Dict], 
                               min_score: float = 0.3, poet_birth_year: Optional[int] = None,
                               poet_death_year: Optional[int] = None) -> List[Tuple[Dict, float]]:
        """
        Main method: Filter artwork candidates through hard constraints, then score them.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_candidates: List of artwork dictionaries to filter and score
            min_score: Minimum score threshold for inclusion
            poet_birth_year: Optional poet birth year for era scoring
            poet_death_year: Optional poet death year for era scoring
            
        Returns:
            List of (artwork, score) tuples, sorted by score descending
        """
        if not artwork_candidates:
            return []
        
        scored_artworks = []
        
        for artwork in artwork_candidates:
            try:
                # Stage 1: Apply hard constraints
                vision_analysis = artwork.get("vision_analysis")
                if not self.apply_hard_constraints(poem_analysis, artwork, vision_analysis):
                    continue  # Skip this artwork
                
                # Stage 2: Score the artwork
                score = self.score_artwork(
                    poem_analysis, 
                    artwork, 
                    vision_analysis=vision_analysis,
                    poet_birth_year=poet_birth_year,
                    poet_death_year=poet_death_year
                )
                
                # Only include if above minimum score
                if score >= min_score:
                    scored_artworks.append((artwork, score))
                    
            except Exception as e:
                print(f"Error processing artwork '{artwork.get('title', 'Unknown')}': {e}")
                continue
        
        # Sort by score descending
        scored_artworks.sort(key=lambda x: x[1], reverse=True)
        
        return scored_artworks
    
    def _apply_hard_constraints(self, poem_analysis: Dict, artwork_candidates: List[Dict]) -> List[Dict]:
        """
        Apply hard constraints to filter artwork candidates.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork_candidates: List of artwork dictionaries to filter
            
        Returns:
            List of artwork dictionaries that passed hard constraints
        """
        filtered_artworks = []
        
        for artwork in artwork_candidates:
            try:
                vision_analysis = artwork.get("vision_analysis")
                if self.apply_hard_constraints(poem_analysis, artwork, vision_analysis):
                    filtered_artworks.append(artwork)
            except Exception as e:
                print(f"Error applying hard constraints to artwork '{artwork.get('title', 'Unknown')}': {e}")
                continue
        
        return filtered_artworks
    
    def _map_emotions_to_q_codes(self, emotions: List[str]) -> List[str]:
        """Map emotions to Wikidata Q-codes."""
        emotion_mappings = {
            "grief": ["Q4", "Q203", "Q2912397"],  # death, mourning, memorial
            "melancholy": ["Q183", "Q8886", "Q35127"],  # night, loneliness, solitude
            "joy": ["Q2385804", "Q8274", "Q1068639"],  # celebration, dance, festival
            "peace": ["Q23397", "Q35127", "Q483130"],  # landscape, solitude, pastoral
            "love": ["Q316", "Q16538", "Q506"],  # love, romantic, flower
            "hope": ["Q111", "Q525", "Q12133"],  # day, sun, light
            "despair": ["Q183", "Q4", "Q8886"],  # night, death, loneliness
            "nostalgia": ["Q23397", "Q35127", "Q395"]  # landscape, solitude, building
        }
        
        q_codes = []
        for emotion in emotions:
            if emotion.lower() in emotion_mappings:
                q_codes.extend(emotion_mappings[emotion.lower()])
        
        return list(set(q_codes))


def main():
    """Demonstrate the two-stage matcher functionality."""
    matcher = TwoStageMatcher()
    
    # Sample poem analysis
    poem_analysis = {
        "themes": ["nature", "night"],
        "primary_emotions": ["melancholy"],
        "secondary_emotions": ["peace"],
        "emotional_tone": "melancholic",
        "narrative_elements": {
            "setting": "outdoor",
            "time_of_day": "night",
            "season": "spring",
            "human_presence": "central"
        },
        "concrete_elements": {
            "natural_objects": ["tree", "moon", "stars"],
            "man_made_objects": [],
            "living_beings": ["person"]
        },
        "spatial_qualities": "enclosed",
        "color_references": ["dark", "blue", "silver"]
    }
    
    # Sample artwork
    artwork = {
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "year": 1889,
        "subject_q_codes": ["Q183", "Q191163"],  # night, landscape
        "genre_q_codes": ["Q191163"]  # landscape
    }
    
    # Sample vision analysis
    vision_analysis = {
        "success": True,
        "analysis": {
            "detected_objects": ["tree", "moon", "stars", "sky"],
            "setting": "outdoor",
            "time_of_day": "night",
            "season_indicators": "spring",
            "composition": "intimate",
            "mood": "melancholic",
            "dominant_colors": ["blue", "dark", "silver"]
        }
    }
    
    print("Two-Stage Matcher - Demo")
    print("=" * 50)
    
    # Stage 1: Hard constraints
    passes_constraints = matcher.apply_hard_constraints(poem_analysis, artwork, vision_analysis)
    print(f"Passes hard constraints: {passes_constraints}")
    
    if passes_constraints:
        # Stage 2: Scoring
        score = matcher.score_artwork(poem_analysis, artwork, vision_analysis, 1809, 1892)
        print(f"Match score: {score:.3f}")
        
        # Show component scores
        concrete_score = matcher._score_concrete_elements(poem_analysis, artwork, vision_analysis)
        theme_score = matcher._score_theme_match(poem_analysis, artwork)
        emotion_score = matcher._score_emotional_tone(poem_analysis, artwork)
        genre_score = matcher._score_genre_alignment(poem_analysis, artwork)
        specificity_bonus = matcher._calculate_specificity_bonus(poem_analysis, artwork, vision_analysis)
        
        print(f"\nComponent Scores:")
        print(f"  Concrete elements: {concrete_score:.3f}")
        print(f"  Theme match: {theme_score:.3f}")
        print(f"  Emotional tone: {emotion_score:.3f}")
        print(f"  Genre alignment: {genre_score:.3f}")
        print(f"  Specificity bonus: {specificity_bonus:.3f}")


if __name__ == "__main__":
    main()
