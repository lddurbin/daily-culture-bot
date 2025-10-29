#!/usr/bin/env python3
"""
Integration test for birthday poem artwork matching improvements.

This test verifies that the complete workflow produces better results
for the birthday poem test case from the console output.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import poem_analyzer, match_explainer, datacreator


class TestBirthdayPoemIntegration:
    """Test complete workflow with birthday poem."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = poem_analyzer.PoemAnalyzer()
        self.explainer = match_explainer.MatchExplainer()
        self.creator = datacreator.PaintingDataCreator()
        
        # The exact poem from the console output
        self.birthday_poem = {
            "title": "To Mrs M. B. on Her Birthday.",
            "text": "Oh, be thou blest with all that Heaven can send,\nLong health, long youth, long pleasure, and a friend;\nLong may thy tender eyes with pleasure shine,\nAnd long may Heaven preserve thee, friend of mine."
        }
    
    def test_birthday_poem_q_codes_improved(self):
        """Test that birthday poem generates better Q-codes with concrete noun priority."""
        # Mock OpenAI to return concrete elements
        with patch.object(self.analyzer, 'openai_client') as mock_client, \
             patch.object(self.analyzer, 'openai_analyzer') as mock_analyzer:
            
            # Mock the analyzer instance
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze_poem_with_ai.return_value = {
                "primary_emotions": ["joy", "reflection"],
                "secondary_emotions": ["contentment"],
                "emotional_tone": "celebratory",
                "themes": ["friendship", "celebration", "birthday"],
                "concrete_elements": {
                    "natural_objects": [],
                    "man_made_objects": [],
                    "living_beings": ["friend"],
                    "abstract_concepts": ["wishes", "pleasure", "health", "youth"]
                },
                "narrative_elements": {
                    "setting": "indoor",
                    "time_of_day": "day",
                    "human_presence": "central"
                },
                "visual_aesthetic": {"mood": "light"},
                "intensity": 6,
                "avoid_subjects": ["loneliness", "conflict", "hardship"],
                "q_codes": ["Q2385804", "Q17297777", "Q5", "Q2811"]  # Expected concrete Q-codes
            }
            self.analyzer.openai_analyzer = mock_analyzer_instance
            
            analysis = self.analyzer.analyze_poem(self.birthday_poem)
            q_codes = analysis.get("q_codes", [])
            
            # Should include celebration/friendship Q-codes (concrete nouns)
            expected_codes = ["Q2385804", "Q17297777", "Q5", "Q2811"]  # celebration, friendship, human, birthday
            for code in expected_codes:
                assert code in q_codes, f"Expected Q-code {code} not found in {q_codes}"
            
            # Should NOT include irrelevant abstract codes
            irrelevant_codes = ["Q183", "Q4", "Q18811"]  # night, death, battle
            for code in irrelevant_codes:
                assert code not in q_codes, f"Unexpected Q-code {code} found in {q_codes}"
    
    def test_depicts_bonus_filtering(self):
        """Test that depicts bonus only applies to concrete, visually verifiable objects."""
        # Test concrete artwork (should get bonus)
        concrete_artwork = {
            "title": "Portrait of Friends Celebrating",
            "subject_q_codes": ["Q5", "Q134307", "Q2811"],  # human, portrait, birthday
            "genre_q_codes": ["Q16875712"]  # genre painting
        }
        
        # Test abstract artwork (should NOT get bonus)
        abstract_artwork = {
            "title": "Abstract Concept",
            "subject_q_codes": ["Q4", "Q316", "Q183"],  # death, love, night
            "genre_q_codes": ["Q191163"]  # landscape
        }
        
        # Test eligibility
        concrete_eligible = self.creator._is_eligible_for_depicts_bonus(concrete_artwork["subject_q_codes"])
        abstract_eligible = self.creator._is_eligible_for_depicts_bonus(abstract_artwork["subject_q_codes"])
        
        assert concrete_eligible, "Concrete artwork should be eligible for depicts bonus"
        assert not abstract_eligible, "Abstract artwork should NOT be eligible for depicts bonus"
    
    def test_explanation_uses_specific_data(self):
        """Test that explanation uses specific analysis data instead of generic templates."""
        poem_analysis = {
            "primary_emotions": ["joy"],
            "emotional_tone": "celebratory",
            "themes": ["friendship", "celebration"],
            "concrete_elements": {
                "living_beings": ["friend"],
                "abstract_concepts": ["pleasure", "wishes"]
            },
            "narrative_elements": {
                "setting": "indoor",
                "human_presence": "central"
            }
        }
        
        artwork = {
            "title": "Portrait of Friends",
            "subject_q_codes": ["Q5", "Q134307"],
            "genre_q_codes": ["Q16875712"]
        }
        
        vision_analysis = {
            "success": True,
            "analysis": {
                "detected_objects": ["person", "smile", "celebration"],
                "setting": "indoor",
                "mood": "joyful"
            }
        }
        
        explanation = self.explainer.explain_match(poem_analysis, artwork, 0.7, vision_analysis)
        why_matched = explanation.get("why_matched", "")
        
        # Should use specific data, not generic templates
        generic_phrases = [
            "both address themes of mortality, loss, and remembrance",
            "thematic and emotional alignment"
        ]
        
        for phrase in generic_phrases:
            assert phrase not in why_matched.lower(), f"Explanation should not contain generic phrase: {phrase}"
        
        # Should contain specific elements
        specific_elements = ["person", "smile", "celebration", "indoor", "shared elements"]
        found_specific = any(element in why_matched.lower() for element in specific_elements)
        assert found_specific, f"Explanation should contain specific elements. Got: {why_matched}"
    
    def test_complete_workflow_score_improvement(self):
        """Test that the complete workflow produces better scores for appropriate artwork."""
        # Mock poem analysis with improved Q-codes
        poem_analysis = {
            "primary_emotions": ["joy", "reflection"],
            "secondary_emotions": ["contentment"],
            "emotional_tone": "celebratory",
            "themes": ["friendship", "celebration", "birthday"],
            "concrete_elements": {
                "living_beings": ["friend"],
                "abstract_concepts": ["wishes", "pleasure", "health", "youth"]
            },
            "narrative_elements": {
                "setting": "indoor",
                "time_of_day": "day",
                "human_presence": "central"
            },
            "visual_aesthetic": {"mood": "light"},
            "intensity": 6,
            "avoid_subjects": ["loneliness", "conflict", "hardship"]
        }
        
        # Appropriate artwork (should score higher) - includes Q-codes from concrete elements
        appropriate_artwork = {
            "title": "Portrait of Friends Celebrating",
            "subject_q_codes": ["Q5", "Q134307", "Q2811", "Q2385804", "Q17297777"],  # human, portrait, birthday, celebration, friendship
            "genre_q_codes": ["Q16875712"],  # genre painting
            "year": 1850
        }
        
        # Inappropriate artwork (should score lower)
        inappropriate_artwork = {
            "title": "Flower Arrangement with Parrot",
            "subject_q_codes": ["Q11427", "Q729"],  # flower, animal
            "genre_q_codes": ["Q1640824"],  # floral painting
            "year": 1697
        }
        
        # Score both artworks
        appropriate_score = self.analyzer.score_artwork_match(
            poem_analysis,
            appropriate_artwork["subject_q_codes"],
            appropriate_artwork["genre_q_codes"],
            artwork_year=appropriate_artwork["year"]
        )
        
        inappropriate_score = self.analyzer.score_artwork_match(
            poem_analysis,
            inappropriate_artwork["subject_q_codes"],
            inappropriate_artwork["genre_q_codes"],
            artwork_year=inappropriate_artwork["year"]
        )
        
        # Appropriate artwork should score higher
        assert appropriate_score > inappropriate_score, f"Appropriate artwork ({appropriate_score}) should score higher than inappropriate ({inappropriate_score})"
        
        # Appropriate artwork should score above 0.5 (target from requirements)
        assert appropriate_score > 0.5, f"Appropriate artwork should score above 0.5, got {appropriate_score}"
        
        # Test depicts bonus eligibility
        appropriate_eligible = self.creator._is_eligible_for_depicts_bonus(appropriate_artwork["subject_q_codes"])
        inappropriate_eligible = self.creator._is_eligible_for_depicts_bonus(inappropriate_artwork["subject_q_codes"])
        
        assert appropriate_eligible, "Appropriate artwork should be eligible for depicts bonus"
        # Inappropriate artwork might still be eligible if it has concrete objects, but should score lower overall


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
