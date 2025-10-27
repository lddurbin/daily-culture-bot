#!/usr/bin/env python3
"""
Unit tests for vision_analyzer.py module.

Tests the GPT-4 Vision integration for artwork image analysis.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import vision_analyzer
from vision_analyzer import VisionAnalyzer


class TestVisionAnalyzerInit:
    """Test VisionAnalyzer initialization."""
    
    def test_initialization_with_openai_client(self):
        """Test successful initialization with OpenAI client."""
        mock_client = Mock()
        
        analyzer = VisionAnalyzer(mock_client)
        
        assert analyzer.openai_client == mock_client
    
    def test_initialization_without_openai_client(self):
        """Test initialization without OpenAI client."""
        with patch.dict(os.environ, {}, clear=True):
            analyzer = VisionAnalyzer(None)
            
            assert analyzer.openai_client is None
    
    def test_initialization_with_openai_import_error(self):
        """Test initialization when OpenAI is not available."""
        with patch('vision_analyzer.OpenAI', None):
            analyzer = VisionAnalyzer(None)
            
            assert analyzer.openai_client is None


class TestAnalyzeArtworkImage:
    """Test GPT-4 Vision artwork image analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analyzer = VisionAnalyzer(self.mock_client)
    
    def test_analyze_artwork_image_success(self):
        """Test successful artwork image analysis."""
        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"detected_objects": ["figure", "trees", "river"], "dominant_colors": ["brown", "orange", "grey"], "color_palette": "muted", "setting": "outdoor", "time_of_day": "dusk", "season_indicators": "autumn", "human_presence": "central", "composition": "intimate", "spatial_qualities": "open", "movement_energy": "flowing", "mood": "melancholic", "style_characteristics": "realistic"}'
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        image_url = "https://example.com/image.jpg"
        artwork_title = "Test Artwork"
        result = self.analyzer.analyze_artwork_image(image_url, artwork_title)
        
        # Verify API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args
        
        assert call_args[1]["model"] == "gpt-4o"
        assert call_args[1]["max_tokens"] == 1000
        assert call_args[1]["temperature"] == 0.3
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "analysis" in result
        assert result["success"] == True
        
        analysis = result["analysis"]
        assert "detected_objects" in analysis
        assert "dominant_colors" in analysis
        assert "color_palette" in analysis
        assert "setting" in analysis
        assert "time_of_day" in analysis
        assert "season_indicators" in analysis
        assert "human_presence" in analysis
        assert "composition" in analysis
        assert "spatial_qualities" in analysis
        assert "movement_energy" in analysis
        assert "mood" in analysis
        assert "style_characteristics" in analysis
        
        # Verify specific values
        assert analysis["detected_objects"] == ["figure", "trees", "river"]
        assert analysis["dominant_colors"] == ["brown", "orange", "grey"]
        assert analysis["color_palette"] == "muted"
        assert analysis["setting"] == "outdoor"
        assert analysis["time_of_day"] == "dusk"
        assert analysis["season_indicators"] == "autumn"
        assert analysis["human_presence"] == "central"
        assert analysis["composition"] == "intimate"
        assert analysis["spatial_qualities"] == "open"
        assert analysis["movement_energy"] == "flowing"
        assert analysis["mood"] == "melancholic"
        assert analysis["style_characteristics"] == "realistic"
    
    def test_analyze_artwork_image_no_openai_client(self):
        """Test analysis when OpenAI client is not available."""
        analyzer = VisionAnalyzer(None)
        
        result = analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        
        # Should return error response
        assert result["success"] == False
        assert "error" in result
        assert result["artwork_title"] == "Test Artwork"
    
    def test_analyze_artwork_image_empty_url(self):
        """Test analysis with empty image URL."""
        result = self.analyzer.analyze_artwork_image("", "Test Artwork")
        
        # Should return error response
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_none_url(self):
        """Test analysis with None image URL."""
        result = self.analyzer.analyze_artwork_image(None, "Test Artwork")
        
        # Should return error response
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_json_error(self):
        """Test analysis when API returns invalid JSON."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        
        # Should return error response
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_api_error(self):
        """Test analysis when OpenAI API raises an exception."""
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = self.analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        
        # Should return error response
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_caching(self):
        """Test that analysis results are cached."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"detected_objects": ["test"], "dominant_colors": ["red"], "color_palette": "warm", "setting": "outdoor", "time_of_day": "day", "season_indicators": "summer", "human_presence": "absent", "composition": "expansive", "spatial_qualities": "open", "movement_energy": "static", "mood": "joyful", "style_characteristics": "realistic"}'
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        image_url = "https://example.com/image.jpg"
        artwork_title = "Test Artwork"
        
        # First call
        result1 = self.analyzer.analyze_artwork_image(image_url, artwork_title)
        
        # Second call with same URL and title
        result2 = self.analyzer.analyze_artwork_image(image_url, artwork_title)
        
        # Should only call API once due to caching
        assert self.mock_client.chat.completions.create.call_count == 1
        assert result1 == result2
    
    def test_analyze_artwork_image_different_titles(self):
        """Test that different artwork titles are not cached together."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"detected_objects": ["test"], "dominant_colors": ["red"], "color_palette": "warm", "setting": "outdoor", "time_of_day": "day", "season_indicators": "summer", "human_presence": "absent", "composition": "expansive", "spatial_qualities": "open", "movement_energy": "static", "mood": "joyful", "style_characteristics": "realistic"}'
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call with different artwork titles
        self.analyzer.analyze_artwork_image("https://example.com/image.jpg", "Artwork 1")
        self.analyzer.analyze_artwork_image("https://example.com/image.jpg", "Artwork 2")
        
        # Should call API twice
        assert self.mock_client.chat.completions.create.call_count == 2


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_analyze_artwork_image_network_error(self):
        """Test handling of network errors."""
        analyzer = VisionAnalyzer(Mock())
        analyzer.openai_client.chat.completions.create.side_effect = ConnectionError("Network error")
        
        result = analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_timeout_error(self):
        """Test handling of timeout errors."""
        analyzer = VisionAnalyzer(Mock())
        analyzer.openai_client.chat.completions.create.side_effect = TimeoutError("Request timeout")
        
        result = analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        
        assert result["success"] == False
        assert "error" in result
    
    def test_analyze_artwork_image_invalid_url(self):
        """Test handling of invalid URLs."""
        analyzer = VisionAnalyzer(Mock())
        
        # Test with various invalid URL formats
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com/image.jpg",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for url in invalid_urls:
            result = analyzer.analyze_artwork_image(url, "Test Artwork")
            # Should still attempt analysis (OpenAI will handle invalid URLs)
            assert isinstance(result, dict)


class TestPerformance:
    """Test performance characteristics."""
    
    def test_analyze_artwork_image_performance(self):
        """Test that analysis completes in reasonable time."""
        import time
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"detected_objects": ["test"], "dominant_colors": ["red"], "color_palette": "warm", "setting": "outdoor", "time_of_day": "day", "season_indicators": "summer", "human_presence": "absent", "composition": "expansive", "spatial_qualities": "open", "movement_energy": "static", "mood": "joyful", "style_characteristics": "realistic"}'
        
        analyzer = VisionAnalyzer(Mock())
        analyzer.openai_client.chat.completions.create.return_value = mock_response
        
        start_time = time.time()
        result = analyzer.analyze_artwork_image("https://example.com/image.jpg", "Test Artwork")
        end_time = time.time()
        
        # Should complete quickly with mocked API
        assert (end_time - start_time) < 1.0
        assert isinstance(result, dict)


class TestIntegration:
    """Integration tests with real OpenAI API (if available)."""
    
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), 
                       reason="OpenAI API key not available")
    def test_real_openai_integration(self):
        """Test with real OpenAI API if available."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            analyzer = VisionAnalyzer(client)
            
            # Use a public domain artwork image
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"
            
            result = analyzer.analyze_artwork_image(image_url, "Starry Night")
            
            # Should return valid analysis
            assert isinstance(result, dict)
            assert "detected_objects" in result
            assert "setting" in result
            assert "mood" in result
            
            # Should detect some elements in Starry Night
            assert len(result["detected_objects"]) > 0
            assert result["setting"] in ["outdoor", "celestial", "abstract"]
            
        except ImportError:
            pytest.skip("OpenAI library not available")
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")


class TestExtractQCodesFromVisionAnalysis:
    """Test Q-code extraction from vision analysis results."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = VisionAnalyzer(None)
    
    def test_extract_q_codes_successful_analysis(self):
        """Test Q-code extraction from successful analysis."""
        analysis = {
            "success": True,
            "analysis": {
                "detected_objects": ["tree", "flower", "ocean", "mountain", "house", "ship", "bird", "horse", "dog", "cat"],
                "setting": "seascape",
                "time_of_day": "night"
            }
        }
        
        q_codes = self.analyzer.extract_q_codes_from_vision_analysis(analysis)
        
        # Should extract Q-codes for detected objects
        assert "Q10884" in q_codes  # tree
        assert "Q11427" in q_codes  # rose/flower
        assert "Q9430" in q_codes   # ocean
        assert "Q8502" in q_codes   # mountain
        assert "Q3947" in q_codes   # house
        assert "Q11446" in q_codes  # ship
        assert "Q5113" in q_codes   # bird
        assert "Q726" in q_codes    # horse
        assert "Q144" in q_codes    # dog
        assert "Q146" in q_codes    # cat
        
        # Should extract Q-codes for setting
        assert "Q16970" in q_codes  # seascape
        
        # Should extract Q-codes for time of day
        assert "Q183" in q_codes    # night
        
        # Should not have duplicates
        assert len(q_codes) == len(set(q_codes))
    
    def test_extract_q_codes_failed_analysis(self):
        """Test Q-code extraction from failed analysis."""
        analysis = {
            "success": False,
            "error": "API Error"
        }
        
        q_codes = self.analyzer.extract_q_codes_from_vision_analysis(analysis)
        
        assert q_codes == []
    
    def test_extract_q_codes_no_analysis_data(self):
        """Test Q-code extraction when analysis data is missing."""
        analysis = {
            "success": True
        }
        
        q_codes = self.analyzer.extract_q_codes_from_vision_analysis(analysis)
        
        assert q_codes == []
    
    def test_extract_q_codes_empty_objects(self):
        """Test Q-code extraction with empty detected objects."""
        analysis = {
            "success": True,
            "analysis": {
                "detected_objects": [],
                "setting": "landscape",
                "time_of_day": "day"
            }
        }
        
        q_codes = self.analyzer.extract_q_codes_from_vision_analysis(analysis)
        
        # Should still extract Q-codes for setting and time
        assert "Q191163" in q_codes  # landscape
        assert "Q111" in q_codes      # day
        assert len(q_codes) == 2
    
    def test_extract_q_codes_unknown_objects(self):
        """Test Q-code extraction with unknown objects."""
        analysis = {
            "success": True,
            "analysis": {
                "detected_objects": ["unknown_object", "another_unknown"],
                "setting": "abstract",
                "time_of_day": "ambiguous"
            }
        }
        
        q_codes = self.analyzer.extract_q_codes_from_vision_analysis(analysis)
        
        # Should return empty list for unknown objects/settings
        assert q_codes == []


class TestCacheManagement:
    """Test cache management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analyzer = VisionAnalyzer(self.mock_client)
    
    def test_get_cache_stats_empty_cache(self):
        """Test cache stats with empty cache."""
        stats = self.analyzer.get_cache_stats()
        
        assert stats["total_entries"] == 0
        assert stats["successful_analyses"] == 0
        assert stats["failed_analyses"] == 0
        assert stats["total_tokens_used"] == 0
        assert stats["cache_hit_rate"] == "N/A"
    
    def test_get_cache_stats_with_entries(self):
        """Test cache stats with cached entries."""
        # Add some mock cache entries
        self.analyzer.analysis_cache = {
            "url1_title1": {
                "success": True,
                "tokens": {"total_tokens": 100}
            },
            "url2_title2": {
                "success": True,
                "tokens": {"total_tokens": 150}
            },
            "url3_title3": {
                "success": False,
                "error": "API Error"
            }
        }
        
        stats = self.analyzer.get_cache_stats()
        
        assert stats["total_entries"] == 3
        assert stats["successful_analyses"] == 2
        assert stats["failed_analyses"] == 1
        assert stats["total_tokens_used"] == 250
        assert stats["cache_hit_rate"] == "N/A"
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add some mock cache entries
        self.analyzer.analysis_cache = {
            "url1_title1": {"success": True},
            "url2_title2": {"success": False}
        }
        
        assert len(self.analyzer.analysis_cache) == 2
        
        self.analyzer.clear_cache()
        
        assert len(self.analyzer.analysis_cache) == 0
    
    def test_is_enabled_with_client(self):
        """Test is_enabled when OpenAI client is available."""
        analyzer = VisionAnalyzer(Mock())
        
        assert analyzer.is_enabled() == True
    
    def test_is_enabled_without_client(self):
        """Test is_enabled when OpenAI client is not available."""
        with patch.dict(os.environ, {}, clear=True):
            analyzer = VisionAnalyzer(None)
            
            assert analyzer.is_enabled() == False


if __name__ == "__main__":
    pytest.main([__file__])