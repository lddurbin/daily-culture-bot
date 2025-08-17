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
from typing import List, Dict, Optional
import re


class PaintingDataCreator:
    def __init__(self):
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self.commons_api = "https://commons.wikimedia.org/w/api.php"
        
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

    def query_wikidata_paintings(self, limit: int = 50, offset: int = 0, filter_type: str = "both", random_order: bool = False) -> List[Dict]:
        """
        Query Wikidata for paintings with detailed information.
        
        Args:
            limit: Number of results to return
            offset: Offset for pagination
            filter_type: "license", "age", or "both"
            random_order: Whether to randomize the order of results
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
            # Age-based filter (traditional approach)
            filter_clause = """
            # Artist death date filter for public domain (died before 1953 for 70+ year rule)
            ?artist wdt:P570 ?deathDate .
            FILTER(YEAR(?deathDate) < 1953)
            
            # Additional filters for old paintings (pre-1900 for safety)
            OPTIONAL { ?painting wdt:P571 ?inception . BIND(YEAR(?inception) as ?year) }
            FILTER(!BOUND(?year) || ?year < 1900)
            
            # Exclude contemporary or potentially copyrighted works
            FILTER NOT EXISTS { ?painting wdt:P136 wd:Q5415 }  # Exclude Pop art
            FILTER NOT EXISTS { ?painting wdt:P136 wd:Q186030 } # Exclude Abstract Expressionism
            """
            
        else:  # filter_type == "both"
            # Combined filter - either license OR age criteria
            filter_clause = """
            # Get copyright and license information
            OPTIONAL { ?painting wdt:P6216 ?copyright }  # Copyright status of the work
            OPTIONAL { ?image wdt:P275 ?license }        # License of the image file
            OPTIONAL { ?artist wdt:P570 ?deathDate }     # Artist death date
            
            # COMBINED FILTER - Either explicit license OR age-based safety
            FILTER(
              # Option 1: Explicit public domain or compatible licenses
              ?copyright = wd:Q19652 ||                     # Public domain
              ?copyright = wd:Q15687061 ||                  # Public domain in the United States
              ?copyright = wd:Q19652668 ||                  # Public domain due to expiration
              ?license = wd:Q6938433 ||                     # CC0 (public domain dedication)
              ?license = wd:Q14947546 ||                    # CC BY (attribution required)
              ?license = wd:Q18199165 ||                    # CC BY-SA (attribution + share-alike)
              ?license = wd:Q19113751 ||                    # CC BY 2.0
              ?license = wd:Q18810333 ||                    # CC BY 3.0
              ?license = wd:Q20007257 ||                    # CC BY 4.0
              ?license = wd:Q27016754 ||                    # CC BY-SA 2.0
              ?license = wd:Q14946043 ||                    # CC BY-SA 3.0
              ?license = wd:Q18810341 ||                    # CC BY-SA 4.0
              
              # Option 2: Traditional age-based safety (artist died before 1953)
              (BOUND(?deathDate) && YEAR(?deathDate) < 1953)
            )
            """

        # Choose ordering - random or by year
        if random_order:
            order_clause = "ORDER BY RAND()"
        else:
            order_clause = "ORDER BY DESC(?year)"

        sparql_query = f"""
        SELECT DISTINCT ?painting ?paintingLabel ?artistLabel ?image ?year ?styleLabel 
               ?museumLabel ?originLabel ?mediumLabel ?copyrightLabel ?licenseLabel WHERE {{
          ?painting wdt:P31 wd:Q3305213 .  # Instance of painting
          ?painting wdt:P170 ?artist .      # Creator
          ?painting wdt:P18 ?image .        # Image
          
          {filter_clause}
          
          # Get optional metadata
          OPTIONAL {{ ?painting wdt:P571 ?inception . BIND(YEAR(?inception) as ?year) }}
          OPTIONAL {{ ?painting wdt:P136 ?style }}
          OPTIONAL {{ ?painting wdt:P276 ?museum }}
          OPTIONAL {{ ?painting wdt:P495 ?origin }}
          OPTIONAL {{ ?painting wdt:P186 ?medium }}
          
          # Quality filter - prefer works with institutional backing
          FILTER(BOUND(?museum) || BOUND(?copyright) || BOUND(?license))
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
        }}
        {order_clause}
        LIMIT {limit}
        OFFSET {offset}
        """
        
        headers = {
            'User-Agent': 'PaintingDataCreator/1.0 (https://github.com/ugurelveren/daily-painting-bot)'
        }
        
        try:
            response = requests.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                headers=headers,
                timeout=15
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
            
            headers = {
                'User-Agent': 'PaintingDataCreator/1.0 (https://github.com/ugurelveren/daily-painting-bot)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
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
            
        # Extract filename from URL
        filename_match = re.search(r'/([^/]+\.(jpg|jpeg|png|gif))$', commons_url, re.IGNORECASE)
        if not filename_match:
            return commons_url
            
        filename = filename_match.group(1)
        
        # Create a higher resolution URL (800px width)
        base_url = "https://upload.wikimedia.org/wikipedia/commons/thumb"
        # Get the first two characters for the directory structure
        md5_chars = filename[:2]
        return f"{base_url}/{md5_chars[0]}/{md5_chars}/{filename}/800px-{filename}"

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
            
            headers = {
                'User-Agent': 'PaintingDataCreator/1.0 (https://github.com/ugurelveren/daily-painting-bot)'
            }
            
            response = requests.get(
                self.wikidata_endpoint,
                params={'query': sparql_query, 'format': 'json'},
                headers=headers,
                timeout=10
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

    def process_painting_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Process raw Wikidata results into the format used by the daily painting bot.
        """
        processed_paintings = []
        
        for item in raw_data:
            try:
                # Extract basic information
                title = item.get('paintingLabel', {}).get('value', 'Unknown Title')
                artist = item.get('artistLabel', {}).get('value', 'Unknown Artist')
                
                # Skip if we don't have basic info
                if title == 'Unknown Title' or artist == 'Unknown Artist':
                    continue
                
                # Get image URL
                image_url = item.get('image', {}).get('value', '')
                if image_url:
                    image_url = self.get_high_res_image_url(image_url)
                
                # Get year
                year = item.get('year', {}).get('value')
                if year:
                    try:
                        year = int(year)
                    except ValueError:
                        year = None
                
                # Get style
                style = item.get('styleLabel', {}).get('value', 'Unknown')
                
                # Get museum
                museum = item.get('museumLabel', {}).get('value', 'Unknown Location')
                
                # Get origin
                origin = item.get('originLabel', {}).get('value', 'Unknown')
                
                # Get medium
                medium = item.get('mediumLabel', {}).get('value', 'Unknown medium')
                
                # Get Wikidata URL
                wikidata_url = item.get('painting', {}).get('value', '')
                
                # Get dimensions
                dimensions = self.get_painting_dimensions(wikidata_url)
                if not dimensions:
                    dimensions = "Unknown dimensions"
                
                # Get or generate a fact
                fact = self.get_wikipedia_summary(title)
                if not fact:
                    fact = f"A {style.lower()} painting by {artist}."
                
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
                    "fact": self.clean_text(fact),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                processed_paintings.append(painting_entry)
                print(f"Processed: {title} by {artist}")
                
                # Add a small delay to be respectful to the APIs
                time.sleep(0.5)
                
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
                "fact": "One of the most recognizable works of Japanese art in the world.",
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
                "fact": "Created during Klimt's 'Golden Period' when he used gold leaf extensively.",
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
                "fact": "Painted using pointillism technique with tiny dots of color.",
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
                "fact": "Shows Velázquez himself painting a portrait of the Spanish royal family.",
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
                "fact": "Part of a series of approximately 250 oil paintings by Monet.",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        return sample_paintings[:count]

    def fetch_paintings(self, count: int = 1, filter_type: str = "both", random_order: bool = True, 
                       use_sample_on_error: bool = True) -> List[Dict]:
        """
        Fetch and process painting data from Wikidata, fallback to sample data if needed.
        
        Args:
            count: Number of paintings to fetch
            filter_type: "license", "age", or "both"
            random_order: Whether to randomize the order of results
            use_sample_on_error: Whether to use sample data if API fails
        """
        filter_desc = {"license": "license-based", "age": "age-based", "both": "combined license+age"}
        order_desc = "random order" if random_order else "chronological order"
        print(f"Fetching {count} paintings from Wikidata using {filter_desc[filter_type]} filter in {order_desc}...")
        
        all_paintings = []
        batch_size = 50
        
        # Add random offset for extra variety when using random order
        if random_order:
            max_offset = min(500, count * 5)  # Reasonable random range
            random_offset = random.randint(0, max_offset)
            print(f"Using random starting offset: {random_offset}")
        else:
            random_offset = 0
        
        offset = random_offset
        max_retries = 2
        
        for retry in range(max_retries):
            try:
                while len(all_paintings) < count:
                    print(f"Fetching batch starting at offset {offset}...")
                    
                    raw_data = self.query_wikidata_paintings(
                        limit=batch_size, 
                        offset=offset, 
                        filter_type=filter_type,
                        random_order=random_order
                    )
                    
                    if not raw_data:
                        print("No more data available.")
                        break
                    
                    processed_batch = self.process_painting_data(raw_data)
                    all_paintings.extend(processed_batch)
                    
                    offset += batch_size
                    
                    # Add delay between batches
                    time.sleep(1)
                    
                    # Break if we've fetched enough
                    if len(processed_batch) < batch_size // 2:  # Less data means we're near the end
                        break
                
                # If we got some paintings, break the retry loop
                if all_paintings:
                    break
                    
            except Exception as e:
                print(f"Attempt {retry + 1} failed: {e}")
                if retry < max_retries - 1:
                    print("Retrying...")
                    time.sleep(2)
        
        # Fallback to sample data if no paintings were fetched and user allows it
        if not all_paintings and use_sample_on_error:
            print("Could not fetch from Wikidata. Using sample paintings...")
            all_paintings = self.create_sample_paintings(count)
        
        # Return only the requested count
        return all_paintings[:count]

    def get_daily_painting(self) -> Dict:
        """
        Get a single random painting for daily use.
        Returns a dictionary with painting data or None if no painting found.
        """
        paintings = self.fetch_paintings(count=1)
        return paintings[0] if paintings else None

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
            print(f"   Fact: {painting['fact'][:100]}...")
    
    else:
        print("No paintings were fetched. Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
