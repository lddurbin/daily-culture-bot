import json
import requests
import os
import tempfile
from datetime import date
import datacreator
import poem_fetcher
import poem_analyzer
import email_sender
import sys
import argparse
import re

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Daily Culture Bot - Fetch and display artwork and poem information')
    parser.add_argument('--output', '-o', action='store_true', help='Save artwork data to JSON file')
    parser.add_argument('--save-image', '-i', action='store_true', help='Download and save artwork images')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of artworks to fetch (default: 1)')
    parser.add_argument('--html', action='store_true', help='Generate HTML gallery page')
    parser.add_argument('--fast', action='store_true', help='Skip Wikidata API and use sample data only (much faster)')
    parser.add_argument('--poems', '-p', action='store_true', help='Also fetch random poems')
    parser.add_argument('--poem-count', type=int, default=1, help='Number of poems to fetch (default: 1)')
    parser.add_argument('--poems-only', action='store_true', help='Fetch only poems, no artwork')
    parser.add_argument('--complementary', action='store_true', help='Match artwork to poem themes (automatically enables --poems)')
    parser.add_argument('--email', help='Email address to send content to (enables email feature)')
    parser.add_argument('--email-format', choices=['html', 'text', 'both'], default='both', 
                       help='Email format: html, text, or both (default: both)')
    
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

def generate_html_gallery(paintings, image_paths, poems=None, match_status=None, poem_analyses=None, output_filename="artwork_gallery.html"):
    """Generate an HTML gallery page for the artworks."""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Artwork Gallery - {date.today().strftime('%B %d, %Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
        }}
        
        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.2rem;
            color: #a0a0a0;
            font-weight: 300;
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }}
        
        .artwork {{
            background: #1a1a1a;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid #2a2a2a;
        }}
        
        .artwork:hover {{
            transform: translateY(-8px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
            border-color: #667eea;
        }}
        
        .artwork-image {{
            position: relative;
            height: 300px;
            overflow: hidden;
        }}
        
        .artwork-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .artwork:hover .artwork-image img {{
            transform: scale(1.05);
        }}
        
        .artwork-info {{
            padding: 1.5rem;
        }}
        
        .artwork-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}
        
        .artwork-artist {{
            font-size: 1rem;
            color: #667eea;
            margin-bottom: 1rem;
            font-weight: 500;
        }}
        
        .artwork-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        
        .detail-item {{
            background: #2a2a2a;
            padding: 0.75rem;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}
        
        .detail-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }}
        
        .detail-value {{
            font-size: 0.9rem;
            color: #ffffff;
            font-weight: 400;
        }}
        
        .artwork-links {{
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
        }}
        
        .artwork-links a {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1rem;
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
            flex: 1;
            text-align: center;
        }}
        
        .artwork-links a:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid #2a2a2a;
            color: #a0a0a0;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .gallery {{
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }}
            
            .artwork-details {{
                grid-template-columns: 1fr;
            }}
            
            .artwork-links {{
                flex-direction: column;
            }}
        }}
        
        /* Loading animation */
        .artwork-image::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            z-index: 1;
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        
        .artwork-image img {{
            position: relative;
            z-index: 2;
        }}
        
        /* Poems Section Styles */
        .poems-section {{
            margin-top: 4rem;
            padding-top: 3rem;
            border-top: 2px solid #2a2a2a;
        }}
        
        .poems-title {{
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .poems-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
        }}
        
        .poem-card {{
            background: #1a1a1a;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid #2a2a2a;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .poem-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
            border-color: #667eea;
        }}
        
        .poem-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}
        
        .poem-author {{
            font-size: 1rem;
            color: #667eea;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }}
        
        .poem-text {{
            margin-bottom: 1.5rem;
        }}
        
        .poem-text pre {{
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 1rem;
            line-height: 1.6;
            color: #e0e0e0;
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #0f0f0f;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 0;
        }}
        
        .poem-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: #a0a0a0;
        }}
        
        .poem-lines {{
            background: #2a2a2a;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 500;
        }}
        
        .poem-source {{
            font-style: italic;
        }}
        
        .poem-themes {{
            background: #2a2a2a;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 0.9rem;
            color: #667eea;
            font-weight: 500;
            border-left: 3px solid #667eea;
        }}
        
        /* Match Status Badges */
        .match-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
            vertical-align: middle;
        }}
        
        .match-badge.matched {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }}
        
        .match-badge.fallback {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }}
        
        .match-badge.sample {{
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .poems-container {{
                grid-template-columns: 1fr;
            }}
            
            .poem-card {{
                padding: 1.5rem;
            }}
            
            .poems-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Daily Culture Gallery</h1>
            <p>{date.today().strftime('%B %d, %Y')} • {len(paintings)} Artwork{'s' if len(paintings) != 1 else ''}{f' • {len(poems)} Poem{"s" if len(poems) != 1 else ""}' if poems else ''}</p>
        </div>
        
        <div class="gallery">"""
    
    for i, painting in enumerate(paintings):
        image_path = image_paths[i] if i < len(image_paths) and image_paths[i] else None
        image_src = f"./{os.path.basename(image_path)}" if image_path else painting['image']
        
        # Get match status and themes for this artwork
        status = match_status[i] if match_status and i < len(match_status) else "unknown"
        status_badge = ""
        if status == "matched":
            status_badge = '<span class="match-badge matched">🎯 Matched to Poem</span>'
        elif status == "fallback":
            status_badge = '<span class="match-badge fallback">🎲 Random Selection</span>'
        elif status == "sample":
            status_badge = '<span class="match-badge sample">⚡ Sample Data</span>'
        
        html_content += f"""
            <div class="artwork">
                <div class="artwork-image">
                    <img src="{image_src}" alt="{painting['title']}" loading="lazy">
                </div>
                <div class="artwork-info">
                    <h2 class="artwork-title">{painting['title']} {status_badge}</h2>
                    <p class="artwork-artist">by {painting['artist']} ({painting['year'] or 'Unknown year'})</p>
                    
                    <div class="artwork-details">
                        <div class="detail-item">
                            <div class="detail-label">Style</div>
                            <div class="detail-value">{painting['style']}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Medium</div>
                            <div class="detail-value">{painting['medium']}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Museum</div>
                            <div class="detail-value">{painting['museum']}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Origin</div>
                            <div class="detail-value">{painting['origin']}</div>
                        </div>
                    </div>
                    
                    <div class="artwork-links">
                        <a href="{painting['image']}" target="_blank">View Original</a>
                        <a href="{painting['wikidata']}" target="_blank">Wikidata</a>
                    </div>
                </div>
            </div>"""
    
    html_content += f"""
        </div>"""
    
    # Add poems section if poems are provided
    if poems:
        html_content += f"""
        
        <div class="poems-section">
            <h2 class="poems-title">📝 Daily Poems</h2>
            <div class="poems-container">"""
        
        for i, poem in enumerate(poems):
            # Add theme information if available
            theme_info = ""
            if poem_analyses and i < len(poem_analyses):
                analysis = poem_analyses[i]
                if analysis.get("has_themes"):
                    themes = analysis.get("themes", [])
                    if themes:
                        theme_info = f'<div class="poem-themes">🎭 Themes: {", ".join(themes)}</div>'
            
            html_content += f"""
                <div class="poem-card">
                    <h3 class="poem-title">{poem['title']}</h3>
                    <p class="poem-author">by {poem['author']}</p>
                    {theme_info}
                    <div class="poem-text">
                        <pre>{poem['text']}</pre>
                    </div>
                    <div class="poem-meta">
                        <span class="poem-lines">{poem['line_count']} lines</span>
                        <span class="poem-source">{poem['source']}</span>
                    </div>
                </div>"""
        
        html_content += f"""
            </div>
        </div>"""
    
    html_content += f"""
        
        <div class="footer">
            <p>Generated by Daily Culture Bot • {date.today().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_filename

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
    creator = datacreator.PaintingDataCreator()
    poem_fetcher_instance = poem_fetcher.PoemFetcher()
    poem_analyzer_instance = poem_analyzer.PoemAnalyzer()
    
    paintings = []
    poems = []
    match_status = []  # Track which paintings were matched vs fallback
    
    # Handle complementary mode (poems first, then match artwork)
    if args.complementary:
        print(f"🎭 Complementary mode: Fetching poems first, then matching artwork...")
        
        # Fetch poems first
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
        print("🔍 Analyzing poem themes...")
        poem_analyses = poem_analyzer_instance.analyze_multiple_poems(poems)
        
        # Get combined Q-codes from all poems
        all_q_codes = poem_analyzer_instance.get_combined_q_codes(poem_analyses)
        
        if all_q_codes:
            print(f"🎨 Searching for artwork matching themes: {all_q_codes}")
            
            if args.fast:
                print("⚡ Fast mode: Using sample artwork data...")
                paintings = creator.create_sample_paintings(args.count)
                match_status = ["sample"] * len(paintings)
            else:
                # Try to fetch matching artwork
                paintings = creator.fetch_paintings_by_subject(all_q_codes, count=args.count)
                
                if paintings:
                    match_status = ["matched"] * len(paintings)
                    print(f"✅ Found {len(paintings)} artwork{'s' if len(paintings) != 1 else ''} matching poem themes")
                else:
                    print("⚠️ No artwork found matching poem themes, using random artwork")
                    paintings = creator.fetch_paintings(count=args.count)
                    match_status = ["fallback"] * len(paintings)
        else:
            print("⚠️ No themes detected in poems, using random artwork")
            if args.fast:
                paintings = creator.create_sample_paintings(args.count)
                match_status = ["sample"] * len(paintings)
            else:
                paintings = creator.fetch_paintings(count=args.count)
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
                paintings = creator.fetch_paintings(count=args.count)
            
            if not paintings:
                print("❌ Could not fetch paintings from Wikidata.")
                print("💡 Try again later or check your internet connection.")
                print("💡 You can also use --fast flag to use sample data if needed.")
                raise ValueError("Failed to fetch paintings from Wikidata API")
            
            print(f"✅ Selected {len(paintings)} painting{'s' if len(paintings) != 1 else ''}")
            match_status = ["random"] * len(paintings)
        
        # Fetch poems if requested
        if args.poems or args.poems_only:
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
    
    # Generate HTML gallery if requested
    if args.html:
        # Prepare additional data for complementary mode
        poem_analyses = []
        if args.complementary and poems:
            poem_analyses = poem_analyzer_instance.analyze_multiple_poems(poems)
        
        html_filename = generate_html_gallery(paintings, image_paths, poems, match_status, poem_analyses)
        print(f"🌐 HTML gallery saved to: {html_filename}")
    
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
            print(f"\n{i+1}. 📝 {poem['title']} by {poem['author']}")
            print(f"   Lines: {poem['line_count']} | Source: {poem['source']}")
            print(f"   Text preview: {poem['text'][:100]}...")
    
    print("\n" + "="*80)
    print("✅ Culture information retrieved successfully!")
    
    if args.html:
        print(f"\n🌐 Open {html_filename} in your browser to view the gallery!")

if __name__ == "__main__":
    main()