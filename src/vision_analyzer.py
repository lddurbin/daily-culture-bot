#!/usr/bin/env python3
"""
Vision Analyzer Module for Daily Culture Bot

This module contains GPT-4 Vision integration for artwork image analysis.
Analyzes artwork images to extract visual elements, composition, mood, and
other characteristics for better poem-artwork matching.
"""

import json
import re
import time
from typing import Dict, List, Optional
from openai import OpenAI
import os


class VisionAnalyzer:
    """Handles GPT-4 Vision API integration for artwork image analysis."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        """
        Initialize vision analyzer.
        
        Args:
            openai_client: OpenAI client instance (optional, will create if not provided)
        """
        if openai_client:
            self.openai_client = openai_client
        else:
            # Initialize OpenAI client if API key is available
            if os.getenv('OPENAI_API_KEY'):
                try:
                    self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                    print("✅ OpenAI Vision API initialized")
                except Exception as e:
                    print(f"❌ OpenAI Vision initialization failed: {e}")
                    self.openai_client = None
            else:
                print("❌ OPENAI_API_KEY not found for vision analysis")
                self.openai_client = None
        
        # Enhanced cache for analysis results to avoid redundant API calls
        self.analysis_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "total_requests": 0}
    
    def analyze_artwork_image(self, image_url: str, artwork_title: str = "") -> Dict:
        """
        Analyze artwork image using GPT-4 Vision API.
        
        Args:
            image_url: URL of the artwork image
            artwork_title: Title of the artwork (for caching and logging)
            
        Returns:
            Dictionary with vision analysis results
        """
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI client not initialized",
                "artwork_title": artwork_title
            }
        
        # Check cache first
        cache_key = f"{image_url}_{artwork_title}"
        self.cache_stats["total_requests"] += 1
        
        if cache_key in self.analysis_cache:
            self.cache_stats["hits"] += 1
            print(f"📋 Using cached vision analysis for: {artwork_title} (cache hit)")
            return self.analysis_cache[cache_key]
        
        self.cache_stats["misses"] += 1
        
        prompt = """Analyze this artwork and return ONLY a JSON object:
{
  "detected_objects": ["specific objects visible in the image"],
  "dominant_colors": ["color1", "color2", "color3"],
  "color_palette": "warm|cool|muted|vibrant|monochrome",
  "setting": "indoor|outdoor|abstract|urban|rural|seascape|celestial",
  "time_of_day": "dawn|day|dusk|night|ambiguous",
  "season_indicators": "spring|summer|autumn|winter|none",
  "human_presence": "central|peripheral|absent",
  "composition": "intimate|expansive|chaotic|ordered",
  "spatial_qualities": "enclosed|open|vertical|horizontal|centered",
  "movement_energy": "static|flowing|explosive|rhythmic",
  "mood": "light|dark|dramatic|serene|turbulent|joyful|melancholic",
  "style_characteristics": "realistic|impressionistic|abstract|symbolic"
}

Return ONLY valid JSON with no additional text."""
        
        try:
            start_time = time.time()
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from OpenAI response")
            
            # Get token usage
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            result = {
                "success": True,
                "analysis": analysis_result,
                "tokens": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                "processing_time": processing_time,
                "artwork_title": artwork_title,
                "image_url": image_url
            }
            
            # Cache the result
            self.analysis_cache[cache_key] = result
            
            print(f"🎨 Vision analysis completed for: {artwork_title} ({total_tokens} tokens, {processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "artwork_title": artwork_title,
                "image_url": image_url
            }
            
            # Cache error result to avoid retrying immediately
            self.analysis_cache[cache_key] = error_result
            
            print(f"❌ Vision analysis failed for {artwork_title}: {e}")
            return error_result
    
    def extract_q_codes_from_vision_analysis(self, analysis: Dict) -> List[str]:
        """
        Extract Wikidata Q-codes from vision analysis results.
        
        Args:
            analysis: Vision analysis result dictionary
            
        Returns:
            List of Wikidata Q-codes
        """
        if not analysis.get("success") or not analysis.get("analysis"):
            return []
        
        vision_data = analysis["analysis"]
        q_codes = []
        
        # Map detected objects to Q-codes
        detected_objects = vision_data.get("detected_objects", [])
        for obj in detected_objects:
            obj_lower = obj.lower()
            # This would be expanded with comprehensive object mappings
            if obj_lower in ["tree", "trees"]:
                q_codes.append("Q10884")  # tree
            elif obj_lower in ["flower", "flowers", "rose", "roses"]:
                q_codes.append("Q11427")  # rose
            elif obj_lower in ["ocean", "sea", "water"]:
                q_codes.append("Q9430")   # ocean
            elif obj_lower in ["mountain", "mountains"]:
                q_codes.append("Q8502")  # mountain
            elif obj_lower in ["house", "houses", "building", "buildings"]:
                q_codes.append("Q3947")  # house
            elif obj_lower in ["ship", "ships", "boat", "boats"]:
                q_codes.append("Q11446") # ship
            elif obj_lower in ["bird", "birds"]:
                q_codes.append("Q5113")  # bird
            elif obj_lower in ["horse", "horses"]:
                q_codes.append("Q726")   # horse
            elif obj_lower in ["dog", "dogs"]:
                q_codes.append("Q144")   # dog
            elif obj_lower in ["cat", "cats"]:
                q_codes.append("Q146")   # cat
        
        # Map settings to Q-codes
        setting = vision_data.get("setting", "")
        if setting == "seascape":
            q_codes.append("Q16970")  # seascape
        elif setting == "landscape":
            q_codes.append("Q191163") # landscape
        elif setting == "portrait":
            q_codes.append("Q134307") # portrait
        
        # Map time of day to Q-codes
        time_of_day = vision_data.get("time_of_day", "")
        if time_of_day == "night":
            q_codes.append("Q183")    # night
        elif time_of_day == "day":
            q_codes.append("Q111")    # day
        
        # Remove duplicates
        return list(set(q_codes))
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the analysis cache."""
        total_entries = len(self.analysis_cache)
        successful_analyses = sum(1 for result in self.analysis_cache.values() if result.get("success"))
        failed_analyses = total_entries - successful_analyses
        
        total_tokens = sum(
            result.get("tokens", {}).get("total_tokens", 0) 
            for result in self.analysis_cache.values() 
            if result.get("success")
        )
        
        return {
            "total_entries": total_entries,
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "total_tokens_used": total_tokens,
            "cache_hit_rate": "N/A"  # Would need hit tracking for accurate rate
        }
    
    def clear_cache(self):
        """Clear the analysis cache."""
        self.analysis_cache.clear()
        print("🗑️ Vision analysis cache cleared")
    
    def should_skip_vision_analysis(self, artwork: Dict) -> bool:
        """
        Determine if vision analysis should be skipped for an artwork with good metadata.
        
        Args:
            artwork: Dictionary containing artwork data
            
        Returns:
            True if vision analysis should be skipped, False otherwise
        """
        # Skip if artwork has comprehensive subject information
        subject_q_codes = artwork.get('subject_q_codes', [])
        if len(subject_q_codes) >= 3:  # Has 3+ subject codes
            return True
        
        # Skip if artwork has detailed genre information
        genre_q_codes = artwork.get('genre_q_codes', [])
        if len(genre_q_codes) >= 2:  # Has 2+ genre codes
            return True
        
        # Skip if artwork has comprehensive depicts information
        depicts = artwork.get('depicts', [])
        if len(depicts) >= 3:  # Has 3+ depicts entries
            return True
        
        # Skip if artwork has detailed style/medium information
        style = artwork.get('style', '')
        medium = artwork.get('medium', '')
        if style and medium and len(style) > 10 and len(medium) > 10:
            return True
        
        return False
    
    def is_enabled(self) -> bool:
        """Check if vision analysis is enabled (has OpenAI client)."""
        return self.openai_client is not None


if __name__ == "__main__":
    print("Vision analyzer module - use daily_culture_bot.py for CLI access")
