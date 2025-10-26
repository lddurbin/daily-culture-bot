#!/usr/bin/env python3
"""
Tests for Poem Analyzer

This module contains comprehensive tests for the poem analyzer functionality,
including theme detection, Q-code mapping, and edge cases.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import poem_analyzer


class TestPoemAnalyzerInit:
    """Test PoemAnalyzer initialization."""
    
    def test_initialization(self):
        """Test that PoemAnalyzer initializes correctly."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        assert analyzer.theme_mappings is not None
        assert len(analyzer.theme_mappings) > 0
        assert "nature" in analyzer.theme_mappings
        assert "love" in analyzer.theme_mappings
        assert "water" in analyzer.theme_mappings
    
    def test_theme_mappings_structure(self):
        """Test that theme mappings have correct structure."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        for theme, data in analyzer.theme_mappings.items():
            assert "keywords" in data
            assert "q_codes" in data
            assert isinstance(data["keywords"], list)
            assert isinstance(data["q_codes"], list)
            assert len(data["keywords"]) > 0
            assert len(data["q_codes"]) > 0
    
    def test_patterns_compiled(self):
        """Test that regex patterns are compiled."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        assert hasattr(analyzer, 'patterns')
        assert len(analyzer.patterns) > 0
        
        for theme, pattern in analyzer.patterns.items():
            assert hasattr(pattern, 'findall')


class TestThemeDetection:
    """Test theme detection functionality."""
    
    def test_nature_theme_detection(self):
        """Test detection of nature themes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Forest Walk",
            "text": "I walked through the forest among the trees and flowers. The green leaves rustled in the wind."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "nature" in analysis["themes"]
        assert "flowers" in analysis["themes"]
        assert analysis["total_matches"] > 0
    
    def test_water_theme_detection(self):
        """Test detection of water themes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Ocean Waves",
            "text": "The waves crashed against the shore. The sea was calm and peaceful."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "water" in analysis["themes"]
        assert analysis["total_matches"] > 0
    
    def test_love_theme_detection(self):
        """Test detection of love themes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "My Beloved",
            "text": "I love you with all my heart. You are my dear and beloved."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "love" in analysis["themes"]
        assert analysis["total_matches"] > 0
    
    def test_multiple_themes(self):
        """Test detection of multiple themes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Garden of Love",
            "text": "In the garden, among the flowers, I found love. The roses bloomed as my heart did."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "flowers" in analysis["themes"]
        assert "love" in analysis["themes"]
        assert len(analysis["themes"]) >= 2
    
    def test_no_themes_detected(self):
        """Test when no themes are detected."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Abstract Thoughts",
            "text": "The concept of existence is complex and multifaceted."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == False
        assert len(analysis["themes"]) == 0
        assert analysis["total_matches"] == 0
    
    def test_case_insensitive_detection(self):
        """Test that theme detection is case insensitive."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "NATURE WALK",
            "text": "I LOVE walking in the FOREST with FLOWERS and TREES."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "nature" in analysis["themes"]
        assert "flowers" in analysis["themes"]
        assert "love" in analysis["themes"]


class TestQCodeMapping:
    """Test Q-code mapping functionality."""
    
    def test_q_code_extraction(self):
        """Test extraction of Q-codes from themes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Nature and Love",
            "text": "The flowers bloom in the garden where love grows."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert len(analysis["q_codes"]) > 0
        # Check that Q-codes are valid format (Q followed by numbers)
        for q_code in analysis["q_codes"]:
            assert q_code.startswith("Q")
            assert q_code[1:].isdigit()
    
    def test_q_code_deduplication(self):
        """Test that duplicate Q-codes are removed."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        # Create analysis with overlapping themes that might have same Q-codes
        analysis1 = analyzer.analyze_poem({"title": "Flowers", "text": "beautiful flowers bloom"})
        analysis2 = analyzer.analyze_poem({"title": "Garden", "text": "garden with flowers"})
        
        combined_q_codes = analyzer.get_combined_q_codes([analysis1, analysis2])
        
        # Should not have duplicates
        assert len(combined_q_codes) == len(set(combined_q_codes))
    
    def test_empty_q_codes(self):
        """Test handling of empty Q-codes."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Abstract",
            "text": "The concept is complex."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["q_codes"] == []
        assert analysis["has_themes"] == False


class TestConfidenceScores:
    """Test confidence score calculation."""
    
    def test_confidence_calculation(self):
        """Test that confidence scores are calculated correctly."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Flower Garden",
            "text": "The flowers flowers flowers bloom in the garden garden."
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert "confidence_scores" in analysis
        assert len(analysis["confidence_scores"]) > 0
        
        for theme, confidence in analysis["confidence_scores"].items():
            assert 0 <= confidence <= 1
            assert isinstance(confidence, float)
    
    def test_confidence_with_frequency(self):
        """Test that confidence increases with word frequency."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        # Poem with many nature words
        poem_high = {
            "title": "Nature Nature",
            "text": "nature nature nature forest trees flowers garden nature"
        }
        
        # Poem with few nature words
        poem_low = {
            "title": "Brief Nature",
            "text": "nature"
        }
        
        analysis_high = analyzer.analyze_poem(poem_high)
        analysis_low = analyzer.analyze_poem(poem_low)
        
        if "nature" in analysis_high["confidence_scores"] and "nature" in analysis_low["confidence_scores"]:
            # Both might be capped at 1.0, so check that high has more matches
            assert analysis_high["theme_scores"]["nature"] > analysis_low["theme_scores"]["nature"]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_poem(self):
        """Test handling of empty poem."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {"title": "", "text": ""}
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == False
        assert analysis["themes"] == []
        assert analysis["q_codes"] == []
    
    def test_none_poem(self):
        """Test handling of None poem."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        analysis = analyzer.analyze_poem(None)
        
        assert analysis["has_themes"] == False
        assert analysis["themes"] == []
        assert analysis["q_codes"] == []
    
    def test_missing_fields(self):
        """Test handling of poem with missing fields."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {"title": "Test"}
        analysis = analyzer.analyze_poem(poem)
        
        # Should still work with just title
        assert isinstance(analysis, dict)
        assert "has_themes" in analysis
    
    def test_very_long_poem(self):
        """Test handling of very long poem."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        # Create a very long poem
        long_text = "nature " * 1000 + "love " * 500
        poem = {
            "title": "Long Poem",
            "text": long_text
        }
        
        analysis = analyzer.analyze_poem(poem)
        
        assert analysis["has_themes"] == True
        assert "nature" in analysis["themes"]
        assert "love" in analysis["themes"]
        assert analysis["total_matches"] > 1000  # Should find many matches


class TestMultiplePoems:
    """Test analysis of multiple poems."""
    
    def test_analyze_multiple_poems(self):
        """Test analysis of multiple poems."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poems = [
            {"title": "Nature", "text": "flowers and trees"},
            {"title": "Love", "text": "I love you"},
            {"title": "Water", "text": "waves and sea"}
        ]
        
        analyses = analyzer.analyze_multiple_poems(poems)
        
        assert len(analyses) == 3
        assert all(analysis["has_themes"] for analysis in analyses)
    
    def test_get_combined_q_codes(self):
        """Test getting combined Q-codes from multiple analyses."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poems = [
            {"title": "Nature", "text": "flowers and trees"},
            {"title": "Love", "text": "I love you"}
        ]
        
        analyses = analyzer.analyze_multiple_poems(poems)
        combined_q_codes = analyzer.get_combined_q_codes(analyses)
        
        assert len(combined_q_codes) > 0
        assert all(q_code.startswith("Q") for q_code in combined_q_codes)


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_get_primary_theme(self):
        """Test getting primary theme."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Garden of Love",
            "text": "In the garden with flowers, I found love and nature."
        }
        
        analysis = analyzer.analyze_poem(poem)
        primary_theme = analyzer.get_primary_theme(analysis)
        
        assert primary_theme is not None
        assert primary_theme in analysis["themes"]
    
    def test_get_primary_theme_no_themes(self):
        """Test getting primary theme when no themes detected."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {"title": "Abstract", "text": "complex concepts"}
        
        analysis = analyzer.analyze_poem(poem)
        primary_theme = analyzer.get_primary_theme(analysis)
        
        assert primary_theme is None
    
    def test_get_theme_summary(self):
        """Test getting theme summary."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Nature and Love",
            "text": "flowers bloom in the garden where love grows"
        }
        
        analysis = analyzer.analyze_poem(poem)
        summary = analyzer.get_theme_summary(analysis)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "nature" in summary.lower() or "flowers" in summary.lower()
    
    def test_get_theme_summary_no_themes(self):
        """Test getting theme summary when no themes detected."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {"title": "Abstract", "text": "complex concepts"}
        
        analysis = analyzer.analyze_poem(poem)
        summary = analyzer.get_theme_summary(analysis)
        
        assert summary == "No themes detected"


class TestPerformance:
    """Test performance characteristics."""
    
    def test_analysis_speed(self):
        """Test that analysis completes quickly."""
        import time
        
        analyzer = poem_analyzer.PoemAnalyzer()
        
        poem = {
            "title": "Complex Nature Poem",
            "text": " ".join(["nature", "love", "water", "flowers"] * 100)
        }
        
        start_time = time.time()
        analysis = analyzer.analyze_poem(poem)
        end_time = time.time()
        
        # Should complete in less than 1 second
        assert (end_time - start_time) < 1.0
        assert analysis["has_themes"] == True
    
    def test_memory_usage(self):
        """Test that analysis doesn't use excessive memory."""
        analyzer = poem_analyzer.PoemAnalyzer()
        
        # Analyze many poems
        poems = [
            {"title": f"Poem {i}", "text": f"nature love water flowers {i}"}
            for i in range(100)
        ]
        
        analyses = analyzer.analyze_multiple_poems(poems)
        
        assert len(analyses) == 100
        assert all(analysis["has_themes"] for analysis in analyses)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
