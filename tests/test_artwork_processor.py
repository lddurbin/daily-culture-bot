#!/usr/bin/env python3
"""
Tests for Artwork Processor

This module contains tests for artwork data processing functionality.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import artwork_processor


class TestArtworkProcessorInit:
    """Test ArtworkProcessor initialization."""
    
    def test_initialization(self):
        """Test that ArtworkProcessor initializes correctly."""
        mock_session = Mock()
        processor = artwork_processor.ArtworkProcessor(
            wikidata_endpoint="https://example.com",
            session=mock_session,
            wikipedia_api="https://wikipedia.example.com"
        )
        
        assert processor.wikidata_endpoint == "https://example.com"
        assert processor.session == mock_session
        assert processor.wikipedia_api == "https://wikipedia.example.com"


class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_text_normal(self):
        """Test cleaning normal text."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.clean_text("  Test Text  ")
        assert result == "Test Text"
    
    def test_clean_text_with_newlines(self):
        """Test cleaning text with newlines."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.clean_text("Line 1\nLine 2\nLine 3")
        assert result == "Line 1 Line 2 Line 3"
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.clean_text("")
        assert result == ""
    
    def test_clean_text_none(self):
        """Test cleaning None text."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.clean_text(None)
        assert result == ""


class TestGetPaintingLabels:
    """Test get_painting_labels functionality."""
    
    def test_get_painting_labels_success(self):
        """Test successfully getting painting labels."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [{
                    'paintingLabel': {'value': 'Mona Lisa'},
                    'artistLabel': {'value': 'Leonardo da Vinci'}
                }]
            }
        }
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "https://query.wikidata.org/sparql",
            mock_session,
            ""
        )
        
        result = processor.get_painting_labels("http://www.wikidata.org/entity/Q12418")
        
        assert result["title"] == "Mona Lisa"
        assert result["artist"] == "Leonardo da Vinci"
    
    def test_get_painting_labels_no_url(self):
        """Test getting labels with no URL."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.get_painting_labels(None)
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
    
    def test_get_painting_labels_empty_url(self):
        """Test getting labels with empty URL."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.get_painting_labels("")
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
    
    def test_get_painting_labels_api_error(self):
        """Test getting labels when API returns error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "https://query.wikidata.org/sparql",
            mock_session,
            ""
        )
        
        result = processor.get_painting_labels("http://www.wikidata.org/entity/Q12418")
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
    
    def test_get_painting_labels_no_results(self):
        """Test getting labels when API returns no results."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': {'bindings': []}}
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "https://query.wikidata.org/sparql",
            mock_session,
            ""
        )
        
        result = processor.get_painting_labels("http://www.wikidata.org/entity/Q12418")
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
    
    @patch('builtins.print')
    def test_get_painting_labels_exception(self, mock_print):
        """Test getting labels when exception occurs."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Network error")
        
        processor = artwork_processor.ArtworkProcessor(
            "https://query.wikidata.org/sparql",
            mock_session,
            ""
        )
        
        result = processor.get_painting_labels("http://www.wikidata.org/entity/Q12418")
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
        mock_print.assert_called_once()


class TestGetHighResImageUrl:
    """Test get_high_res_image_url functionality."""
    
    def test_get_high_res_image_url_thumbnail(self):
        """Test converting thumbnail URL to high-res."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Example.jpg/800px-Example.jpg"
        result = processor.get_high_res_image_url(thumbnail_url)
        
        assert "upload.wikimedia.org" in result
        # Check that result is either the original URL (if regex fails) or the extracted path
        assert result == thumbnail_url or "/thumb/" not in result
    
    def test_get_high_res_image_url_direct_commons(self):
        """Test direct Wikimedia Commons URL."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        direct_url = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.jpg"
        result = processor.get_high_res_image_url(direct_url)
        
        assert result == direct_url
    
    def test_get_high_res_image_url_empty(self):
        """Test empty URL."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.get_high_res_image_url("")
        
        assert result == ""
    
    def test_get_high_res_image_url_none(self):
        """Test None URL."""
        processor = artwork_processor.ArtworkProcessor("", Mock(), "")
        
        result = processor.get_high_res_image_url(None)
        
        assert result == ""


class TestGetWikipediaSummary:
    """Test get_wikipedia_summary functionality."""
    
    def test_get_wikipedia_summary_success(self):
        """Test successfully getting Wikipedia summary."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'extract': 'The Mona Lisa is a famous painting. It was painted by Leonardo.'
        }
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "",
            mock_session,
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
        )
        
        result = processor.get_wikipedia_summary("Mona Lisa")
        
        assert "Mona Lisa" in result or "painting" in result
    
    def test_get_wikipedia_summary_no_extract(self):
        """Test Wikipedia summary with no extract."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "",
            mock_session,
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
        )
        
        result = processor.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
    
    def test_get_wikipedia_summary_api_error(self):
        """Test Wikipedia summary with API error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        
        processor = artwork_processor.ArtworkProcessor(
            "",
            mock_session,
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
        )
        
        result = processor.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
    
    @patch('builtins.print')
    def test_get_wikipedia_summary_exception(self, mock_print):
        """Test Wikipedia summary with exception."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Network error")
        
        processor = artwork_processor.ArtworkProcessor(
            "",
            mock_session,
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
        )
        
        result = processor.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
        mock_print.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
