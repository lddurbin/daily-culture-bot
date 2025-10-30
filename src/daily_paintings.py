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

# Structured logging setup
try:
    from . import logging_config, context as run_context
except ImportError:
    import logging_config  # type: ignore
    import context as run_context  # type: ignore

logging_config.configure_logging()
_base_logger = logging_config.get_logger(__name__)

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
    parser.add_argument('--no-vision', action='store_true',
                       help='Disable GPT-4 Vision analysis for artwork images')
    parser.add_argument('--vision-candidates', type=int, default=6,
                       help='Number of top candidates to analyze with vision (default: 6, 0 = analyze all)')
    parser.add_argument('--no-multi-pass', action='store_true',
                       help='Disable multi-pass analysis (skip AI-driven candidate selection)')
    parser.add_argument('--candidate-count', type=int, default=6,
                       help='Number of candidate artworks to fetch for multi-pass analysis (default: 6)')
    parser.add_argument('--explain-matches', action='store_true',
                       help='Generate detailed explanations for artwork-poem matches')
    
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
    # Seed correlation id for this run
    cid = run_context.new_correlation_id()
    logger = _base_logger.bind(correlation_id=cid)
    
    # Validate complementary mode constraints
    if args.complementary and args.poems_only:
        logger.error("invalid_cli_flags", complementary=args.complementary, poems_only=args.poems_only)
        print("❌ Error: --complementary and --poems-only cannot be used together")
        print("💡 Use --complementary to match artwork to poems, or --poems-only for poems only")
        return
    
    # Auto-enable poems when using complementary mode
    if args.complementary and not args.poems:
        args.poems = True
        logger.info("complementary_auto_enable_poems")
        print("📝 Complementary mode automatically enabled poem fetching")
    
    # Initialize the data creators
    creator = datacreator.PaintingDataCreator(query_timeout=args.query_timeout)
    poem_fetcher_instance = poem_fetcher.PoemFetcher(enable_poet_dates=not args.no_poet_dates)
    poem_analyzer_instance = poem_analyzer.PoemAnalyzer()
    
    # Initialize match explainer for complementary mode
    match_explainer = None
    try:
        try:
            from . import match_explainer
        except ImportError:
            import match_explainer
        match_explainer = match_explainer.MatchExplainer()
        logger.info("match_explainer_initialized")
        print("✅ Match explainer initialized")
    except ImportError:
        logger.warning("match_explainer_missing")
        print("⚠️ Match explainer not available")
    
    paintings = []
    poems = []
    match_status = []  # Track which paintings were matched vs fallback
    match_explanations = []  # Store match explanations for each artwork
    
    # Handle complementary mode (poems first, then match artwork)
    if args.complementary:
        logger.info("mode_complementary_start")
        print(f"🎭 Complementary mode: Fetching poems first, then matching artwork...")
        
        # Fetch poems first
        if args.email:
            # For email mode, use retry mechanism to ensure we get poems under 300 words
            logger.info("fetch_poems_for_email", poem_count=args.poem_count)
            print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''} for email (≤300 words each)...")
            
            if args.fast:
                logger.info("fast_mode_poems")
                print("⚡ Fast mode: Using sample poem data...")
                poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
                # Apply word count filtering to sample poems
                poems = poem_fetcher_instance.filter_poems_by_word_count(poems, max_words=300)
            else:
                poems = poem_fetcher_instance.fetch_poems_with_word_limit(args.poem_count, max_words=300)
        else:
            # Regular complementary mode - fetch poems normally
            logger.info("fetch_poems", poem_count=args.poem_count)
            print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''}...")
            
            if args.fast:
                logger.info("fast_mode_poems")
                print("⚡ Fast mode: Using sample poem data...")
                poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
            else:
                poems = poem_fetcher_instance.fetch_random_poems(args.poem_count)
        
        if not poems:
            logger.error("poetrydb_fetch_failed")
            print("❌ Could not fetch poems from PoetryDB.")
            print("💡 Try again later or check your internet connection.")
            raise ValueError("Failed to fetch poems from PoetryDB API")
        
        logger.info("poems_selected", count=len(poems))
        print(f"✅ Selected {len(poems)} poem{'s' if len(poems) != 1 else ''}")
        
        # Analyze poems and fetch matching artwork
        logger.info("analyze_poems_start")
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
        # Fallback: derive Q-codes from concrete elements and subject suggestions if still empty
        if not all_q_codes and poem_analyses:
            try:
                try:
                    from . import poem_themes as _pt
                except ImportError:
                    import poem_themes as _pt
                object_map = getattr(_pt, "OBJECT_MAPPINGS", {})
                concrete = poem_analyses[0].get("concrete_elements", {}) or {}
                suggestions = poem_analyses[0].get("subject_suggestions", []) or []
                derived = []
                for cat in ("natural_objects", "man_made_objects", "living_beings", "abstract_concepts"):
                    for term in concrete.get(cat, []) or []:
                        if isinstance(term, str) and term.lower() in object_map:
                            derived.extend(object_map[term.lower()]["q_codes"])
                for term in suggestions:
                    if isinstance(term, str):
                        key = term.lower().strip()
                        if key in object_map:
                            derived.extend(object_map[key]["q_codes"])
                if derived:
                    all_q_codes.extend(derived)
            except Exception:
                pass
        # De-duplicate
        all_q_codes = list(set(all_q_codes))
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
            logger.info("search_artworks", q_codes=all_q_codes, genres=emotion_genres)
            print(f"\n🎨 Searching for artwork matching themes and emotions: {all_q_codes}")
            if emotion_genres:
                print(f"   With genre filtering: {emotion_genres}")
            
            if args.fast:
                logger.info("fast_mode_artworks")
                print("⚡ Fast mode: Using sample artwork data...")
                paintings = creator.create_sample_paintings(args.count)
                match_status = ["sample"] * len(paintings)
            else:
                # Extract poet dates from poem for era-based matching
                poet_birth_year = poems[0].get('poet_birth_year')
                poet_death_year = poems[0].get('poet_death_year')
                
                if poet_birth_year and poet_death_year:
                    print(f"🎭 Era-based matching enabled for poet: {poems[0].get('author')} ({poet_birth_year}-{poet_death_year})")
                
                # Multi-pass analysis: First pass - fetch candidates, Second pass - AI selection
                if not args.no_multi_pass:
                    logger.info("multipass_first_pass_start", candidate_count=candidate_count)
                    print("🔄 Multi-pass analysis: Fetching candidate artworks...")
                    
                    # First pass: Fetch more candidates than needed for better selection
                    candidate_count = max(args.count * 3, args.candidate_count)  # Use CLI flag or default
                    print(f"📋 First pass: Fetching {candidate_count} candidate artworks...")
                else:
                    logger.info("single_pass_start", count=candidate_count)
                    print("⚡ Single-pass analysis: Fetching artwork directly...")
                    candidate_count = args.count
                
                # Pass vision analysis flag to the creator
                enable_vision = not args.no_vision
                if not enable_vision:
                    print("🚫 Vision analysis disabled by --no-vision flag")
                
                scored_candidates = creator.fetch_artwork_by_subject_with_scoring(
                    poem_analysis=poem_analyses[0],
                    q_codes=all_q_codes, 
                    count=candidate_count,
                    genres=emotion_genres if emotion_genres else None,
                    min_score=args.min_match_score * 0.7,  # Lower threshold for candidates
                    max_sitelinks=args.max_fame_level,
                    poet_birth_year=poet_birth_year,
                    poet_death_year=poet_death_year,
                    enable_vision_analysis=enable_vision,
                    vision_candidate_limit=args.vision_candidates if enable_vision else 0
                )
                
                if scored_candidates:
                    if not args.no_multi_pass:
                        print(f"✅ First pass: Found {len(scored_candidates)} candidate artworks")
                        
                        # Second pass: AI-driven selection from candidates
                        print("🤖 Second pass: AI-driven candidate selection...")
                        
                        # Check if OpenAI client is available
                        if not poem_analyzer_instance.openai_client:
                            print("⚠️ AI selection failed: OpenAI client not initialized")
                            print("🔄 Fallback: Using top scored candidates")
                            paintings = [painting for painting, score in scored_candidates[:args.count]]
                            match_status = ["scored"] * len(paintings)
                        else:
                            # Import OpenAI analyzer for second pass
                            try:
                                try:
                                    from . import openai_analyzer
                                except ImportError:
                                    import openai_analyzer
                                openai_analyzer_instance = openai_analyzer.OpenAIAnalyzer(
                                    poem_analyzer_instance.openai_client,
                                    poem_analyzer_instance.theme_mappings,
                                    poem_analyzer_instance.emotion_mappings
                                )
                            except Exception as e:
                                print(f"⚠️ OpenAI analyzer import failed: {e}")
                                # Fallback to top scored candidates
                                paintings = [painting for painting, score in scored_candidates[:args.count]]
                                match_status = ["scored"] * len(paintings)
                                print(f"🔄 Fallback: Using top {len(paintings)} scored candidates")
                            else:
                                # Extract candidate artworks (without scores for AI selection)
                                candidate_artworks = [painting for painting, score in scored_candidates]
                                
                                # Use AI to select best matches
                                ai_selections = openai_analyzer_instance.select_best_artwork_matches(
                                    poem=poems[0],
                                    candidates=candidate_artworks,
                                    count=args.count
                                )
                                
                                if ai_selections:
                                    paintings = [artwork for artwork, reasoning in ai_selections]
                                    match_status = ["ai_selected"] * len(paintings)
                                    print(f"✅ Second pass: AI selected {len(paintings)} best matches")
                                    
                                    # Display AI reasoning
                                    for i, (artwork, reasoning) in enumerate(ai_selections):
                                        print(f"   {i+1}. {artwork['title']} by {artwork['artist']}")
                                        print(f"      AI reasoning: {reasoning}")
                                else:
                                    # Fallback to top scored candidates
                                    paintings = [painting for painting, score in scored_candidates[:args.count]]
                                    match_status = ["scored"] * len(paintings)
                                    print(f"⚠️ AI selection failed, using top scored candidates")
                    else:
                        # Single-pass: Use top scored candidates directly
                        paintings = [painting for painting, score in scored_candidates[:args.count]]
                        match_status = ["scored"] * len(paintings)
                        print(f"✅ Found {len(paintings)} high-quality matches")
                        for i, (painting, score) in enumerate(scored_candidates[:args.count]):
                            print(f"   - {painting['title']} by {painting['artist']} (match score: {score:.2f})")
                    
                    # Generate detailed match explanations for complementary mode
                    if (match_explainer and poems and paintings and 
                        (args.explain_matches or args.complementary)):
                        print("📝 Generating detailed match explanations...")
                        poem_analysis = poem_analyses[0]  # Use first poem analysis
                        
                        for i, painting in enumerate(paintings):
                            try:
                                # Calculate match score for explanation
                                artwork_q_codes = painting.get('subject_q_codes', []) + painting.get('vision_q_codes', [])
                                artwork_genres = painting.get('genre_q_codes', [])
                                artwork_year = painting.get('year')
                                
                                match_score = poem_analyzer_instance.score_artwork_match(
                                    poem_analysis,
                                    artwork_q_codes,
                                    artwork_genres,
                                    artwork_year=artwork_year,
                                    poet_birth_year=poet_birth_year,
                                    poet_death_year=poet_death_year
                                )
                                
                                # Generate explanation
                                explanation = match_explainer.explain_match(
                                    poem_analysis=poem_analysis,
                                    artwork=painting,
                                    score=match_score,
                                    vision_analysis=painting.get('vision_analysis')
                                )
                                
                                match_explanations.append(explanation)
                                
                                print(f"   📋 Explanation for {painting['title']}: {explanation['why_matched']}")
                                
                            except Exception as e:
                                print(f"⚠️ Error generating explanation for {painting['title']}: {e}")
                                match_explanations.append({
                                    "match_score": 0.5,
                                    "overall_assessment": "unknown",
                                    "why_matched": "Explanation generation failed",
                                    "specific_connections": [],
                                    "concrete_matches": {},
                                    "potential_tensions": []
                                })
                else:
                    print(f"⚠️ No candidate artworks found, using random obscure artwork")
                    paintings = creator.fetch_paintings(count=args.count, max_sitelinks=args.max_fame_level)
                    match_status = ["fallback"] * len(paintings)
        else:
            print("⚠️ No Q-codes derived from analysis; using random obscure artwork")
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
                # For email mode, use retry mechanism to ensure we get poems under 300 words
                print(f"📝 Fetching {args.poem_count} poem{'s' if args.poem_count != 1 else ''} for email (≤300 words each)...")
                
                if args.fast:
                    print("⚡ Fast mode: Using sample poem data...")
                    poems = poem_fetcher_instance.create_sample_poems(args.poem_count)
                    # Apply word count filtering to sample poems
                    poems = poem_fetcher_instance.filter_poems_by_word_count(poems, max_words=300)
                else:
                    poems = poem_fetcher_instance.fetch_poems_with_word_limit(args.poem_count, max_words=300)
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
            # Include match explanations in artwork output for complementary mode
            output_data = paintings.copy()
            if args.complementary and match_explanations:
                for i, painting in enumerate(output_data):
                    if i < len(match_explanations):
                        painting['match_explanation'] = match_explanations[i]
            
            output_filename = f"artwork_{date.today().strftime('%Y%m%d')}.json"
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"📄 Artwork data saved to: {output_filename}")
        
        if poems:
            poem_filename = f"poems_{date.today().strftime('%Y%m%d')}.json"
            with open(poem_filename, 'w', encoding='utf-8') as f:
                json.dump(poems, f, indent=2, ensure_ascii=False)
            print(f"📝 Poems data saved to: {poem_filename}")
        
        # Save match explanations separately if available
        if args.complementary and match_explanations:
            explanations_filename = f"match_explanations_{date.today().strftime('%Y%m%d')}.json"
            with open(explanations_filename, 'w', encoding='utf-8') as f:
                json.dump(match_explanations, f, indent=2, ensure_ascii=False)
            print(f"📋 Match explanations saved to: {explanations_filename}")
    
    
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
                image_paths=email_image_paths,
                match_explanations=match_explanations
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
            year_str = str(painting.get('year', 'Unknown')) if painting.get('year') else 'Unknown'
            
            # Add era match info if we have poet dates
            era_info = ""
            if args.complementary and poems and len(poems) > 0:
                poet_birth = poems[0].get('poet_birth_year')
                poet_death = poems[0].get('poet_death_year')
                poem_author = poems[0].get('author')
                
                if poet_birth and poet_death and painting.get('year'):
                    era_info = f" (era match with {poem_author}: {poet_birth}-{poet_death})"
            
            print(f"\n{i+1}. 🎨 {painting['title']} by {painting['artist']} ({year_str}{era_info})")
            print(f"   Style: {painting['style']} | Medium: {painting['medium']}")
            print(f"   Museum: {painting['museum']} | Origin: {painting['origin']}")
            if i < len(image_paths) and image_paths[i]:
                print(f"   🖼️ Local image: {image_paths[i]}")
            else:
                print(f"   🖼️ Image URL: {painting['image']}")
            
            # Display match explanation for complementary mode
            if args.complementary and i < len(match_explanations):
                explanation = match_explanations[i]
                print(f"   📋 Match Score: {explanation['match_score']:.2f} ({explanation['overall_assessment']})")
                print(f"   💡 Why matched: {explanation['why_matched']}")
                
                if explanation.get('specific_connections'):
                    print(f"   🔗 Connections: {', '.join(explanation['specific_connections'][:3])}")
                
                if explanation.get('concrete_matches', {}).get('shared_objects'):
                    shared_objects = explanation['concrete_matches']['shared_objects']
                    if shared_objects:
                        print(f"   🎯 Shared elements: {', '.join(shared_objects[:3])}")
                
                if explanation.get('potential_tensions'):
                    print(f"   ⚠️ Potential tensions: {', '.join(explanation['potential_tensions'][:2])}")
    
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