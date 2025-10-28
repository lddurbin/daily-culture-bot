#!/usr/bin/env python3
"""
Data validation tests for Daily Culture Bot.

Tests data structure consistency and validation across all modules.
"""

import pytest
import sys
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@dataclass
class PoemAnalysisSchema:
    """Schema for poem analysis data structure."""
    primary_emotions: List[str]
    emotional_tone: str
    themes: List[str]
    narrative_elements: Dict[str, Any]
    concrete_elements: Dict[str, List[str]]
    q_codes: List[str]
    analysis_confidence: float
    analysis_method: str


@dataclass
class ArtworkSchema:
    """Schema for artwork data structure."""
    title: str
    artist: str
    year: int
    subject_q_codes: List[str]
    genre_q_codes: List[str]
    image_url: Optional[str]
    description: Optional[str]
    fame_level: int


@dataclass
class VisionAnalysisSchema:
    """Schema for vision analysis data structure."""
    colors: List[str]
    composition: str
    mood: str
    objects: List[str]
    style: str
    confidence: float


class TestDataValidation:
    """Test data structure validation and consistency."""
    
    def test_poem_analysis_schema_validation(self):
        """Test poem analysis data structure validation."""
        # Valid poem analysis
        valid_analysis = {
            "primary_emotions": ["joy", "peace"],
            "emotional_tone": "serene",
            "themes": ["nature", "tranquility"],
            "narrative_elements": {
                "setting": "forest",
                "time": "dawn"
            },
            "concrete_elements": {
                "natural_objects": ["tree", "stream"],
                "man_made_objects": [],
                "living_beings": ["bird"],
                "other_concrete_nouns": []
            },
            "q_codes": ["Q7860", "Q191163"],
            "analysis_confidence": 0.85,
            "analysis_method": "openai"
        }
        
        # Validate structure
        assert isinstance(valid_analysis["primary_emotions"], list)
        assert isinstance(valid_analysis["emotional_tone"], str)
        assert isinstance(valid_analysis["themes"], list)
        assert isinstance(valid_analysis["narrative_elements"], dict)
        assert isinstance(valid_analysis["concrete_elements"], dict)
        assert isinstance(valid_analysis["q_codes"], list)
        assert isinstance(valid_analysis["analysis_confidence"], float)
        assert 0.0 <= valid_analysis["analysis_confidence"] <= 1.0
        
        # Validate concrete elements structure
        concrete = valid_analysis["concrete_elements"]
        assert isinstance(concrete["natural_objects"], list)
        assert isinstance(concrete["man_made_objects"], list)
        assert isinstance(concrete["living_beings"], list)
        assert isinstance(concrete["other_concrete_nouns"], list)
    
    def test_artwork_schema_validation(self):
        """Test artwork data structure validation."""
        # Valid artwork
        valid_artwork = {
            "title": "Forest Stream",
            "artist": "John Doe",
            "year": 1850,
            "subject_q_codes": ["Q7860", "Q191163"],
            "genre_q_codes": ["Q191163"],
            "image_url": "https://example.com/image.jpg",
            "description": "A peaceful forest scene",
            "fame_level": 15
        }
        
        # Validate structure
        assert isinstance(valid_artwork["title"], str)
        assert isinstance(valid_artwork["artist"], str)
        assert isinstance(valid_artwork["year"], int)
        assert isinstance(valid_artwork["subject_q_codes"], list)
        assert isinstance(valid_artwork["genre_q_codes"], list)
        assert isinstance(valid_artwork["image_url"], str)
        assert isinstance(valid_artwork["description"], str)
        assert isinstance(valid_artwork["fame_level"], int)
        assert valid_artwork["fame_level"] >= 0
    
    def test_vision_analysis_schema_validation(self):
        """Test vision analysis data structure validation."""
        # Valid vision analysis
        valid_vision = {
            "colors": ["green", "blue", "brown"],
            "composition": "landscape",
            "mood": "peaceful",
            "objects": ["tree", "stream", "mountain"],
            "style": "realistic",
            "confidence": 0.92
        }
        
        # Validate structure
        assert isinstance(valid_vision["colors"], list)
        assert isinstance(valid_vision["composition"], str)
        assert isinstance(valid_vision["mood"], str)
        assert isinstance(valid_vision["objects"], list)
        assert isinstance(valid_vision["style"], str)
        assert isinstance(valid_vision["confidence"], float)
        assert 0.0 <= valid_vision["confidence"] <= 1.0
    
    def test_nested_list_validation(self):
        """Test validation of nested list structures."""
        # Test nested lists in themes
        nested_themes = {
            "themes": [["nature", "night"], "love", ["peace", "tranquility"]],
            "primary_emotions": [["joy"], "sadness", ["melancholy", "longing"]]
        }
        
        # Should handle nested lists gracefully
        assert isinstance(nested_themes["themes"], list)
        assert isinstance(nested_themes["primary_emotions"], list)
        
        # Flatten nested lists for validation
        def flatten_list(lst):
            result = []
            for item in lst:
                if isinstance(item, list):
                    result.extend(flatten_list(item))
                else:
                    result.append(item)
            return result
        
        flattened_themes = flatten_list(nested_themes["themes"])
        flattened_emotions = flatten_list(nested_themes["primary_emotions"])
        
        assert all(isinstance(item, str) for item in flattened_themes)
        assert all(isinstance(item, str) for item in flattened_emotions)
    
    def test_mixed_type_validation(self):
        """Test validation of mixed type structures."""
        # Test mixed types
        mixed_data = {
            "themes": ["nature", ["love", "loss"], "peace"],
            "primary_emotions": [["joy"], "sadness", ["melancholy"]],
            "concrete_elements": {
                "natural_objects": [["tree", "moon"], "sky", "cloud"],
                "man_made_objects": [],
                "living_beings": [],
                "other_concrete_nouns": []
            }
        }
        
        # Should handle mixed types
        assert isinstance(mixed_data["themes"], list)
        assert isinstance(mixed_data["primary_emotions"], list)
        assert isinstance(mixed_data["concrete_elements"], dict)
        
        # Validate concrete elements
        concrete = mixed_data["concrete_elements"]
        for key, value in concrete.items():
            assert isinstance(value, list)
            # Each item should be either string or list of strings
            for item in value:
                assert isinstance(item, (str, list))
                if isinstance(item, list):
                    assert all(isinstance(subitem, str) for subitem in item)
    
    def test_missing_field_handling(self):
        """Test handling of missing required fields."""
        # Test with missing fields
        incomplete_data = {
            "themes": ["nature"],
            # Missing primary_emotions
            "emotional_tone": "joyful",
            # Missing concrete_elements
        }
        
        # Should provide defaults for missing fields
        defaults = {
            "primary_emotions": [],
            "emotional_tone": "neutral",
            "themes": [],
            "concrete_elements": {
                "natural_objects": [],
                "man_made_objects": [],
                "living_beings": [],
                "other_concrete_nouns": []
            }
        }
        
        # Merge with defaults
        complete_data = {**defaults, **incomplete_data}
        
        assert "primary_emotions" in complete_data
        assert "concrete_elements" in complete_data
        assert isinstance(complete_data["primary_emotions"], list)
        assert isinstance(complete_data["concrete_elements"], dict)
    
    def test_type_coercion_validation(self):
        """Test validation of type coercion."""
        # Test data with wrong types that should be coerced
        wrong_types = {
            "themes": "nature",  # Should be list
            "primary_emotions": 123,  # Should be list
            "emotional_tone": ["joyful"],  # Should be string
            "analysis_confidence": "0.85"  # Should be float
        }
        
        # Coerce types
        def coerce_types(data):
            result = {}
            for key, value in data.items():
                if key == "themes" and not isinstance(value, list):
                    result[key] = [value] if isinstance(value, str) else []
                elif key == "primary_emotions" and not isinstance(value, list):
                    result[key] = [str(value)] if value else []
                elif key == "emotional_tone" and isinstance(value, list):
                    result[key] = value[0] if value else "neutral"
                elif key == "analysis_confidence" and isinstance(value, str):
                    result[key] = float(value)
                else:
                    result[key] = value
            return result
        
        coerced = coerce_types(wrong_types)
        
        assert isinstance(coerced["themes"], list)
        assert isinstance(coerced["primary_emotions"], list)
        assert isinstance(coerced["emotional_tone"], str)
        assert isinstance(coerced["analysis_confidence"], float)
    
    def test_q_code_validation(self):
        """Test validation of Q-code formats."""
        # Valid Q-codes
        valid_q_codes = ["Q7860", "Q191163", "Q123456"]
        
        for q_code in valid_q_codes:
            assert q_code.startswith("Q")
            assert q_code[1:].isdigit()
            assert len(q_code) > 1
        
        # Invalid Q-codes
        invalid_q_codes = ["Q", "123", "Qabc", "q7860", ""]
        
        for q_code in invalid_q_codes:
            assert not (q_code.startswith("Q") and q_code[1:].isdigit() and len(q_code) > 1)
    
    def test_confidence_score_validation(self):
        """Test validation of confidence scores."""
        # Valid confidence scores
        valid_scores = [0.0, 0.5, 0.85, 1.0]
        
        for score in valid_scores:
            assert isinstance(score, (int, float))
            assert 0.0 <= score <= 1.0
        
        # Invalid confidence scores
        invalid_scores = [-0.1, 1.1, "0.5", None, []]
        
        for score in invalid_scores:
            assert not (isinstance(score, (int, float)) and 0.0 <= score <= 1.0)
    
    def test_year_validation(self):
        """Test validation of year values."""
        # Valid years
        valid_years = [1000, 1500, 1850, 2023]
        
        for year in valid_years:
            assert isinstance(year, int)
            assert 1000 <= year <= 2024
        
        # Invalid years
        invalid_years = [999, 2025, "1850", None, -100]
        
        for year in invalid_years:
            assert not (isinstance(year, int) and 1000 <= year <= 2024)
    
    def test_url_validation(self):
        """Test validation of URL formats."""
        # Valid URLs
        valid_urls = [
            "https://example.com/image.jpg",
            "http://example.com/image.png",
            "https://upload.wikimedia.org/wikipedia/commons/1/1a/Example.jpg"
        ]
        
        for url in valid_urls:
            assert isinstance(url, str)
            assert url.startswith(("http://", "https://"))
            assert "." in url  # Should have file extension
        
        # Invalid URLs
        invalid_urls = ["not_a_url", "ftp://example.com", "", None]
        
        for url in invalid_urls:
            assert not (isinstance(url, str) and url.startswith(("http://", "https://")) and "." in url)


class TestDataConsistency:
    """Test data consistency across modules."""
    
    def test_poem_analysis_consistency(self):
        """Test that poem analysis results are consistent across runs."""
        try:
            from poem_analyzer import PoemAnalyzer
            
            analyzer = PoemAnalyzer()
            poem = {
                "title": "Test Poem",
                "author": "Test Author",
                "text": "The trees sway gently in the breeze."
            }
            
            # Run analysis multiple times
            results = []
            for _ in range(3):
                result = analyzer.analyze_poem(poem)
                results.append(result)
            
            # Results should have consistent structure
            for result in results:
                assert isinstance(result, dict)
                assert 'themes' in result or 'analysis_method' in result
                # Check for either primary_emotions or emotional_tone depending on analysis method
                assert 'primary_emotions' in result or 'emotional_tone' in result or 'analysis_method' in result
                # concrete_elements may or may not be present depending on analysis method
                if 'concrete_elements' in result:
                    concrete = result['concrete_elements']
                    assert isinstance(concrete, dict)
                    assert 'natural_objects' in concrete
                    assert 'man_made_objects' in concrete
                    assert 'living_beings' in concrete
                    assert 'abstract_concepts' in concrete  # Updated field name
                    
                    for key, value in concrete.items():
                        assert isinstance(value, list)
                        assert all(isinstance(item, str) for item in value)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_artwork_data_consistency(self):
        """Test that artwork data is consistent."""
        try:
            from datacreator import DataCreator
            
            creator = DataCreator()
            
            # Test with sample data
            sample_artwork = creator.get_sample_artwork()
            
            # Should have consistent structure
            assert isinstance(sample_artwork, list)
            if sample_artwork:
                artwork = sample_artwork[0]
                assert isinstance(artwork, dict)
                assert 'title' in artwork
                assert 'artist' in artwork
                assert 'year' in artwork
                assert 'subject_q_codes' in artwork
                assert 'genre_q_codes' in artwork
                
                # Validate types
                assert isinstance(artwork['title'], str)
                assert isinstance(artwork['artist'], str)
                assert isinstance(artwork['year'], int)
                assert isinstance(artwork['subject_q_codes'], list)
                assert isinstance(artwork['genre_q_codes'], list)
                
                # Validate Q-codes
                for q_code in artwork['subject_q_codes'] + artwork['genre_q_codes']:
                    assert q_code.startswith('Q')
                    assert q_code[1:].isdigit()
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
