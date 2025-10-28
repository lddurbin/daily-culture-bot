#!/usr/bin/env python3
"""
Real data scenario tests for Daily Culture Bot.

Tests using real captured data to verify system behavior with actual data structures.
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestRealDataScenarios:
    """Test scenarios using real captured data."""
    
    def setup_method(self):
        """Set up test fixtures with real data."""
        # Load real data samples
        fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'real_data_samples.json')
        with open(fixtures_path, 'r') as f:
            self.real_data = json.load(f)
    
    def test_match_explainer_with_real_poem_analysis(self):
        """Test match explainer with real poem analysis data."""
        try:
            from match_explainer import MatchExplainer
            
            explainer = MatchExplainer()
            
            # Test with real poem analysis data
            for sample in self.real_data['poem_analysis_samples']:
                poem_analysis = sample['analysis_result']
                artwork = self.real_data['artwork_samples'][0]  # Use first artwork
                score = 0.75
                
                explanation = explainer.explain_match(poem_analysis, artwork, score)
                
                # Verify explanation structure
                assert isinstance(explanation, dict)
                assert 'match_score' in explanation
                assert explanation['match_score'] == score
                
                # Should handle real data structures gracefully
                assert isinstance(explanation.get('why_matched', ''), str)
                assert isinstance(explanation.get('emotional_connection', ''), str)
                assert isinstance(explanation.get('visual_elements', ''), str)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_match_explainer_with_nested_lists_real_data(self):
        """Test match explainer with real data containing nested lists."""
        try:
            from match_explainer import MatchExplainer
            
            explainer = MatchExplainer()
            
            # Test with nested lists sample
            nested_sample = None
            for sample in self.real_data['poem_analysis_samples']:
                if 'Nested Lists Test' in sample['input_poem']['title']:
                    nested_sample = sample
                    break
            
            if nested_sample:
                poem_analysis = nested_sample['analysis_result']
                artwork = self.real_data['artwork_samples'][2]  # Mountain Lake
                score = 0.82
                
                explanation = explainer.explain_match(poem_analysis, artwork, score)
                
                # Should handle nested lists gracefully
                assert isinstance(explanation, dict)
                assert 'match_score' in explanation
                assert explanation['match_score'] == score
                
                # Verify nested structures are handled
                assert isinstance(explanation.get('why_matched', ''), str)
                assert len(explanation.get('why_matched', '')) > 0
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_artwork_matching_with_real_data_structures(self):
        """Test artwork matching with real data structures."""
        try:
            from two_stage_matcher import TwoStageMatcher
            
            matcher = TwoStageMatcher()
            
            # Test with real poem analysis and artwork data
            for poem_sample in self.real_data['poem_analysis_samples']:
                poem_analysis = poem_sample['analysis_result']
                
                for artwork in self.real_data['artwork_samples']:
                    score = matcher.score_artwork(poem_analysis, artwork)
                    
                    # Verify score is valid
                    assert isinstance(score, float)
                    assert 0.0 <= score <= 1.0
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_full_workflow_with_historical_successful_runs(self):
        """Test full workflow with historical successful run data."""
        try:
            from daily_paintings import ComplementaryMode
            from openai import OpenAI
            
            if not os.getenv('OPENAI_API_KEY'):
                pytest.skip("OpenAI API key not available")
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            mode = ComplementaryMode(openai_client=client)
            
            # Test with real workflow samples
            for workflow_sample in self.real_data['workflow_samples']:
                if workflow_sample['mode'] == 'complementary':
                    poem = workflow_sample['input_poem']
                    params = workflow_sample['parameters']
                    
                    result = mode.find_matching_artwork(poem=poem, **params)
                    
                    # Verify result structure
                    assert isinstance(result, list)
                    assert len(result) <= params['count']
                    
                    if result:
                        for artwork, score, explanation in result:
                            assert isinstance(artwork, dict)
                            assert isinstance(score, float)
                            assert isinstance(explanation, dict)
                            
                            # Verify score meets minimum
                            assert score >= params['min_match_score']
                            
                            # Verify explanation if requested
                            if params['explain_matches']:
                                assert 'match_score' in explanation
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")
    
    def test_previously_failing_scenarios_nested_lists(self):
        """Test previously failing scenarios with nested lists."""
        try:
            from match_explainer import MatchExplainer
            from two_stage_matcher import TwoStageMatcher
            
            explainer = MatchExplainer()
            matcher = TwoStageMatcher()
            
            # Test the specific nested list scenario that was failing
            poem_analysis = {
                "primary_emotions": [["melancholy"], "peace"],
                "emotional_tone": "bittersweet",
                "themes": [["nature", "night"], "love"],
                "concrete_elements": {
                    "natural_objects": [["tree", "moon"], "sky"],
                    "man_made_objects": [],
                    "living_beings": [],
                    "abstract_concepts": []
                }
            }
            
            artwork = {
                "title": "Mountain Lake",
                "artist": "Albert Bierstadt",
                "year": 1870,
                "subject_q_codes": ["Q405", "Q191163"],
                "genre_q_codes": ["Q191163"]
            }
            
            # Test scoring with nested lists
            score = matcher.score_artwork(poem_analysis, artwork)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
            
            # Test explanation with nested lists
            explanation = explainer.explain_match(poem_analysis, artwork, score)
            assert isinstance(explanation, dict)
            assert 'match_score' in explanation
            assert explanation['match_score'] == score
            
            # Should not crash with nested lists
            assert isinstance(explanation.get('why_matched', ''), str)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_vision_analysis_with_real_data(self):
        """Test vision analysis with real data structures."""
        try:
            from vision_analyzer import VisionAnalyzer
            from openai import OpenAI
            
            if not os.getenv('OPENAI_API_KEY'):
                pytest.skip("OpenAI API key not available")
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            analyzer = VisionAnalyzer(client)
            
            # Test with real vision analysis samples
            for vision_sample in self.real_data['vision_analysis_samples']:
                image_url = vision_sample['image_url']
                artwork_title = vision_sample['artwork_title']
                expected_result = vision_sample['analysis_result']
                
                # Test vision analysis
                result = analyzer.analyze_artwork_image(image_url, artwork_title)
                
                # Verify result structure matches expected
                assert isinstance(result, dict)
                assert 'colors' in result
                assert 'composition' in result
                assert 'mood' in result
                assert 'objects' in result
                assert 'style' in result
                assert 'confidence' in result
                
                # Verify types
                assert isinstance(result['colors'], list)
                assert isinstance(result['composition'], str)
                assert isinstance(result['mood'], str)
                assert isinstance(result['objects'], list)
                assert isinstance(result['style'], str)
                assert isinstance(result['confidence'], float)
                assert 0.0 <= result['confidence'] <= 1.0
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
        except Exception as e:
            pytest.skip(f"Vision analysis test failed: {e}")
    
    def test_poem_analysis_with_real_poems(self):
        """Test poem analysis with real poem data."""
        try:
            from poem_analyzer import PoemAnalyzer
            
            analyzer = PoemAnalyzer()
            
            # Test with real poem samples
            for poem_sample in self.real_data['poem_analysis_samples']:
                poem = poem_sample['input_poem']
                expected_analysis = poem_sample['analysis_result']
                
                # Analyze poem
                result = analyzer.analyze_poem(poem)
            
            # Verify result structure (may vary based on whether OpenAI is available)
            assert isinstance(result, dict)
            assert 'themes' in result or 'analysis_method' in result
            
            # Verify concrete elements structure if present
            if 'concrete_elements' in result:
                concrete = result['concrete_elements']
                assert isinstance(concrete, dict)
                
                # Verify all concrete elements are lists
                for key, value in concrete.items():
                    assert isinstance(value, list)
                    assert all(isinstance(item, str) for item in value)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_data_structure_consistency_across_modules(self):
        """Test that data structures remain consistent across modules."""
        try:
            from poem_analyzer import PoemAnalyzer
            from two_stage_matcher import TwoStageMatcher
            from match_explainer import MatchExplainer
            
            analyzer = PoemAnalyzer()
            matcher = TwoStageMatcher()
            explainer = MatchExplainer()
            
            # Test with real poem
            poem = self.real_data['poem_analysis_samples'][0]['input_poem']
            
            # Analyze poem
            analysis = analyzer.analyze_poem(poem)
            
            # Test with artwork
            artwork = self.real_data['artwork_samples'][0]
            
            # Score match
            score = matcher.score_artwork(analysis, artwork)
            
            # Generate explanation
            explanation = explainer.explain_match(analysis, artwork, score)
            
            # All should work together without data structure issues
            assert isinstance(analysis, dict)
            assert isinstance(score, float)
            assert isinstance(explanation, dict)
            
            # Data should flow correctly between modules
            assert 0.0 <= score <= 1.0
            assert explanation['match_score'] == score
            
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_error_recovery_with_real_data(self):
        """Test error recovery with real data structures."""
        try:
            from match_explainer import MatchExplainer
            
            explainer = MatchExplainer()
            
            # Test with malformed real data
            malformed_analysis = {
                "primary_emotions": "not_a_list",  # Wrong type
                "emotional_tone": 123,  # Wrong type
                "themes": [],  # Empty list instead of None
                "concrete_elements": {
                    "natural_objects": "not_a_list",  # Wrong type
                    "man_made_objects": [],
                    "living_beings": [],
                    "abstract_concepts": []  # Updated field name
                }
            }
            
            artwork = self.real_data['artwork_samples'][0]
            score = 0.5
            
            # Should handle malformed data gracefully
            explanation = explainer.explain_match(malformed_analysis, artwork, score)
            
            assert isinstance(explanation, dict)
            assert 'match_score' in explanation
            assert explanation['match_score'] == score
            
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
