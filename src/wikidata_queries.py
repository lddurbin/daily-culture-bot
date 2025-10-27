#!/usr/bin/env python3
"""
Wikidata Query Module for Daily Culture Bot

This module contains SPARQL query methods for fetching artwork data from Wikidata.
Extracted from datacreator.py to improve code organization and maintainability.
"""

import requests
import time
from typing import List, Dict, Optional


class WikidataQueries:
    """Handles SPARQL queries to Wikidata for artwork data."""
    
    def __init__(self, wikidata_endpoint: str, session: requests.Session, 
                 query_timeout: int = 60, query_cache: dict = None, 
                 cache_max_size: int = 50):
        """
        Initialize Wikidata query handler.
        
        Args:
            wikidata_endpoint: Wikidata SPARQL endpoint URL
            session: Requests session for HTTP calls
            query_timeout: Timeout for queries in seconds
            query_cache: Cache dictionary for query results
            cache_max_size: Maximum cache size
        """
        self.wikidata_endpoint = wikidata_endpoint
        self.session = session
        self.query_timeout = query_timeout
        self.query_cache = query_cache or {}
        self.cache_max_size = cache_max_size
    
    def _get_cache_key(self, query_type: str, **params) -> str:
        """Generate a cache key for query parameters."""
        # Create a deterministic key from parameters
        key_parts = [query_type]
        for k, v in sorted(params.items()):
            if isinstance(v, list):
                key_parts.append(f"{k}:{','.join(sorted(v))}")
            else:
                key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)
    
    def _manage_cache_size(self):
        """Remove oldest entries if cache is too large."""
        if len(self.query_cache) > self.cache_max_size:
            # Remove oldest 25% of entries
            items_to_remove = len(self.query_cache) // 4
            oldest_keys = list(self.query_cache.keys())[:items_to_remove]
            for key in oldest_keys:
                del self.query_cache[key]
    
    def query_artwork_by_subject(self, q_codes: List[str], limit: int = 50, 
                                offset: int = 0, random_order: bool = True, 
                                genres: List[str] = None, max_sitelinks: int = 20, 
                                artwork_types: List[str] = None) -> List[Dict]:
        """
        Query Wikidata for visual artwork (paintings, photographs, sculptures, etc.) 
        matching specific subjects/themes and genres.
        Optimized for better performance and reduced timeouts.
        
        Args:
            q_codes: List of Wikidata Q-codes for subjects to match
            limit: Number of results to return
            offset: Offset for pagination
            random_order: Whether to randomize the order of results
            genres: List of genre Q-codes to filter by
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            artwork_types: List of artwork type Q-codes to filter by
            
        Returns:
            List of raw Wikidata results
        """
        if not q_codes:
            return []
        
        # Check cache first
        cache_key = self._get_cache_key("artwork_by_subject", 
                                      q_codes=q_codes, limit=limit, offset=offset, 
                                      max_sitelinks=max_sitelinks, artwork_types=artwork_types)
        
        if cache_key in self.query_cache:
            print("📋 Using cached query result")
            return self.query_cache[cache_key]
        
        # Limit Q-codes to prevent overly complex queries
        if len(q_codes) > 10:
            print(f"⚠️ Too many Q-codes ({len(q_codes)}), limiting to first 10 for performance")
            q_codes = q_codes[:10]
        
        # Default artwork types if not specified
        if artwork_types is None:
            artwork_types = [
                "Q3305213",  # painting
                "Q125191",   # photograph
                "Q860861",   # sculpture
            ]  # Reduced to most common types for better performance
        
        # Create simplified Q-code filter clause
        q_code_list = ', '.join([f'wd:{q_code}' for q_code in q_codes])
        artwork_type_list = ', '.join([f'wd:{art_type}' for art_type in artwork_types])
        
        # Simplified query structure for better performance
        sparql_query = f"""
        SELECT ?artwork ?image ?sitelinks WHERE {{
          ?artwork wdt:P31 ?artworkType .
          FILTER(?artworkType IN ({artwork_type_list}))
          
          ?artwork wdt:P18 ?image .
          ?artwork wikibase:sitelinks ?sitelinks .
          FILTER(?sitelinks < {max_sitelinks})
          
          # Match by subject/depicts properties (simplified)
          ?artwork wdt:P180 ?subject .
          FILTER(?subject IN ({q_code_list}))
        }}
        ORDER BY RAND()
        LIMIT {limit}
        OFFSET {offset}
        """
        
        # Use longer timeout for complex queries
        timeout = self.query_timeout if len(q_codes) > 5 else min(30, self.query_timeout)
        max_retries = 2  # Reduced retries for faster fallback
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.wikidata_endpoint,
                    params={'query': sparql_query, 'format': 'json'},
                    timeout=timeout
                )
                response.raise_for_status()
                
                data = response.json()
                results = data['results']['bindings']
                
                # Cache the results
                self.query_cache[cache_key] = results
                self._manage_cache_size()
                
                return results
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff
                    print(f"⚠️ Wikidata query attempt {attempt + 1} failed: {e}")
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"❌ Error querying Wikidata for subjects after {max_retries} attempts: {e}")
                    return []
    
    def query_wikidata_paintings(self, limit: int = 50, offset: int = 0, 
                                filter_type: str = "both", random_order: bool = False, 
                                max_sitelinks: int = 20) -> List[Dict]:
        """
        Query Wikidata for paintings with detailed information.
        Optimized for better performance and reduced timeouts.
        
        Args:
            limit: Number of results to return
            offset: Offset for pagination
            filter_type: "license", "age", or "both"
            random_order: Whether to randomize the order of results
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
        """
        
        # Check cache first
        cache_key = self._get_cache_key("wikidata_paintings", 
                                      limit=limit, offset=offset, 
                                      max_sitelinks=max_sitelinks)
        
        if cache_key in self.query_cache:
            print("📋 Using cached painting query result")
            return self.query_cache[cache_key]
        
        # Simplified query structure for better performance
        # Remove complex license filtering that causes timeouts
        sparql_query = f"""
        SELECT ?painting ?image ?sitelinks WHERE {{
          ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
          ?painting wdt:P18 ?image .        # Image
          ?painting wikibase:sitelinks ?sitelinks .  # Wikipedia sitelinks count
          
          # Filter out paintings with excessive Wikipedia coverage (fame filter)
          FILTER(?sitelinks < {max_sitelinks})
        }}
        ORDER BY RAND()
        LIMIT {limit}
        OFFSET {offset}
        """
        
        # Use longer timeout for better reliability
        timeout = self.query_timeout
        max_retries = 2  # Reduced retries for faster fallback
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.wikidata_endpoint,
                    params={'query': sparql_query, 'format': 'json'},
                    timeout=timeout
                )
                response.raise_for_status()
                
                data = response.json()
                results = data['results']['bindings']
                
                # Cache the results
                self.query_cache[cache_key] = results
                self._manage_cache_size()
                
                return results
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff
                    print(f"⚠️ Wikidata query attempt {attempt + 1} failed: {e}")
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"❌ Error querying Wikidata after {max_retries} attempts: {e}")
                    return []
    
    def get_artwork_inception_date(self, wikidata_url: str) -> Optional[int]:
        """
        Get artwork inception/creation date from Wikidata URL.
        Returns year as integer or None if unavailable.
        
        Uses P571 (inception) property from Wikidata.
        """
        if not wikidata_url:
            return None
        
        try:
            # Extract Q-ID from URL
            q_id = wikidata_url.split('/')[-1]
            
            sparql_query = f"""
            SELECT ?inception WHERE {{
              wd:{q_id} wdt:P571 ?inception .
            }}
            LIMIT 1
            """
            
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                if results:
                    inception_value = results[0].get('inception', {}).get('value', '')
                    if inception_value:
                        # Parse date string to extract year
                        # Handle various formats: YYYY, YYYY-MM-DD, date ranges
                        import re
                        year_match = re.match(r'^(\d{4})', inception_value)
                        if year_match:
                            return int(year_match.group(1))
        except Exception as e:
            print(f"Error getting inception date: {e}")
        
        return None
    
    def get_painting_dimensions(self, wikidata_url: str) -> str:
        """
        Get painting dimensions from Wikidata URL.
        """
        if not wikidata_url:
            return "Unknown dimensions"
        
        try:
            # Extract Q-ID from URL
            q_id = wikidata_url.split('/')[-1]
            
            sparql_query = f"""
            SELECT ?height ?width WHERE {{
              wd:{q_id} wdt:P2048 ?height .
              wd:{q_id} wdt:P2049 ?width .
            }}
            """
            
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                if results:
                    height = results[0].get('height', {}).get('value')
                    width = results[0].get('width', {}).get('value')
                    if height and width:
                        return f"{height} cm × {width} cm"
        except Exception as e:
            print(f"Error getting dimensions: {e}")
        
        return "Unknown dimensions"
