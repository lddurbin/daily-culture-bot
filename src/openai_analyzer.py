#!/usr/bin/env python3
"""
OpenAI Analyzer Module for Daily Culture Bot

This module contains OpenAI integration for poem analysis.
Extracted from poem_analyzer.py to improve code organization and maintainability.
"""

import json
import re
from typing import Dict, List, Optional


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
            print(f"OpenAI analysis error: {e}")
            raise ValueError(f"OpenAI API error: {e}")
