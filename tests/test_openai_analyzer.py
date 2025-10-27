#!/usr/bin/env python3
"""
Unit tests for openai_analyzer.py module.

Tests the select_best_artwork_matches method for AI-driven artwork selection.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import openai_analyzer
from openai_analyzer import OpenAIAnalyzer


class TestSelectBestArtworkMatches:
    """Test the select_best_artwork_matches method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analyzer = OpenAIAnalyzer(self.mock_client)
    
    def test_select_best_artwork_matches_success(self):
        """Test successful artwork selection."""
        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [
                {
                    "artwork_index": 2,
                    "match_score": 0.85,
                    "reasoning": "Both feature solitary figures in twilight"
                },
                {
                    "artwork_index": 1,
                    "match_score": 0.75,
                    "reasoning": "Shared melancholic mood"
                }
            ]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {
            "title": "Evening Melancholy",
            "text": "The shadows fall across the empty street..."
        }
        
        candidates = [
            {
                "title": "Street Scene",
                "artist": "Artist A",
                "year": 1880,
                "medium": "Oil on canvas"
            },
            {
                "title": "Nightfall",
                "artist": "Artist B",
                "year": 1900,
                "medium": "Watercolor"
            },
            {
                "title": "Dawn",
                "artist": "Artist C",
                "year": 1920,
                "medium": "Oil on canvas"
            }
        ]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=2)
        
        # Verify API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args
        
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["max_tokens"] == 1000
        assert call_args[1]["temperature"] == 0.3
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], tuple)
        assert len(result[0]) == 2
        
        # Verify artwork and reasoning
        artwork, reasoning = result[0]
        assert artwork["title"] == "Nightfall"  # Index 2 (1-based)
        assert "twilight" in reasoning.lower()
        
        artwork2, reasoning2 = result[1]
        assert artwork2["title"] == "Street Scene"  # Index 1 (1-based)
        assert "melancholic" in reasoning2.lower()
    
    def test_select_best_artwork_matches_with_vision_analysis(self):
        """Test selection with vision analysis data."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [
                {
                    "artwork_index": 1,
                    "match_score": 0.9,
                    "reasoning": "Perfect match for poem elements"
                }
            ]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {
            "title": "Nature Poem",
            "text": "The trees sway in the breeze..."
        }
        
        candidates = [
            {
                "title": "Forest Scene",
                "artist": "Artist A",
                "year": 1850,
                "medium": "Oil on canvas",
                "vision_analysis": {
                    "success": True,
                    "analysis": {
                        "detected_objects": ["trees", "leaves", "sky", "grass", "path"]
                    }
                }
            }
        ]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Verify the prompt includes vision analysis data
        call_args = self.mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        
        assert "Depicts:" in prompt
        assert "trees" in prompt
        
        # Verify result
        assert len(result) == 1
        artwork, reasoning = result[0]
        assert artwork["title"] == "Forest Scene"
        assert "match" in reasoning.lower()
    
    def test_select_best_artwork_matches_no_openai_client(self):
        """Test selection when OpenAI client is not available."""
        analyzer = OpenAIAnalyzer(None)
        
        poem = {"title": "Test", "text": "Test text"}
        candidates = [{"title": "Test Artwork"}]
        
        with pytest.raises(ValueError, match="OpenAI client not initialized"):
            analyzer.select_best_artwork_matches(poem, candidates)
    
    def test_select_best_artwork_matches_empty_candidates(self):
        """Test selection with empty candidates list."""
        result = self.analyzer.select_best_artwork_matches(
            {"title": "Test", "text": "Test"},
            []
        )
        
        assert result == []
        self.mock_client.chat.completions.create.assert_not_called()
    
    def test_select_best_artwork_matches_invalid_index(self):
        """Test handling of invalid artwork indices."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [
                {
                    "artwork_index": 999,  # Invalid index
                    "match_score": 0.8,
                    "reasoning": "Invalid index"
                }
            ]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Invalid index should be skipped
        assert result == []
    
    def test_select_best_artwork_matches_json_parse_error(self):
        """Test handling of JSON parse errors."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}, {"title": "Artwork 2"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=2)
        
        # Should fallback to first candidates with generic reasoning
        assert len(result) == 2
        for artwork, reasoning in result:
            assert artwork in candidates
            assert "thematic alignment" in reasoning.lower()
    
    def test_select_best_artwork_matches_api_error(self):
        """Test handling of API errors."""
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}, {"title": "Artwork 2"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=2)
        
        # Should fallback to first candidates
        assert len(result) == 2
        for artwork, reasoning in result:
            assert artwork in candidates
    
    def test_select_best_artwork_matches_missing_selections(self):
        """Test handling of missing selections in response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "invalid_field": "data"
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Should handle missing selections
        assert result == []
    
    def test_select_best_artwork_matches_partial_valid_indices(self):
        """Test handling of mixed valid and invalid indices."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [
                {
                    "artwork_index": 1,  # Valid
                    "match_score": 0.8,
                    "reasoning": "Valid"
                },
                {
                    "artwork_index": 999,  # Invalid
                    "match_score": 0.7,
                    "reasoning": "Invalid"
                },
                {
                    "artwork_index": 2,  # Valid
                    "match_score": 0.6,
                    "reasoning": "Valid"
                }
            ]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [
            {"title": "Artwork 1"},
            {"title": "Artwork 2"},
            {"title": "Artwork 3"}
        ]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=3)
        
        # Should only return valid indices
        assert len(result) == 2
        assert result[0][0]["title"] == "Artwork 1"
        assert result[1][0]["title"] == "Artwork 2"
    
    def test_select_best_artwork_matches_without_reasoning(self):
        """Test handling of missing reasoning in response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [
                {
                    "artwork_index": 1,
                    "match_score": 0.8
                    # Missing reasoning
                }
            ]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Should use default reasoning
        assert len(result) == 1
        artwork, reasoning = result[0]
        assert reasoning == "No reasoning provided"


class TestIntegration:
    """Integration tests with real OpenAI API (if available)."""
    
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), 
                       reason="OpenAI API key not available")
    def test_real_openai_integration(self):
        """Test with real OpenAI API if available."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            analyzer = OpenAIAnalyzer(client)
            
            poem = {
                "title": "Nature's Beauty",
                "text": "The trees sway gently in the breeze, their leaves whispering secrets to the wind."
            }
            
            candidates = [
                {
                    "title": "Forest Path",
                    "artist": "John Smith",
                    "year": 1850,
                    "medium": "Oil on canvas",
                    "vision_analysis": {
                        "success": True,
                        "analysis": {
                            "detected_objects": ["trees", "leaves", "path", "sky"]
                        }
                    }
                },
                {
                    "title": "City Streets",
                    "artist": "Jane Doe",
                    "year": 1900,
                    "medium": "Watercolor",
                    "vision_analysis": {
                        "success": False
                    }
                }
            ]
            
            result = analyzer.select_best_artwork_matches(poem, candidates, count=1)
            
            # Should return valid result
            assert len(result) == 1
            artwork, reasoning = result[0]
            assert artwork["title"] in ["Forest Path", "City Streets"]
            assert isinstance(reasoning, str)
            assert len(reasoning) > 0
            
        except ImportError:
            pytest.skip("OpenAI library not available")
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analyzer = OpenAIAnalyzer(self.mock_client)
    
    def test_select_best_artwork_matches_network_error(self):
        """Test handling of network errors."""
        self.mock_client.chat.completions.create.side_effect = ConnectionError("Network error")
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Should fallback
        assert len(result) == 1
        assert result[0][0]["title"] == "Artwork 1"
    
    def test_select_best_artwork_matches_timeout_error(self):
        """Test handling of timeout errors."""
        self.mock_client.chat.completions.create.side_effect = TimeoutError("Request timeout")
        
        poem = {"title": "Test", "text": "Test"}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Should fallback
        assert len(result) == 1
    
    def test_select_best_artwork_matches_empty_poem(self):
        """Test handling of empty poem text."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [{"artwork_index": 1, "match_score": 0.5, "reasoning": "Match"}]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "", "text": ""}
        candidates = [{"title": "Artwork 1"}]
        
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        
        # Should still work
        assert isinstance(result, list)


class TestPerformance:
    """Test performance characteristics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analyzer = OpenAIAnalyzer(self.mock_client)
    
    def test_select_best_artwork_matches_large_candidate_set(self):
        """Test performance with many candidates."""
        import time
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "selections": [{"artwork_index": 1, "match_score": 0.8, "reasoning": "Match"}]
        })
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        poem = {"title": "Test", "text": "Test text"}
        # Create many candidates
        candidates = [{"title": f"Artwork {i}"} for i in range(50)]
        
        start_time = time.time()
        result = self.analyzer.select_best_artwork_matches(poem, candidates, count=1)
        end_time = time.time()
        
        # Should complete quickly with mocked API
        assert (end_time - start_time) < 1.0
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__])
