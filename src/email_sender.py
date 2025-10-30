#!/usr/bin/env python3
"""
Email Sender for Daily Culture Bot

This module handles sending artwork and poem content via SMTP.
Supports both HTML and plain text email formats with image attachments.
"""

import smtplib
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
from typing import List, Dict, Optional, Union
import tempfile
import requests


class EmailSender:
    """Handles email sending for artwork and poem content."""
    
    def __init__(self):
        """Initialize email sender with SMTP configuration from environment."""
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_username)
        
        # Auto-detect SSL/TLS based on port
        self.use_ssl = self.smtp_port == 465
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required SMTP configuration is present."""
        required_vars = ['SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _download_image(self, image_url: str, headers: Dict[str, str]) -> Optional[str]:
        """Download image from URL and return local path."""
        try:
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(response.content)
                return tmp_file.name
        except Exception as e:
            print(f"⚠️ Warning: Could not download image {image_url}: {e}")
            return None
    
    def build_html_email(self, paintings: List[Dict], poems: List[Dict], 
                        match_status: Optional[List[str]] = None,
                        poem_analyses: Optional[List[Dict]] = None,
                        match_explanations: Optional[List[Dict]] = None) -> str:
        """Build HTML email content."""
        today = date.today().strftime('%B %d, %Y')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Culture Delivery - {today}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.9;
        }}
        .artwork-section, .poem-section {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .artwork-item, .poem-item {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .artwork-item:last-child, .poem-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        .artwork-image {{
            text-align: center;
            margin: 15px 0;
        }}
        .artwork-image img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .artwork-title, .poem-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .artwork-artist, .poem-author {{
            font-size: 16px;
            color: #667eea;
            margin-bottom: 15px;
        }}
        .artwork-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .detail-item {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}
        .detail-label {{
            font-size: 12px;
            font-weight: bold;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .detail-value {{
            font-size: 14px;
            color: #333;
        }}
        .artwork-links {{
            margin-top: 15px;
        }}
        .artwork-links a {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
            font-size: 14px;
        }}
        .poem-text {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-family: Georgia, serif;
            font-size: 16px;
            line-height: 1.8;
            white-space: pre-wrap;
            margin: 15px 0;
        }}
        .poem-meta {{
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }}
        .match-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .match-badge.matched {{
            background: #10b981;
            color: white;
        }}
        .match-badge.fallback {{
            background: #f59e0b;
            color: white;
        }}
        .match-badge.sample {{
            background: #8b5cf6;
            color: white;
        }}
        .poem-themes {{
            background: #e0f2fe;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 14px;
            color: #0369a1;
        }}
        .poem-emotions {{
            background: #fef3c7;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 14px;
            color: #92400e;
        }}
        .match-explanation {{
            background: #f1f5f9;
            padding: 14px;
            border-radius: 8px;
            border-left: 4px solid #0ea5e9;
            margin-top: 10px;
            font-size: 14px;
            color: #334155;
        }}
        .match-explanation .title {{
            font-weight: bold;
            margin-bottom: 6px;
        }}
        .match-explanation .meta {{
            color: #475569;
            margin-bottom: 6px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            color: #666;
        }}
        @media (max-width: 600px) {{
            .artwork-details {{
                grid-template-columns: 1fr;
            }}
            .artwork-links a {{
                display: block;
                margin-bottom: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨📝 Daily Culture Delivery</h1>
        <p>{today}</p>
    </div>
"""
        
        # Add artwork section
        if paintings:
            html_content += f"""
    <div class="artwork-section">
        <h2 class="section-title">🎨 Artwork</h2>
"""
            
            for i, painting in enumerate(paintings):
                # Get match status badge
                status_badge = ""
                if match_status and i < len(match_status):
                    status = match_status[i]
                    if status == "matched":
                        status_badge = '<span class="match-badge matched">🎯 Matched</span>'
                    elif status == "fallback":
                        status_badge = '<span class="match-badge fallback">🎲 Random</span>'
                    elif status == "sample":
                        status_badge = '<span class="match-badge sample">⚡ Sample</span>'
                
                html_content += f"""
        <div class="artwork-item">
            <h3 class="artwork-title">{painting['title']} {status_badge}</h3>
            <p class="artwork-artist">by {painting['artist']} ({painting['year'] or 'Unknown year'})</p>
            <div class="artwork-image">
                <img src="cid:artwork_{i}" alt="{painting['title']}" />
            </div>
            {f'<p class="detail-value">{painting.get("description")}</p>' if painting.get('description') else ''}
            
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
            {(
                (lambda exp: f"""
            <div class=\"match-explanation\">
                <div class=\"title\">Why this matches</div>
                <div class=\"meta\">Score: {exp.get('match_score', '')} • {exp.get('overall_assessment', '')}</div>
                <div class=\"body\">{exp.get('why_matched', '')}</div>
            </div>
            """) (match_explanations[i])
            ) if (match_explanations and i < len(match_explanations)) else ''}
        </div>
"""
            
            html_content += "    </div>\n"
        
        # Add poem section
        if poems:
            html_content += f"""
    <div class="poem-section">
        <h2 class="section-title">📝 Poetry</h2>
"""
            
            for i, poem in enumerate(poems):
                # Add theme information if available
                theme_info = ""
                if poem_analyses and i < len(poem_analyses):
                    analysis = poem_analyses[i]
                    if analysis.get("has_themes"):
                        themes = analysis.get("themes", [])
                        if themes:
                            theme_info = f'<div class="poem-themes">🎭 Themes: {", ".join(themes)}</div>'
                    # Emotions (primary) as badges
                    emotions_info = ""
                    primary_emotions = analysis.get("primary_emotions", []) or analysis.get("emotions", [])
                    if primary_emotions:
                        emotions_info = f'<div class="poem-emotions">💗 Emotions: {", ".join(primary_emotions)}</div>'
                    if emotions_info:
                        theme_info = theme_info + emotions_info
                
                html_content += f"""
        <div class="poem-item">
            <h3 class="poem-title">{poem['title']}</h3>
            <p class="poem-author">by {poem['author']}{f" {poem.get('poet_lifespan', '')}" if poem.get('poet_lifespan') else ''}</p>
            {theme_info}
            <div class="poem-text">{poem['text']}</div>
            <div class="poem-meta">
                {poem['line_count']} lines • Source: {poem['source']}
            </div>
        </div>
"""
            
            html_content += "    </div>\n"
        
        html_content += f"""
    <div class="footer">
        <p>Generated by Daily Culture Bot • {date.today().strftime('%Y-%m-%d')}</p>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def build_plain_text_email(self, paintings: List[Dict], poems: List[Dict],
                              match_status: Optional[List[str]] = None,
                              poem_analyses: Optional[List[Dict]] = None) -> str:
        """Build plain text email content."""
        today = date.today().strftime('%B %d, %Y')
        
        text_content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🎨📝 DAILY CULTURE DELIVERY                        ║
║                                    {today:<20} ║
╚══════════════════════════════════════════════════════════════════════════════╝

"""
        
        # Add artwork section
        if paintings:
            text_content += "🎨 ARTWORK\n"
            text_content += "=" * 50 + "\n\n"
            
            for i, painting in enumerate(paintings):
                # Get match status
                status_text = ""
                if match_status and i < len(match_status):
                    status = match_status[i]
                    if status == "matched":
                        status_text = " [🎯 MATCHED]"
                    elif status == "fallback":
                        status_text = " [🎲 RANDOM]"
                    elif status == "sample":
                        status_text = " [⚡ SAMPLE]"
                
                text_content += f"""
{i+1}. {painting['title']}{status_text}
   Artist: {painting['artist']} ({painting['year'] or 'Unknown year'})
   Style: {painting['style']}
   Medium: {painting['medium']}
   Museum: {painting['museum']}
   Origin: {painting['origin']}
   Image: {painting['image']}
   Wikidata: {painting['wikidata']}

"""
        
        # Add poem section
        if poems:
            text_content += "📝 POETRY\n"
            text_content += "=" * 50 + "\n\n"
            
            for i, poem in enumerate(poems):
                # Add theme information if available
                theme_text = ""
                if poem_analyses and i < len(poem_analyses):
                    analysis = poem_analyses[i]
                    if analysis.get("has_themes"):
                        themes = analysis.get("themes", [])
                        if themes:
                            theme_text = f"\n   Themes: {', '.join(themes)}"
                
                text_content += f"""
{i+1}. {poem['title']}
   Author: {poem['author']}{f" {poem.get('poet_lifespan', '')}" if poem.get('poet_lifespan') else ''}{theme_text}
   Lines: {poem['line_count']}
   Source: {poem['source']}

   {poem['text']}

"""
        
        text_content += f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Generated by Daily Culture Bot • {date.today().strftime('%Y-%m-%d'):<20} ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return text_content
    
    def create_multipart_email(self, to_email: str, subject: str, 
                              paintings: List[Dict], poems: List[Dict],
                              email_format: str = "both",
                              match_status: Optional[List[str]] = None,
                              poem_analyses: Optional[List[Dict]] = None,
                              image_paths: Optional[List[str]] = None,
                              match_explanations: Optional[List[Dict]] = None) -> MIMEMultipart:
        """Create multipart email with HTML and/or text content."""
        if not self._validate_email(to_email):
            raise ValueError(f"Invalid email address: {to_email}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = self.smtp_from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Build content based on format
        if email_format in ["text", "both"]:
            text_content = self.build_plain_text_email(paintings, poems, match_status, poem_analyses)
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        if email_format in ["html", "both"]:
            html_content = self.build_html_email(paintings, poems, match_status, poem_analyses, match_explanations)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Add image attachments for HTML emails
        if email_format in ["html", "both"] and image_paths:
            try:
                from PIL import Image
                from io import BytesIO
                
                for i, image_path in enumerate(image_paths):
                    if image_path and os.path.exists(image_path):
                        try:
                            # Resize image to max 800px width to keep email size reasonable
                            with Image.open(image_path) as img:
                                # Calculate new size maintaining aspect ratio
                                max_size = 800
                                if img.width > max_size:
                                    ratio = max_size / img.width
                                    new_height = int(img.height * ratio)
                                    img = img.resize((max_size, new_height), Image.Resampling.LANCZOS)
                                
                                # Save to bytes buffer
                                buffer = BytesIO()
                                img.save(buffer, format='JPEG', quality=85, optimize=True)
                                buffer.seek(0)
                                image_data = buffer.read()
                            
                            # Create image attachment
                            image_part = MIMEImage(image_data)
                            image_part.add_header('Content-ID', f'<artwork_{i}>')
                            image_part.add_header('Content-Disposition', 'inline', filename=f'artwork_{i}.jpg')
                            msg.attach(image_part)
                        except Exception as e:
                            print(f"⚠️ Warning: Could not attach image {image_path}: {e}")
            except ImportError:
                # Pillow not available, skip image attachments
                print("⚠️ Warning: Pillow not available, skipping image attachments to reduce email size")
        
        return msg
    
    def send_email(self, to_email: str, paintings: List[Dict], poems: List[Dict],
                  email_format: str = "both", match_status: Optional[List[str]] = None,
                  poem_analyses: Optional[List[Dict]] = None, 
                  image_paths: Optional[List[str]] = None,
                  match_explanations: Optional[List[Dict]] = None) -> bool:
        """
        Send email with artwork and poem content.
        
        Args:
            to_email: Recipient email address
            paintings: List of painting dictionaries
            poems: List of poem dictionaries
            email_format: "html", "text", or "both" (default: "both")
            match_status: List of match status strings for paintings
            poem_analyses: List of poem analysis dictionaries
            image_paths: List of local image file paths for attachments
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Validate email format
            if email_format not in ["html", "text", "both"]:
                raise ValueError(f"Invalid email format: {email_format}. Must be 'html', 'text', or 'both'")
            
            # Create subject
            today = date.today().strftime('%B %d, %Y')
            subject = f"Daily Culture Delivery - {today}"
            
            # Create email message
            msg = self.create_multipart_email(
                to_email, subject, paintings, poems, email_format,
                match_status, poem_analyses, image_paths, match_explanations
            )
            
            # Send email
            if self.use_ssl:
                # Use SSL (port 465)
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # Use TLS (port 587)
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
