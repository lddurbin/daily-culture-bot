#!/usr/bin/env python3
"""
Artwork Processing Module for Daily Culture Bot

This module contains data processing methods for artwork information.
Extracted from datacreator.py to improve code organization and maintainability.
"""

import re
import time
from datetime import datetime
from typing import List, Dict, Optional


class ArtworkProcessor:
    """Handles processing and formatting of artwork data."""
    
    def __init__(self, wikidata_endpoint: str, session, wikipedia_api: str):
        """
        Initialize artwork processor.
        
        Args:
            wikidata_endpoint: Wikidata SPARQL endpoint URL
            session: Requests session for HTTP calls
            wikipedia_api: Wikipedia API endpoint URL
        """
        self.wikidata_endpoint = wikidata_endpoint
        self.session = session
        self.wikipedia_api = wikipedia_api
    
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
    
    def process_painting_data(self, raw_data: List[Dict], wikidata_queries) -> List[Dict]:
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
                
                # Fetch inception date from Wikidata
                try:
                    year = wikidata_queries.get_artwork_inception_date(wikidata_url)
                except Exception as e:
                    print(f"Error fetching inception date for {title}: {e}")
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
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Art_Project.jpg/800px-The_Kiss_-_Gustav_Klimt_-_Google_Art_Project.jpg",
                "year": 1908,
                "style": "Art Nouveau",
                "museum": "Belvedere Palace, Vienna",
                "origin": "Austria",
                "medium": "Oil and gold leaf on canvas",
                "dimensions": "180 cm × 180 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q123456",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "The Starry Night",
                "artist": "Vincent van Gogh",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/800px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
                "year": 1889,
                "style": "Post-Impressionism",
                "museum": "Museum of Modern Art, New York",
                "origin": "Netherlands",
                "medium": "Oil on canvas",
                "dimensions": "73.7 cm × 92.1 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q455354",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Girl with a Pearl Earring",
                "artist": "Johannes Vermeer",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg",
                "year": 1665,
                "style": "Dutch Golden Age",
                "museum": "Mauritshuis, The Hague",
                "origin": "Netherlands",
                "medium": "Oil on canvas",
                "dimensions": "44.5 cm × 39 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q123456",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "The Persistence of Memory",
                "artist": "Salvador Dalí",
                "image": "https://upload.wikimedia.org/wikipedia/en/thumb/d/dd/The_Persistence_of_Memory.jpg/800px-The_Persistence_of_Memory.jpg",
                "year": 1931,
                "style": "Surrealism",
                "museum": "Museum of Modern Art, New York",
                "origin": "Spain",
                "medium": "Oil on canvas",
                "dimensions": "24 cm × 33 cm",
                "wikidata": "https://www.wikidata.org/wiki/Q123456",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        return sample_paintings[:count]
