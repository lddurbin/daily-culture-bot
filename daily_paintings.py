import json
import requests
from mastodon import Mastodon
import os
import random
import tempfile

# Load painting data
with open("paintings_detailed.json", "r") as f:
    paintings = json.load(f)

# Pick a random painting
painting = random.choice(paintings)

# Define headers to comply with Wikimedia policy
headers = {
    "User-Agent": "DailyCanvasBot/1.0 (https://github.com/ugurelveren/daily-painting-bot)"
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


#Post to Mastodon
mastodon = Mastodon(
    access_token = os.environ["MASTODON_ACCESS_TOKEN"],
    api_base_url = os.environ["MASTODON_BASE_URL"]
)

media = mastodon.media_post(image_path)
mastodon.status_post(caption, media_ids=[media])

# Optional: cleanup
os.remove(image_path)
