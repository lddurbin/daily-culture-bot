#!/usr/bin/env python3
"""
Tests for PoemFetcher class
"""

import pytest
import sys
import os

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


if __name__ == "__main__":
    pytest.main([__file__])
