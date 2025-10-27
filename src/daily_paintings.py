import json
import requests
import os
import tempfile
from datetime import date
import sys
import argparse
import re

# Import from same package - support both relative and absolute imports
try:
    from . import datacreator
    from . import poem_fetcher
    from . import poem_analyzer
    from . import email_sender
except ImportError:
    # If running as script, use absolute imports
    import datacreator
    import poem_fetcher
    import poem_analyzer
    import email_sender

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Daily Culture Bot - Fetch and display artwork and poem information')
    parser.add_argument('--output', '-o', action='store_true', help='Save artwork data to JSON file')
    parser.add_argument('--save-image', '-i', action='store_true', help='Download and save artwork images')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of artworks to fetch (default: 1)')
    parser.add_argument('--fast', action='store_true', help='Skip Wikidata API and use sample data only (much faster)')
    parser.add_argument('--poems', '-p', action='store_true', help='Also fetch random poems')
    parser.add_argument('--poem-count', type=int, default=1, help='Number of poems to fetch (default: 1)')
    parser.add_argument('--poems-only', action='store_true', help='Fetch only poems, no artwork')
    parser.add_argument('--complementary', action='store_true', help='Match artwork to poem themes (automatically enables --poems)')
    parser.add_argument('--no-poet-dates', action='store_true',
                       help='Disable poet date fetching (faster, avoids Wikidata timeouts)')
    parser.add_argument('--email', help='Email address to send content to (enables email feature)')
    parser.add_argument('--email-format', choices=['html', 'text', 'both'], default='both', 
                       help='Email format: html, text, or both (default: both)')
    parser.add_argument('--max-fame-level', type=int, default=20, 
                       help='Maximum fame level (sitelinks) for artwork (default: 20, lower=more obscure)')
    parser.add_argument('--min-match-score', type=float, default=0.4,
                       help='Minimum match quality score 0.0-1.0 (default: 0.4)')
    parser.add_argument('--query-timeout', type=int, default=60,
                       help='Wikidata query timeout in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # Validate email address if provided
    if args.email:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, args.email):
            print(f"❌ Error: Invalid email address format: {args.email}")
            sys.exit(1)
    
    return args

def download_image(painting, headers, save_dir="."):
    """Download image for a painting and return the local path."""
    try:
        response = requests.get(painting["image"], headers=headers, timeout=30)
        content_type = response.headers.get("Content-Type", "")
        
        if "image/" not in content_type:
            print(f"⚠️ Warning: Invalid image content type for {painting['title']}: {content_type}")
            return None
        
        # Save image to a file
        file_ext = ".jpg" if "jpeg" in content_type else ".png"
        safe_title = "".join(c for c in painting['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{painting['year']}{file_ext}"
        image_path = os.path.join(save_dir, filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        return image_path
    except Exception as e:
        print(f"⚠️ Warning: Could not download image for {painting['title']}: {e}")
        return None


def main():
    args = parse_arguments()
    
    # Validate complementary mode constraints
    if args.complementary and args.poems_only:
        print("❌ Error: --complementary and --poems-only cannot be used together")
        print("💡 Use --complementary to match artwork to poems, or --poems-only for poems only")
        return
    
    # Auto-enable poems when using complementary mode
    if args.complementary and not args.poems:
        args.poems = True
        print("📝 Complementary mode automatically enabled poem fetching")
    
    # Initialize the data creators
    creator = datacreator.PaintingDataCreator(query_timeout=args.query_timeout)
    poem_fetcher_instance = poem_fetcher.PoemFetcher(enable_poet_dates=not args.no_poet_dates)
    poem_analyzer_instance = poem_analyzer.PoemAnalyzer()
    
    paintings = []
    poems = []
    match_status = []  # Track which paintings were matched vs fallback
    
    # Handle complementary mode (poems first, then match artwork)
    if args.complementary:
        print(f"🎭 Complementary mode: Fetching poems first, then matching artwork...")
        
        # Fetch poems first
        if args.email:
            # For email mode, use retry mechanism to ensure we get poems under 200 words
            print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''} for email (≤200 words each)...")
            
            if args.fast:
                print("⚡ Fast mode: Using sample poem data...")
                poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
                # Apply word count filtering to sample poems
                poems = poem_fetcher_instance.filter_poems_by_word_count(poems, max_words=200)
            else:
                poems = poem_fetcher_instance.fetch_poems_with_word_limit(args.poem_count, max_words=200)
        else:
            # Regular complementary mode - fetch poems normally
            print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''}...")
            
            if args.fast:
                print("⚡ Fast mode: Using sample poem data...")
                poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
            else:
                poems = poem_fetcher_instance.fetch_random_poems(args.poem_count)
        
        if not poems:
            print("❌ Could not fetch poems from PoetryDB.")
            print("💡 Try again later or check your internet connection.")
            raise ValueError("Failed to fetch poems from PoetryDB API")
        
        print(f"✅ Selected {len(poems)} poem{'s' if len(poems) != 1 else ''}")
        
        # Analyze poems and fetch matching artwork
        print("🔍 Analyzing poem themes and emotions...")
        poem_analyses = poem_analyzer_instance.analyze_multiple_poems(poems)
        
        # Get combined Q-codes from all poems (themes + emotions)
        all_q_codes = poem_analyzer_instance.get_combined_q_codes(poem_analyses)
        
        # Get emotion-specific Q-codes and genres
        emotion_q_codes = []
        emotion_genres = []
        for analysis in poem_analyses:
            if analysis.get("emotions"):
                emotion_q_codes.extend(poem_analyzer_instance.get_emotion_q_codes(analysis["emotions"]))
                # Add genre Q-codes for emotions
                for emotion in analysis["emotions"]:
                    emotion_lower = emotion.lower()
                    if emotion_lower in poem_analyzer_instance.emotion_mappings:
                        emotion_genres.extend(poem_analyzer_instance.emotion_mappings[emotion_lower]["genres"])
        
        # Combine all Q-codes
        all_q_codes.extend(emotion_q_codes)
        all_q_codes = list(set(all_q_codes))  # Remove duplicates
        emotion_genres = list(set(emotion_genres))  # Remove duplicates
        
        # Print analysis results
        for i, analysis in enumerate(poem_analyses):
            poem = poems[i]
            print(f"\n📝 Analysis for '{poem['title']}':")
            print(f"   Method: {analysis.get('analysis_method', 'unknown')}")
            if analysis.get("primary_emotions"):
                print(f"   Primary emotions: {analysis['primary_emotions']}")
            if analysis.get("secondary_emotions"):
                print(f"   Secondary emotions: {analysis['secondary_emotions']}")
            if analysis.get("emotional_tone") and analysis.get("emotional_tone") != "unknown":
                print(f"   Emotional tone: {analysis['emotional_tone']}")
            if analysis.get("themes"):
                print(f"   Themes: {analysis['themes']}")
            if analysis.get("imagery_type"):
                print(f"   Imagery type: {analysis['imagery_type']}")
            if analysis.get("visual_aesthetic"):
                aesthetic = analysis['visual_aesthetic']
                print(f"   Visual aesthetic: {aesthetic.get('mood', 'unknown')} mood, {aesthetic.get('color_palette', 'unknown')} colors")
            if analysis.get("intensity"):
                print(f"   Intensity: {analysis['intensity']}/10")
            if analysis.get("subject_suggestions"):
                print(f"   Subject suggestions: {analysis['subject_suggestions']}")
            if analysis.get("avoid_subjects"):
                print(f"   Avoid subjects: {analysis['avoid_subjects']}")
        
        if all_q_codes:
            print(f"\n🎨 Searching for artwork matching themes and emotions: {all_q_codes}")
            if emotion_genres:
                print(f"   With genre filtering: {emotion_genres}")
            
            if args.fast:
                print("⚡ Fast mode: Using sample artwork data...")
                paintings = creator.create_sample_paintings(args.count)
                match_status = ["sample"] * len(paintings)
            else:
                # Try to fetch matching artwork with scoring system
                scored_results = creator.fetch_artwork_by_subject_with_scoring(
                    poem_analysis=poem_analyses[0],
                    q_codes=all_q_codes, 
                    count=args.count,
                    genres=emotion_genres if emotion_genres else None,
                    min_score=args.min_match_score,
                    max_sitelinks=args.max_fame_level
                )
                
                if scored_results:
                    paintings = [painting for painting, score in scored_results]
                    scores = [score for painting, score in scored_results]
                    match_status = ["matched"] * len(paintings)
                    print(f"✅ Found {len(paintings)} high-quality matches (score >= {args.min_match_score})")
                    for i, (painting, score) in enumerate(scored_results):
                        print(f"   - {painting['title']} by {painting['artist']} (match score: {score:.2f})")
                else:
                    print(f"⚠️ No high-quality matches found (score >= {args.min_match_score}), using random obscure artwork")
                    paintings = creator.fetch_paintings(count=args.count, max_sitelinks=args.max_fame_level)
                    match_status = ["fallback"] * len(paintings)
        else:
            print("⚠️ No themes or emotions detected in poems, using random obscure artwork")
            if args.fast:
                paintings = creator.create_sample_paintings(args.count)
                match_status = ["sample"] * len(paintings)
            else:
                paintings = creator.fetch_paintings(count=args.count, max_sitelinks=args.max_fame_level)
                match_status = ["fallback"] * len(paintings)
    
    # Regular mode (paintings first, then poems if requested)
    else:
        # Fetch paintings unless poems-only mode
        if not args.poems_only:
            print(f"🎨 Fetching {args.count} painting{'s' if args.count != 1 else ''}...")
            
            # Get multiple paintings
            if args.fast:
                print("⚡ Fast mode: Using sample data only...")
                paintings = creator.create_sample_paintings(args.count)
            else:
                paintings = creator.fetch_paintings(count=args.count, max_sitelinks=args.max_fame_level)
            
            if not paintings:
                print("❌ Could not fetch paintings from Wikidata.")
                print("💡 Try again later or check your internet connection.")
                print("💡 You can also use --fast flag to use sample data if needed.")
                raise ValueError("Failed to fetch paintings from Wikidata API")
            
            print(f"✅ Selected {len(paintings)} painting{'s' if len(paintings) != 1 else ''}")
            match_status = ["random"] * len(paintings)
        
        # Fetch poems if requested
        if args.poems or args.poems_only:
            if args.email:
                # For email mode, use retry mechanism to ensure we get poems under 200 words
                print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''} for email (≤200 words each)...")
                
                if args.fast:
                    print("⚡ Fast mode: Using sample poem data...")
                    poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
                    # Apply word count filtering to sample poems
                    poems = poem_fetcher_instance.filter_poems_by_word_count(poems, max_words=200)
                else:
                    poems = poem_fetcher_instance.fetch_poems_with_word_limit(args.poem_count, max_words=200)
            else:
                # Regular mode - fetch poems normally
                print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''}...")
                
                if args.fast:
                    print("⚡ Fast mode: Using sample poem data...")
                    poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
                else:
                    poems = poem_fetcher_instance.fetch_random_poems(args.poem_count)
        
        if not poems:
            print("❌ Could not fetch poems from PoetryDB.")
            print("💡 Try again later or check your internet connection.")
            if not args.poems_only:  # Only raise error if poems-only mode
                print("💡 Continuing with artwork only...")
                poems = []
            else:
                raise ValueError("Failed to fetch poems from PoetryDB API")
        else:
            print(f"✅ Selected {len(poems)} poem{'s' if len(poems) != 1 else ''}")
    
    # Define headers to comply with Wikimedia policy
    headers = {
        "User-Agent": "DailyCultureBot/1.0 (https://github.com/yourusername/daily-culture-bot)"
    }
    
    # Download images if requested
    image_paths = []
    if args.save_image and paintings:
        print("📥 Downloading images...")
        for i, painting in enumerate(paintings):
            print(f"  Downloading image {i+1}/{len(paintings)}: {painting['title']}")
            image_path = download_image(painting, headers)
            image_paths.append(image_path)
    
    # Save to JSON if requested
    if args.output:
        if paintings:
            output_filename = f"artwork_{date.today().strftime('%Y%m%d')}.json"
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(paintings, f, indent=2, ensure_ascii=False)
            print(f"📄 Artwork data saved to: {output_filename}")
        
        if poems:
            poem_filename = f"poems_{date.today().strftime('%Y%m%d')}.json"
            with open(poem_filename, 'w', encoding='utf-8') as f:
                json.dump(poems, f, indent=2, ensure_ascii=False)
            print(f"📝 Poems data saved to: {poem_filename}")
    
    
    # Send email if requested
    if args.email:
        print(f"📧 Sending email to {args.email}...")
        
        try:
            # Initialize email sender
            email_sender_instance = email_sender.EmailSender()
            
            # Prepare poem analyses for complementary mode
            poem_analyses = []
            if args.complementary and poems:
                poem_analyses = poem_analyzer_instance.analyze_multiple_poems(poems)
            
            # Download images for email if HTML format is requested
            email_image_paths = []
            if args.email_format in ["html", "both"] and paintings:
                print("📥 Downloading images for email...")
                for i, painting in enumerate(paintings):
                    print(f"  Downloading image {i+1}/{len(paintings)}: {painting['title']}")
                    image_path = download_image(painting, headers)
                    email_image_paths.append(image_path)
            
            # Send email
            success = email_sender_instance.send_email(
                to_email=args.email,
                paintings=paintings,
                poems=poems,
                email_format=args.email_format,
                match_status=match_status,
                poem_analyses=poem_analyses,
                image_paths=email_image_paths
            )
            
            if success:
                print(f"✅ Email sent successfully to {args.email}")
            else:
                print(f"❌ Failed to send email to {args.email}")
                print("💡 Check your SMTP configuration and try again")
                
        except ValueError as e:
            print(f"❌ Email configuration error: {e}")
            print("💡 Please check your environment variables (SMTP_HOST, SMTP_USERNAME, etc.)")
        except Exception as e:
            print(f"❌ Unexpected error sending email: {e}")
            print("💡 Email feature will be skipped, continuing with normal workflow...")
    
    # Display artwork information
    if paintings:
        print("\n" + "="*80)
        print("ARTWORK INFORMATION")
        print("="*80)
        
        for i, painting in enumerate(paintings):
            print(f"\n{i+1}. 🎨 {painting['title']} by {painting['artist']} ({painting['year']})")
            print(f"   Style: {painting['style']} | Medium: {painting['medium']}")
            print(f"   Museum: {painting['museum']} | Origin: {painting['origin']}")
            if i < len(image_paths) and image_paths[i]:
                print(f"   🖼️ Local image: {image_paths[i]}")
            else:
                print(f"   🖼️ Image URL: {painting['image']}")
    
    # Display poem information
    if poems:
        print("\n" + "="*80)
        print("POEM INFORMATION")
        print("="*80)
        
        for i, poem in enumerate(poems):
            lifespan = f" {poem.get('poet_lifespan', '')}" if poem.get('poet_lifespan') else ''
            print(f"\n{i+1}. 📝 {poem['title']} by {poem['author']}{lifespan}")
            print(f"   Lines: {poem['line_count']} | Source: {poem['source']}")
            print(f"   Text preview: {poem['text'][:100]}...")
    
    print("\n" + "="*80)
    print("✅ Culture information retrieved successfully!")

if __name__ == "__main__":
    main()