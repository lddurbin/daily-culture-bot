#!/usr/bin/env python3
"""
GPT-4 Vision Cost Estimation Test

This script tests GPT-4 Vision API costs for artwork image analysis
to estimate the cost impact before implementing full vision analysis.
"""

import os
import json
import time
from typing import Dict, List
from openai import OpenAI
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VisionCostEstimator:
    def __init__(self):
        """Initialize the cost estimator with OpenAI client."""
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                print("✅ OpenAI API initialized for vision cost estimation")
            except Exception as e:
                print(f"❌ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            print("❌ OPENAI_API_KEY not found in environment")
    
    def get_sample_artwork_images(self) -> List[Dict[str, str]]:
        """Get sample artwork images for testing."""
        # Sample artwork images from Wikimedia Commons
        sample_images = [
            {
                "title": "The Starry Night",
                "artist": "Vincent van Gogh",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
                "description": "Famous post-impressionist painting with swirling sky"
            },
            {
                "title": "Mona Lisa",
                "artist": "Leonardo da Vinci", 
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/687px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
                "description": "Renaissance portrait with enigmatic smile"
            },
            {
                "title": "The Great Wave off Kanagawa",
                "artist": "Hokusai",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/1280px-The_Great_Wave_off_Kanagawa.jpg",
                "description": "Japanese woodblock print with dramatic wave"
            },
            {
                "title": "The Scream",
                "artist": "Edvard Munch",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/1280px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
                "description": "Expressionist painting with figure in distress"
            },
            {
                "title": "Water Lilies",
                "artist": "Claude Monet",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1919%2C_Metropolitan_Museum_of_Art.jpg/1280px-Claude_Monet_-_Water_Lilies_-_1919%2C_Metropolitan_Museum_of_Art.jpg",
                "description": "Impressionist landscape with water lilies"
            }
        ]
        return sample_images
    
    def analyze_artwork_image(self, image_url: str, title: str) -> Dict:
        """Analyze artwork image using GPT-4 Vision."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
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
                import re
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
            
            return {
                "success": True,
                "analysis": analysis_result,
                "tokens": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                "processing_time": processing_time,
                "title": title
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "title": title
            }
    
    def calculate_costs(self, token_usage: List[Dict]) -> Dict:
        """Calculate estimated costs based on token usage."""
        # GPT-4 Vision pricing (as of 2024)
        # These are approximate rates - actual rates may vary
        input_cost_per_1k = 0.01  # $0.01 per 1K input tokens
        output_cost_per_1k = 0.03  # $0.03 per 1K output tokens
        
        total_prompt_tokens = sum(usage["tokens"]["prompt_tokens"] for usage in token_usage)
        total_completion_tokens = sum(usage["tokens"]["completion_tokens"] for usage in token_usage)
        total_tokens = sum(usage["tokens"]["total_tokens"] for usage in token_usage)
        
        input_cost = (total_prompt_tokens / 1000) * input_cost_per_1k
        output_cost = (total_completion_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost
        
        avg_tokens_per_image = total_tokens / len(token_usage)
        avg_cost_per_image = total_cost / len(token_usage)
        
        return {
            "total_images": len(token_usage),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_tokens_per_image": avg_tokens_per_image,
            "avg_cost_per_image": avg_cost_per_image,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "breakdown": {
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens
            }
        }
    
    def run_cost_estimation(self) -> Dict:
        """Run the full cost estimation test."""
        print("🔍 Starting GPT-4 Vision cost estimation test...")
        print("=" * 60)
        
        if not self.openai_client:
            return {"error": "OpenAI client not initialized"}
        
        # Get sample images
        sample_images = self.get_sample_artwork_images()
        print(f"📸 Testing with {len(sample_images)} sample artwork images")
        
        results = []
        successful_analyses = []
        
        for i, image in enumerate(sample_images, 1):
            print(f"\n🎨 Analyzing {i}/{len(sample_images)}: {image['title']} by {image['artist']}")
            print(f"   URL: {image['url']}")
            
            try:
                result = self.analyze_artwork_image(image['url'], image['title'])
                results.append(result)
                
                if result["success"]:
                    successful_analyses.append(result)
                    tokens = result["tokens"]
                    print(f"   ✅ Success: {tokens['total_tokens']} tokens, {result['processing_time']:.2f}s")
                    print(f"      Prompt: {tokens['prompt_tokens']}, Completion: {tokens['completion_tokens']}")
                else:
                    print(f"   ❌ Failed: {result['error']}")
                
                # Add delay to be respectful to API
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "title": image['title']
                })
        
        # Calculate costs
        if successful_analyses:
            cost_analysis = self.calculate_costs(successful_analyses)
            
            print("\n" + "=" * 60)
            print("💰 COST ESTIMATION RESULTS")
            print("=" * 60)
            print(f"Successful analyses: {len(successful_analyses)}/{len(sample_images)}")
            print(f"Total tokens used: {cost_analysis['total_tokens']:,}")
            print(f"Total estimated cost: ${cost_analysis['total_cost']:.4f}")
            print(f"Average tokens per image: {cost_analysis['avg_tokens_per_image']:.0f}")
            print(f"Average cost per image: ${cost_analysis['avg_cost_per_image']:.4f}")
            print(f"Input cost: ${cost_analysis['input_cost']:.4f}")
            print(f"Output cost: ${cost_analysis['output_cost']:.4f}")
            
            # Projections
            print("\n📊 PROJECTIONS")
            print("-" * 30)
            print(f"Cost for 100 artworks: ${cost_analysis['avg_cost_per_image'] * 100:.2f}")
            print(f"Cost for 1000 artworks: ${cost_analysis['avg_cost_per_image'] * 1000:.2f}")
            print(f"Cost for 10000 artworks: ${cost_analysis['avg_cost_per_image'] * 10000:.2f}")
            
            # Recommendations
            print("\n💡 RECOMMENDATIONS")
            print("-" * 30)
            if cost_analysis['avg_cost_per_image'] < 0.01:
                print("✅ Cost is reasonable (< $0.01 per artwork)")
                print("   Proceed with vision analysis implementation")
            elif cost_analysis['avg_cost_per_image'] < 0.05:
                print("⚠️  Cost is moderate ($0.01-0.05 per artwork)")
                print("   Consider implementing with usage limits")
            else:
                print("❌ Cost is high (> $0.05 per artwork)")
                print("   Consider alternatives or batch processing")
            
            return {
                "success": True,
                "cost_analysis": cost_analysis,
                "results": results,
                "recommendations": {
                    "proceed": cost_analysis['avg_cost_per_image'] < 0.01,
                    "moderate": cost_analysis['avg_cost_per_image'] < 0.05,
                    "high_cost": cost_analysis['avg_cost_per_image'] >= 0.05
                }
            }
        else:
            print("\n❌ No successful analyses to calculate costs")
            return {
                "success": False,
                "error": "No successful vision analyses",
                "results": results
            }


def main():
    """Run the cost estimation test."""
    estimator = VisionCostEstimator()
    results = estimator.run_cost_estimation()
    
    # Save results to file
    with open("vision_cost_estimation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to vision_cost_estimation_results.json")
    
    return results


if __name__ == "__main__":
    main()
