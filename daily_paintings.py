import json
import requests
import os
import tempfile
from datetime import date
import datacreator
import sys

# Check if running in output mode
OUTPUT_MODE = "--output" in sys.argv or "-o" in sys.argv
SAVE_IMAGE = "--save-image" in sys.argv or "-i" in sys.argv

# Initialize the data creator
creator = datacreator.PaintingDataCreator()

print("🎨 Fetching today's painting...")

# Get a random painting using datacreator
painting = creator.get_daily_painting()

if painting is None:
    print("❌ Could not fetch a painting from Wikidata. Trying fallback...")
    # Fallback to sample paintings if API fails
    sample_paintings = creator.create_sample_paintings(1)
    if sample_paintings:
        painting = sample_paintings[0]
        print("📋 Using sample painting as fallback")
    else:
        raise ValueError("Failed to get any painting data")

print(f"✅ Selected: {painting['title']} by {painting['artist']} ({painting['year']})")

# Define headers to comply with Wikimedia policy
headers = {
    "User-Agent": "DailyCanvasBot/1.0 (https://github.com/yourusername/daily-canvas)"
}

# Download and save image if requested
image_path = None
if SAVE_IMAGE:
    print("📥 Downloading image...")
    
    try:
        # Get image content with better error handling
        response = requests.get(painting["image"], headers=headers, timeout=30)
        content_type = response.headers.get("Content-Type", "")
        
        # Check if we got a valid image
        if "image/" not in content_type:
            print(f"⚠️ Warning: Invalid image content type: {content_type}")
            print(f"🖼️ Image URL: {painting['image']}")
            print("📋 Skipping image download, but continuing with artwork data...")
        else:
            # Save image to a file
            file_ext = ".jpg" if "jpeg" in content_type else ".png"
            safe_title = "".join(c for c in painting['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{painting['year']}{file_ext}"
            image_path = filename
            
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            print(f"🖼️ Image saved as: {image_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not download image: {e}")
        print(f"🖼️ Image URL: {painting['image']}")
        print("📋 Continuing with artwork data...")

# Format the artwork information
artwork_info = f"""🎨 {painting['title']} by {painting['artist']} ({painting['year']})
Style: {painting['style']}
Medium: {painting['medium']}
Museum: {painting['museum']}
Origin: {painting['origin']}
Dimensions: {painting['dimensions']}
Fun fact: {painting['fact']}
Image URL: {painting['image']}
Wikidata: {painting['wikidata']}"""

# Output the artwork information
if OUTPUT_MODE:
    # Save to JSON file
    output_filename = f"artwork_{date.today().strftime('%Y%m%d')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(painting, f, indent=2, ensure_ascii=False)
    print(f"📄 Artwork data saved to: {output_filename}")

print("\n" + "="*60)
print("ARTWORK INFORMATION")
print("="*60)
print(artwork_info)
print("="*60)

if image_path:
    print(f"🖼️ Local image file: {image_path}")
else:
    print(f"🖼️ Image URL: {painting['image']}")

print("✅ Artwork information retrieved successfully!")
