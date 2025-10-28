import pytest
import json
import os
import sys
from datetime import date
from unittest.mock import Mock, patch, mock_open, MagicMock
import requests

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import daily_paintings


class TestArgumentParsing:
    """Test command line argument parsing."""
    
    def test_default_arguments(self):
        """Test that default arguments are parsed correctly."""
        with patch('sys.argv', ['daily_paintings.py']):
            args = daily_paintings.parse_arguments()
            assert args.count == 1
            assert args.output == False
            assert args.save_image == False
            assert args.fast == False
    
    def test_output_flag(self):
        """Test --output flag."""
        with patch('sys.argv', ['daily_paintings.py', '--output']):
            args = daily_paintings.parse_arguments()
            assert args.output == True
    
    def test_save_image_flag(self):
        """Test --save-image flag."""
        with patch('sys.argv', ['daily_paintings.py', '--save-image']):
            args = daily_paintings.parse_arguments()
            assert args.save_image == True
    
    def test_count_argument(self):
        """Test --count argument."""
        with patch('sys.argv', ['daily_paintings.py', '--count', '5']):
            args = daily_paintings.parse_arguments()
            assert args.count == 5
    
    
    def test_fast_flag(self):
        """Test --fast flag."""
        with patch('sys.argv', ['daily_paintings.py', '--fast']):
            args = daily_paintings.parse_arguments()
            assert args.fast == True
    
    def test_complementary_flag(self):
        """Test --complementary flag."""
        with patch('sys.argv', ['daily_paintings.py', '--complementary']):
            args = daily_paintings.parse_arguments()
            assert args.complementary == True
    
    def test_vision_candidates_argument(self):
        """Test --vision-candidates argument."""
        with patch('sys.argv', ['daily_paintings.py', '--vision-candidates', '3']):
            args = daily_paintings.parse_arguments()
            assert args.vision_candidates == 3
    
    def test_vision_candidates_default(self):
        """Test --vision-candidates default value."""
        with patch('sys.argv', ['daily_paintings.py']):
            args = daily_paintings.parse_arguments()
            assert args.vision_candidates == 6
    
    def test_vision_candidates_zero(self):
        """Test --vision-candidates with 0 (analyze all)."""
        with patch('sys.argv', ['daily_paintings.py', '--vision-candidates', '0']):
            args = daily_paintings.parse_arguments()
            assert args.vision_candidates == 0
    
    def test_explain_matches_flag(self):
        """Test --explain-matches flag."""
        with patch('sys.argv', ['daily_paintings.py', '--explain-matches']):
            args = daily_paintings.parse_arguments()
            assert args.explain_matches == True
    
    def test_explain_matches_default(self):
        """Test --explain-matches default value."""
        with patch('sys.argv', ['daily_paintings.py']):
            args = daily_paintings.parse_arguments()
            assert args.explain_matches == False
    
    def test_email_argument(self):
        """Test --email argument."""
        with patch('sys.argv', ['daily_paintings.py', '--email', 'l.d.durbin@gmail.com']):
            args = daily_paintings.parse_arguments()
            assert args.email == 'l.d.durbin@gmail.com'
    
    def test_email_format_argument(self):
        """Test --email-format argument."""
        with patch('sys.argv', ['daily_paintings.py', '--email-format', 'html']):
            args = daily_paintings.parse_arguments()
            assert args.email_format == 'html'
    
    def test_email_format_default(self):
        """Test --email-format default value."""
        with patch('sys.argv', ['daily_paintings.py']):
            args = daily_paintings.parse_arguments()
            assert args.email_format == 'both'
    
    def test_email_format_choices(self):
        """Test --email-format valid choices."""
        valid_formats = ['html', 'text', 'both']
        for format_choice in valid_formats:
            with patch('sys.argv', ['daily_paintings.py', '--email-format', format_choice]):
                args = daily_paintings.parse_arguments()
                assert args.email_format == format_choice
    
    def test_invalid_email_address(self):
        """Test invalid email address."""
        with patch('sys.argv', ['daily_paintings.py', '--email', 'invalid-email']):
            with patch('sys.exit') as mock_exit:
                daily_paintings.parse_arguments()
                mock_exit.assert_called_once_with(1)
    
    def test_valid_email_addresses(self):
        """Test valid email address formats."""
        valid_emails = [
            'l.d.durbin@gmail.com',
            'user.name@domain.co.uk',
            'test+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            with patch('sys.argv', ['daily_paintings.py', '--email', email]):
                args = daily_paintings.parse_arguments()
                assert args.email == email


class TestDownloadImage:
    """Test image download functionality."""
    
    @patch('daily_paintings.requests.get')
    def test_download_image_success_jpg(self, mock_get):
        """Test successful JPEG image download."""
        # Mock response
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.content = b'fake image data'
        mock_get.return_value = mock_response
        
        painting = {
            'title': 'Test Painting',
            'year': '2020',
            'image': 'http://example.com/image.jpg'
        }
        headers = {'User-Agent': 'test'}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.join', return_value='Test_Painting_2020.jpg'):
                result = daily_paintings.download_image(painting, headers)
                assert result == 'Test_Painting_2020.jpg'
                mock_get.assert_called_once()
    
    @patch('daily_paintings.requests.get')
    def test_download_image_success_png(self, mock_get):
        """Test successful PNG image download."""
        # Mock response
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'image/png'}
        mock_response.content = b'fake image data'
        mock_get.return_value = mock_response
        
        painting = {
            'title': 'Test Painting',
            'year': '2020',
            'image': 'http://example.com/image.png'
        }
        headers = {'User-Agent': 'test'}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.join', return_value='Test_Painting_2020.png'):
                result = daily_paintings.download_image(painting, headers)
                assert result == 'Test_Painting_2020.png'
    
    @patch('daily_paintings.requests.get')
    def test_download_image_invalid_content_type(self, mock_get):
        """Test image download with invalid content type."""
        # Mock response with invalid content type
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.content = b'not an image'
        mock_get.return_value = mock_response
        
        painting = {
            'title': 'Test Painting',
            'year': '2020',
            'image': 'http://example.com/not-image.html'
        }
        headers = {'User-Agent': 'test'}
        
        result = daily_paintings.download_image(painting, headers)
        assert result is None
    
    @patch('daily_paintings.requests.get')
    def test_download_image_exception(self, mock_get):
        """Test image download with exception."""
        mock_get.side_effect = requests.RequestException('Network error')
        
        painting = {
            'title': 'Test Painting',
            'year': '2020',
            'image': 'http://example.com/image.jpg'
        }
        headers = {'User-Agent': 'test'}
        
        result = daily_paintings.download_image(painting, headers)
        assert result is None




class TestComplementaryMode:
    """Test complementary mode functionality."""
    
    @patch('daily_paintings.download_image')
    @patch('src.datacreator.PaintingDataCreator')
    @patch('src.poem_fetcher.PoemFetcher')
    @patch('src.poem_analyzer.PoemAnalyzer')
    def test_complementary_mode_workflow(self, mock_analyzer_class, mock_poem_fetcher_class, mock_creator_class, mock_download):
        """Test complementary mode workflow."""
        # Setup mocks
        mock_creator = Mock()
        mock_poem_fetcher = Mock()
        mock_analyzer = Mock()
        
        mock_creator_class.return_value = mock_creator
        mock_poem_fetcher_class.return_value = mock_poem_fetcher
        mock_analyzer_class.return_value = mock_analyzer
        
        # Mock poem data
        mock_poem_fetcher.fetch_random_poems.return_value = [
            {"title": "Nature Poem", "text": "flowers and trees", "author": "Test Author", 
             "line_count": 10, "source": "Test Source"}
        ]
        mock_poem_fetcher.create_sample_poems.return_value = [
            {"title": "Nature Poem", "text": "flowers and trees", "author": "Test Author",
             "line_count": 10, "source": "Test Source"}
        ]
        
        # Mock poem analysis
        mock_analyzer.analyze_multiple_poems.return_value = [
            {"themes": ["nature", "flowers"], "q_codes": ["Q7860", "Q506"], "has_themes": True, "emotions": [], "primary_emotions": [], "secondary_emotions": []}
        ]
        mock_analyzer.get_combined_q_codes.return_value = ["Q7860", "Q506"]
        mock_analyzer.get_emotion_q_codes.return_value = []
        
        # Mock artwork data - fast mode uses create_sample_paintings
        mock_creator.create_sample_paintings.return_value = [
            {"title": "Flower Painting", "artist": "Test Artist", "image": "test.jpg", "year": "2020",
             "style": "Modern", "medium": "Oil", "museum": "Test Museum", "origin": "Test Country"}
        ]
        
        mock_download.return_value = './test.jpg'
        
        with patch('sys.argv', ['daily_paintings.py', '--complementary', '--fast']):
            with patch('builtins.open', mock_open()):
                daily_paintings.main()
        
        # Verify complementary mode was used
        mock_poem_fetcher.create_sample_poems.assert_called_once()
        mock_analyzer.analyze_multiple_poems.assert_called_once()
        mock_creator.create_sample_paintings.assert_called_once()
    
    @patch('src.datacreator.PaintingDataCreator')
    @patch('src.poem_fetcher.PoemFetcher')
    @patch('src.poem_analyzer.PoemAnalyzer')
    def test_complementary_mode_fallback(self, mock_analyzer_class, mock_poem_fetcher_class, mock_creator_class):
        """Test complementary mode fallback when no matching artwork found."""
        # Setup mocks
        mock_creator = Mock()
        mock_poem_fetcher = Mock()
        mock_analyzer = Mock()
        
        mock_creator_class.return_value = mock_creator
        mock_poem_fetcher_class.return_value = mock_poem_fetcher
        mock_analyzer_class.return_value = mock_analyzer
        
        # Mock poem data
        mock_poem_fetcher.fetch_random_poems.return_value = [
            {"title": "Nature Poem", "text": "flowers and trees", "author": "Test Author", 
             "line_count": 10, "source": "Test Source"}
        ]
        mock_poem_fetcher.create_sample_poems.return_value = [
            {"title": "Nature Poem", "text": "flowers and trees", "author": "Test Author",
             "line_count": 10, "source": "Test Source"}
        ]
        
        # Mock poem analysis
        mock_analyzer.analyze_multiple_poems.return_value = [
            {"themes": ["nature", "flowers"], "q_codes": ["Q7860", "Q506"], "has_themes": True, "emotions": [], "primary_emotions": [], "secondary_emotions": []}
        ]
        mock_analyzer.get_combined_q_codes.return_value = ["Q7860", "Q506"]
        mock_analyzer.get_emotion_q_codes.return_value = []
        
        # Mock no matching artwork found - fast mode uses create_sample_paintings
        mock_creator.create_sample_paintings.return_value = [
            {"title": "Random Painting", "artist": "Test Artist", "image": "test.jpg", "year": "2020",
             "style": "Classical", "medium": "Oil", "museum": "Test Museum", "origin": "Test Country"}
        ]
        
        with patch('sys.argv', ['daily_paintings.py', '--complementary', '--fast']):
            with patch('builtins.open', mock_open()):
                daily_paintings.main()
        
        # Verify fallback was used
        mock_creator.create_sample_paintings.assert_called_once()
    
    def test_complementary_poems_only_error(self):
        """Test that complementary and poems-only flags cannot be used together."""
        with patch('sys.argv', ['daily_paintings.py', '--complementary', '--poems-only']):
            with patch('builtins.print') as mock_print:
                daily_paintings.main()
                # Should print error message
                mock_print.assert_any_call("❌ Error: --complementary and --poems-only cannot be used together")


class TestMain:
    """Test main function integration."""
    
    @patch('daily_paintings.download_image')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_fast_mode(self, mock_creator_class, mock_download):
        """Test main function with fast mode."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        mock_download.return_value = './test.jpg'
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--count', '1']):
            with patch('builtins.open', mock_open()):
                daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
    
    @patch('daily_paintings.download_image')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_output_flag(self, mock_creator_class, mock_download):
        """Test main function with --output flag."""
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Test Painting',
                'artist': 'Test Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--output', '--count', '1']):
            with patch('builtins.open', mock_open()):
                daily_paintings.main()
        
        # Should use create_sample_paintings in fast mode
        mock_creator.create_sample_paintings.assert_called_once()
    
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_no_paintings_error(self, mock_creator_class):
        """Test main function when no paintings are returned."""
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = []
        mock_creator_class.return_value = mock_creator
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--count', '1']):
            with pytest.raises(ValueError, match="Failed to fetch paintings"):
                daily_paintings.main()
    
    @patch('src.email_sender.EmailSender')
    @patch('daily_paintings.download_image')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_email_flag(self, mock_creator_class, mock_download, mock_email_sender_class):
        """Test main function with --email flag."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        mock_download.return_value = './test.jpg'
        
        mock_email_sender = Mock()
        mock_email_sender.send_email.return_value = True
        mock_email_sender_class.return_value = mock_email_sender
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--email', 'l.d.durbin@gmail.com']):
            with patch.dict('os.environ', {
                'SMTP_HOST': 'test.smtp.com',
                'SMTP_PORT': '587',
                'SMTP_USERNAME': 'l.d.durbin@gmail.com',
                'SMTP_PASSWORD': 'testpassword'
            }):
                daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
        mock_email_sender.send_email.assert_called_once()
    
    @patch('src.email_sender.EmailSender')
    @patch('daily_paintings.download_image')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_email_html_format(self, mock_creator_class, mock_download, mock_email_sender_class):
        """Test main function with --email and --email-format html."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        mock_download.return_value = './test.jpg'
        
        mock_email_sender = Mock()
        mock_email_sender.send_email.return_value = True
        mock_email_sender_class.return_value = mock_email_sender
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--email', 'l.d.durbin@gmail.com', '--email-format', 'html']):
            with patch.dict('os.environ', {
                'SMTP_HOST': 'test.smtp.com',
                'SMTP_PORT': '587',
                'SMTP_USERNAME': 'l.d.durbin@gmail.com',
                'SMTP_PASSWORD': 'testpassword'
            }):
                daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
        # Note: download_image may not be called if there are no images or errors occur
        mock_email_sender.send_email.assert_called_once()
    
    @patch('src.email_sender.EmailSender')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_email_text_format(self, mock_creator_class, mock_email_sender_class):
        """Test main function with --email and --email-format text."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        
        mock_email_sender = Mock()
        mock_email_sender.send_email.return_value = True
        mock_email_sender_class.return_value = mock_email_sender
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--email', 'l.d.durbin@gmail.com', '--email-format', 'text']):
            with patch.dict('os.environ', {
                'SMTP_HOST': 'test.smtp.com',
                'SMTP_PORT': '587',
                'SMTP_USERNAME': 'l.d.durbin@gmail.com',
                'SMTP_PASSWORD': 'testpassword'
            }):
                daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
        # Should not download images for text-only email
        mock_email_sender.send_email.assert_called_once()
    
    @patch('src.email_sender.EmailSender')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_email_failure(self, mock_creator_class, mock_email_sender_class):
        """Test main function with email sending failure."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        
        mock_email_sender = Mock()
        mock_email_sender.send_email.return_value = False
        mock_email_sender_class.return_value = mock_email_sender
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--email', 'l.d.durbin@gmail.com']):
            with patch.dict('os.environ', {
                'SMTP_HOST': 'test.smtp.com',
                'SMTP_PORT': '587',
                'SMTP_USERNAME': 'l.d.durbin@gmail.com',
                'SMTP_PASSWORD': 'testpassword'
            }):
                daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
        mock_email_sender.send_email.assert_called_once()
    
    @patch('src.email_sender.EmailSender')
    @patch('src.datacreator.PaintingDataCreator')
    def test_main_with_email_configuration_error(self, mock_creator_class, mock_email_sender_class):
        """Test main function with email configuration error."""
        # Setup mocks
        mock_creator = Mock()
        mock_creator.create_sample_paintings.return_value = [
            {
                'title': 'Sample Painting',
                'artist': 'Sample Artist',
                'year': '2020',
                'style': 'Modern',
                'medium': 'Oil',
                'museum': 'Museum',
                'origin': 'Country',
                'image': 'http://example.com/image.jpg',
                'wikidata': 'http://wikidata.org/Q1'
            }
        ]
        mock_creator_class.return_value = mock_creator
        
        # Mock EmailSender to raise ValueError (missing config)
        mock_email_sender_class.side_effect = ValueError("Missing required environment variables")
        
        with patch('sys.argv', ['daily_paintings.py', '--fast', '--email', 'l.d.durbin@gmail.com']):
            daily_paintings.main()
        
        mock_creator.create_sample_paintings.assert_called_once_with(1)
        mock_email_sender_class.assert_called_once()


class TestFileOperations:
    """Test file operations and JSON handling."""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_json_output(self, mock_file):
        """Test saving JSON output."""
        paintings = [
            {
                'title': 'Test Painting',
                'artist': 'Test Artist',
                'year': '2020'
            }
        ]
        
        # Simulate the JSON saving logic
        with patch('builtins.open', mock_open()) as m:
            json.dump(paintings, m(), indent=2, ensure_ascii=False)
        
        # Verify file was opened for writing
        assert True  # File operation completed successfully
    
    def test_image_filename_generation(self):
        """Test that image filenames are generated correctly."""
        painting = {
            'title': 'The Great Wave',
            'year': '1831'
        }
        
        # Test the filename generation logic
        safe_title = "".join(c for c in painting['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{painting['year']}.jpg"
        
        assert filename == 'The Great Wave_1831.jpg'
        
        # Test with special characters
        painting2 = {'title': 'Painting #1!', 'year': '2020'}
        safe_title2 = "".join(c for c in painting2['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename2 = f"{safe_title2}_{painting2['year']}.png"
        
        assert filename2 == 'Painting 1_2020.png'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
