#!/usr/bin/env python3
"""
Tests for PoemFetcher class
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.poem_fetcher import PoemFetcher


class TestPoemFetcher:
    """Test cases for PoemFetcher class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.fetcher = PoemFetcher()
    
    def test_count_words_empty_poem(self):
        """Test word counting with empty poem"""
        poem = {}
        assert self.fetcher.count_words(poem) == 0
        
        poem = {"text": ""}
        assert self.fetcher.count_words(poem) == 0
        
        poem = {"text": None}
        assert self.fetcher.count_words(poem) == 0
    
    def test_count_words_simple_poem(self):
        """Test word counting with simple poem"""
        poem = {"text": "Hello world"}
        assert self.fetcher.count_words(poem) == 2
        
        poem = {"text": "The quick brown fox jumps over the lazy dog"}
        assert self.fetcher.count_words(poem) == 9
    
    def test_count_words_multiline_poem(self):
        """Test word counting with multiline poem"""
        poem = {
            "text": "Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood"
        }
        assert self.fetcher.count_words(poem) == 21
    
    def test_count_words_with_extra_whitespace(self):
        """Test word counting with extra whitespace"""
        poem = {"text": "  Hello    world  \n\n  "}
        assert self.fetcher.count_words(poem) == 2
        
        poem = {"text": "\t\n  The   quick   brown   fox  \n\n  "}
        assert self.fetcher.count_words(poem) == 4
    
    def test_filter_poems_by_word_count_empty_list(self):
        """Test filtering with empty poem list"""
        poems = []
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=200)
        assert filtered == []
    
    def test_filter_poems_by_word_count_all_pass(self):
        """Test filtering when all poems pass the word count limit"""
        poems = [
            {"title": "Short Poem", "text": "Hello world"},
            {"title": "Another Short", "text": "The quick brown fox"}
        ]
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=200)
        
        assert len(filtered) == 2
        assert all("word_count" in poem for poem in filtered)
        assert filtered[0]["word_count"] == 2
        assert filtered[1]["word_count"] == 4
    
    def test_filter_poems_by_word_count_some_filtered(self):
        """Test filtering when some poems exceed word count limit"""
        poems = [
            {"title": "Short Poem", "text": "Hello world"},
            {"title": "Long Poem", "text": " ".join(["word"] * 250)},  # 250 words
            {"title": "Medium Poem", "text": " ".join(["word"] * 100)}  # 100 words
        ]
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=200)
        
        assert len(filtered) == 2
        assert filtered[0]["title"] == "Short Poem"
        assert filtered[1]["title"] == "Medium Poem"
        assert all(poem["word_count"] <= 200 for poem in filtered)
    
    def test_filter_poems_by_word_count_all_filtered(self):
        """Test filtering when all poems exceed word count limit"""
        poems = [
            {"title": "Long Poem 1", "text": " ".join(["word"] * 250)},
            {"title": "Long Poem 2", "text": " ".join(["word"] * 300)}
        ]
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=200)
        
        assert len(filtered) == 0
    
    def test_filter_poems_by_word_count_custom_limit(self):
        """Test filtering with custom word count limit"""
        poems = [
            {"title": "Short", "text": "Hello world"},
            {"title": "Medium", "text": " ".join(["word"] * 50)},
            {"title": "Long", "text": " ".join(["word"] * 150)}
        ]
        
        # Test with 100 word limit
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=100)
        assert len(filtered) == 2
        
        # Test with 25 word limit
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=25)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Short"
    
    def test_filter_poems_preserves_original_data(self):
        """Test that filtering preserves original poem data"""
        poems = [
            {
                "title": "Test Poem",
                "author": "Test Author",
                "text": "Hello world",
                "line_count": 1,
                "date": "2024-01-01",
                "source": "Test"
            }
        ]
        filtered = self.fetcher.filter_poems_by_word_count(poems, max_words=200)
        
        assert len(filtered) == 1
        poem = filtered[0]
        assert poem["title"] == "Test Poem"
        assert poem["author"] == "Test Author"
        assert poem["line_count"] == 1
        assert poem["date"] == "2024-01-01"
        assert poem["source"] == "Test"
        assert poem["word_count"] == 2  # Added by filter method
    
    def test_fetch_poems_with_word_limit_zero_count(self):
        """Test fetch_poems_with_word_limit with zero count"""
        poems = self.fetcher.fetch_poems_with_word_limit(0, max_words=200)
        assert poems == []
    
    def test_fetch_poems_with_word_limit_negative_count(self):
        """Test fetch_poems_with_word_limit with negative count"""
        poems = self.fetcher.fetch_poems_with_word_limit(-1, max_words=200)
        assert poems == []
    
    def test_fetch_poems_with_word_limit_success(self):
        """Test successful fetch with word limit (using sample data)"""
        # Mock the fetch_random_poems method to return sample data
        original_fetch = self.fetcher.fetch_random_poems
        self.fetcher.fetch_random_poems = lambda count: self.fetcher.create_sample_poems(count)
        
        try:
            poems = self.fetcher.fetch_poems_with_word_limit(2, max_words=200, max_retries=3)
            assert len(poems) == 2
            assert all(poem["word_count"] <= 200 for poem in poems)
            assert all("word_count" in poem for poem in poems)
        finally:
            # Restore original method
            self.fetcher.fetch_random_poems = original_fetch
    
    def test_fetch_poems_with_word_limit_max_retries(self):
        """Test fetch_poems_with_word_limit with max retries exceeded"""
        # Mock fetch_random_poems to always return long poems
        def mock_fetch_long_poems(count):
            return [{"title": f"Long Poem {i}", "text": " ".join(["word"] * 300)} for i in range(count)]
        
        original_fetch = self.fetcher.fetch_random_poems
        self.fetcher.fetch_random_poems = mock_fetch_long_poems
        
        try:
            poems = self.fetcher.fetch_poems_with_word_limit(2, max_words=200, max_retries=2)
            assert len(poems) == 0  # Should return empty list when max retries exceeded
        finally:
            # Restore original method
            self.fetcher.fetch_random_poems = original_fetch
    
    def test_fetch_poems_with_word_limit_mixed_results(self):
        """Test fetch_poems_with_word_limit with mixed short and long poems"""
        # Mock fetch_random_poems to return mixed results
        def mock_fetch_mixed_poems(count):
            return [
                {"title": "Short Poem", "text": "Hello world"},  # 2 words
                {"title": "Long Poem", "text": " ".join(["word"] * 300)},  # 300 words
                {"title": "Medium Poem", "text": " ".join(["word"] * 100)}  # 100 words
            ]
        
        original_fetch = self.fetcher.fetch_random_poems
        self.fetcher.fetch_random_poems = mock_fetch_mixed_poems
        
        try:
            poems = self.fetcher.fetch_poems_with_word_limit(2, max_words=200, max_retries=3)
            assert len(poems) == 2
            assert all(poem["word_count"] <= 200 for poem in poems)
            # Should include the short and medium poems
            titles = [poem["title"] for poem in poems]
            assert "Short Poem" in titles
            assert "Medium Poem" in titles
            assert "Long Poem" not in titles
        finally:
            # Restore original method
            self.fetcher.fetch_random_poems = original_fetch


class TestPoetDateFetching:
    """Test poet date fetching functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = PoemFetcher()
    
    @patch('src.poem_fetcher.requests.Session.get')
    def test_get_poet_dates_valid_poet(self, mock_get):
        """Test fetching poet dates with valid poet name."""
        # Mock Wikidata response with birth and death dates
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'birth': {
                            'value': '1874-03-26',
                            'type': 'time'
                        },
                        'death': {
                            'value': '1963-01-29',
                            'type': 'time'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_poet_dates("Robert Frost")
        
        assert result is not None
        assert result['birth_year'] == 1874
        assert result['death_year'] == 1963
        mock_get.assert_called_once()
    
    @patch('src.poem_fetcher.requests.Session.get')
    def test_get_poet_dates_living_poet(self, mock_get):
        """Test fetching poet dates for living poet (no death date)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'birth': {
                            'value': '1950-01-01',
                            'type': 'time'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_poet_dates("Living Poet")
        
        assert result is not None
        assert result['birth_year'] == 1950
        assert result['death_year'] is None
    
    @patch('src.poem_fetcher.requests.Session.get')
    def test_get_poet_dates_unknown_poet(self, mock_get):
        """Test fetching poet dates for unknown poet."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': []
            }
        }
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_poet_dates("Unknown Poet")
        
        assert result is None
    
    @patch('src.poem_fetcher.requests.Session.get')
    def test_get_poet_dates_api_error(self, mock_get):
        """Test handling API errors gracefully."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_poet_dates("Robert Frost")
        
        assert result is None
    
    def test_get_poet_dates_empty_name(self):
        """Test handling empty poet name."""
        result = self.fetcher.get_poet_dates("")
        assert result is None
        
        result = self.fetcher.get_poet_dates(None)
        assert result is None


class TestEnrichPoemWithDates:
    """Test poem enrichment with date information."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = PoemFetcher()
    
    @patch('src.poem_fetcher.PoemFetcher.get_poet_dates')
    def test_enrich_poem_with_dates_success(self, mock_get_dates):
        """Test enriching poem with poet dates."""
        mock_get_dates.return_value = {
            'birth_year': 1874,
            'death_year': 1963
        }
        
        poem = {
            'title': 'The Road Not Taken',
            'author': 'Robert Frost',
            'text': 'Two roads diverged...'
        }
        
        result = self.fetcher.enrich_poem_with_dates(poem)
        
        assert result['poet_birth_year'] == 1874
        assert result['poet_death_year'] == 1963
        assert result['poet_lifespan'] == "(1874-1963)"
        assert result['title'] == 'The Road Not Taken'  # Original fields preserved
    
    @patch('src.poem_fetcher.PoemFetcher.get_poet_dates')
    def test_enrich_poem_with_dates_living_poet(self, mock_get_dates):
        """Test enriching poem with living poet dates."""
        mock_get_dates.return_value = {
            'birth_year': 1950,
            'death_year': None
        }
        
        poem = {
            'title': 'Modern Poem',
            'author': 'Living Poet',
            'text': 'Modern poetry...'
        }
        
        result = self.fetcher.enrich_poem_with_dates(poem)
        
        assert result['poet_birth_year'] == 1950
        assert result['poet_death_year'] is None
        assert result['poet_lifespan'] == "(1950-present)"
    
    @patch('src.poem_fetcher.PoemFetcher.get_poet_dates')
    def test_enrich_poem_with_dates_no_dates(self, mock_get_dates):
        """Test enriching poem when poet dates are not available."""
        mock_get_dates.return_value = None
        
        poem = {
            'title': 'Unknown Poem',
            'author': 'Unknown Poet',
            'text': 'Unknown poetry...'
        }
        
        result = self.fetcher.enrich_poem_with_dates(poem)
        
        assert result['poet_birth_year'] is None
        assert result['poet_death_year'] is None
        assert result['poet_lifespan'] is None
        assert result['title'] == 'Unknown Poem'  # Original fields preserved
    
    @patch('src.poem_fetcher.PoemFetcher.get_poet_dates')
    def test_enrich_poem_with_dates_error(self, mock_get_dates):
        """Test enriching poem when get_poet_dates raises an error."""
        mock_get_dates.side_effect = Exception("API Error")
        
        poem = {
            'title': 'Error Poem',
            'author': 'Error Poet',
            'text': 'Error poetry...'
        }
        
        result = self.fetcher.enrich_poem_with_dates(poem)
        
        assert result['poet_birth_year'] is None
        assert result['poet_death_year'] is None
        assert result['poet_lifespan'] is None
        assert result['title'] == 'Error Poem'  # Original fields preserved


class TestFormatPoemDataWithDates:
    """Test _format_poem_data includes date enrichment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = PoemFetcher()
    
    @patch('src.poem_fetcher.PoemFetcher.enrich_poem_with_dates')
    def test_format_poem_data_calls_enrich(self, mock_enrich):
        """Test that _format_poem_data calls enrich_poem_with_dates."""
        mock_enrich.return_value = {
            'title': 'Test Poem',
            'author': 'Test Author',
            'text': 'Test text',
            'poet_birth_year': 1874,
            'poet_death_year': 1963,
            'poet_lifespan': '(1874-1963)'
        }
        
        raw_poem = {
            'title': 'Test Poem',
            'author': 'Test Author',
            'lines': ['Test text']
        }
        
        result = self.fetcher._format_poem_data(raw_poem)
        
        assert result is not None
        assert result['poet_birth_year'] == 1874
        assert result['poet_death_year'] == 1963
        assert result['poet_lifespan'] == '(1874-1963)'
        
        # Verify enrich_poem_with_dates was called
        mock_enrich.assert_called_once()
    
    @patch('src.poem_fetcher.PoemFetcher.enrich_poem_with_dates')
    def test_format_poem_data_handles_enrich_error(self, mock_enrich):
        """Test that _format_poem_data handles enrich_poem_with_dates errors."""
        mock_enrich.side_effect = Exception("Enrichment error")
        
        raw_poem = {
            'title': 'Test Poem',
            'author': 'Test Author',
            'lines': ['Test text']
        }
        
        result = self.fetcher._format_poem_data(raw_poem)
        
        # Should return poem even when enrichment fails
        assert result is not None
        assert result['title'] == 'Test Poem'
        assert result['author'] == 'Test Author'
        # Should not have date fields when enrichment fails
        assert 'poet_birth_year' not in result
        assert 'poet_death_year' not in result
        assert 'poet_lifespan' not in result


if __name__ == "__main__":
    pytest.main([__file__])
