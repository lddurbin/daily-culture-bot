import json
import requests
from mastodon import Mastodon
import os
import tempfile
from datetime import date
import datacreator
import sys

# Check if running in dry-run mode
DRY_RUN = "--dry-run" in sys.argv or "-n" in sys.argv

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

# Get image content
response = requests.get(painting["image"], headers=headers)
content_type = response.headers.get("Content-Type", "")

# Only accept JPEGs
if "image/jpeg" not in content_type:
    raise ValueError(f"Invalid image content type: {content_type}")

# Save image to a temporary file
with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
    tmp_file.write(response.content)
    image_path = tmp_file.name

# Format the post
caption = f"""🎨 {painting['title']} by {painting['artist']} ({painting['year']})
Style: {painting['style']}
Medium: {painting['medium']}
Museum: {painting['museum']}
Fun fact: {painting['fact']}
#Art #Painting #DailyArt"""

if DRY_RUN:
    print("\n🧪 DRY RUN MODE - Not posting to Mastodon")
    print("📝 Caption that would be posted:")
    print("-" * 50)
    print(caption)
    print("-" * 50)
    print(f"🖼️ Image URL: {painting['image']}")
    print("✅ Dry run completed successfully!")
    exit(0)

print("📥 Downloading image...")

# Get image content
response = requests.get(painting["image"], headers=headers)
content_type = response.headers.get("Content-Type", "")

# Only accept JPEGs and PNGs (expanded for better compatibility)
if "image/jpeg" not in content_type and "image/png" not in content_type:
    raise ValueError(f"Invalid image content type: {content_type}")

# Save image to a temporary file
file_ext = ".jpg" if "jpeg" in content_type else ".png"
with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
    tmp_file.write(response.content)
    image_path = tmp_file.name

print("📤 Posting to Mastodon...")

# Post to Mastodon
mastodon = Mastodon(
    access_token=os.environ["MASTODON_ACCESS_TOKEN"],
    api_base_url=os.environ["MASTODON_BASE_URL"]
)

media = mastodon.media_post(image_path)
mastodon.status_post(caption, media_ids=[media])

print("✅ Successfully posted to Mastodon!")
print(f"🎨 Today's painting: {painting['title']} by {painting['artist']}")

# Cleanup
os.remove(image_path)
