#!/usr/bin/env python3
"""
Tests for Email Sender functionality.

This module tests the email_sender.py module with both mocked tests
and optional integration tests for actual SMTP sending.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open, MagicMock
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Add parent directory to path to import modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import email_sender


class TestEmailSender:
    """Test EmailSender class functionality."""
    
    def setup_method(self):
        """Set up test environment variables."""
        self.test_env = {
            'SMTP_HOST': 'test.smtp.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@example.com',
            'SMTP_PASSWORD': 'testpassword',
            'SMTP_FROM_EMAIL': 'test@example.com'
        }
        
        # Mock environment variables
        with patch.dict(os.environ, self.test_env):
            self.email_sender = email_sender.EmailSender()
    
    def test_init_with_valid_config(self):
        """Test EmailSender initialization with valid configuration."""
        with patch.dict(os.environ, self.test_env):
            sender = email_sender.EmailSender()
            assert sender.smtp_host == 'test.smtp.com'
            assert sender.smtp_port == 587
            assert sender.smtp_username == 'test@example.com'
            assert sender.smtp_password == 'testpassword'
            assert sender.smtp_from_email == 'test@example.com'
            assert sender.use_ssl == False  # Port 587 uses TLS
    
    def test_init_with_ssl_port(self):
        """Test EmailSender initialization with SSL port."""
        ssl_env = self.test_env.copy()
        ssl_env['SMTP_PORT'] = '465'
        
        with patch.dict(os.environ, ssl_env):
            sender = email_sender.EmailSender()
            assert sender.smtp_port == 465
            assert sender.use_ssl == True  # Port 465 uses SSL
    
    def test_init_missing_required_vars(self):
        """Test EmailSender initialization with missing required variables."""
        incomplete_env = {'SMTP_HOST': 'test.com'}  # Missing other required vars
        
        with patch.dict(os.environ, incomplete_env, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                email_sender.EmailSender()
    
    def test_validate_email_valid(self):
        """Test email validation with valid addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            assert self.email_sender._validate_email(email) == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid addresses."""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test@.com',
            'test@example',
            ''
        ]
        
        for email in invalid_emails:
            assert self.email_sender._validate_email(email) == False
    
    def test_download_image_success(self):
        """Test successful image download."""
        mock_response = Mock()
        mock_response.content = b'fake_image_data'
        mock_response.raise_for_status.return_value = None
        
        with patch('email_sender.requests.get', return_value=mock_response):
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                mock_file = Mock()
                mock_file.name = '/tmp/test_image.jpg'
                mock_temp.return_value.__enter__.return_value = mock_file
                
                result = self.email_sender._download_image('http://example.com/image.jpg', {})
                assert result == '/tmp/test_image.jpg'
    
    def test_download_image_failure(self):
        """Test image download failure."""
        with patch('email_sender.requests.get', side_effect=Exception('Network error')):
            result = self.email_sender._download_image('http://example.com/image.jpg', {})
            assert result is None
    
    def test_build_html_email_with_paintings(self):
        """Test HTML email generation with paintings."""
        paintings = [{
            'title': 'Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'http://example.com/image.jpg',
            'wikidata': 'http://wikidata.org/Q123'
        }]
        
        html = self.email_sender.build_html_email(paintings, [])
        
        assert 'Test Painting' in html
        assert 'Test Artist' in html
        assert 'Modern' in html
        assert 'Oil on Canvas' in html
        assert 'Test Museum' in html
        assert 'Test Country' in html
        assert 'http://example.com/image.jpg' in html
        assert 'http://wikidata.org/Q123' in html
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
    
    def test_build_html_email_with_poems(self):
        """Test HTML email generation with poems."""
        poems = [{
            'title': 'Test Poem',
            'author': 'Test Poet',
            'text': 'This is a test poem\nwith multiple lines.',
            'line_count': 2,
            'source': 'Test Source'
        }]
        
        html = self.email_sender.build_html_email([], poems)
        
        assert 'Test Poem' in html
        assert 'Test Poet' in html
        assert 'This is a test poem' in html
        assert '2 lines' in html
        assert 'Test Source' in html
    
    def test_build_html_email_with_match_status(self):
        """Test HTML email generation with match status badges."""
        paintings = [{
            'title': 'Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'http://example.com/image.jpg',
            'wikidata': 'http://wikidata.org/Q123'
        }]
        
        match_status = ['matched']
        html = self.email_sender.build_html_email(paintings, [], match_status)
        
        assert '🎯 Matched' in html
        assert 'match-badge matched' in html
    
    def test_build_html_email_with_poem_themes(self):
        """Test HTML email generation with poem themes."""
        poems = [{
            'title': 'Test Poem',
            'author': 'Test Poet',
            'text': 'This is a test poem.',
            'line_count': 1,
            'source': 'Test Source'
        }]
        
        poem_analyses = [{
            'has_themes': True,
            'themes': ['nature', 'love']
        }]
        
        html = self.email_sender.build_html_email([], poems, None, poem_analyses)
        
        assert '🎭 Themes: nature, love' in html
        assert 'poem-themes' in html
    
    def test_build_plain_text_email_with_paintings(self):
        """Test plain text email generation with paintings."""
        paintings = [{
            'title': 'Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'http://example.com/image.jpg',
            'wikidata': 'http://wikidata.org/Q123'
        }]
        
        text = self.email_sender.build_plain_text_email(paintings, [])
        
        assert 'Test Painting' in text
        assert 'Test Artist' in text
        assert 'Modern' in text
        assert 'Oil on Canvas' in text
        assert 'Test Museum' in text
        assert 'Test Country' in text
        assert 'http://example.com/image.jpg' in text
        assert 'http://wikidata.org/Q123' in text
        assert '🎨 ARTWORK' in text
        assert '=' * 50 in text
    
    def test_build_plain_text_email_with_poems(self):
        """Test plain text email generation with poems."""
        poems = [{
            'title': 'Test Poem',
            'author': 'Test Poet',
            'text': 'This is a test poem\nwith multiple lines.',
            'line_count': 2,
            'source': 'Test Source'
        }]
        
        text = self.email_sender.build_plain_text_email([], poems)
        
        assert 'Test Poem' in text
        assert 'Test Poet' in text
        assert 'This is a test poem' in text
        assert 'Lines: 2' in text
        assert 'Test Source' in text
        assert '📝 POETRY' in text
    
    def test_build_plain_text_email_with_match_status(self):
        """Test plain text email generation with match status."""
        paintings = [{
            'title': 'Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'http://example.com/image.jpg',
            'wikidata': 'http://wikidata.org/Q123'
        }]
        
        match_status = ['matched']
        text = self.email_sender.build_plain_text_email(paintings, [], match_status)
        
        assert '[🎯 MATCHED]' in text
    
    def test_build_plain_text_email_with_poem_themes(self):
        """Test plain text email generation with poem themes."""
        poems = [{
            'title': 'Test Poem',
            'author': 'Test Poet',
            'text': 'This is a test poem.',
            'line_count': 1,
            'source': 'Test Source'
        }]
        
        poem_analyses = [{
            'has_themes': True,
            'themes': ['nature', 'love']
        }]
        
        text = self.email_sender.build_plain_text_email([], poems, None, poem_analyses)
        
        assert 'Themes: nature, love' in text
    
    def test_create_multipart_email_html_only(self):
        """Test multipart email creation with HTML only."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        msg = self.email_sender.create_multipart_email(
            'test@example.com', 'Test Subject', paintings, [], 'html'
        )
        
        assert isinstance(msg, MIMEMultipart)
        assert msg['From'] == 'test@example.com'
        assert msg['To'] == 'test@example.com'
        assert msg['Subject'] == 'Test Subject'
        
        # Check that HTML content is present
        html_parts = [part for part in msg.walk() if part.get_content_type() == 'text/html']
        assert len(html_parts) == 1
        
        # Decode base64 content to check for 'Test'
        import base64
        html_content = base64.b64decode(html_parts[0].get_payload()).decode('utf-8')
        assert 'Test' in html_content
    
    def test_create_multipart_email_text_only(self):
        """Test multipart email creation with text only."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        msg = self.email_sender.create_multipart_email(
            'test@example.com', 'Test Subject', paintings, [], 'text'
        )
        
        assert isinstance(msg, MIMEMultipart)
        
        # Check that text content is present
        text_parts = [part for part in msg.walk() if part.get_content_type() == 'text/plain']
        assert len(text_parts) == 1
        
        # Decode base64 content to check for 'Test'
        import base64
        text_content = base64.b64decode(text_parts[0].get_payload()).decode('utf-8')
        assert 'Test' in text_content
    
    def test_create_multipart_email_both_formats(self):
        """Test multipart email creation with both HTML and text."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        msg = self.email_sender.create_multipart_email(
            'test@example.com', 'Test Subject', paintings, [], 'both'
        )
        
        assert isinstance(msg, MIMEMultipart)
        
        # Check that both HTML and text content are present
        html_parts = [part for part in msg.walk() if part.get_content_type() == 'text/html']
        text_parts = [part for part in msg.walk() if part.get_content_type() == 'text/plain']
        assert len(html_parts) == 1
        assert len(text_parts) == 1
    
    def test_create_multipart_email_invalid_email(self):
        """Test multipart email creation with invalid email address."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        with pytest.raises(ValueError, match="Invalid email address"):
            self.email_sender.create_multipart_email(
                'invalid-email', 'Test Subject', paintings, []
            )
    
    def test_create_multipart_email_with_image_attachments(self):
        """Test multipart email creation with image attachments."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        # Create temporary image files
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp1:
            # Write a minimal JPEG header to make it a valid image file
            tmp1.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9')
            image_path1 = tmp1.name
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp2:
            # Write a minimal JPEG header to make it a valid image file
            tmp2.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9')
            image_path2 = tmp2.name
        
        try:
            msg = self.email_sender.create_multipart_email(
                'test@example.com', 'Test Subject', paintings, [], 'html',
                image_paths=[image_path1, image_path2]
            )
            
            # Check that image attachments are present
            image_parts = [part for part in msg.walk() if part.get_content_type().startswith('image/')]
            assert len(image_parts) == 2
            
            # Check Content-ID headers
            content_ids = [part.get('Content-ID') for part in image_parts]
            assert '<artwork_0>' in content_ids
            assert '<artwork_1>' in content_ids
            
        finally:
            # Clean up temporary files
            os.unlink(image_path1)
            os.unlink(image_path2)
    
    @patch('email_sender.smtplib.SMTP')
    def test_send_email_success_tls(self, mock_smtp_class):
        """Test successful email sending with TLS."""
        mock_server = Mock()
        mock_smtp_class.return_value = mock_server
        
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        result = self.email_sender.send_email(
            'test@example.com', paintings, [], 'both'
        )
        
        assert result == True
        mock_smtp_class.assert_called_once_with('test.smtp.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'testpassword')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('email_sender.smtplib.SMTP_SSL')
    def test_send_email_success_ssl(self, mock_smtp_ssl_class):
        """Test successful email sending with SSL."""
        # Set up SSL configuration
        ssl_env = self.test_env.copy()
        ssl_env['SMTP_PORT'] = '465'
        
        with patch.dict(os.environ, ssl_env):
            sender = email_sender.EmailSender()
        
        mock_server = Mock()
        mock_smtp_ssl_class.return_value = mock_server
        
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        result = sender.send_email('test@example.com', paintings, [], 'both')
        
        assert result == True
        mock_smtp_ssl_class.assert_called_once_with('test.smtp.com', 465)
        mock_server.login.assert_called_once_with('test@example.com', 'testpassword')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('email_sender.smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp_class):
        """Test email sending with SMTP error."""
        mock_smtp_class.side_effect = smtplib.SMTPException('SMTP Error')
        
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        result = self.email_sender.send_email('test@example.com', paintings, [])
        
        assert result == False
    
    def test_send_email_invalid_format(self):
        """Test email sending with invalid format."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        result = self.email_sender.send_email('test@example.com', paintings, [], 'invalid')
        assert result == False
    
    def test_send_email_invalid_email_address(self):
        """Test email sending with invalid email address."""
        paintings = [{'title': 'Test', 'artist': 'Artist', 'year': '2023', 
                    'style': 'Modern', 'medium': 'Oil', 'museum': 'Museum', 
                    'origin': 'Country', 'image': 'http://example.com/image.jpg', 
                    'wikidata': 'http://wikidata.org/Q123'}]
        
        result = self.email_sender.send_email('invalid-email', paintings, [])
        
        assert result == False


@pytest.mark.skipif(
    os.getenv('TEST_EMAIL_INTEGRATION') != 'true',
    reason="Integration tests require TEST_EMAIL_INTEGRATION=true"
)
class TestEmailIntegration:
    """Integration tests for actual email sending."""
    
    def setup_method(self):
        """Set up integration test environment."""
        # Check if integration test environment is configured
        required_vars = ['SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'TEST_EMAIL_ADDRESS']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            pytest.skip(f"Missing required environment variables for integration tests: {missing}")
        
        # Use test environment variables
        self.test_env = {
            'SMTP_HOST': os.getenv('SMTP_HOST'),
            'SMTP_PORT': os.getenv('SMTP_PORT', '587'),
            'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
            'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
            'SMTP_FROM_EMAIL': os.getenv('SMTP_FROM_EMAIL', os.getenv('SMTP_USERNAME'))
        }
        
        with patch.dict(os.environ, self.test_env):
            self.email_sender = email_sender.EmailSender()
        
        self.test_email = os.getenv('TEST_EMAIL_ADDRESS')
    
    def test_send_real_email_text_only(self):
        """Test sending real email with text format only."""
        paintings = [{
            'title': 'Integration Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png',
            'wikidata': 'https://www.wikidata.org/wiki/Q123'
        }]
        
        result = self.email_sender.send_email(
            self.test_email, paintings, [], 'text'
        )
        
        assert result == True
    
    def test_send_real_email_html_only(self):
        """Test sending real email with HTML format only."""
        paintings = [{
            'title': 'Integration Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png',
            'wikidata': 'https://www.wikidata.org/wiki/Q123'
        }]
        
        result = self.email_sender.send_email(
            self.test_email, paintings, [], 'html'
        )
        
        assert result == True
    
    def test_send_real_email_both_formats(self):
        """Test sending real email with both HTML and text formats."""
        paintings = [{
            'title': 'Integration Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png',
            'wikidata': 'https://www.wikidata.org/wiki/Q123'
        }]
        
        poems = [{
            'title': 'Integration Test Poem',
            'author': 'Test Poet',
            'text': 'This is an integration test poem\nwith multiple lines.',
            'line_count': 2,
            'source': 'Integration Test Source'
        }]
        
        result = self.email_sender.send_email(
            self.test_email, paintings, poems, 'both'
        )
        
        assert result == True
    
    def test_send_real_email_with_complementary_data(self):
        """Test sending real email with complementary mode data."""
        paintings = [{
            'title': 'Integration Test Painting',
            'artist': 'Test Artist',
            'year': '2023',
            'style': 'Modern',
            'medium': 'Oil on Canvas',
            'museum': 'Test Museum',
            'origin': 'Test Country',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png',
            'wikidata': 'https://www.wikidata.org/wiki/Q123'
        }]
        
        poems = [{
            'title': 'Integration Test Poem',
            'author': 'Test Poet',
            'text': 'This is an integration test poem about nature and love.',
            'line_count': 1,
            'source': 'Integration Test Source'
        }]
        
        match_status = ['matched']
        poem_analyses = [{
            'has_themes': True,
            'themes': ['nature', 'love']
        }]
        
        result = self.email_sender.send_email(
            self.test_email, paintings, poems, 'both',
            match_status, poem_analyses
        )
        
        assert result == True
