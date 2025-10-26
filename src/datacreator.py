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

# Import poem_analyzer for scoring system
try:
    from . import poem_analyzer
    POEM_ANALYZER_AVAILABLE = True
except ImportError:
    # Fallback for when running as standalone module
    try:
        import poem_analyzer
        POEM_ANALYZER_AVAILABLE = True
    except ImportError:
        POEM_ANALYZER_AVAILABLE = False


class PaintingDataCreator:
    def __init__(self):
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self.commons_api = "https://commons.wikimedia.org/w/api.php"
        
        # Create a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PaintingDataCreator/1.0 (https://github.com/ugurelveren/daily-painting-bot)'
        })
        
        # Style mappings for better categorization
        self.style_mappings = {
            "Q4692": "Renaissance",
            "Q20826540": "Early Renaissance", 
            "Q131808": "High Renaissance",
            "Q37853": "Baroque",
            "Q40415": "Neoclassicism",
            "Q7547": "Romanticism",
            "Q40834": "Realism", 
            "Q40857": "Impressionism",
            "Q42489": "Post-Impressionism",
            "Q9415": "Modernism",
            "Q34636": "Expressionism",
            "Q39428": "Surrealism",
            "Q5090": "Cubism",
            "Q186030": "Abstract Expressionism",
            "Q5415": "Pop art",
            "Q2458": "Fauvism",
            "Q12124693": "Regionalism"
        }

    def query_paintings_by_subject(self, q_codes: List[str], limit: int = 50, offset: int = 0, random_order: bool = True, genres: List[str] = None, max_sitelinks: int = 20) -> List[Dict]:
        """
        Query Wikidata for paintings matching specific subjects/themes and genres.
        
        Args:
            q_codes: List of Wikidata Q-codes for subjects to match
            limit: Number of results to return
            offset: Offset for pagination
            random_order: Whether to randomize the order of results
            genres: Optional list of genre Q-codes to filter by
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            
        Returns:
            List of raw Wikidata results
        """
        if not q_codes:
            return []
        
        # Create Q-code filter clause
        q_code_filters = " || ".join([f"?subject = wd:{q_code}" for q_code in q_codes])
        
        # Add genre filtering if provided
        genre_filter = ""
        if genres:
            genre_filters = " || ".join([f"?genre = wd:{genre}" for genre in genres])
            genre_filter = f"""UNION {{
            ?painting wdt:P136 ?genre .   # genre
            FILTER({genre_filters})
          }}"""
        
        # Choose ordering
        if random_order:
            order_clause = "ORDER BY RAND()"
        else:
            order_clause = "ORDER BY DESC(?year)"
        
        sparql_query = f"""
        SELECT ?painting ?image ?sitelinks ?subject ?genre WHERE {{
          ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
          ?painting wdt:P18 ?image .        # Has image
          ?painting wikibase:sitelinks ?sitelinks .  # Wikipedia sitelinks count
          
          # Filter out paintings with excessive Wikipedia coverage (fame filter)
          FILTER(?sitelinks < {max_sitelinks})
          
          # Match by subject/depicts properties
          {{
            ?painting wdt:P180 ?subject .    # depicts
            FILTER({q_code_filters})
          }} UNION {{
            ?painting wdt:P921 ?subject .   # main subject
            FILTER({q_code_filters})
          }}{genre_filter}
          
          # Get genre information
          OPTIONAL {{ ?painting wdt:P136 ?genre . }}
        }}
        {order_clause}
        LIMIT {limit}
        OFFSET {offset}
        """
        
        try:
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data['results']['bindings']
            
        except requests.RequestException as e:
            print(f"Error querying Wikidata for subjects: {e}")
            return []

    def query_wikidata_paintings(self, limit: int = 50, offset: int = 0, filter_type: str = "both", random_order: bool = False, max_sitelinks: int = 20) -> List[Dict]:
        """
        Query Wikidata for paintings with detailed information.
        
        Args:
            limit: Number of results to return
            offset: Offset for pagination
            filter_type: "license", "age", or "both"
            random_order: Whether to randomize the order of results
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
        """
        
        if filter_type == "license":
            # Pure license-based filter
            filter_clause = """
            # Get copyright and license information
            OPTIONAL { ?painting wdt:P6216 ?copyright }  # Copyright status of the work
            OPTIONAL { ?image wdt:P275 ?license }        # License of the image file
            
            # PURE LICENSE FILTER - Only explicit public domain or compatible licenses
            FILTER(
              # Explicit public domain status
              ?copyright = wd:Q19652 ||                     # Public domain
              ?copyright = wd:Q15687061 ||                  # Public domain in the United States
              ?copyright = wd:Q19652668 ||                  # Public domain due to expiration
              
              # Creative Commons licenses (open/compatible)
              ?license = wd:Q6938433 ||                     # CC0 (public domain dedication)
              ?license = wd:Q14947546 ||                    # CC BY (attribution required)
              ?license = wd:Q18199165 ||                    # CC BY-SA (attribution + share-alike)
              ?license = wd:Q19113751 ||                    # CC BY 2.0
              ?license = wd:Q18810333 ||                    # CC BY 3.0
              ?license = wd:Q20007257 ||                    # CC BY 4.0
              ?license = wd:Q27016754 ||                    # CC BY-SA 2.0
              ?license = wd:Q14946043 ||                    # CC BY-SA 3.0
              ?license = wd:Q18810341                       # CC BY-SA 4.0
            )
            """
            
        elif filter_type == "age":
            # Simplified age-based filter
            filter_clause = """
            # Artist death date filter for public domain (died before 1953 for 70+ year rule)
            ?artist wdt:P570 ?deathDate .
            FILTER(YEAR(?deathDate) < 1953)
            """
            
        else:  # filter_type == "both"
            # Minimal filter - just paintings with images
            filter_clause = """
            # Just ensure we have paintings with images
            """

        # Choose ordering - random or by year
        if random_order:
            order_clause = "ORDER BY RAND()"
        else:
            order_clause = "ORDER BY DESC(?year)"

        sparql_query = f"""
        SELECT ?painting ?image ?sitelinks WHERE {{
          ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
          ?painting wdt:P18 ?image .        # Image
          ?painting wikibase:sitelinks ?sitelinks .  # Wikipedia sitelinks count
          
          # Filter out paintings with excessive Wikipedia coverage (fame filter)
          FILTER(?sitelinks < {max_sitelinks})
          
          {filter_clause}
        }}
        {order_clause}
        LIMIT {limit}
        OFFSET {offset}
        """
        
        try:
            response = self.session.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                timeout=30  # Reduced from 60 to 30 seconds for faster fallback
            )
            response.raise_for_status()
            
            data = response.json()
            return data['results']['bindings']
            
        except requests.RequestException as e:
            print(f"Error querying Wikidata: {e}")
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
                
                # Use default values for other fields
                year = None
                style = "Classical"
                museum = "Unknown Location"
                origin = "Unknown"
                medium = "Oil on canvas"
                dimensions = "Unknown dimensions"
                
                # Skip fun facts - not needed
                
                # Create the painting entry
                painting_entry = {
                    "title": self.clean_text(title),
                    "artist": self.clean_text(artist),
                    "image": image_url,
                    "year": year,
                    "style": self.clean_text(style),
                    "museum": self.clean_text(museum),
                    "origin": self.clean_text(origin),
                    "medium": self.clean_text(medium),
                    "dimensions": self.clean_text(dimensions),
                    "wikidata": wikidata_url,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                processed_paintings.append(painting_entry)
                print(f"Processed: {title} by {artist}")
                
                # Add a longer delay to be respectful to the APIs
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing painting data: {e}")
                continue
        
        return processed_paintings

    def create_sample_paintings(self, count: int = 5) -> List[Dict]:
        """
        Create sample paintings for testing when Wikidata is not accessible.
        """
        sample_paintings = [
            {
                "title": "The Great Wave off Kanagawa",
                "artist": "Katsushika Hokusai",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/800px-The_Great_Wave_off_Kanagawa.jpg",
                "year": 1831,
                "style": "Ukiyo-e",
                "museum": "Metropolitan Museum of Art, New York",
                "origin": "Japan",
                "medium": "Polychrome woodblock print",
                "dimensions": "25.7 cm × 37.9 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q455354",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "The Kiss",
                "artist": "Gustav Klimt",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg/800px-The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
                "year": 1908,
                "style": "Art Nouveau",
                "museum": "Österreichische Galerie Belvedere, Vienna",
                "origin": "Austria",
                "medium": "Oil and gold leaf on canvas",
                "dimensions": "180 cm × 180 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q203533",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "A Sunday Afternoon on the Island of La Grande Jatte",
                "artist": "Georges Seurat",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg/800px-A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg",
                "year": 1886,
                "style": "Pointillism",
                "museum": "Art Institute of Chicago",
                "origin": "France",
                "medium": "Oil on canvas",
                "dimensions": "207.5 cm × 308.1 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q214316",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Las Meninas",
                "artist": "Diego Velázquez",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Las_Meninas%2C_by_Diego_Vel%C3%A1zquez%2C_from_Prado_in_Google_Earth.jpg/800px-Las_Meninas%2C_by_Diego_Vel%C3%A1zquez%2C_from_Prado_in_Google_Earth.jpg",
                "year": 1656,
                "style": "Baroque",
                "museum": "Museo del Prado, Madrid",
                "origin": "Spain",
                "medium": "Oil on canvas",
                "dimensions": "318 cm × 276 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q125110",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Water Lilies",
                "artist": "Claude Monet",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1919%2C_Mus%C3%A9e_Marmottan_Monet%2C_Paris.jpg/800px-Claude_Monet_-_Water_Lilies_-_1919%2C_Mus%C3%A9e_Marmottan_Monet%2C_Paris.jpg",
                "year": 1919,
                "style": "Impressionism",
                "museum": "Musée de l'Orangerie, Paris",
                "origin": "France",
                "medium": "Oil on canvas",
                "dimensions": "200 cm × 425 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q3012020",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        return sample_paintings[:count]

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

    def fetch_paintings_by_subject(self, q_codes: List[str], count: int = 1, genres: List[str] = None, use_sample_on_error: bool = True, max_sitelinks: int = 20) -> List[Dict]:
        """
        Fetch paintings matching specific subjects/themes and genres from Wikidata.
        
        Args:
            q_codes: List of Wikidata Q-codes for subjects to match
            count: Number of paintings to fetch
            genres: Optional list of genre Q-codes to filter by
            use_sample_on_error: Whether to use sample data if API fails
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            
        Returns:
            List of processed painting dictionaries
        """
        if not q_codes:
            print("No Q-codes provided for subject-based search")
            return []
        
        print(f"Searching for paintings matching subjects: {q_codes}")
        if genres:
            print(f"With genre filtering: {genres}")
        
        all_paintings = []
        batch_size = 10
        
        # Add random offset for variety
        max_offset = min(200, count * 3)  # Smaller range for subject-based search
        random_offset = random.randint(0, max_offset)
        print(f"Using random starting offset: {random_offset}")
        
        offset = random_offset
        max_retries = 2
        
        for retry in range(max_retries):
            try:
                while len(all_paintings) < count:
                    print(f"Fetching subject-based batch starting at offset {offset}...")
                    
                    raw_data = self.query_paintings_by_subject(
                        q_codes=q_codes,
                        limit=batch_size, 
                        offset=offset, 
                        random_order=True,
                        genres=genres,
                        max_sitelinks=max_sitelinks
                    )
                    
                    if not raw_data:
                        print("No more subject-based data available.")
                        break
                    
                    processed_batch = self.process_painting_data(raw_data)
                    all_paintings.extend(processed_batch)
                    
                    offset += batch_size
                    
                    # Shorter delay for subject-based queries
                    time.sleep(1)
                    
                    # Break if we've fetched enough
                    if len(processed_batch) < batch_size // 2:
                        break
                
                # If we got some paintings, break the retry loop
                if all_paintings:
                    break
                    
            except Exception as e:
                print(f"Subject-based search attempt {retry + 1} failed: {e}")
                if retry < max_retries - 1:
                    wait_time = retry + 1
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Return only the requested count
        return all_paintings[:count]

    def fetch_paintings_by_subject_with_scoring(self, poem_analysis: Dict, q_codes: List[str], count: int = 1, 
                                               genres: List[str] = None, min_score: float = 0.4, 
                                               max_sitelinks: int = 20) -> List[Tuple[Dict, float]]:
        """
        Fetch paintings matching specific subjects/themes and score them for quality.
        
        Args:
            poem_analysis: Dictionary containing poem analysis results
            q_codes: List of Wikidata Q-codes for subjects to match
            count: Number of paintings to fetch
            genres: Optional list of genre Q-codes to filter by
            min_score: Minimum match quality score (0.0-1.0)
            max_sitelinks: Maximum number of Wikipedia sitelinks (fame filter)
            
        Returns:
            List of tuples (painting_dict, score) sorted by score descending
        """
        if not q_codes:
            print("No Q-codes provided for subject-based search")
            return []
        
        print(f"Searching for paintings matching subjects: {q_codes}")
        if genres:
            print(f"With genre filtering: {genres}")
        print(f"Minimum match score: {min_score}")
        
        # Fetch larger batch to have more options for scoring
        batch_size = min(50, count * 10)  # Fetch 10x more than needed for better selection
        
        try:
            raw_data = self.query_paintings_by_subject(
                q_codes=q_codes,
                limit=batch_size, 
                offset=0, 
                random_order=True,
                genres=genres,
                max_sitelinks=max_sitelinks
            )
            
            if not raw_data:
                print("No subject-based data available.")
                return []
            
            # Initialize analyzer once outside the loop
            if not POEM_ANALYZER_AVAILABLE:
                print("⚠️ Poem analyzer not available, cannot score paintings")
                return []
            
            analyzer = poem_analyzer.PoemAnalyzer()
            
            # Process and score each painting
            scored_paintings = []
            
            for item in raw_data:
                try:
                    # Get Wikidata URL and image first
                    wikidata_url = item.get('painting', {}).get('value', '')
                    image_url = item.get('image', {}).get('value', '')
                    sitelinks = item.get('sitelinks', {}).get('value', '0')
                    subject = item.get('subject', {}).get('value', '')
                    genre = item.get('genre', {}).get('value', '')
                    
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
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "sitelinks": int(sitelinks),
                        "subject_q_codes": [subject] if subject else [],
                        "genre_q_codes": [genre] if genre else []
                    }
                    
                    # Score the painting using the analyzer (already initialized)
                    score = analyzer.score_artwork_match(
                        poem_analysis, 
                        painting_entry["subject_q_codes"], 
                        painting_entry["genre_q_codes"]
                    )
                    
                    # Only include paintings that meet minimum score
                    if score >= min_score:
                        scored_paintings.append((painting_entry, score))
                        print(f"Scored: {title} by {artist} (score: {score:.2f})")
                    
                    # Add delay to be respectful to APIs
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing painting data: {e}")
                    continue
            
            # Sort by score descending
            scored_paintings.sort(reverse=True, key=lambda x: x[1])
            
            print(f"Found {len(scored_paintings)} paintings with score >= {min_score}")
            
            # Return only the requested count
            return scored_paintings[:count]
            
        except Exception as e:
            print(f"Error in scored fetch: {e}")
            return []

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


def main():
    """
    Main function to demonstrate the data creator functionality.
    """
    creator = PaintingDataCreator()
    
    print("Daily Painting Bot - Data Creator")
    print("=" * 40)
    print("Using combined license+age filter with random selection...")
    
    # Get user input for number of paintings (default to 1 for daily use)
    try:
        count = int(input("How many paintings would you like to fetch? (default: 1): ") or "1")
    except ValueError:
        count = 1
    
    # Fetch paintings with optimal settings
    paintings = creator.fetch_paintings(count)  # Uses defaults: count=1, both filter, random order
    
    if paintings:
        print(f"\nSuccessfully fetched {len(paintings)} painting{'s' if len(paintings) != 1 else ''}!")
        
        # Ask user what to do with the data
        print("\nWhat would you like to do with the data?")
        print("1. Save to new file (new_paintings.json)")
        print("2. Append to existing paintings database")
        print("3. Both")
        
        choice = input("Enter choice (1-3, default: 2): ").strip() or "2"
        
        if choice in ["1", "3"]:
            creator.save_to_json(paintings, "new_paintings.json")
        
        if choice in ["2", "3"]:
            creator.append_to_existing_json(paintings)
        
        print("\nSample of fetched data:")
        for i, painting in enumerate(paintings[:3]):
            print(f"\n{i+1}. {painting['title']} by {painting['artist']} ({painting['year']})")
            print(f"   Style: {painting['style']}")
            print(f"   Museum: {painting['museum']}")
    
    else:
        print("No paintings were fetched. Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
