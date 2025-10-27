#!/usr/bin/env python3
"""
Poem Fetcher for Daily Culture Bot

This module fetches random public domain poems from PoetryDB API.
It provides functionality to get poems and format them for display.
"""

import requests
import json
import random
import re
from datetime import datetime
from typing import List, Dict, Optional


class PoemFetcher:
    def __init__(self, enable_poet_dates: bool = True):
        self.poetrydb_base_url = "https://poetrydb.org"
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DailyCultureBot/1.0 (https://github.com/yourusername/daily-culture-bot)'
        })
        # Cache for poet dates to avoid repeated API calls
        self.poet_date_cache = {
            # Pre-populate with common poets to avoid API calls
            # Include multiple name variations for each poet
            "Robert Frost": {"birth_year": 1874, "death_year": 1963},
            "William Shakespeare": {"birth_year": 1564, "death_year": 1616},
            "Shakespeare": {"birth_year": 1564, "death_year": 1616},
            "William Wordsworth": {"birth_year": 1770, "death_year": 1850},
            "Wordsworth": {"birth_year": 1770, "death_year": 1850},
            "Emily Dickinson": {"birth_year": 1830, "death_year": 1886},
            "Dickinson": {"birth_year": 1830, "death_year": 1886},
            "Walt Whitman": {"birth_year": 1819, "death_year": 1892},
            "Whitman": {"birth_year": 1819, "death_year": 1892},
            "Edgar Allan Poe": {"birth_year": 1809, "death_year": 1849},
            "Poe": {"birth_year": 1809, "death_year": 1849},
            "Maya Angelou": {"birth_year": 1928, "death_year": 2014},
            "Angelou": {"birth_year": 1928, "death_year": 2014},
            "Langston Hughes": {"birth_year": 1901, "death_year": 1967},
            "Hughes": {"birth_year": 1901, "death_year": 1967},
            "Sylvia Plath": {"birth_year": 1932, "death_year": 1963},
            "Plath": {"birth_year": 1932, "death_year": 1963},
            "T.S. Eliot": {"birth_year": 1888, "death_year": 1965},
            "Eliot": {"birth_year": 1888, "death_year": 1965},
            "Pablo Neruda": {"birth_year": 1904, "death_year": 1973},
            "Neruda": {"birth_year": 1904, "death_year": 1973},
            "Rumi": {"birth_year": 1207, "death_year": 1273},
            "Oscar Wilde": {"birth_year": 1854, "death_year": 1900},
            "Wilde": {"birth_year": 1854, "death_year": 1900},
            "John Keats": {"birth_year": 1795, "death_year": 1821},
            "Keats": {"birth_year": 1795, "death_year": 1821},
            "Percy Bysshe Shelley": {"birth_year": 1792, "death_year": 1822},
            "Shelley": {"birth_year": 1792, "death_year": 1822},
            "Lord Byron": {"birth_year": 1788, "death_year": 1824},
            "George Gordon, Lord Byron": {"birth_year": 1788, "death_year": 1824},
            "Byron": {"birth_year": 1788, "death_year": 1824},
            "Samuel Taylor Coleridge": {"birth_year": 1772, "death_year": 1834},
            "Coleridge": {"birth_year": 1772, "death_year": 1834},
            "William Blake": {"birth_year": 1757, "death_year": 1827},
            "Blake": {"birth_year": 1757, "death_year": 1827},
            "Robert Burns": {"birth_year": 1759, "death_year": 1796},
            "Burns": {"birth_year": 1759, "death_year": 1796},
            "Elizabeth Barrett Browning": {"birth_year": 1806, "death_year": 1861},
            "Browning": {"birth_year": 1806, "death_year": 1861},
            "Geoffrey Chaucer": {"birth_year": 1343, "death_year": 1400},
            "Chaucer": {"birth_year": 1343, "death_year": 1400},
        }
        # Option to disable poet date fetching (useful when Wikidata is slow)
        self.enable_poet_dates = enable_poet_dates
    
    def fetch_random_poem(self) -> Optional[Dict]:
        """
        Fetch a single random poem from PoetryDB.
        
        Returns:
            Dict containing poem data or None if failed
        """
        try:
            response = self.session.get(f"{self.poetrydb_base_url}/random", timeout=30)
            response.raise_for_status()
            
            poems = response.json()
            if poems and len(poems) > 0:
                poem = poems[0]
                return self._format_poem_data(poem)
            
        except requests.RequestException as e:
            print(f"Error fetching random poem: {e}")
        except Exception as e:
            print(f"Error processing poem data: {e}")
        
        return None
    
    def fetch_random_poems(self, count: int = 1) -> List[Dict]:
        """
        Fetch multiple random poems from PoetryDB.
        
        Args:
            count: Number of poems to fetch
            
        Returns:
            List of poem dictionaries
        """
        poems = []
        
        try:
            # PoetryDB supports fetching multiple random poems
            response = self.session.get(f"{self.poetrydb_base_url}/random/{count}", timeout=30)
            response.raise_for_status()
            
            raw_poems = response.json()
            if raw_poems:
                for poem in raw_poems:
                    formatted_poem = self._format_poem_data(poem)
                    if formatted_poem:
                        poems.append(formatted_poem)
            
        except requests.RequestException as e:
            print(f"Error fetching random poems: {e}")
        except Exception as e:
            print(f"Error processing poems data: {e}")
        
        return poems
    
    def _format_poem_data(self, raw_poem: Dict) -> Dict:
        """
        Format raw poem data into a standardized format.
        
        Args:
            raw_poem: Raw poem data from PoetryDB
            
        Returns:
            Formatted poem dictionary
        """
        try:
            title = raw_poem.get('title', 'Untitled')
            author = raw_poem.get('author', 'Unknown Author')
            lines = raw_poem.get('lines', [])
            
            # Clean and format the poem text
            poem_text = '\n'.join(lines) if lines else ''
            
            # Create formatted poem entry
            poem_entry = {
                "title": self._clean_text(title),
                "author": self._clean_text(author),
                "text": poem_text,
                "line_count": len(lines),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "PoetryDB",
                "public_domain": True
            }
            
            # Enrich with poet date information
            try:
                poem_entry = self.enrich_poem_with_dates(poem_entry)
            except Exception as e:
                print(f"Error enriching poem with dates: {e}")
                # Continue with poem_entry as-is if enrichment fails
            
            return poem_entry
            
        except Exception as e:
            print(f"Error formatting poem data: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text from API responses.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ')
    
    def count_words(self, poem: Dict) -> int:
        """
        Count the number of words in a poem.
        
        Args:
            poem: Poem dictionary with 'text' field
            
        Returns:
            Number of words in the poem
        """
        if not poem or 'text' not in poem:
            return 0
        
        text = poem['text']
        if not text:
            return 0
        
        # Split by whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    def filter_poems_by_word_count(self, poems: List[Dict], max_words: int = 200) -> List[Dict]:
        """
        Filter poems to only include those with word count <= max_words.
        
        Args:
            poems: List of poem dictionaries
            max_words: Maximum number of words allowed (default: 200)
            
        Returns:
            List of poems that meet the word count criteria
        """
        filtered_poems = []
        
        for poem in poems:
            word_count = self.count_words(poem)
            if word_count <= max_words:
                # Add word count to the poem data for reference
                poem['word_count'] = word_count
                filtered_poems.append(poem)
            else:
                print(f"⚠️ Skipping poem '{poem.get('title', 'Untitled')}' - {word_count} words (exceeds {max_words} word limit)")
        
        return filtered_poems
    
    def fetch_poems_with_word_limit(self, count: int, max_words: int = 200, max_retries: int = 50) -> List[Dict]:
        """
        Fetch poems ensuring all are under the word limit by retrying as needed.
        
        Args:
            count: Number of poems to fetch
            max_words: Maximum number of words allowed (default: 200)
            max_retries: Maximum number of retry attempts (default: 50)
            
        Returns:
            List of poems that meet the word count criteria
        """
        if count <= 0:
            return []
        
        valid_poems = []
        attempts = 0
        batch_size = min(count * 2, 10)  # Fetch more than needed to increase chances
        
        print(f"📝 Fetching poems with word limit of {max_words} words...")
        
        while len(valid_poems) < count and attempts < max_retries:
            attempts += 1
            
            # Fetch a batch of poems
            try:
                if attempts == 1:
                    # First attempt: try to fetch exactly what we need
                    batch_poems = self.fetch_random_poems(count)
                else:
                    # Subsequent attempts: fetch more to increase chances
                    batch_poems = self.fetch_random_poems(batch_size)
                
                if not batch_poems:
                    print(f"⚠️ No poems returned from API (attempt {attempts})")
                    continue
                
                # Filter poems by word count
                for poem in batch_poems:
                    if len(valid_poems) >= count:
                        break
                        
                    word_count = self.count_words(poem)
                    if word_count <= max_words:
                        poem['word_count'] = word_count
                        valid_poems.append(poem)
                        print(f"✅ Found poem {len(valid_poems)}/{count}: '{poem.get('title', 'Untitled')}' ({word_count} words)")
                    else:
                        print(f"⚠️ Skipping poem '{poem.get('title', 'Untitled')}' - {word_count} words (exceeds {max_words} word limit)")
                
                # If we still need more poems, show progress
                if len(valid_poems) < count:
                    remaining = count - len(valid_poems)
                    print(f"📝 Need {remaining} more poem{'s' if remaining != 1 else ''} under {max_words} words (attempt {attempts}/{max_retries})")
                
            except Exception as e:
                print(f"⚠️ Error fetching poems (attempt {attempts}): {e}")
                continue
        
        if len(valid_poems) < count:
            print(f"⚠️ Only found {len(valid_poems)}/{count} poems under {max_words} words after {attempts} attempts")
        else:
            print(f"✅ Successfully found {len(valid_poems)} poem{'s' if len(valid_poems) != 1 else ''} under {max_words} words")
        
        return valid_poems
    
    def get_poet_dates(self, poet_name: str) -> Optional[Dict[str, int]]:
        """
        Get poet birth/death dates from Wikidata.
        Returns dict with birth_year and death_year (None if living/unknown).
        
        Uses Wikidata P569 (birth) and P570 (death) properties.
        """
        if not poet_name:
            return None
        
        # Check cache first (including pre-populated common poets)
        if poet_name in self.poet_date_cache:
            return self.poet_date_cache[poet_name]
        
        print(f"🔍 Looking up poet dates for: {poet_name}")
        
        try:
            # More efficient query: search for exact name match first, then fuzzy
            # Split name into parts for better matching
            name_parts = poet_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                # Try exact match first (much faster)
                sparql_query = f"""
                SELECT ?birth ?death WHERE {{
                  ?person rdfs:label ?name .
                  FILTER(LANG(?name) = "en")
                  FILTER(?name = "{poet_name}" || ?name = "{last_name}, {first_name}")
                  ?person wdt:P569 ?birth .
                  OPTIONAL {{ ?person wdt:P570 ?death }}
                  # Filter to people who are poets/writers
                  {{ ?person wdt:P106 wd:Q49757 }} UNION {{ ?person wdt:P106 wd:Q36180 }}
                }}
                LIMIT 1
                """
            else:
                # Single name - use contains but with poet filter
                sparql_query = f"""
                SELECT ?birth ?death WHERE {{
                  ?person rdfs:label ?name .
                  FILTER(LANG(?name) = "en")
                  FILTER(CONTAINS(LCASE(?name), LCASE("{poet_name}")))
                  ?person wdt:P569 ?birth .
                  OPTIONAL {{ ?person wdt:P570 ?death }}
                  # Filter to people who are poets/writers
                  {{ ?person wdt:P106 wd:Q49757 }} UNION {{ ?person wdt:P106 wd:Q36180 }}
                }}
                LIMIT 1
                """
            
            # Try multiple query strategies with increasing timeout
            query_strategies = [
                (sparql_query, 5),  # Fast exact match
                (sparql_query, 10), # Slower fuzzy match
            ]
            
            for query, timeout in query_strategies:
                try:
                    response = self.session.get(
                        self.wikidata_endpoint,
                        params={'query': query, 'format': 'json'},
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data['results']['bindings']
                        if results:
                            birth_value = results[0].get('birth', {}).get('value', '')
                            death_value = results[0].get('death', {}).get('value', '')
                            
                            # Extract years from date strings
                            birth_year = None
                            death_year = None
                            
                            if birth_value:
                                birth_match = re.match(r'^(\d{4})', birth_value)
                                if birth_match:
                                    birth_year = int(birth_match.group(1))
                            
                            if death_value:
                                death_match = re.match(r'^(\d{4})', death_value)
                                if death_match:
                                    death_year = int(death_match.group(1))
                            
                            result = {
                                'birth_year': birth_year,
                                'death_year': death_year
                            }
                            
                            # Cache the result
                            self.poet_date_cache[poet_name] = result
                            print(f"✅ Found poet dates for {poet_name}: {birth_year}-{death_year if death_year else 'present'}")
                            return result
                        else:
                            # No results with this strategy, try next
                            continue
                    else:
                        # HTTP error, try next strategy
                        continue
                        
                except Exception as query_error:
                    # Query failed, try next strategy
                    print(f"Query strategy failed for {poet_name}: {query_error}")
                    continue
        except Exception as e:
            print(f"❌ Error getting poet dates for {poet_name}: {e}")
        
        # Cache None result to avoid repeated failed lookups
        self.poet_date_cache[poet_name] = None
        print(f"⚠️ No poet dates found for: {poet_name}")
        return None
    
    def enrich_poem_with_dates(self, poem: Dict) -> Dict:
        """
        Enrich poem dictionary with poet date information.
        Adds poet_birth_year, poet_death_year, and poet_lifespan fields.
        """
        # If poet date fetching is disabled, just add None values
        if not self.enable_poet_dates:
            poem['poet_birth_year'] = None
            poem['poet_death_year'] = None
            poem['poet_lifespan'] = None
            return poem
        
        try:
            poet_name = poem.get('author', '')
            if not poet_name:
                poem['poet_birth_year'] = None
                poem['poet_death_year'] = None
                poem['poet_lifespan'] = None
                return poem
            
            poet_dates = self.get_poet_dates(poet_name)
            
            if poet_dates:
                birth_year = poet_dates.get('birth_year')
                death_year = poet_dates.get('death_year')
                
                poem['poet_birth_year'] = birth_year
                poem['poet_death_year'] = death_year
                
                # Format lifespan string
                if birth_year and death_year:
                    poem['poet_lifespan'] = f"({birth_year}-{death_year})"
                elif birth_year:
                    poem['poet_lifespan'] = f"({birth_year}-present)"
                else:
                    poem['poet_lifespan'] = None
            else:
                poem['poet_birth_year'] = None
                poem['poet_death_year'] = None
                poem['poet_lifespan'] = None
            
            return poem
        except Exception as e:
            print(f"Error enriching poem with dates: {e}")
            poem['poet_birth_year'] = None
            poem['poet_death_year'] = None
            poem['poet_lifespan'] = None
            return poem
    
    def create_sample_poems(self, count: int = 3) -> List[Dict]:
        """
        Create sample poems for testing when PoetryDB is not accessible.
        
        Args:
            count: Number of sample poems to create
            
        Returns:
            List of sample poem dictionaries
        """
        sample_poems = [
            {
                "title": "The Road Not Taken",
                "author": "Robert Frost",
                "text": "Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could\nTo where it bent in the undergrowth;\n\nThen took the other, as just as fair,\nAnd having perhaps the better claim,\nBecause it was grassy and wanted wear;\nThough as for that the passing there\nHad worn them really about the same,\n\nAnd both that morning equally lay\nIn leaves no step had trodden black.\nOh, I kept the first for another day!\nYet knowing how way leads on to way,\nI doubted if I should ever come back.\n\nI shall be telling this with a sigh\nSomewhere ages and ages hence:\nTwo roads diverged in a wood, and I—\nI took the one less traveled by,\nAnd that has made all the difference.",
                "line_count": 20,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "Sample Data",
                "public_domain": True,
                "poet_birth_year": 1874,
                "poet_death_year": 1963,
                "poet_lifespan": "(1874-1963)"
            },
            {
                "title": "Sonnet 18",
                "author": "William Shakespeare",
                "text": "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer's lease hath all too short a date;\nSometime too hot the eye of heaven shines,\nAnd often is his gold complexion dimm'd;\nAnd every fair from fair sometime declines,\nBy chance or nature's changing course untrimm'd;\nBut thy eternal summer shall not fade\nNor lose possession of that fair thou owest;\nNor shall Death brag thou wander'st in his shade,\nWhen in eternal lines to time thou growest:\nSo long as men can breathe or eyes can see,\nSo long lives this, and this gives life to thee.",
                "line_count": 14,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "Sample Data",
                "public_domain": True,
                "poet_birth_year": 1564,
                "poet_death_year": 1616,
                "poet_lifespan": "(1564-1616)"
            },
            {
                "title": "I Wandered Lonely as a Cloud",
                "author": "William Wordsworth",
                "text": "I wandered lonely as a cloud\nThat floats on high o'er vales and hills,\nWhen all at once I saw a crowd,\nA host, of golden daffodils;\nBeside the lake, beneath the trees,\nFluttering and dancing in the breeze.\n\nContinuous as the stars that shine\nAnd twinkle on the milky way,\nThey stretched in never-ending line\nAlong the margin of a bay:\nTen thousand saw I at a glance,\nTossing their heads in sprightly dance.\n\nThe waves beside them danced; but they\nOut-did the sparkling waves in glee:\nA poet could not but be gay,\nIn such a jocund company:\nI gazed—and gazed—but little thought\nWhat wealth the show to me had brought:\n\nFor oft, when on my couch I lie\nIn vacant or in pensive mood,\nThey flash upon that inward eye\nWhich is the bliss of solitude;\nAnd then my heart with pleasure fills,\nAnd dances with the daffodils.",
                "line_count": 24,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "Sample Data",
                "public_domain": True,
                "poet_birth_year": 1770,
                "poet_death_year": 1850,
                "poet_lifespan": "(1770-1850)"
            }
        ]
        
        return sample_poems[:count]
    
    def get_daily_poem(self) -> Optional[Dict]:
        """
        Get a single random poem for daily use.
        
        Returns:
            Poem dictionary or None if no poem found
        """
        return self.fetch_random_poem()
    
    def save_poems_to_json(self, poems: List[Dict], filename: str = None) -> str:
        """
        Save poems data to a JSON file.
        
        Args:
            poems: List of poem dictionaries
            filename: Output filename (defaults to poems_YYYYMMDD.json)
            
        Returns:
            Filename where poems were saved
        """
        if filename is None:
            filename = f"poems_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(poems, f, indent=2, ensure_ascii=False)
            print(f"📝 Poems data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving poems to JSON: {e}")
            return None


def main():
    """
    Main function to demonstrate the poem fetcher functionality.
    """
    fetcher = PoemFetcher()
    
    print("Daily Culture Bot - Poem Fetcher")
    print("=" * 40)
    
    # Get user input for number of poems
    try:
        count = int(input("How many poems would you like to fetch? (default: 1): ") or "1")
    except ValueError:
        count = 1
    
    # Fetch poems
    poems = fetcher.fetch_random_poems(count)
    
    if poems:
        print(f"\nSuccessfully fetched {len(poems)} poem{'s' if len(poems) != 1 else ''}!")
        
        # Save to JSON
        filename = fetcher.save_poems_to_json(poems)
        
        # Display poems
        print("\n" + "="*80)
        print("POEM INFORMATION")
        print("="*80)
        
        for i, poem in enumerate(poems):
            print(f"\n{i+1}. 📝 {poem['title']} by {poem['author']}")
            print(f"   Lines: {poem['line_count']} | Source: {poem['source']}")
            print(f"   Text preview: {poem['text'][:100]}...")
    
    else:
        print("No poems were fetched. Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
