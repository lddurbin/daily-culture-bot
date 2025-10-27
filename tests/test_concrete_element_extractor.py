#!/usr/bin/env python3
"""
Unit tests for concrete_element_extractor.py module.

Tests the spaCy-based concrete noun extraction functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import concrete_element_extractor
from concrete_element_extractor import ConcreteElementExtractor


class TestConcreteElementExtractorInit:
    """Test ConcreteElementExtractor initialization."""
    
    @patch('concrete_element_extractor.spacy.load')
    def test_initialization_success(self, mock_spacy_load):
        """Test successful initialization with spaCy model."""
        mock_nlp = Mock()
        mock_spacy_load.return_value = mock_nlp
        
        extractor = ConcreteElementExtractor()
        
        assert extractor.nlp == mock_nlp
        mock_spacy_load.assert_called_once_with("en_core_web_sm")
    
    @patch('concrete_element_extractor.spacy.load')
    def test_initialization_failure(self, mock_spacy_load):
        """Test initialization when spaCy model is not available."""
        mock_spacy_load.side_effect = OSError("Model not found")
        
        extractor = ConcreteElementExtractor()
        
        assert extractor.nlp is None


class TestExtractConcreteNouns:
    """Test concrete noun extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = ConcreteElementExtractor()
        self.mock_nlp = Mock()
        self.extractor.nlp = self.mock_nlp
    
    def test_extract_concrete_nouns_with_nlp_available(self):
        """Test noun extraction when spaCy model is available."""
        # Mock spaCy document and tokens
        mock_doc = Mock()
        mock_token1 = Mock()
        mock_token1.pos_ = "NOUN"
        mock_token1.lemma_ = "tree"
        mock_token1.ent_type_ = ""
        mock_token1.is_stop = False
        
        mock_token2 = Mock()
        mock_token2.pos_ = "NOUN"
        mock_token2.lemma_ = "house"
        mock_token2.ent_type_ = ""
        mock_token2.is_stop = False
        
        mock_token3 = Mock()
        mock_token3.pos_ = "NOUN"
        mock_token3.lemma_ = "person"
        mock_token3.ent_type_ = "PERSON"
        mock_token3.is_stop = False
        
        mock_token4 = Mock()
        mock_token4.pos_ = "VERB"
        mock_token4.lemma_ = "run"
        mock_token4.ent_type_ = ""
        mock_token4.is_stop = False
        
        # Mock the document to be iterable
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2, mock_token3, mock_token4]))
        self.mock_nlp.return_value = mock_doc
        
        text = "The tree near the house belongs to a person who runs."
        result = self.extractor.extract_concrete_nouns(text)
        
        # Verify result structure
        assert "natural_objects" in result
        assert "man_made_objects" in result
        assert "living_beings" in result
        assert "abstract_concepts" in result
        assert "settings" in result
        assert "all_nouns" in result
        
        # Check that nouns were categorized correctly
        assert "tree" in result["natural_objects"]
        assert "house" in result["man_made_objects"]
        assert "person" in result["living_beings"]
        assert "run" not in result["natural_objects"]  # VERB should be ignored
    
    def test_extract_concrete_nouns_without_nlp(self):
        """Test noun extraction when spaCy model is not available."""
        self.extractor.nlp = None
        
        text = "The tree near the house."
        result = self.extractor.extract_concrete_nouns(text)
        
        # Should return empty structure
        expected = {
            "natural_objects": [],
            "man_made_objects": [],
            "living_beings": [],
            "abstract_concepts": [],
            "settings": [],
            "all_nouns": []
        }
        assert result == expected
    
    def test_extract_concrete_nouns_empty_text(self):
        """Test noun extraction with empty text."""
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([]))
        self.mock_nlp.return_value = mock_doc
        
        result = self.extractor.extract_concrete_nouns("")
        
        expected = {
            "natural_objects": [],
            "man_made_objects": [],
            "living_beings": [],
            "abstract_concepts": [],
            "settings": [],
            "all_nouns": []
        }
        assert result == expected
    
    def test_extract_concrete_nouns_removes_duplicates(self):
        """Test that duplicate elements are removed."""
        mock_doc = Mock()
        mock_token1 = Mock()
        mock_token1.pos_ = "NOUN"
        mock_token1.lemma_ = "tree"
        mock_token1.ent_type_ = ""
        mock_token1.is_stop = False
        
        mock_token2 = Mock()
        mock_token2.pos_ = "NOUN"
        mock_token2.lemma_ = "tree"
        mock_token2.ent_type_ = ""
        mock_token2.is_stop = False
        
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2]))
        self.mock_nlp.return_value = mock_doc
        
        text = "The tree and another tree."
        result = self.extractor.extract_concrete_nouns(text)
        
        assert result["natural_objects"] == ["tree"]  # Should be deduplicated
    
    def test_extract_concrete_nouns_case_insensitive(self):
        """Test that noun extraction is case insensitive."""
        mock_doc = Mock()
        mock_token = Mock()
        mock_token.pos_ = "NOUN"
        mock_token.lemma_ = "Tree"  # Capitalized
        mock_token.ent_type_ = ""
        mock_token.is_stop = False
        
        mock_doc.__iter__ = Mock(return_value=iter([mock_token]))
        self.mock_nlp.return_value = mock_doc
        
        text = "The Tree."
        result = self.extractor.extract_concrete_nouns(text)
        
        assert "tree" in result["natural_objects"]  # Should be lowercase


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_extract_concrete_nouns_with_nlp_error(self):
        """Test handling of errors during spaCy processing."""
        extractor = ConcreteElementExtractor()
        mock_nlp = Mock()
        extractor.nlp = mock_nlp
        
        # Mock spaCy to raise an exception
        mock_nlp.side_effect = Exception("spaCy processing error")
        
        text = "Some text"
        
        # Should handle the error gracefully
        with pytest.raises(Exception):
            extractor.extract_concrete_nouns(text)
    
    def test_extract_concrete_nouns_with_invalid_input(self):
        """Test handling of invalid input types."""
        extractor = ConcreteElementExtractor()
        
        # Test with None input
        result = extractor.extract_concrete_nouns(None)
        expected_empty = {
            "natural_objects": [],
            "man_made_objects": [],
            "living_beings": [],
            "abstract_concepts": [],
            "settings": [],
            "all_nouns": []
        }
        assert result == expected_empty
        
        # Test with non-string input
        with pytest.raises(ValueError):
            extractor.extract_concrete_nouns(123)


class TestPerformance:
    """Test performance characteristics."""
    
    def test_extract_concrete_nouns_performance(self):
        """Test that extraction completes in reasonable time."""
        import time
        
        extractor = ConcreteElementExtractor()
        mock_nlp = Mock()
        extractor.nlp = mock_nlp
        
        # Mock a simple document
        mock_doc = Mock()
        mock_token = Mock()
        mock_token.pos_ = "NOUN"
        mock_token.lemma_ = "test"
        mock_token.ent_type_ = ""
        mock_token.is_stop = False
        mock_doc.__iter__ = Mock(return_value=iter([mock_token]))
        mock_nlp.return_value = mock_doc
        
        text = " ".join(["test"] * 1000)  # Long text
        
        start_time = time.time()
        result = extractor.extract_concrete_nouns(text)
        end_time = time.time()
        
        # Should complete in less than 1 second
        assert (end_time - start_time) < 1.0
        assert isinstance(result, dict)


class TestIntegration:
    """Integration tests with real spaCy model (if available)."""
    
    @pytest.mark.skipif(not hasattr(concrete_element_extractor, 'spacy'), 
                       reason="spaCy not available")
    def test_real_spacy_integration(self):
        """Test with real spaCy model if available."""
        try:
            extractor = ConcreteElementExtractor()
            if extractor.nlp is None:
                pytest.skip("spaCy model not available")
            
            text = """
            I wandered lonely as a cloud
            That floats on high o'er vales and hills,
            When all at once I saw a crowd,
            A host, of golden daffodils;
            Beside the lake, beneath the trees,
            Fluttering and dancing in the breeze.
            """
            
            result = extractor.extract_concrete_nouns(text)
            
            # Should extract concrete elements
            assert isinstance(result, dict)
            assert "natural_objects" in result
            assert "man_made_objects" in result
            assert "living_beings" in result
            assert "abstract_concepts" in result
            assert "settings" in result
            assert "all_nouns" in result
            
            # Should find some elements in this nature poem
            assert len(result["natural_objects"]) > 0
            assert "cloud" in result["natural_objects"] or "tree" in result["natural_objects"]
            
        except OSError:
            pytest.skip("spaCy model 'en_core_web_sm' not installed")


if __name__ == "__main__":
    pytest.main([__file__])