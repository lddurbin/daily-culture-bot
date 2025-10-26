#!/usr/bin/env python3
"""
Poem Fetcher for Daily Culture Bot

This module fetches random public domain poems from PoetryDB API.
It provides functionality to get poems and format them for display.
"""

import requests
import json
import random
from datetime import datetime
from typing import List, Dict, Optional


class PoemFetcher:
    def __init__(self):
        self.poetrydb_base_url = "https://poetrydb.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DailyCultureBot/1.0 (https://github.com/yourusername/daily-culture-bot)'
        })
    
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
                "public_domain": True
            },
            {
                "title": "Sonnet 18",
                "author": "William Shakespeare",
                "text": "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer's lease hath all too short a date;\nSometime too hot the eye of heaven shines,\nAnd often is his gold complexion dimm'd;\nAnd every fair from fair sometime declines,\nBy chance or nature's changing course untrimm'd;\nBut thy eternal summer shall not fade\nNor lose possession of that fair thou owest;\nNor shall Death brag thou wander'st in his shade,\nWhen in eternal lines to time thou growest:\nSo long as men can breathe or eyes can see,\nSo long lives this, and this gives life to thee.",
                "line_count": 14,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "Sample Data",
                "public_domain": True
            },
            {
                "title": "I Wandered Lonely as a Cloud",
                "author": "William Wordsworth",
                "text": "I wandered lonely as a cloud\nThat floats on high o'er vales and hills,\nWhen all at once I saw a crowd,\nA host, of golden daffodils;\nBeside the lake, beneath the trees,\nFluttering and dancing in the breeze.\n\nContinuous as the stars that shine\nAnd twinkle on the milky way,\nThey stretched in never-ending line\nAlong the margin of a bay:\nTen thousand saw I at a glance,\nTossing their heads in sprightly dance.\n\nThe waves beside them danced; but they\nOut-did the sparkling waves in glee:\nA poet could not but be gay,\nIn such a jocund company:\nI gazed—and gazed—but little thought\nWhat wealth the show to me had brought:\n\nFor oft, when on my couch I lie\nIn vacant or in pensive mood,\nThey flash upon that inward eye\nWhich is the bliss of solitude;\nAnd then my heart with pleasure fills,\nAnd dances with the daffodils.",
                "line_count": 24,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "Sample Data",
                "public_domain": True
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
