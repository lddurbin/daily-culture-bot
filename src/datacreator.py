#!/usr/bin/env python3
"""
Data Creator for Daily Painting Bot

This script generates painting data by fetching information from Wikimedia and Wikidata.
It creates JSON data with detailed painting information for art databases.
"""

import json
import requests
import time
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
import concurrent.futures
from threading import Lock

# Import configuration data
try:
    from . import wikidata_config
except ImportError:
    # Fallback for when running as standalone module
    try:
        import wikidata_config
    except ImportError:
        wikidata_config = None

# Import extracted modules
try:
    from . import wikidata_queries
    from . import artwork_processor
    from . import poem_analyzer
    from . import vision_analyzer
except ImportError:
    # Fallback for when running as standalone module
    try:
        import wikidata_queries
        import artwork_processor
        import poem_analyzer
        import vision_analyzer
    except ImportError:
        wikidata_queries = None
        artwork_processor = None
        poem_analyzer = None
        vision_analyzer = None

# Check if poem analyzer is available
POEM_ANALYZER_AVAILABLE = poem_analyzer is not None

# Check if vision analyzer is available
VISION_ANALYZER_AVAILABLE = vision_analyzer is not None


class PaintingDataCreator:
    def __init__(self, query_timeout: int = 60):
        # Import configuration from separate module
        if wikidata_config:
            self.wikidata_endpoint = wikidata_config.WIKIDATA_ENDPOINT
            self.wikipedia_api = wikidata_config.WIKIPEDIA_API
            self.commons_api = wikidata_config.COMMONS_API
            self.style_mappings = wikidata_config.STYLE_MAPPINGS
        else:
            # Fallback if module not available
            self.wikidata_endpoint = "https://query.wikidata.org/sparql"
            self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            self.commons_api = "https://commons.wikimedia.org/w/api.php"
            self.style_mappings = {}
            print("⚠️ Warning: wikidata_config module not available, using fallback configuration")
        
        # Create a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PaintingDataCreator/1.0 (https://github.com/ugurelveren/daily-painting-bot)'
        })
        
        # Simple query cache to avoid repeated expensive queries
        self.query_cache = {}
        self.cache_max_size = 50  # Limit cache size
        self.query_timeout = query_timeout  # Configurable timeout
        
        # Thread lock for thread-safe operations
        self.cache_lock = Lock()
        
        # Initialize extracted modules
        if wikidata_queries:
            self.queries = wikidata_queries.WikidataQueries(
                self.wikidata_endpoint, self.session, self.query_timeout, 
                self.query_cache, self.cache_max_size
            )
        else:
            self.queries = None
            print("⚠️ Warning: wikidata_queries module not available")
        
        if artwork_processor:
            self.processor = artwork_processor.ArtworkProcessor(
                self.wikidata_endpoint, self.session, self.wikipedia_api
            )
        else:
            self.processor = None
            print("⚠️ Warning: artwork_processor module not available")
        
        # Initialize vision analyzer
        if vision_analyzer:
            self.vision_analyzer = vision_analyzer.VisionAnalyzer()
            print("✅ Vision analyzer initialized")
        else:
            self.vision_analyzer = None
            print("⚠️ Warning: vision_analyzer module not available")

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

    def query_artwork_by_subject(self, q_codes: List[str], limit: int = 50, offset: int = 0, random_order: bool = True, genres: List[str] = None, max_sitelinks: int = 20, artwork_types: List[str] = None) -> List[Dict]:
        """
        Query Wikidata for visual artwork (paintings, photographs, sculptures, etc.) matching specific subjects/themes and genres.
        Optimized for better performance and reduced timeouts.
        
        Args:
            q_codes: List of Wikidata Q-codes for subjects to match
            limit: Number of results to return
            offset: Offset for pagination
            random_order: Whether to randomize the order of results
            genres: Optional list of genre Q-codes to filter by
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            artwork_types: List of artwork type Q-codes (default: paintings, photos, sculptures)
            
        Returns:
            List of raw Wikidata results
        """
        """Delegate to wikidata_queries module."""
        if self.queries:
            return self.queries.query_artwork_by_subject(q_codes, limit, offset, random_order, genres, max_sitelinks, artwork_types)
        else:
            print("❌ Wikidata queries module not available")
            return []

    def query_wikidata_paintings(self, limit: int = 50, offset: int = 0, filter_type: str = "both", random_order: bool = False, max_sitelinks: int = 20) -> List[Dict]:
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
        """Delegate to wikidata_queries module."""
        if self.queries:
            return self.queries.query_wikidata_paintings(limit, offset, filter_type, random_order, max_sitelinks)
        else:
            print("❌ Wikidata queries module not available")
            return []

    def get_wikipedia_summary(self, title: str) -> Optional[str]:
        """
        Get a brief description from Wikipedia to use as a fact.
        """
        try:
            # Clean the title for Wikipedia API
            clean_title = title.replace(" ", "_")
            url = f"{self.wikipedia_api}{clean_title}"
            
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                # Return first sentence as a fact
                if extract:
                    sentences = extract.split('. ')
                    return sentences[0] + '.' if sentences else extract[:200] + "..."
            
        except Exception as e:
            print(f"Error getting Wikipedia summary for {title}: {e}")
        
        return None

    def get_high_res_image_url(self, commons_url: str) -> str:
        """
        Convert Wikimedia Commons image URL to a higher resolution version.
        """
        if not commons_url:
            return ""
            
        # If it's already a thumbnail URL, try to get the original
        if "/thumb/" in commons_url:
            # Extract the original filename from thumbnail URL
            # Format: /thumb/path/to/file.jpg/800px-filename.jpg
            original_match = re.search(r'/thumb/([^/]+/[^/]+\.(jpg|jpeg|png|gif))', commons_url)
            if original_match:
                original_path = original_match.group(1)
                return f"https://upload.wikimedia.org/wikipedia/commons/{original_path}"
            else:
                # If we can't parse it, return the original URL
                return commons_url
        
        # If it's a direct commons URL, return as-is
        if "commons.wikimedia.org" in commons_url or "upload.wikimedia.org" in commons_url:
            return commons_url
            
        # For other URLs, return as-is
        return commons_url

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

    def clean_text(self, text: str) -> str:
        """
        Clean text from Wikidata responses.
        """
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ')

    def get_painting_labels(self, wikidata_url: str) -> Dict[str, str]:
        """
        Get labels for a painting from its Wikidata URL.
        """
        if not wikidata_url:
            return {"title": "Unknown Title", "artist": "Unknown Artist"}
        
        try:
            # Extract Q-ID from URL
            q_id = wikidata_url.split('/')[-1]
            
            # Simple query to get labels
            sparql_query = f"""
            SELECT ?paintingLabel ?artistLabel WHERE {{
              wd:{q_id} rdfs:label ?paintingLabel .
              wd:{q_id} wdt:P170 ?artist .
              ?artist rdfs:label ?artistLabel .
              FILTER(LANG(?paintingLabel) = "en")
              FILTER(LANG(?artistLabel) = "en")
            }}
            LIMIT 1
            """
            
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                if results:
                    return {
                        "title": results[0].get('paintingLabel', {}).get('value', 'Unknown Title'),
                        "artist": results[0].get('artistLabel', {}).get('value', 'Unknown Artist')
                    }
        except Exception as e:
            print(f"Error getting labels: {e}")
        
        return {"title": "Unknown Title", "artist": "Unknown Artist"}

    def process_painting_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Process raw Wikidata results into the format used by the daily painting bot.
        """
        if self.processor and self.queries:
            return self.processor.process_painting_data(raw_data, self.queries)
        else:
            # Fallback to inline processing if modules not available
            print("⚠️ Using fallback processing - modules not available")
            return self._process_painting_data_fallback(raw_data)
    
    def _process_painting_data_fallback(self, raw_data: List[Dict]) -> List[Dict]:
        """Fallback processing method when modules are not available."""
        processed_paintings = []
        
        for item in raw_data:
            try:
                # Get Wikidata URL and image first
                wikidata_url = item.get('painting', {}).get('value', '')
                image_url = item.get('image', {}).get('value', '')
                
                if not wikidata_url or not image_url:
                    continue
                
                # Get labels using a separate, simple query
                labels = self.get_painting_labels(wikidata_url)
                title = labels.get('title', 'Unknown Title')
                artist = labels.get('artist', 'Unknown Artist')
                
                # Skip if we don't have basic info
                if title == 'Unknown Title' or artist == 'Unknown Artist':
                    continue
                
                # Process image URL
                if image_url:
                    image_url = self.get_high_res_image_url(image_url)
                
                # Create the painting entry
                painting_entry = {
                    "title": self.clean_text(title),
                    "artist": self.clean_text(artist),
                    "image": image_url,
                    "year": None,
                    "style": "Classical",
                    "museum": "Unknown Location",
                    "origin": "Unknown",
                    "medium": "Oil on canvas",
                    "dimensions": "Unknown dimensions",
                    "wikidata": wikidata_url,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                processed_paintings.append(painting_entry)
                print(f"Processed: {title} by {artist}")
                
            except Exception as e:
                print(f"Error processing painting data: {e}")
                continue
        
        return processed_paintings
    
    def _get_painting_labels_fallback(self, wikidata_url: str) -> Dict[str, str]:
        """Fallback method to get painting labels."""
        if not wikidata_url:
            return {"title": "Unknown Title", "artist": "Unknown Artist"}
        
        try:
            # Extract Q-ID from URL
            q_id = wikidata_url.split('/')[-1]
            
            # Simple query to get labels
            sparql_query = f"""
            SELECT ?paintingLabel ?artistLabel WHERE {{
              wd:{q_id} rdfs:label ?paintingLabel .
              wd:{q_id} wdt:P170 ?artist .
              ?artist rdfs:label ?artistLabel .
              FILTER(LANG(?paintingLabel) = "en")
              FILTER(LANG(?artistLabel) = "en")
            }}
            LIMIT 1
            """
            
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                if results:
                    return {
                        "title": results[0].get('paintingLabel', {}).get('value', 'Unknown Title'),
                        "artist": results[0].get('artistLabel', {}).get('value', 'Unknown Artist')
                    }
        except Exception as e:
            print(f"Error getting labels: {e}")
        
        return {"title": "Unknown Title", "artist": "Unknown Artist"}
    
    def _get_high_res_image_url_fallback(self, commons_url: str) -> str:
        """Fallback method to get high-res image URL."""
        if not commons_url:
            return ""
            
        # If it's already a thumbnail URL, try to get the original
        if "/thumb/" in commons_url:
            # Extract the original filename from thumbnail URL
            original_match = re.search(r'/thumb/([^/]+/[^/]+\.(jpg|jpeg|png|gif))', commons_url)
            if original_match:
                original_path = original_match.group(1)
                return f"https://upload.wikimedia.org/wikipedia/commons/{original_path}"
            else:
                return commons_url
        
        # If it's a direct commons URL, return as-is
        if "commons.wikimedia.org" in commons_url or "upload.wikimedia.org" in commons_url:
            return commons_url
            
        return commons_url
    
    def _clean_text_fallback(self, text: str) -> str:
        """Fallback method to clean text."""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ')
    
    def get_painting_labels(self, wikidata_url: str) -> Dict[str, str]:
        """Get labels for a painting from its Wikidata URL."""
        if self.processor:
            return self.processor.get_painting_labels(wikidata_url)
        else:
            return self._get_painting_labels_fallback(wikidata_url)
    
    def get_high_res_image_url(self, commons_url: str) -> str:
        """Convert Wikimedia Commons image URL to a higher resolution version."""
        if self.processor:
            return self.processor.get_high_res_image_url(commons_url)
        else:
            return self._get_high_res_image_url_fallback(commons_url)
    
    def clean_text(self, text: str) -> str:
        """Clean text from Wikidata responses."""
        if self.processor:
            return self.processor.clean_text(text)
        else:
            return self._clean_text_fallback(text)

    def create_sample_paintings(self, count: int = 5) -> List[Dict]:
        """
        Create sample paintings for testing when Wikidata is not accessible.
        """
        """Delegate to artwork_processor module."""
        if self.processor:
            return self.processor.create_sample_paintings(count)
        else:
            print("❌ Artwork processor module not available")
            return []

    def fetch_paintings(self, count: int = 1, filter_type: str = "both", random_order: bool = True, 
                       use_sample_on_error: bool = True, max_sitelinks: int = 20) -> List[Dict]:
        """
        Fetch and process painting data from Wikidata, fallback to sample data if needed.
        
        Args:
            count: Number of paintings to fetch
            filter_type: "license", "age", or "both"
            random_order: Whether to randomize the order of results
            use_sample_on_error: Whether to use sample data if API fails
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
        """
        filter_desc = {"license": "license-based", "age": "age-based", "both": "combined license+age"}
        order_desc = "random order" if random_order else "chronological order"
        print(f"Fetching {count} paintings from Wikidata using {filter_desc[filter_type]} filter in {order_desc}...")
        
        all_paintings = []
        batch_size = 10  # Much smaller batch size
        
        # Add random offset for extra variety when using random order
        if random_order:
            max_offset = min(500, count * 5)  # Reasonable random range
            random_offset = random.randint(0, max_offset)
            print(f"Using random starting offset: {random_offset}")
        else:
            random_offset = 0
        
        offset = random_offset
        max_retries = 2  # Reduced from 3 to 2 for faster fallback
        
        for retry in range(max_retries):
            try:
                while len(all_paintings) < count:
                    print(f"Fetching batch starting at offset {offset}...")
                    
                    raw_data = self.query_wikidata_paintings(
                        limit=batch_size, 
                        offset=offset, 
                        filter_type=filter_type,
                        random_order=random_order,
                        max_sitelinks=max_sitelinks
                    )
                    
                    if not raw_data:
                        print("No more data available.")
                        break
                    
                    processed_batch = self.process_painting_data(raw_data)
                    all_paintings.extend(processed_batch)
                    
                    offset += batch_size
                    
                    # Reduced delay between batches for faster execution
                    time.sleep(2)
                    
                    # Break if we've fetched enough
                    if len(processed_batch) < batch_size // 2:  # Less data means we're near the end
                        break
                
                # If we got some paintings, break the retry loop
                if all_paintings:
                    break
                    
            except Exception as e:
                print(f"Attempt {retry + 1} failed: {e}")
                if retry < max_retries - 1:
                    # Faster backoff: 1, 2 seconds
                    wait_time = retry + 1
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Return empty list if no paintings were fetched (no automatic fallback)
        if not all_paintings:
            print("Could not fetch from Wikidata. No paintings retrieved.")
        
        # Return only the requested count
        return all_paintings[:count]

    def fetch_artwork_by_subject(self, q_codes: List[str], count: int = 1, genres: List[str] = None, use_sample_on_error: bool = True, max_sitelinks: int = 20, artwork_types: List[str] = None) -> List[Dict]:
        """
        Fetch visual artwork matching specific subjects/themes and genres from Wikidata.
        Uses progressive fallback: specific artwork types → broader types → random artwork.
        
        Args:
            q_codes: List of Wikidata Q-codes for subjects to match
            count: Number of artworks to fetch
            genres: Optional list of genre Q-codes to filter by
            use_sample_on_error: Whether to use sample data if API fails
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            artwork_types: List of artwork type Q-codes (default: paintings, photos, sculptures)
            
        Returns:
            List of processed artwork dictionaries
        """
        if not q_codes:
            print("No Q-codes provided for subject-based search")
            return []
        
        print(f"Searching for artwork matching subjects: {q_codes}")
        if genres:
            print(f"With genre filtering: {genres}")
        
        # Progressive fallback strategy
        fallback_strategies = [
            {
                "name": "specific artwork types",
                "artwork_types": artwork_types or ["Q3305213", "Q125191", "Q860861"],  # paintings, photos, sculptures
                "max_sitelinks": max_sitelinks
            },
            {
                "name": "broader artwork types", 
                "artwork_types": ["Q3305213", "Q125191", "Q860861", "Q42973", "Q93184", "Q11661"],  # + drawings, prints, murals
                "max_sitelinks": max_sitelinks + 10  # Slightly more famous
            },
            {
                "name": "all visual art",
                "artwork_types": ["Q3305213", "Q125191", "Q860861", "Q42973", "Q93184", "Q11661", "Q11060274", "Q1044167"],  # + digital art, illustrations
                "max_sitelinks": max_sitelinks + 20  # Even more famous
            },
            {
                "name": "random artwork",
                "artwork_types": None,  # Will use regular random fetch
                "max_sitelinks": max_sitelinks
            }
        ]
        
        for strategy in fallback_strategies:
            print(f"🎨 Trying {strategy['name']}...")
            
            try:
                if strategy["artwork_types"] is None:
                    # Use regular random fetch as final fallback
                    print("🔄 Falling back to random artwork...")
                    return self.fetch_paintings(count=count, max_sitelinks=strategy["max_sitelinks"])
                
                # Try subject-based search with current strategy
                raw_data = self.query_artwork_by_subject(
                    q_codes=q_codes,
                    limit=count * 5,  # Fetch more to have options
                    offset=0,
                    random_order=True,
                    genres=genres,
                    max_sitelinks=strategy["max_sitelinks"],
                    artwork_types=strategy["artwork_types"]
                )
                
                if raw_data:
                    print(f"✅ Found {len(raw_data)} artworks with {strategy['name']}")
                    processed_artwork = self.process_painting_data(raw_data)
                    if processed_artwork:
                        return processed_artwork[:count]
                
                print(f"⚠️ No results with {strategy['name']}, trying next strategy...")
                
            except Exception as e:
                print(f"❌ Error with {strategy['name']}: {e}")
                continue
        
        print("❌ All fallback strategies failed")
        return []

    def fetch_artwork_by_subject_with_scoring(self, poem_analysis: Dict, q_codes: List[str], count: int = 1, 
                                             genres: List[str] = None, min_score: float = 0.4, 
                                             max_sitelinks: int = 20, poet_birth_year: Optional[int] = None,
                                             poet_death_year: Optional[int] = None, enable_vision_analysis: bool = True,
                                             vision_candidate_limit: int = 6) -> List[Tuple[Dict, float]]:
        """
        Fetch visual artwork matching specific subjects/themes and score them for quality.
        Uses progressive fallback with scoring: try scoring first, then fall back to un-scored matches.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            q_codes: List of Wikidata Q-codes for subjects to match
            count: Number of artworks to fetch
            genres: Optional list of genre Q-codes to filter by
            min_score: Minimum match quality score (0.0-1.0)
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            poet_birth_year: Optional year poet was born (for era matching)
            poet_death_year: Optional year poet died (for era matching)
            
        Returns:
            List of tuples (artwork_dict, score) sorted by score descending
        """
        if not q_codes:
            print("No Q-codes provided for subject-based search")
            return []
        
        print(f"Searching for artwork matching subjects: {q_codes}")
        if genres:
            print(f"With genre filtering: {genres}")
        print(f"Minimum match score: {min_score}")
        
        # Initialize analyzer
        if not POEM_ANALYZER_AVAILABLE:
            print("⚠️ Poem analyzer not available, using un-scored artwork")
            # Fall back to regular artwork fetch without scoring
            artwork = self.fetch_artwork_by_subject(q_codes, count, genres, max_sitelinks=max_sitelinks)
            return [(art, 0.5) for art in artwork]  # Give neutral score
        
        analyzer = poem_analyzer.PoemAnalyzer()
        
        # Progressive fallback with scoring
        fallback_strategies = [
            {
                "name": "direct depicts matches",
                "artwork_types": ["Q3305213", "Q125191", "Q860861"],  # paintings, photos, sculptures
                "max_sitelinks": max_sitelinks,
                "min_score": min_score,
                "use_direct_depicts": True,  # NEW: Use direct depicts query
                "depicts_bonus": 0.5  # NEW: Bonus for direct depicts matches
            },
            {
                "name": "scored specific artwork",
                "artwork_types": ["Q3305213", "Q125191", "Q860861"],  # paintings, photos, sculptures
                "max_sitelinks": max_sitelinks,
                "min_score": min_score,
                "use_direct_depicts": False,
                "depicts_bonus": 0.0
            },
            {
                "name": "scored broader artwork",
                "artwork_types": ["Q3305213", "Q125191", "Q860861", "Q42973", "Q93184", "Q11661"],  # + drawings, prints, murals
                "max_sitelinks": max_sitelinks + 10,
                "min_score": min_score * 0.8,  # Lower threshold
                "use_direct_depicts": False,
                "depicts_bonus": 0.0
            },
            {
                "name": "un-scored artwork",
                "artwork_types": ["Q3305213", "Q125191", "Q860861", "Q42973", "Q93184", "Q11661", "Q11060274", "Q1044167"],
                "max_sitelinks": max_sitelinks + 20,
                "min_score": 0.0,  # Accept any artwork
                "use_direct_depicts": False,
                "depicts_bonus": 0.0
            }
        ]
        
        for strategy in fallback_strategies:
            print(f"🎨 Trying {strategy['name']}...")
            
            try:
                # Fetch artwork with current strategy
                if strategy.get("use_direct_depicts", False):
                    # Use direct depicts query for more targeted matching
                    raw_data = self.queries.query_artwork_by_direct_depicts(
                        q_codes=q_codes,
                        limit=count * 10,  # Fetch more for better selection
                        offset=0,
                        random_order=True,
                        genres=genres,
                        max_sitelinks=strategy["max_sitelinks"],
                        artwork_types=strategy["artwork_types"]
                    )
                else:
                    # Use regular subject query
                    raw_data = self.query_artwork_by_subject(
                        q_codes=q_codes,
                        limit=count * 10,  # Fetch more for better selection
                        offset=0,
                        random_order=True,
                        genres=genres,
                        max_sitelinks=strategy["max_sitelinks"],
                        artwork_types=strategy["artwork_types"]
                    )
                
                if not raw_data:
                    print(f"⚠️ No results with {strategy['name']}, trying next strategy...")
                    continue
                
                # Process and score each artwork using parallel processing with selective vision analysis
                scored_artwork = self._score_and_filter_artwork_parallel(
                    raw_data, strategy, poem_analysis, genres, (poet_birth_year, poet_death_year), analyzer, enable_vision_analysis,
                    selective_vision=True, vision_candidate_limit=vision_candidate_limit
                )
                
                if scored_artwork:
                    print(f"✅ Found {len(scored_artwork)} artworks with {strategy['name']}")
                    return scored_artwork[:count]
                else:
                    print(f"⚠️ No scored results with {strategy['name']}, trying next strategy...")
                
            except Exception as e:
                print(f"❌ Error with {strategy['name']}: {e}")
                continue
        
        print("❌ All scoring strategies failed, falling back to random artwork")
        # Final fallback to random artwork
        random_artwork = self.fetch_paintings(count=count, max_sitelinks=max_sitelinks)
        return [(art, 0.3) for art in random_artwork]  # Give low score for random
    
    def _score_and_filter_artwork_parallel(self, raw_data: List[Dict], strategy: Dict, poem_analysis: Dict, 
                                          genres: List[str], poet_years: Tuple[Optional[int], Optional[int]], 
                                          analyzer, enable_vision_analysis: bool = False, max_workers: int = 4, 
                                          selective_vision: bool = True, vision_candidate_limit: int = 6) -> List[Tuple[Dict, float]]:
        """
        Process and score artwork from raw data using parallel processing.
        
        Args:
            raw_data: List of raw Wikidata query results
            strategy: Strategy dict with min_score and other parameters
            poem_analysis: Poem analysis results for scoring
            genres: List of genre Q-codes to filter by
            poet_years: Tuple of (poet_birth_year, poet_death_year)
            analyzer: PoemAnalyzer instance for scoring
            enable_vision_analysis: Whether to enable vision analysis
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of tuples (artwork_entry, score) sorted by score descending
        """
        scored_artwork = []
        
        def process_single_artwork(item, enable_vision_for_this_item=False):
            """Process a single artwork item."""
            try:
                # Extract fields from raw data
                fields = self._extract_artwork_fields_from_raw(item)
                if not fields:
                    return None
                
                # Build artwork entry from fields
                artwork_entry = self._build_artwork_entry_from_fields(fields, fields['wikidata_url'], enable_vision_analysis=enable_vision_for_this_item)
                if not artwork_entry:
                    return None
                
                # Score the artwork using the analyzer with era information
                poet_birth_year, poet_death_year = poet_years
                score = analyzer.score_artwork_match(
                    poem_analysis, 
                    artwork_entry["subject_q_codes"], 
                    artwork_entry["genre_q_codes"],
                    artwork_year=artwork_entry.get('year'),
                    poet_birth_year=poet_birth_year,
                    poet_death_year=poet_death_year
                )
                
                # Apply depicts bonus for direct depicts matches
                depicts_bonus = strategy.get("depicts_bonus", 0.0)
                if depicts_bonus > 0:
                    score += depicts_bonus
                    score = min(score, 1.0)  # Cap at 1.0
                
                # Only return artwork that meets minimum score
                if score >= strategy["min_score"]:
                    bonus_text = f" (+{depicts_bonus:.1f} depicts bonus)" if depicts_bonus > 0 else ""
                    vision_text = " [vision analyzed]" if enable_vision_for_this_item else ""
                    print(f"Scored: {artwork_entry['title']} by {artwork_entry['artist']} (score: {score:.2f}{bonus_text}{vision_text})")
                    return (artwork_entry, score)
                
                return None
                
            except Exception as e:
                print(f"Error processing artwork data: {e}")
                return None
        
        # Implement selective vision analysis strategy
        if enable_vision_analysis and selective_vision and self.vision_analyzer and self.vision_analyzer.is_enabled():
            print(f"🎯 Selective vision analysis: First pass without vision, then analyze top {vision_candidate_limit} candidates")
            
            # First pass: Process all artworks without vision analysis
            print(f"🔄 First pass: Processing {len(raw_data)} artworks without vision analysis...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_item = {executor.submit(process_single_artwork, item, False): item for item in raw_data}
                
                for future in concurrent.futures.as_completed(future_to_item):
                    result = future.result()
                    if result is not None:
                        scored_artwork.append(result)
            
            # Sort by score descending
            scored_artwork.sort(reverse=True, key=lambda x: x[1])
            
            # Second pass: Apply vision analysis to top candidates
            if len(scored_artwork) > 0:
                top_candidates = scored_artwork[:min(vision_candidate_limit, len(scored_artwork))]
                print(f"🔍 Second pass: Applying vision analysis to top {len(top_candidates)} candidates...")
                
                # Re-process top candidates with vision analysis
                vision_enhanced_candidates = []
                for artwork_entry, original_score in top_candidates:
                    # Find the original raw data for this artwork
                    original_item = None
                    for item in raw_data:
                        if self._extract_artwork_fields_from_raw(item) and self._extract_artwork_fields_from_raw(item).get('title') == artwork_entry['title']:
                            original_item = item
                            break
                    
                    if original_item:
                        # Re-process with vision analysis
                        fields = self._extract_artwork_fields_from_raw(original_item)
                        if fields:
                            enhanced_entry = self._build_artwork_entry_from_fields(fields, fields['wikidata_url'], enable_vision_analysis=True)
                            if enhanced_entry:
                                # Re-score with vision analysis
                                poet_birth_year, poet_death_year = poet_years
                                enhanced_score = analyzer.score_artwork_match(
                                    poem_analysis, 
                                    enhanced_entry["subject_q_codes"], 
                                    enhanced_entry["genre_q_codes"],
                                    artwork_year=enhanced_entry.get('year'),
                                    poet_birth_year=poet_birth_year,
                                    poet_death_year=poet_death_year
                                )
                                
                                # Apply depicts bonus
                                depicts_bonus = strategy.get("depicts_bonus", 0.0)
                                if depicts_bonus > 0:
                                    enhanced_score += depicts_bonus
                                    enhanced_score = min(enhanced_score, 1.0)
                                
                                vision_enhanced_candidates.append((enhanced_entry, enhanced_score))
                                print(f"🎨 Vision-enhanced: {enhanced_entry['title']} (score: {enhanced_score:.2f})")
                
                # Replace top candidates with vision-enhanced versions
                if vision_enhanced_candidates:
                    scored_artwork = vision_enhanced_candidates + scored_artwork[len(top_candidates):]
                    scored_artwork.sort(reverse=True, key=lambda x: x[1])
                    print(f"✅ Vision analysis applied to {len(vision_enhanced_candidates)} top candidates")
        
        else:
            # Standard processing (all artworks with or without vision analysis)
            vision_enabled = enable_vision_analysis and self.vision_analyzer and self.vision_analyzer.is_enabled()
            vision_text = "with vision analysis" if vision_enabled else "without vision analysis"
            print(f"🔄 Processing {len(raw_data)} artworks in parallel (max {max_workers} workers) {vision_text}...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_item = {executor.submit(process_single_artwork, item, vision_enabled): item for item in raw_data}
                
                for future in concurrent.futures.as_completed(future_to_item):
                    result = future.result()
                    if result is not None:
                        scored_artwork.append(result)
            
            # Sort by score descending
            scored_artwork.sort(reverse=True, key=lambda x: x[1])
        
        return scored_artwork

    def _score_and_filter_artwork(self, raw_data: List[Dict], strategy: Dict, poem_analysis: Dict, 
                                 genres: List[str], poet_years: Tuple[Optional[int], Optional[int]], 
                                 analyzer, enable_vision_analysis: bool = False) -> List[Tuple[Dict, float]]:
        """
        Process and score artwork from raw data using the given strategy.
        
        Args:
            raw_data: List of raw Wikidata query results
            strategy: Strategy dict with min_score and other parameters
            poem_analysis: Poem analysis results for scoring
            genres: List of genre Q-codes to filter by
            poet_years: Tuple of (poet_birth_year, poet_death_year)
            analyzer: PoemAnalyzer instance for scoring
            
        Returns:
            List of tuples (artwork_entry, score) sorted by score descending
        """
        scored_artwork = []
        poet_birth_year, poet_death_year = poet_years
        
        for item in raw_data:
            try:
                # Extract fields from raw data
                fields = self._extract_artwork_fields_from_raw(item)
                if not fields:
                    continue
                
                # Build artwork entry from fields
                artwork_entry = self._build_artwork_entry_from_fields(fields, fields['wikidata_url'], enable_vision_analysis=enable_vision_analysis)
                if not artwork_entry:
                    continue
                
                # Score the artwork using the analyzer with era information
                score = analyzer.score_artwork_match(
                    poem_analysis, 
                    artwork_entry["subject_q_codes"], 
                    artwork_entry["genre_q_codes"],
                    artwork_year=artwork_entry.get('year'),
                    poet_birth_year=poet_birth_year,
                    poet_death_year=poet_death_year
                )
                
                # Apply depicts bonus for direct depicts matches
                depicts_bonus = strategy.get("depicts_bonus", 0.0)
                if depicts_bonus > 0:
                    score += depicts_bonus
                    score = min(score, 1.0)  # Cap at 1.0
                
                # Only include artwork that meets minimum score
                if score >= strategy["min_score"]:
                    scored_artwork.append((artwork_entry, score))
                    bonus_text = f" (+{depicts_bonus:.1f} depicts bonus)" if depicts_bonus > 0 else ""
                    print(f"Scored: {artwork_entry['title']} by {artwork_entry['artist']} (score: {score:.2f}{bonus_text})")
                
                # Add delay to be respectful to APIs
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing artwork data: {e}")
                continue
        
        # Sort by score descending
        scored_artwork.sort(reverse=True, key=lambda x: x[1])
        
        return scored_artwork
    
    def _extract_artwork_fields_from_raw(self, raw_item: Dict) -> Optional[Dict]:
        """
        Extract artwork fields from raw Wikidata query result.
        
        Args:
            raw_item: Raw item from Wikidata query result
            
        Returns:
            Dict with extracted fields or None if validation fails
        """
        # Get Wikidata URL and image first
        wikidata_url = raw_item.get('artwork', {}).get('value', '')
        image_url = raw_item.get('image', {}).get('value', '')
        sitelinks = raw_item.get('sitelinks', {}).get('value', '0')
        subject = raw_item.get('subject', {}).get('value', '')
        genre = raw_item.get('genre', {}).get('value', '')
        artwork_type = raw_item.get('artworkType', {}).get('value', '')
        
        # Validate required fields
        if not wikidata_url or not image_url:
            return None
        
        return {
            'wikidata_url': wikidata_url,
            'image_url': image_url,
            'sitelinks': sitelinks,
            'subject': subject,
            'genre': genre,
            'artwork_type': artwork_type
        }

    def _build_artwork_entry_from_fields(self, fields: Dict, wikidata_url: str, enable_vision_analysis: bool = True) -> Optional[Dict]:
        """
        Build complete artwork entry from extracted fields.
        
        Args:
            fields: Dict with extracted artwork fields
            wikidata_url: Wikidata URL for the artwork
            enable_vision_analysis: Whether to perform vision analysis on the artwork image
            
        Returns:
            Complete artwork entry dict or None if validation fails
        """
        # Get labels using a separate, simple query
        labels = self.get_painting_labels(wikidata_url)
        title = labels.get('title', 'Unknown Title')
        artist = labels.get('artist', 'Unknown Artist')
        
        # Skip if we don't have basic info
        if title == 'Unknown Title' or artist == 'Unknown Artist':
            return None
        
        # Process image URL
        image_url = fields['image_url']
        if image_url:
            image_url = self.get_high_res_image_url(image_url)
        
        # Determine medium based on artwork type
        medium = self._get_medium_from_type(fields['artwork_type'])
        
        # Get artwork inception date (year)
        artwork_year = self.get_artwork_inception_date(wikidata_url)
        
        # Build preliminary artwork entry to check metadata quality
        preliminary_entry = {
            'title': title,
            'artist': artist,
            'subject_q_codes': fields.get('subject_q_codes', []),
            'genre_q_codes': fields.get('genre_q_codes', []),
            'depicts': fields.get('depicts', []),
            'style': fields.get('style', ''),
            'medium': medium,
            'year': artwork_year
        }
        
        # Perform vision analysis if enabled and vision analyzer is available
        vision_analysis = None
        vision_q_codes = []
        if enable_vision_analysis and self.vision_analyzer and self.vision_analyzer.is_enabled() and image_url:
            # Check if we should skip vision analysis due to good metadata
            if self.vision_analyzer.should_skip_vision_analysis(preliminary_entry):
                print(f"⏭️ Skipping vision analysis for {title} (good metadata available)")
            else:
                try:
                    print(f"🔍 Analyzing artwork image: {title}")
                    vision_analysis = self.vision_analyzer.analyze_artwork_image(image_url, title)
                    
                    if vision_analysis.get("success"):
                        # Extract Q-codes from vision analysis
                        vision_q_codes = self.vision_analyzer.extract_q_codes_from_vision_analysis(vision_analysis)
                        print(f"🎨 Vision analysis completed for {title}: {len(vision_q_codes)} Q-codes extracted")
                    else:
                        print(f"⚠️ Vision analysis failed for {title}: {vision_analysis.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Error during vision analysis for {title}: {e}")
                    vision_analysis = None
        
        # Create artwork entry
        artwork_entry = {
            "title": self.clean_text(title),
            "artist": self.clean_text(artist),
            "image": image_url,
            "year": artwork_year,
            "style": "Classical",
            "museum": "Unknown Location",
            "origin": "Unknown",
            "medium": medium,
            "dimensions": "Unknown dimensions",
            "wikidata": wikidata_url,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sitelinks": int(fields['sitelinks']),
            "subject_q_codes": [fields['subject']] if fields['subject'] else [],
            "genre_q_codes": [fields['genre']] if fields['genre'] else [],
            "artwork_type": fields['artwork_type'],
            "vision_analysis": vision_analysis,
            "vision_q_codes": vision_q_codes
        }
        
        return artwork_entry

    def _get_medium_from_type(self, artwork_type: str) -> str:
        """Get appropriate medium description from artwork type Q-code."""
        if wikidata_config:
            return wikidata_config.MEDIUM_MAPPINGS.get(artwork_type, "Mixed media")
        else:
            # Fallback mapping
            medium_mapping = {
                "Q3305213": "Oil on canvas",  # painting
                "Q125191": "Photograph",       # photograph
                "Q860861": "Marble sculpture", # sculpture
                "Q42973": "Pencil on paper",   # drawing
                "Q93184": "Print",            # print
                "Q11661": "Mural",            # mural
                "Q11060274": "Digital art",    # digital art
                "Q1044167": "Illustration"    # illustration
            }
            return medium_mapping.get(artwork_type, "Mixed media")
    
    def get_vision_analyzer_stats(self) -> Dict:
        """Get vision analyzer cache statistics."""
        if self.vision_analyzer:
            return self.vision_analyzer.get_cache_stats()
        else:
            return {
                "total_entries": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
                "total_tokens_used": 0,
                "cache_hit_rate": "N/A"
            }
    
    def clear_vision_analyzer_cache(self):
        """Clear the vision analyzer cache."""
        if self.vision_analyzer:
            self.vision_analyzer.clear_cache()
        else:
            print("⚠️ Vision analyzer not available")
    
    def is_vision_analysis_enabled(self) -> bool:
        """Check if vision analysis is enabled."""
        return self.vision_analyzer is not None and self.vision_analyzer.is_enabled()

    def get_daily_painting(self, max_sitelinks: int = 20) -> Dict:
        """
        Get a single random painting for daily use.
        Returns a dictionary with painting data or None if no painting found.
        """
        try:
            # Get a random offset to ensure different results each time
            import random
            random_offset = random.randint(0, 1000)
            
            # Query to get multiple paintings and pick one randomly
            sparql_query = f"""
            SELECT ?painting ?image ?paintingLabel ?artistLabel ?sitelinks WHERE {{
              ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
              ?painting wdt:P18 ?image .        # Has image
              ?painting wikibase:sitelinks ?sitelinks .  # Wikipedia sitelinks count
              ?painting rdfs:label ?paintingLabel .
              ?painting wdt:P170 ?artist .
              ?artist rdfs:label ?artistLabel .
              FILTER(LANG(?paintingLabel) = "en")
              FILTER(LANG(?artistLabel) = "en")
              FILTER(?sitelinks < {max_sitelinks})
            }}
            LIMIT 10
            OFFSET {random_offset}
            """
            
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=15  # Shorter timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                
                if results:
                    # Randomly select one painting from the results
                    item = random.choice(results)
                    
                    # Process the result
                    title = item.get('paintingLabel', {}).get('value', 'Unknown Title')
                    artist = item.get('artistLabel', {}).get('value', 'Unknown Artist')
                    image_url = item.get('image', {}).get('value', '')
                    wikidata_url = item.get('painting', {}).get('value', '')
                    
                    if image_url:
                        image_url = self.get_high_res_image_url(image_url)
                    
                    # Create painting entry
                    painting_entry = {
                        "title": self.clean_text(title),
                        "artist": self.clean_text(artist),
                        "image": image_url,
                        "year": None,
                        "style": "Classical",
                        "museum": "Unknown Location",
                        "origin": "Unknown",
                        "medium": "Oil on canvas",
                        "dimensions": "Unknown dimensions",
                        "wikidata": wikidata_url,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    return painting_entry
        except Exception as e:
            print(f"Error fetching daily painting: {e}")
            return None

    def save_to_json(self, paintings: List[Dict], filename: str = "new_paintings.json"):
        """
        Save the paintings data to a JSON file.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(paintings, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(paintings)} paintings to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def append_to_existing_json(self, paintings: List[Dict], filename: str = "paintings_database.json"):
        """
        Append new paintings to existing JSON file, avoiding duplicates.
        """
        try:
            # Load existing data
            existing_paintings = []
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_paintings = json.load(f)
            except FileNotFoundError:
                print(f"File {filename} not found. Creating new file.")
            
            # Get existing titles to avoid duplicates
            existing_titles = {p.get('title', '').lower() for p in existing_paintings}
            
            # Filter out duplicates
            new_paintings = [p for p in paintings if p.get('title', '').lower() not in existing_titles]
            
            if new_paintings:
                # Append new paintings
                all_paintings = existing_paintings + new_paintings
                
                # Save back to file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_paintings, f, indent=2, ensure_ascii=False)
                
                print(f"Added {len(new_paintings)} new paintings to {filename}")
                print(f"Total paintings in database: {len(all_paintings)}")
            else:
                print("No new paintings to add (all were duplicates).")
                
        except Exception as e:
            print(f"Error appending to JSON: {e}")


# CLI entry point moved to daily_culture_bot.py
# Use: python daily_culture_bot.py
