#!/usr/bin/env python3
"""
OpenAI Analyzer Module for Daily Culture Bot

This module contains OpenAI integration for poem analysis.
Extracted from poem_analyzer.py to improve code organization and maintainability.
"""

import json
import re
from typing import Dict, List, Optional, Tuple


class OpenAIAnalyzer:
    """Handles OpenAI API integration for poem analysis."""
    
    def __init__(self, openai_client, theme_mappings: Dict, emotion_mappings: Dict):
        """
        Initialize OpenAI analyzer.
        
        Args:
            openai_client: OpenAI client instance
            theme_mappings: Theme mappings dictionary
            emotion_mappings: Emotion mappings dictionary
        """
        self.openai_client = openai_client
        self.theme_mappings = theme_mappings
        self.emotion_mappings = emotion_mappings
    
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
  "narrative_elements": {{
    "has_protagonist": true/false,
    "protagonist_type": "human|animal|abstract|none",
    "setting": "indoor|outdoor|abstract|urban|rural|seascape|celestial",
    "time_of_day": "dawn|day|dusk|night|ambiguous",
    "season": "spring|summer|autumn|winter|timeless",
    "human_presence": "central|peripheral|absent|implied",
    "weather": "clear|stormy|rainy|snowy|foggy|ambiguous"
  }},
  "concrete_elements": {{
    "natural_objects": ["specific nature elements mentioned"],
    "man_made_objects": ["specific objects, buildings, tools mentioned"],
    "living_beings": ["people, animals mentioned"],
    "abstract_concepts": ["love, death, time, etc."]
  }},
  "symbolic_objects": ["objects with symbolic meaning"],
  "spatial_qualities": "enclosed|open|vertical|horizontal|centered|dispersed",
  "movement_energy": "static|flowing|explosive|rhythmic|stagnant",
  "color_references": ["explicit color words in poem"],
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
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert poetry analyst. Analyze poems for emotions, themes, and visual art suggestions. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                ai_result = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
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
                "narrative_elements": ai_result.get("narrative_elements", {}),
                "concrete_elements": ai_result.get("concrete_elements", {}),
                "symbolic_objects": ai_result.get("symbolic_objects", []),
                "spatial_qualities": ai_result.get("spatial_qualities", "unknown"),
                "movement_energy": ai_result.get("movement_energy", "unknown"),
                "color_references": ai_result.get("color_references", []),
                "imagery_type": ai_result.get("imagery_type", "concrete"),
                "visual_aesthetic": ai_result.get("visual_aesthetic", {}),
                "subject_suggestions": ai_result.get("subject_suggestions", []),
                "intensity": ai_result.get("intensity", 5),
                "avoid_subjects": ai_result.get("avoid_subjects", []),
                "q_codes": q_codes
            }
            
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            raise ValueError(f"OpenAI API error: {e}")
    
    def select_best_artwork_matches(self, poem: Dict, candidates: List[Dict], count: int = 3) -> List[Tuple[Dict, str]]:
        """
        Given poem and candidate artworks, use AI to select best matches.
        
        Args:
            poem: Dictionary containing poem data with 'title' and 'text' keys
            candidates: List of candidate artwork dictionaries
            count: Number of best matches to select
            
        Returns:
            List of (artwork, reasoning) tuples sorted by match quality
        """
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        if not candidates:
            return []
        
        title = poem.get('title', '')
        text = poem.get('text', '')
        full_text = f"{title}\n\n{text}".strip()
        
        # Build candidate descriptions
        candidate_descriptions = []
        for i, artwork in enumerate(candidates, 1):
            title = artwork.get('title', 'Unknown Title')
            artist = artwork.get('artist', 'Unknown Artist')
            year = artwork.get('year', 'Unknown Year')
            medium = artwork.get('medium', 'Unknown Medium')
            
            # Get depicts information
            depicts_list = []
            if artwork.get('vision_analysis', {}).get('success'):
                detected_objects = artwork['vision_analysis']['analysis'].get('detected_objects', [])
                depicts_list = detected_objects[:5]  # Limit to top 5 objects
            
            description = f"{i}. \"{title}\" by {artist} ({year}) - {medium}"
            if depicts_list:
                description += f"\n   Depicts: {', '.join(depicts_list)}"
            
            candidate_descriptions.append(description)
        
        candidates_text = "\n".join(candidate_descriptions)
        
        prompt = f"""Given this poem and these candidate artworks, select the {count} best matches.
For each selection, explain why it pairs well with the poem.

Poem: {full_text}

Candidates:
{candidates_text}

Return ONLY a JSON object:
{{
  "selections": [
    {{
      "artwork_index": 1,
      "match_score": 0.85,
      "reasoning": "Both feature solitary figures in twilight..."
    }}
  ]
}}

Select artworks that best match the poem's:
- Concrete elements (objects, settings, scenes)
- Emotional tone and mood
- Visual aesthetic and composition
- Narrative elements (time, place, characters)
- Symbolic meaning and themes

Return ONLY valid JSON with no additional text."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert art curator. Select artworks that best complement poems based on visual, thematic, and emotional alignment. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                ai_result = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    ai_result = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from OpenAI response")
            
            # Process selections
            selections = ai_result.get("selections", [])
            results = []
            
            for selection in selections:
                artwork_index = selection.get("artwork_index", 1) - 1  # Convert to 0-based index
                reasoning = selection.get("reasoning", "No reasoning provided")
                
                # Validate index
                if 0 <= artwork_index < len(candidates):
                    artwork = candidates[artwork_index]
                    results.append((artwork, reasoning))
            
            print(f"🤖 AI selected {len(results)} best artwork matches from {len(candidates)} candidates")
            return results
            
        except Exception as e:
            print(f"OpenAI selection error: {e}")
            # Fallback: return first few candidates with generic reasoning
            fallback_results = []
            for i, artwork in enumerate(candidates[:count]):
                reasoning = f"Selected based on thematic alignment with poem"
                fallback_results.append((artwork, reasoning))
            return fallback_results