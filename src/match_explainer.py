#!/usr/bin/env python3
"""
Match Explainer Module for Daily Culture Bot

This module generates human-readable explanations for poem-artwork pairings,
helping users understand why specific artworks were matched to poems and
providing transparency into the matching algorithm.
"""

from typing import Dict, List, Optional, Tuple
import json


class MatchExplainer:
    """Generates detailed explanations for poem-artwork matches."""
    
    def __init__(self):
        """Initialize the match explainer."""
        pass
    
    def explain_match(self, poem_analysis: Dict, artwork: Dict, score: float, 
                     vision_analysis: Optional[Dict] = None) -> Dict:
        """
        Generate detailed explanation of why artwork matches poem.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            artwork: Dictionary containing artwork data
            score: Match score (0.0-1.0)
            vision_analysis: Optional vision analysis results
            
        Returns:
            Dictionary with detailed match explanation
        """
        explanation = {
            "match_score": round(score, 3),
            "overall_assessment": self._get_overall_assessment(score),
            "why_matched": "",
            "specific_connections": [],
            "concrete_matches": {
                "shared_objects": [],
                "setting_alignment": "",
                "temporal_alignment": "",
                "emotional_resonance": ""
            },
            "potential_tensions": [],
            "analysis_details": {
                "poem_themes": poem_analysis.get("themes", []),
                "poem_emotions": poem_analysis.get("primary_emotions", []) + poem_analysis.get("secondary_emotions", []),
                "artwork_subjects": artwork.get("subject_q_codes", []),
                "artwork_genres": artwork.get("genre_q_codes", [])
            }
        }
        
        # Generate specific connections
        connections = self._find_specific_connections(poem_analysis, artwork, vision_analysis)
        explanation["specific_connections"] = connections
        
        # Generate concrete matches
        concrete_matches = self._find_concrete_matches(poem_analysis, artwork, vision_analysis)
        explanation["concrete_matches"] = concrete_matches
        
        # Generate overall summary
        explanation["why_matched"] = self._generate_summary(score, connections, concrete_matches)
        
        # Find potential tensions
        tensions = self._find_potential_tensions(poem_analysis, artwork, vision_analysis)
        explanation["potential_tensions"] = tensions
        
        return explanation
    
    def _get_overall_assessment(self, score: float) -> str:
        """Get overall assessment based on match score."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "strong"
        elif score >= 0.4:
            return "moderate"
        elif score >= 0.2:
            return "weak"
        else:
            return "poor"
    
    def _find_specific_connections(self, poem_analysis: Dict, artwork: Dict, 
                                 vision_analysis: Optional[Dict]) -> List[str]:
        """Find specific connections between poem and artwork."""
        connections = []
        
        # Theme connections
        poem_themes = poem_analysis.get("themes", [])
        artwork_subjects = artwork.get("subject_q_codes", [])
        
        theme_connections = self._map_themes_to_connections(poem_themes, artwork_subjects)
        connections.extend(theme_connections)
        
        # Emotional connections
        poem_emotions = poem_analysis.get("primary_emotions", []) + poem_analysis.get("secondary_emotions", [])
        emotional_connections = self._map_emotions_to_connections(poem_emotions, artwork_subjects)
        connections.extend(emotional_connections)
        
        # Setting connections
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            setting_connection = self._map_setting_to_connection(poem_setting, artwork_subjects, vision_analysis)
            if setting_connection:
                connections.append(setting_connection)
        
        # Time of day connections
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            time_connection = self._map_time_to_connection(poem_time, artwork_subjects, vision_analysis)
            if time_connection:
                connections.append(time_connection)
        
        # Vision analysis connections
        if vision_analysis and vision_analysis.get("success"):
            vision_connections = self._map_vision_to_connections(poem_analysis, vision_analysis)
            connections.extend(vision_connections)
        
        return connections[:5]  # Limit to top 5 connections
    
    def _map_themes_to_connections(self, poem_themes: List[str], artwork_subjects: List[str]) -> List[str]:
        """Map poem themes to artwork connections."""
        connections = []
        
        theme_mappings = {
            "nature": ["Both feature natural elements and landscapes"],
            "flowers": ["Both involve floral imagery and botanical themes"],
            "water": ["Both depict water scenes, oceans, or aquatic elements"],
            "love": ["Both explore themes of love, romance, and affection"],
            "death": ["Both address themes of mortality, loss, and remembrance"],
            "war": ["Both depict conflict, battle, or military themes"],
            "night": ["Both feature nocturnal scenes and darkness"],
            "day": ["Both depict daylight scenes and brightness"],
            "city": ["Both feature urban settings and city life"],
            "animals": ["Both include animal imagery and wildlife"],
            "seasons": ["Both reflect seasonal changes and temporal themes"]
        }
        
        for theme in poem_themes:
            # Handle case where theme might be a list or other non-string type
            if isinstance(theme, str):
                if theme.lower() in theme_mappings:
                    connections.append(theme_mappings[theme.lower()])
            elif isinstance(theme, list):
                # If theme is a list, process each item
                for sub_theme in theme:
                    if isinstance(sub_theme, str) and sub_theme.lower() in theme_mappings:
                        connections.append(theme_mappings[sub_theme.lower()])
        
        return connections
    
    def _map_emotions_to_connections(self, poem_emotions: List[str], artwork_subjects: List[str]) -> List[str]:
        """Map poem emotions to artwork connections."""
        connections = []
        
        emotion_mappings = {
            "melancholy": ["Both convey a sense of melancholy and introspection"],
            "joy": ["Both express joy, celebration, and positive emotions"],
            "peace": ["Both evoke feelings of peace, tranquility, and serenity"],
            "love": ["Both explore themes of love, passion, and emotional connection"],
            "hope": ["Both convey hope, optimism, and forward-looking themes"],
            "despair": ["Both express despair, hopelessness, and emotional darkness"],
            "nostalgia": ["Both evoke nostalgia, memory, and longing for the past"],
            "grief": ["Both address grief, loss, and mourning"]
        }
        
        for emotion in poem_emotions:
            # Handle case where emotion might be a list or other non-string type
            if isinstance(emotion, str):
                if emotion.lower() in emotion_mappings:
                    connections.append(emotion_mappings[emotion.lower()])
            elif isinstance(emotion, list):
                # If emotion is a list, process each item
                for sub_emotion in emotion:
                    if isinstance(sub_emotion, str) and sub_emotion.lower() in emotion_mappings:
                        connections.append(emotion_mappings[sub_emotion.lower()])
        
        return connections
    
    def _map_setting_to_connection(self, poem_setting: str, artwork_subjects: List[str], 
                                 vision_analysis: Optional[Dict]) -> Optional[str]:
        """Map poem setting to artwork connection."""
        setting_mappings = {
            "indoor": "Both are set in indoor, interior spaces",
            "outdoor": "Both feature outdoor, exterior settings",
            "urban": "Both depict urban environments and cityscapes",
            "rural": "Both show rural, countryside settings",
            "seascape": "Both feature ocean, sea, or coastal scenes",
            "celestial": "Both include sky, celestial, or heavenly imagery"
        }
        
        if poem_setting in setting_mappings:
            return setting_mappings[poem_setting]
        
        # Check vision analysis for setting match
        if vision_analysis and vision_analysis.get("success"):
            vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
            if vision_setting == poem_setting:
                return f"Both are set in {poem_setting} environments"
        
        return None
    
    def _map_time_to_connection(self, poem_time: str, artwork_subjects: List[str], 
                              vision_analysis: Optional[Dict]) -> Optional[str]:
        """Map poem time of day to artwork connection."""
        time_mappings = {
            "dawn": "Both depict dawn, sunrise, or early morning scenes",
            "day": "Both show daylight, bright, or sunny scenes",
            "dusk": "Both feature dusk, sunset, or twilight moments",
            "night": "Both depict night, darkness, or nocturnal scenes"
        }
        
        if poem_time in time_mappings:
            return time_mappings[poem_time]
        
        # Check vision analysis for time match
        if vision_analysis and vision_analysis.get("success"):
            vision_time = vision_analysis.get("analysis", {}).get("time_of_day", "")
            if vision_time == poem_time:
                return f"Both are set during {poem_time}"
        
        return None
    
    def _map_vision_to_connections(self, poem_analysis: Dict, vision_analysis: Dict) -> List[str]:
        """Map vision analysis to poem connections."""
        connections = []
        vision_data = vision_analysis.get("analysis", {})
        
        # Color palette connections
        poem_colors = poem_analysis.get("color_references", [])
        vision_colors = vision_data.get("dominant_colors", [])
        
        if poem_colors and vision_colors:
            color_overlap = set(poem_colors) & set(vision_colors)
            if color_overlap:
                connections.append(f"Both feature similar color palettes: {', '.join(color_overlap)}")
        
        # Mood connections
        poem_mood = poem_analysis.get("visual_aesthetic", {}).get("mood", "")
        vision_mood = vision_data.get("mood", "")
        
        if poem_mood and vision_mood and poem_mood == vision_mood:
            connections.append(f"Both convey a {poem_mood} mood and atmosphere")
        
        # Composition connections
        poem_composition = poem_analysis.get("spatial_qualities", "")
        vision_composition = vision_data.get("composition", "")
        
        if poem_composition and vision_composition:
            composition_mappings = {
                "intimate": "Both have intimate, close-up compositions",
                "expansive": "Both feature expansive, wide compositions",
                "chaotic": "Both have dynamic, chaotic compositions",
                "ordered": "Both show ordered, structured compositions"
            }
            
            if poem_composition in composition_mappings:
                connections.append(composition_mappings[poem_composition])
        
        return connections
    
    def _find_concrete_matches(self, poem_analysis: Dict, artwork: Dict, 
                             vision_analysis: Optional[Dict]) -> Dict:
        """Find concrete matches between poem and artwork."""
        concrete_matches = {
            "shared_objects": [],
            "setting_alignment": "",
            "temporal_alignment": "",
            "emotional_resonance": ""
        }
        
        # Shared objects
        poem_objects = poem_analysis.get("concrete_elements", {})
        poem_natural = poem_objects.get("natural_objects", [])
        poem_man_made = poem_objects.get("man_made_objects", [])
        poem_living = poem_objects.get("living_beings", [])
        
        all_poem_objects = poem_natural + poem_man_made + poem_living
        
        if vision_analysis and vision_analysis.get("success"):
            vision_objects = vision_analysis.get("analysis", {}).get("detected_objects", [])
            shared_objects = set(all_poem_objects) & set(vision_objects)
            concrete_matches["shared_objects"] = list(shared_objects)
        
        # Setting alignment
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            concrete_matches["setting_alignment"] = f"Both feature {poem_setting} settings"
        
        # Temporal alignment
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            concrete_matches["temporal_alignment"] = f"Both are set during {poem_time}"
        
        # Emotional resonance
        poem_emotions = poem_analysis.get("primary_emotions", [])
        if poem_emotions:
            concrete_matches["emotional_resonance"] = f"Both convey {', '.join(poem_emotions[:2])} emotions"
        
        return concrete_matches
    
    def _find_potential_tensions(self, poem_analysis: Dict, artwork: Dict, 
                               vision_analysis: Optional[Dict]) -> List[str]:
        """Find potential tensions or mismatches."""
        tensions = []
        
        # Setting conflicts
        poem_setting = poem_analysis.get("narrative_elements", {}).get("setting", "")
        if poem_setting and poem_setting != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_setting = vision_analysis.get("analysis", {}).get("setting", "")
                if vision_setting and vision_setting != poem_setting:
                    tensions.append(f"Setting mismatch: poem is {poem_setting}, artwork is {vision_setting}")
        
        # Time conflicts
        poem_time = poem_analysis.get("narrative_elements", {}).get("time_of_day", "")
        if poem_time and poem_time != "ambiguous":
            if vision_analysis and vision_analysis.get("success"):
                vision_time = vision_analysis.get("analysis", {}).get("time_of_day", "")
                if vision_time and vision_time != poem_time and vision_time != "ambiguous":
                    tensions.append(f"Time mismatch: poem is {poem_time}, artwork is {vision_time}")
        
        # Mood conflicts
        poem_mood = poem_analysis.get("visual_aesthetic", {}).get("mood", "")
        if poem_mood:
            if vision_analysis and vision_analysis.get("success"):
                vision_mood = vision_analysis.get("analysis", {}).get("mood", "")
                if vision_mood and vision_mood != poem_mood:
                    mood_conflicts = {
                        ("light", "dark"): "Mood contrast: poem is light, artwork is dark",
                        ("dark", "light"): "Mood contrast: poem is dark, artwork is light",
                        ("serene", "turbulent"): "Mood contrast: poem is serene, artwork is turbulent",
                        ("turbulent", "serene"): "Mood contrast: poem is turbulent, artwork is serene"
                    }
                    
                    conflict_key = (poem_mood, vision_mood)
                    if conflict_key in mood_conflicts:
                        tensions.append(mood_conflicts[conflict_key])
        
        return tensions
    
    def _generate_summary(self, score: float, connections: List[str], 
                         concrete_matches: Dict) -> str:
        """Generate overall summary of the match."""
        if score >= 0.8:
            strength = "excellent"
        elif score >= 0.6:
            strength = "strong"
        elif score >= 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        if connections:
            primary_connection = connections[0]
            return f"This is a {strength} match because {primary_connection.lower()}"
        elif concrete_matches.get("shared_objects"):
            objects = concrete_matches["shared_objects"]
            return f"This is a {strength} match featuring shared elements: {', '.join(objects[:2])}"
        else:
            return f"This is a {strength} match based on thematic and emotional alignment"


if __name__ == "__main__":
    print("Match explainer module - use daily_culture_bot.py for CLI access")
