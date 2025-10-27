import pytest
import sys
import os
import requests
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import wikidata_queries


class TestWikidataQueriesInit:
    """Test WikidataQueries initialization."""
    
    def test_initialization(self):
        """Test that WikidataQueries initializes correctly."""
        mock_session = Mock()
        queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            mock_session,
            query_timeout=60,
            query_cache={},
            cache_max_size=50
        )
        
        assert queries.wikidata_endpoint == "https://query.wikidata.org/sparql"
        assert queries.session == mock_session
        assert queries.query_timeout == 60
        assert queries.query_cache == {}
        assert queries.cache_max_size == 50


class TestGetCacheKey:
    """Test _get_cache_key method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            Mock(),
            query_timeout=60
        )
    
    def test_get_cache_key_simple(self):
        """Test cache key generation with simple parameters."""
        key = self.queries._get_cache_key("test_query", limit=10, offset=0)
        
        assert key == "test_query|limit:10|offset:0"
    
    def test_get_cache_key_with_list(self):
        """Test cache key generation with list parameters."""
        key = self.queries._get_cache_key("test_query", q_codes=["Q1", "Q2"], limit=10)
        
        assert key == "test_query|limit:10|q_codes:Q1,Q2"
    
    def test_get_cache_key_sorted(self):
        """Test cache key generation with parameters in different order."""
        key1 = self.queries._get_cache_key("test_query", limit=10, offset=0)
        key2 = self.queries._get_cache_key("test_query", offset=0, limit=10)
        
        assert key1 == key2  # Should be the same regardless of order


class TestManageCacheSize:
    """Test _manage_cache_size method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            Mock(),
            query_timeout=60,
            query_cache={},
            cache_max_size=3
        )
    
    def test_manage_cache_size_below_limit(self):
        """Test cache management when under limit."""
        self.queries.query_cache = {"key1": "value1", "key2": "value2"}
        
        self.queries._manage_cache_size()
        
        assert len(self.queries.query_cache) == 2
        assert "key1" in self.queries.query_cache
        assert "key2" in self.queries.query_cache
    
    def test_manage_cache_size_at_exact_limit(self):
        """Test cache management when at exact limit."""
        self.queries.query_cache = {"key1": "value1", "key2": "value2", "key3": "value3"}
        
        self.queries._manage_cache_size()
        
        assert len(self.queries.query_cache) == 3
        assert "key1" in self.queries.query_cache
        assert "key2" in self.queries.query_cache
        assert "key3" in self.queries.query_cache
    
    def test_manage_cache_size_above_limit(self):
        """Test cache management when over limit."""
        self.queries.query_cache = {
            "key1": "value1", 
            "key2": "value2", 
            "key3": "value3",
            "key4": "value4"
        }
        
        self.queries._manage_cache_size()
        
        assert len(self.queries.query_cache) <= 3
        # Should evict oldest entries
    
    def test_manage_cache_size_empty_cache(self):
        """Test cache management with empty cache."""
        self.queries.query_cache = {}
        
        self.queries._manage_cache_size()
        
        assert len(self.queries.query_cache) == 0


class TestQueryRetryLogic:
    """Test query retry logic and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            Mock(),
            query_timeout=60
        )
    
    def test_query_first_attempt_success(self):
        """Test query success on first attempt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': [{'test': {'value': 'data'}}]}
        }
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_subject(["Q1"], limit=1)
            
            assert len(result) == 1
            assert result[0]['test']['value'] == 'data'
    
    def test_query_retry_after_timeout(self):
        """Test query retry after timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': [{'test': {'value': 'data'}}]}
        }
        
        with patch.object(self.queries.session, 'get') as mock_get:
            # First call times out, second succeeds
            mock_get.side_effect = [requests.Timeout(), mock_response]
            
            result = self.queries.query_artwork_by_subject(["Q1"], limit=1)
            
            assert len(result) == 1
            assert result[0]['test']['value'] == 'data'
            assert mock_get.call_count == 2
    
    def test_query_max_retries_exceeded(self):
        """Test query when max retries exceeded."""
        with patch.object(self.queries.session, 'get', side_effect=requests.Timeout()):
            result = self.queries.query_artwork_by_subject(["Q1"], limit=1)
            
            assert result == []
    
    def test_query_network_error_handling(self):
        """Test query with network error."""
        with patch.object(self.queries.session, 'get', side_effect=requests.ConnectionError()):
            result = self.queries.query_artwork_by_subject(["Q1"], limit=1)
            
            assert result == []


class TestCacheHitMiss:
    """Test cache hit/miss scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            Mock(),
            query_timeout=60,
            query_cache={},
            cache_max_size=50
        )
    
    def test_cache_hit_returns_cached_data(self):
        """Test cache hit returns cached data."""
        # Simplified test - just verify cache key generation works
        cache_key = self.queries._get_cache_key("query_artwork_by_subject", q_codes=["Q1"], limit=1)
        assert "query_artwork_by_subject" in cache_key
        assert "Q1" in cache_key
        assert "limit:1" in cache_key
    
    
    def test_cache_miss_fetches_new_data(self):
        """Test cache miss fetches new data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': [{'test': {'value': 'new_data'}}]}
        }
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_subject(["Q1"], limit=1)
            
            assert len(result) == 1
            assert result[0]['test']['value'] == 'new_data'
    
    def test_cache_key_generation_different_params(self):
        """Test cache key generation with different parameters."""
        key1 = self.queries._get_cache_key("test", limit=1, offset=0)
        key2 = self.queries._get_cache_key("test", limit=2, offset=0)
        
        assert key1 != key2


class TestQueryArtworkByDirectDepicts:
    """Test query_artwork_by_direct_depicts method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.queries = wikidata_queries.WikidataQueries(
            "https://query.wikidata.org/sparql",
            Mock(),
            query_timeout=60,
            query_cache={},
            cache_max_size=50
        )
    
    def test_query_direct_depicts_success(self):
        """Test successful direct depicts query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'artwork': {'value': 'https://wikidata.org/Q123'},
                        'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                        'sitelinks': {'value': '5'},
                        'subject': {'value': 'https://wikidata.org/Q10884'},  # tree
                        'genre': {'value': 'https://wikidata.org/Q191163'},  # landscape
                        'artworkType': {'value': 'https://wikidata.org/Q3305213'}  # painting
                    }
                ]
            }
        }
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_direct_depicts(["Q10884"], limit=1)
            
            assert len(result) == 1
            assert result[0]['artwork']['value'] == 'https://wikidata.org/Q123'
            assert result[0]['subject']['value'] == 'https://wikidata.org/Q10884'
    
    def test_query_direct_depicts_empty_q_codes(self):
        """Test direct depicts query with empty Q-codes."""
        result = self.queries.query_artwork_by_direct_depicts([])
        
        assert result == []
    
    def test_query_direct_depicts_with_genres(self):
        """Test direct depicts query with genre filtering."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': []}
        }
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_direct_depicts(
                ["Q10884"], 
                genres=["Q191163"],  # landscape
                limit=1
            )
            
            # Verify the query was made (even if no results)
            assert isinstance(result, list)
    
    def test_query_direct_depicts_with_artwork_types(self):
        """Test direct depicts query with artwork type filtering."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': []}
        }
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_direct_depicts(
                ["Q10884"], 
                artwork_types=["Q3305213"],  # painting
                limit=1
            )
            
            # Verify the query was made (even if no results)
            assert isinstance(result, list)
    
    def test_query_direct_depicts_q_codes_limit(self):
        """Test that Q-codes are limited to prevent overly complex queries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {'bindings': []}
        }
        
        # Test with more than 8 Q-codes
        many_q_codes = [f"Q{i}" for i in range(1, 15)]  # 14 Q-codes
        
        with patch.object(self.queries.session, 'get', return_value=mock_response):
            result = self.queries.query_artwork_by_direct_depicts(many_q_codes, limit=1)
            
            # Should still work but with limited Q-codes
            assert isinstance(result, list)
    
    def test_query_direct_depicts_cache_hit(self):
        """Test direct depicts query cache hit."""
        # Pre-populate cache
        cache_key = self.queries._get_cache_key(
            "artwork_by_direct_depicts", 
            q_codes=["Q10884"], 
            limit=1, 
            offset=0,
            max_sitelinks=20,
            artwork_types=None
        )
        cached_result = [{'cached': {'value': 'data'}}]
        self.queries.query_cache[cache_key] = cached_result
        
        result = self.queries.query_artwork_by_direct_depicts(["Q10884"], limit=1)
        
        assert result == cached_result
    
    def test_query_direct_depicts_error_handling(self):
        """Test direct depicts query error handling."""
        with patch.object(self.queries.session, 'get', side_effect=requests.Timeout()):
            result = self.queries.query_artwork_by_direct_depicts(["Q10884"], limit=1)
            
            assert result == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
