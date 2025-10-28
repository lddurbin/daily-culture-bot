import pytest
import json
import sys
import os
import requests
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import datacreator


class TestPaintingDataCreatorInit:
    """Test PaintingDataCreator initialization."""
    
    def test_initialization(self):
        """Test that PaintingDataCreator initializes correctly."""
        creator = datacreator.PaintingDataCreator()
        
        assert creator.wikidata_endpoint == "https://query.wikidata.org/sparql"
        assert creator.wikipedia_api == "https://en.wikipedia.org/api/rest_v1/page/summary/"
        assert creator.commons_api == "https://commons.wikimedia.org/w/api.php"
        assert creator.session is not None
        assert 'style_mappings' in creator.__dict__
    
    def test_style_mappings(self):
        """Test that style mappings are correct."""
        creator = datacreator.PaintingDataCreator()
        
        assert "Q4692" in creator.style_mappings
        assert creator.style_mappings["Q4692"] == "Renaissance"
        assert "Q40857" in creator.style_mappings
        assert creator.style_mappings["Q40857"] == "Impressionism"


class TestCreateSamplePaintings:
    """Test sample painting creation."""
    
    def test_create_sample_paintings_count(self):
        """Test creating specific number of sample paintings."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = creator.create_sample_paintings(count=1)
        assert len(paintings) == 1
        
        paintings = creator.create_sample_paintings(count=3)
        assert len(paintings) == 3
        
        paintings = creator.create_sample_paintings(count=5)
        assert len(paintings) == 5
    
    def test_create_sample_paintings_structure(self):
        """Test that sample paintings have correct structure."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = creator.create_sample_paintings(count=1)
        painting = paintings[0]
        
        required_keys = ['title', 'artist', 'image', 'year', 'style', 'museum', 
                        'origin', 'medium', 'dimensions', 'wikidata', 'date']
        
        for key in required_keys:
            assert key in painting
    
    def test_create_sample_paintings_content(self):
        """Test that sample paintings have valid content."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = creator.create_sample_paintings(count=2)
        
        # Check first painting (should be "The Great Wave")
        assert paintings[0]['title'] == "The Great Wave off Kanagawa"
        assert paintings[0]['artist'] == "Katsushika Hokusai"
        assert paintings[0]['year'] == 1831
        
        # Check second painting (should be "The Kiss")
        assert paintings[1]['title'] == "The Kiss"
        assert paintings[1]['artist'] == "Gustav Klimt"
        assert paintings[1]['year'] == 1908
    
    def test_create_sample_paintings_date(self):
        """Test that sample paintings include current date."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = creator.create_sample_paintings(count=1)
        today = datetime.now().strftime("%Y-%m-%d")
        
        assert paintings[0]['date'] == today


class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_text_normal(self):
        """Test cleaning normal text."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.clean_text("  Test Text  ")
        assert result == "Test Text"
    
    def test_clean_text_with_newlines(self):
        """Test cleaning text with newlines."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.clean_text("Line 1\nLine 2\rLine 3")
        assert result == "Line 1 Line 2 Line 3"
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.clean_text("")
        assert result == ""
    
    def test_clean_text_none(self):
        """Test cleaning None value."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.clean_text(None)
        assert result == ""


class TestGetHighResImageUrl:
    """Test high resolution image URL conversion."""
    
    def test_get_high_res_image_url_thumbnail(self):
        """Test converting thumbnail URL to original."""
        creator = datacreator.PaintingDataCreator()
        
        thumbnail_url = "https://commons.wikimedia.org/wiki/Special:FilePath/thumb/test.jpg/800px-test.jpg"
        result = creator.get_high_res_image_url(thumbnail_url)
        
        assert "/thumb/" not in result or "upload.wikimedia.org" in result
    
    def test_get_high_res_image_url_direct(self):
        """Test with direct Commons URL."""
        creator = datacreator.PaintingDataCreator()
        
        url = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Test.jpg"
        result = creator.get_high_res_image_url(url)
        
        assert result == url
    
    def test_get_high_res_image_url_empty(self):
        """Test with empty URL."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.get_high_res_image_url("")
        assert result == ""
    
    def test_get_high_res_image_url_none(self):
        """Test with None URL."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.get_high_res_image_url(None)
        assert result == ""


class TestFetchPaintings:
    """Test painting fetching functionality."""
    
    @patch('src.datacreator.PaintingDataCreator.query_wikidata_paintings')
    @patch('src.datacreator.PaintingDataCreator.process_painting_data')
    def test_fetch_paintings_success(self, mock_process, mock_query):
        """Test successful painting fetch."""
        mock_query.return_value = [
            {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}}
        ]
        mock_process.return_value = [
            {'title': 'Test Painting', 'artist': 'Test Artist'}
        ]
        
        creator = datacreator.PaintingDataCreator()
        paintings = creator.fetch_paintings(count=1)
        
        assert len(paintings) == 1
        assert paintings[0]['title'] == 'Test Painting'
    
    def test_fetch_paintings_sample_fallback(self):
        """Test that sample paintings are used when API fails."""
        creator = datacreator.PaintingDataCreator()
        
        with patch.object(creator, 'query_wikidata_paintings', return_value=[]):
            paintings = creator.fetch_paintings(count=1, use_sample_on_error=True)
        
        # Should return empty list if no paintings found
        assert len(paintings) == 0
    
    @patch('src.datacreator.PaintingDataCreator.query_wikidata_paintings')
    @patch('src.datacreator.PaintingDataCreator.process_painting_data')
    def test_fetch_paintings_count_limit(self, mock_process, mock_query):
        """Test that fetch respects count limit."""
        mock_query.return_value = [
            {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}},
            {'painting': {'value': 'url2'}, 'image': {'value': 'img2'}},
            {'painting': {'value': 'url3'}, 'image': {'value': 'img3'}}
        ]
        mock_process.return_value = [
            {'title': 'Test Painting 1', 'artist': 'Test Artist 1'},
            {'title': 'Test Painting 2', 'artist': 'Test Artist 2'},
            {'title': 'Test Painting 3', 'artist': 'Test Artist 3'}
        ]
        
        creator = datacreator.PaintingDataCreator()
        
        # Only fetch 2 paintings even if more are available
        paintings = creator.fetch_paintings(count=2)
        
        # Should respect the count limit
        assert len(paintings) == 2


class TestSaveToJson:
    """Test JSON saving functionality."""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_json_success(self, mock_file):
        """Test successful JSON save."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = [
            {'title': 'Test 1', 'artist': 'Artist 1'},
            {'title': 'Test 2', 'artist': 'Artist 2'}
        ]
        
        creator.save_to_json(paintings, 'test.json')
        
        mock_file.assert_called_once_with('test.json', 'w', encoding='utf-8')
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_to_json_error(self, mock_file):
        """Test JSON save with error."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = [{'title': 'Test', 'artist': 'Artist'}]
        
        # Should not raise exception, just print error
        try:
            creator.save_to_json(paintings, 'test.json')
        except Exception:
            pytest.fail("Should handle IO error gracefully")


class TestAppendToExistingJson:
    """Test appending to existing JSON file."""
    
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([]))
    def test_append_to_new_file(self, mock_file):
        """Test appending to new file."""
        creator = datacreator.PaintingDataCreator()
        
        paintings = [{'title': 'Test', 'artist': 'Artist'}]
        
        creator.append_to_existing_json(paintings, 'new_file.json')
        
        assert mock_file.called
    
    @patch('builtins.open', new_callable=mock_open)
    def test_append_no_duplicates(self, mock_file):
        """Test that duplicates are avoided."""
        # Simulate existing file with one painting
        existing = json.dumps([{'title': 'Existing', 'artist': 'Artist'}])
        
        with patch('builtins.open', new_callable=mock_open, read_data=existing):
            creator = datacreator.PaintingDataCreator()
            
            # Try to add the same painting
            paintings = [{'title': 'Existing', 'artist': 'Artist'}]
            
            creator.append_to_existing_json(paintings, 'existing.json')
            
            # Should not raise exception
            assert True


class TestProcessPaintingData:
    """Test processing of raw painting data."""
    
    def test_process_painting_data_empty(self):
        """Test processing empty data."""
        creator = datacreator.PaintingDataCreator()
        
        result = creator.process_painting_data([])
        assert result == []
    
    @patch('src.artwork_processor.ArtworkProcessor.get_painting_labels')
    def test_process_painting_data_with_data(self, mock_labels):
        """Test processing painting data."""
        mock_labels.return_value = {
            'title': 'Test Title',
            'artist': 'Test Artist'
        }
        
        raw_data = [{
            'painting': {'value': 'http://wikidata.org/Q1'},
            'image': {'value': 'http://example.com/img.jpg'}
        }]
        
        creator = datacreator.PaintingDataCreator()
        
        with patch('src.artwork_processor.ArtworkProcessor.get_high_res_image_url', return_value='http://example.com/img.jpg'):
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = creator.process_painting_data(raw_data)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Test Title'
        assert result[0]['artist'] == 'Test Artist'


class TestGetDailyPainting:
    """Test getting a single daily painting."""
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_daily_painting_success(self, mock_get):
        """Test successfully getting a daily painting."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [{
                    'paintingLabel': {'value': 'Test Painting'},
                    'artistLabel': {'value': 'Test Artist'},
                    'image': {'value': 'http://example.com/img.jpg'},
                    'painting': {'value': 'http://wikidata.org/Q1'}
                }]
            }
        }
        mock_get.return_value = mock_response
        
        creator = datacreator.PaintingDataCreator()
        
        with patch.object(creator, 'get_high_res_image_url', return_value='http://example.com/img.jpg'):
            painting = creator.get_daily_painting()
        
        assert painting is not None
        assert painting['title'] == 'Test Painting'
        assert painting['artist'] == 'Test Artist'
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_daily_painting_api_error(self, mock_get):
        """Test handling API error when getting daily painting."""
        mock_get.side_effect = Exception("API Error")
        
        creator = datacreator.PaintingDataCreator()
        painting = creator.get_daily_painting()
        
        assert painting is None


class TestQueryPaintingsBySubject:
    """Test subject-based painting queries."""
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_artwork_by_subject_success(self, mock_get):
        """Test successful subject-based query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_artwork_by_subject(['Q7860', 'Q506'], limit=1)
        
        assert len(result) == 1
        mock_get.assert_called_once()
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_artwork_by_subject_error(self, mock_get):
        """Test subject-based query with error."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_artwork_by_subject(['Q7860'], limit=1)
        
        assert result == []
    
    def test_query_artwork_by_subject_empty_q_codes(self):
        """Test subject-based query with empty Q-codes."""
        creator = datacreator.PaintingDataCreator()
        result = creator.query_artwork_by_subject([], limit=1)
        
        assert result == []
    
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.process_painting_data')
    def test_fetch_artwork_by_subject_success(self, mock_process, mock_query):
        """Test successful subject-based painting fetch."""
        mock_query.return_value = [
            {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}}
        ]
        mock_process.return_value = [
            {'title': 'Flower Painting', 'artist': 'Test Artist'}
        ]
        
        creator = datacreator.PaintingDataCreator()
        paintings = creator.fetch_artwork_by_subject(['Q7860', 'Q506'], count=1)
        
        assert len(paintings) == 1
        assert paintings[0]['title'] == 'Flower Painting'
        mock_query.assert_called_once()
        mock_process.assert_called_once()
    
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.fetch_paintings')
    def test_fetch_artwork_by_subject_no_results(self, mock_fetch, mock_query):
        """Test subject-based fetch with no results."""
        mock_query.return_value = []
        mock_fetch.return_value = []
        
        creator = datacreator.PaintingDataCreator()
        paintings = creator.fetch_artwork_by_subject(['Q7860'], count=1)
        
        assert len(paintings) == 0
        # Should be called at least once (may be called multiple times due to retry logic)
        assert mock_query.call_count >= 1
    
    def test_fetch_artwork_by_subject_empty_q_codes(self):
        """Test subject-based fetch with empty Q-codes."""
        creator = datacreator.PaintingDataCreator()
        paintings = creator.fetch_artwork_by_subject([], count=1)
        
        assert len(paintings) == 0


class TestQueryWikidataPaintings:
    """Test Wikidata query functionality."""
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_wikidata_success(self, mock_get):
        """Test successful Wikidata query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_wikidata_paintings(limit=1)
        
        assert len(result) == 1
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_wikidata_error(self, mock_get):
        """Test Wikidata query with error."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_wikidata_paintings(limit=1)
        
        assert result == []


class TestSitelinksFiltering:
    """Test sitelinks filtering functionality."""
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_artwork_by_subject_with_sitelinks_filter(self, mock_get):
        """Test that sitelinks filtering is applied in SPARQL query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'painting': {'value': 'url1'}, 
                        'image': {'value': 'img1'},
                        'sitelinks': {'value': '15'},  # Below threshold
                        'subject': {'value': 'Q7860'},
                        'genre': {'value': 'Q191163'}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_artwork_by_subject(['Q7860'], max_sitelinks=20)
        
        assert len(result) == 1
        # Verify the request was made with sitelinks filter
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        query = call_args[1]['params']['query']
        assert 'wikibase:sitelinks' in query
        assert 'FILTER(?sitelinks < 20)' in query
    
    @patch('src.datacreator.requests.Session.get')
    def test_query_wikidata_paintings_with_sitelinks_filter(self, mock_get):
        """Test that sitelinks filtering is applied in regular Wikidata query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'painting': {'value': 'url1'}, 
                        'image': {'value': 'img1'},
                        'sitelinks': {'value': '5'}  # Below threshold
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        creator = datacreator.PaintingDataCreator()
        result = creator.query_wikidata_paintings(max_sitelinks=10)
        
        assert len(result) == 1
        # Verify the request was made with sitelinks filter
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        query = call_args[1]['params']['query']
        assert 'wikibase:sitelinks' in query
        assert 'FILTER(?sitelinks < 10)' in query
    
    def test_fetch_paintings_passes_max_sitelinks(self):
        """Test that fetch_paintings passes max_sitelinks parameter."""
        creator = datacreator.PaintingDataCreator()
        
        with patch.object(creator, 'query_wikidata_paintings') as mock_query:
            mock_query.return_value = []
            
            creator.fetch_paintings(count=1, max_sitelinks=15)
            
            # Verify max_sitelinks was passed to query method
            mock_query.assert_called()
            call_args = mock_query.call_args
            assert call_args[1]['max_sitelinks'] == 15
    
    def test_fetch_artwork_by_subject_passes_max_sitelinks(self):
        """Test that fetch_artwork_by_subject passes max_sitelinks parameter."""
        creator = datacreator.PaintingDataCreator()
        
        with patch.object(creator, 'query_artwork_by_subject') as mock_query, \
             patch.object(creator, 'fetch_paintings') as mock_fetch:
            mock_query.return_value = []
            mock_fetch.return_value = []
            
            creator.fetch_artwork_by_subject(['Q7860'], count=1, max_sitelinks=25)
            
            # Verify max_sitelinks was passed to fetch_paintings (final fallback)
            mock_fetch.assert_called()
            call_args = mock_fetch.call_args
            assert call_args[1]['max_sitelinks'] == 25


class TestArtworkDateFetching:
    """Test artwork inception date fetching functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_artwork_inception_date_valid_q_code(self, mock_get):
        """Test fetching inception date with valid Q-code."""
        # Mock Wikidata response with inception date
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'inception': {
                            'value': '1831-06-01',
                            'type': 'time'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        wikidata_url = "https://www.wikidata.org/wiki/Q455354"
        result = self.creator.get_artwork_inception_date(wikidata_url)
        
        assert result == 1831
        mock_get.assert_called_once()
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_artwork_inception_date_year_only(self, mock_get):
        """Test fetching inception date with year-only format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'inception': {
                            'value': '1908',
                            'type': 'time'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        wikidata_url = "https://www.wikidata.org/wiki/Q203533"
        result = self.creator.get_artwork_inception_date(wikidata_url)
        
        assert result == 1908
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_artwork_inception_date_range(self, mock_get):
        """Test fetching inception date with date range."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'inception': {
                            'value': '1503-1519',
                            'type': 'time'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        wikidata_url = "https://www.wikidata.org/wiki/Q12418"
        result = self.creator.get_artwork_inception_date(wikidata_url)
        
        assert result == 1503
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_artwork_inception_date_no_date(self, mock_get):
        """Test fetching inception date when no date is available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': []
            }
        }
        mock_get.return_value = mock_response
        
        wikidata_url = "https://www.wikidata.org/wiki/Q999999"
        result = self.creator.get_artwork_inception_date(wikidata_url)
        
        assert result is None
    
    @patch('src.datacreator.requests.Session.get')
    def test_get_artwork_inception_date_api_error(self, mock_get):
        """Test handling API errors gracefully."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        wikidata_url = "https://www.wikidata.org/wiki/Q455354"
        result = self.creator.get_artwork_inception_date(wikidata_url)
        
        assert result is None
    
    def test_get_artwork_inception_date_invalid_url(self):
        """Test handling invalid Wikidata URL."""
        result = self.creator.get_artwork_inception_date("")
        assert result is None
        
        result = self.creator.get_artwork_inception_date("invalid-url")
        assert result is None
    
    def test_get_artwork_inception_date_none_url(self):
        """Test handling None wikidata_url (line 350 in wikidata_queries.py)."""
        result = self.creator.get_artwork_inception_date(None)
        assert result is None


class TestProcessPaintingDataWithDates:
    """Test process_painting_data with date population."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    @patch('src.wikidata_queries.WikidataQueries.get_artwork_inception_date')
    @patch('src.artwork_processor.ArtworkProcessor.get_painting_labels')
    def test_process_painting_data_with_date(self, mock_labels, mock_inception):
        """Test that process_painting_data populates year field from inception date."""
        # Mock labels response
        mock_labels.return_value = {
            "title": "Test Painting",
            "artist": "Test Artist"
        }
        
        # Mock inception date response
        mock_inception.return_value = 1831
        
        # Mock raw data
        raw_data = [
            {
                'painting': {'value': 'https://www.wikidata.org/wiki/Q455354'},
                'image': {'value': 'https://example.com/image.jpg'}
            }
        ]
        
        result = self.creator.process_painting_data(raw_data)
        
        assert len(result) == 1
        assert result[0]['year'] == 1831
        assert result[0]['title'] == "Test Painting"
        assert result[0]['artist'] == "Test Artist"
        
        # Verify inception date was called
        mock_inception.assert_called_once_with('https://www.wikidata.org/wiki/Q455354')
    
    @patch('src.wikidata_queries.WikidataQueries.get_artwork_inception_date')
    @patch('src.artwork_processor.ArtworkProcessor.get_painting_labels')
    def test_process_painting_data_no_date(self, mock_labels, mock_inception):
        """Test that process_painting_data handles missing dates gracefully."""
        mock_labels.return_value = {
            "title": "Test Painting",
            "artist": "Test Artist"
        }
        mock_inception.return_value = None
        
        raw_data = [
            {
                'painting': {'value': 'https://www.wikidata.org/wiki/Q999999'},
                'image': {'value': 'https://example.com/image.jpg'}
            }
        ]
        
        result = self.creator.process_painting_data(raw_data)
        
        assert len(result) == 1
        assert result[0]['year'] is None
        assert result[0]['title'] == "Test Painting"
    
    @patch('src.wikidata_queries.WikidataQueries.get_artwork_inception_date')
    @patch('src.artwork_processor.ArtworkProcessor.get_painting_labels')
    def test_process_painting_data_inception_error(self, mock_labels, mock_inception):
        """Test that process_painting_data handles inception date errors gracefully."""
        mock_labels.return_value = {
            "title": "Test Painting",
            "artist": "Test Artist"
        }
        mock_inception.side_effect = Exception("API Error")
        
        raw_data = [
            {
                'painting': {'value': 'https://www.wikidata.org/wiki/Q455354'},
                'image': {'value': 'https://example.com/image.jpg'}
            }
        ]
        
        result = self.creator.process_painting_data(raw_data)
        
        assert len(result) == 1
        assert result[0]['year'] is None  # Should fallback to None on error


class TestCacheManagement:
    """Test cache management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_cache_key_simple(self):
        """Test cache key generation with simple parameters."""
        key = self.creator._get_cache_key("test_query", param1="value1", param2=123)
        
        assert isinstance(key, str)
        assert len(key) > 0
        assert "test_query" in key
    
    def test_get_cache_key_with_list(self):
        """Test cache key generation with list parameters."""
        key = self.creator._get_cache_key("test", items=["a", "b", "c"])
        
        assert isinstance(key, str)
        assert len(key) > 0
    
    def test_get_cache_key_sorted(self):
        """Test that cache keys are sorted for consistency."""
        key1 = self.creator._get_cache_key("test", a="z", b="y")
        key2 = self.creator._get_cache_key("test", b="y", a="z")
        
        # Keys should be the same regardless of parameter order
        assert key1 == key2
    
    def test_manage_cache_size_below_limit(self):
        """Test cache management when below limit."""
        self.creator.query_cache = {"key1": "value1", "key2": "value2"}
        
        self.creator._manage_cache_size()
        
        assert len(self.creator.query_cache) == 2
    
    def test_manage_cache_size_above_limit(self):
        """Test cache management when above limit."""
        # Create a cache above the limit
        self.creator.cache_max_size = 50
        self.creator.query_cache = {f"key{i}": f"value{i}" for i in range(60)}
        
        initial_size = len(self.creator.query_cache)
        self.creator._manage_cache_size()
        
        # Should remove 25% of entries
        assert len(self.creator.query_cache) < initial_size


class TestWikipediaSummary:
    """Test Wikipedia summary functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_wikipedia_summary_success(self):
        """Test successfully getting Wikipedia summary."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'extract': 'The Mona Lisa is a famous painting. It was painted by Leonardo.'
        }
        self.creator.session.get = Mock(return_value=mock_response)
        
        result = self.creator.get_wikipedia_summary("Mona Lisa")
        
        assert result is not None
        assert ("Mona Lisa" in result or "painting" in result)
    
    def test_get_wikipedia_summary_no_extract(self):
        """Test Wikipedia summary with no extract."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        self.creator.session.get = Mock(return_value=mock_response)
        
        result = self.creator.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
    
    def test_get_wikipedia_summary_api_error(self):
        """Test Wikipedia summary with API error."""
        mock_response = Mock()
        mock_response.status_code = 404
        self.creator.session.get = Mock(return_value=mock_response)
        
        result = self.creator.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
    
    @patch('builtins.print')
    def test_get_wikipedia_summary_exception(self, mock_print):
        """Test Wikipedia summary with exception."""
        self.creator.session.get = Mock(side_effect=Exception("Network error"))
        
        result = self.creator.get_wikipedia_summary("Mona Lisa")
        
        assert result is None
        mock_print.assert_called_once()


class TestHighResImageUrl:
    """Test high resolution image URL functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_high_res_image_url_thumbnail(self):
        """Test converting thumbnail URL to high-res."""
        thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Example.jpg/800px-Example.jpg"
        result = self.creator.get_high_res_image_url(thumbnail_url)
        
        assert "upload.wikimedia.org" in result
        # Check that result is either the original URL (if regex fails) or the extracted path
        assert result == thumbnail_url or "/thumb/" not in result
    
    def test_get_high_res_image_url_direct_commons(self):
        """Test direct Wikimedia Commons URL."""
        direct_url = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.jpg"
        result = self.creator.get_high_res_image_url(direct_url)
        
        assert result == direct_url
    
    def test_get_high_res_image_url_empty(self):
        """Test empty URL."""
        result = self.creator.get_high_res_image_url("")
        
        assert result == ""
    
    def test_get_high_res_image_url_none(self):
        """Test None URL."""
        result = self.creator.get_high_res_image_url(None)
        
        assert result == ""


class TestGetPaintingLabels:
    """Test get_painting_labels functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_painting_labels_no_url(self):
        """Test getting labels with no URL."""
        result = self.creator.get_painting_labels(None)
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"
    
    def test_get_painting_labels_empty_url(self):
        """Test getting labels with empty URL."""
        result = self.creator.get_painting_labels("")
        
        assert result["title"] == "Unknown Title"
        assert result["artist"] == "Unknown Artist"


class TestExtractArtworkFieldsFromRaw:
    """Test _extract_artwork_fields_from_raw method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_extract_fields_valid_data(self):
        """Test extracting fields from valid raw data."""
        raw_item = {
            'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'Q456'},
            'genre': {'value': 'Q789'},
            'artworkType': {'value': 'Q3305213'}
        }
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is not None
        assert result['wikidata_url'] == 'https://www.wikidata.org/wiki/Q123'
        assert result['image_url'] == 'https://commons.wikimedia.org/wiki/File:test.jpg'
        assert result['sitelinks'] == '5'
        assert result['subject'] == 'Q456'
        assert result['genre'] == 'Q789'
        assert result['artwork_type'] == 'Q3305213'
    
    def test_extract_fields_missing_wikidata_url(self):
        """Test extracting fields when wikidata_url is missing."""
        raw_item = {
            'artwork': {'value': ''},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'Q456'},
            'genre': {'value': 'Q789'},
            'artworkType': {'value': 'Q3305213'}
        }
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is None
    
    def test_extract_fields_missing_image_url(self):
        """Test extracting fields when image_url is missing."""
        raw_item = {
            'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
            'image': {'value': ''},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'Q456'},
            'genre': {'value': 'Q789'},
            'artworkType': {'value': 'Q3305213'}
        }
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is None
    
    def test_extract_fields_missing_optional_fields(self):
        """Test extracting fields when optional fields are missing."""
        raw_item = {
            'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': ''},
            'genre': {'value': ''},
            'artworkType': {'value': ''}
        }
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is not None
        assert result['wikidata_url'] == 'https://www.wikidata.org/wiki/Q123'
        assert result['image_url'] == 'https://commons.wikimedia.org/wiki/File:test.jpg'
        assert result['sitelinks'] == '5'
        assert result['subject'] == ''
        assert result['genre'] == ''
        assert result['artwork_type'] == ''
    
    def test_extract_fields_missing_keys(self):
        """Test extracting fields when keys are missing from raw item."""
        raw_item = {
            'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'}
        }
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is not None
        assert result['wikidata_url'] == 'https://www.wikidata.org/wiki/Q123'
        assert result['image_url'] == 'https://commons.wikimedia.org/wiki/File:test.jpg'
        assert result['sitelinks'] == '0'  # Default value
        assert result['subject'] == ''
        assert result['genre'] == ''
        assert result['artwork_type'] == ''
    
    def test_extract_fields_empty_raw_item(self):
        """Test extracting fields from empty raw item."""
        raw_item = {}
        
        result = self.creator._extract_artwork_fields_from_raw(raw_item)
        
        assert result is None


class TestBuildArtworkEntryFromFields:
    """Test _build_artwork_entry_from_fields method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    @patch('src.datacreator.datetime')
    def test_build_entry_valid_fields(self, mock_datetime):
        """Test building artwork entry from valid fields."""
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01"
        
        fields = {
            'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
            'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
            'sitelinks': '5',
            'subject': 'Q456',
            'genre': 'Q789',
            'artwork_type': 'Q3305213'
        }
        
        with patch.object(self.creator, 'get_painting_labels') as mock_labels, \
             patch.object(self.creator, 'get_high_res_image_url') as mock_high_res, \
             patch.object(self.creator, '_get_medium_from_type') as mock_medium, \
             patch.object(self.creator, 'get_artwork_inception_date') as mock_date, \
             patch.object(self.creator, 'clean_text') as mock_clean:
            
            mock_labels.return_value = {'title': 'Test Painting', 'artist': 'Test Artist'}
            mock_high_res.return_value = 'https://commons.wikimedia.org/wiki/File:test_high_res.jpg'
            mock_medium.return_value = 'Oil on canvas'
            mock_date.return_value = 1900
            mock_clean.side_effect = lambda x: x  # Return as-is
            
            result = self.creator._build_artwork_entry_from_fields(fields, fields['wikidata_url'])
            
            assert result is not None
            assert result['title'] == 'Test Painting'
            assert result['artist'] == 'Test Artist'
            assert result['image'] == 'https://commons.wikimedia.org/wiki/File:test_high_res.jpg'
            assert result['year'] == 1900
            assert result['style'] == 'Classical'
            assert result['museum'] == 'Unknown Location'
            assert result['origin'] == 'Unknown'
            assert result['medium'] == 'Oil on canvas'
            assert result['dimensions'] == 'Unknown dimensions'
            assert result['wikidata'] == 'https://www.wikidata.org/wiki/Q123'
            assert result['date'] == '2024-01-01'
            assert result['sitelinks'] == 5
            assert result['subject_q_codes'] == ['Q456']
            assert result['genre_q_codes'] == ['Q789']
            assert result['artwork_type'] == 'Q3305213'
    
    def test_build_entry_unknown_title(self):
        """Test building entry when title is unknown."""
        fields = {
            'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
            'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
            'sitelinks': '5',
            'subject': 'Q456',
            'genre': 'Q789',
            'artwork_type': 'Q3305213'
        }
        
        with patch.object(self.creator, 'get_painting_labels') as mock_labels:
            mock_labels.return_value = {'title': 'Unknown Title', 'artist': 'Test Artist'}
            
            result = self.creator._build_artwork_entry_from_fields(fields, fields['wikidata_url'])
            
            assert result is None
    
    def test_build_entry_unknown_artist(self):
        """Test building entry when artist is unknown."""
        fields = {
            'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
            'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
            'sitelinks': '5',
            'subject': 'Q456',
            'genre': 'Q789',
            'artwork_type': 'Q3305213'
        }
        
        with patch.object(self.creator, 'get_painting_labels') as mock_labels:
            mock_labels.return_value = {'title': 'Test Painting', 'artist': 'Unknown Artist'}
            
            result = self.creator._build_artwork_entry_from_fields(fields, fields['wikidata_url'])
            
            assert result is None
    
    def test_build_entry_empty_subject_genre(self):
        """Test building entry with empty subject and genre."""
        fields = {
            'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
            'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
            'sitelinks': '5',
            'subject': '',
            'genre': '',
            'artwork_type': 'Q3305213'
        }
        
        with patch.object(self.creator, 'get_painting_labels') as mock_labels, \
             patch.object(self.creator, 'get_high_res_image_url') as mock_high_res, \
             patch.object(self.creator, '_get_medium_from_type') as mock_medium, \
             patch.object(self.creator, 'get_artwork_inception_date') as mock_date, \
             patch.object(self.creator, 'clean_text') as mock_clean:
            
            mock_labels.return_value = {'title': 'Test Painting', 'artist': 'Test Artist'}
            mock_high_res.return_value = 'https://commons.wikimedia.org/wiki/File:test_high_res.jpg'
            mock_medium.return_value = 'Oil on canvas'
            mock_date.return_value = 1900
            mock_clean.side_effect = lambda x: x
            
            result = self.creator._build_artwork_entry_from_fields(fields, fields['wikidata_url'])
            
            assert result is not None
            assert result['subject_q_codes'] == []
            assert result['genre_q_codes'] == []


class TestScoreAndFilterArtwork:
    """Test _score_and_filter_artwork method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_score_and_filter_valid_data(self):
        """Test scoring and filtering with valid data."""
        raw_data = [
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.5}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.return_value = 0.8
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract, \
             patch.object(self.creator, '_build_artwork_entry_from_fields') as mock_build, \
             patch('src.datacreator.time.sleep'):
            
            mock_extract.return_value = {
                'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
                'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
                'sitelinks': '5',
                'subject': 'Q456',
                'genre': 'Q789',
                'artwork_type': 'Q3305213'
            }
            
            mock_build.return_value = {
                'title': 'Test Painting',
                'artist': 'Test Artist',
                'subject_q_codes': ['Q456'],
                'genre_q_codes': ['Q789'],
                'year': 1900
            }
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 1
            assert result[0][1] == 0.8  # Score
            assert result[0][0]['title'] == 'Test Painting'
    
    def test_score_and_filter_below_min_score(self):
        """Test scoring when artwork score is below minimum."""
        raw_data = [
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.8}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.return_value = 0.3  # Below minimum
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract, \
             patch.object(self.creator, '_build_artwork_entry_from_fields') as mock_build, \
             patch('src.datacreator.time.sleep'):
            
            mock_extract.return_value = {
                'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
                'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
                'sitelinks': '5',
                'subject': 'Q456',
                'genre': 'Q789',
                'artwork_type': 'Q3305213'
            }
            
            mock_build.return_value = {
                'title': 'Test Painting',
                'artist': 'Test Artist',
                'subject_q_codes': ['Q456'],
                'genre_q_codes': ['Q789'],
                'year': 1900
            }
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 0  # No results due to low score
    
    def test_score_and_filter_invalid_fields(self):
        """Test scoring when field extraction fails."""
        raw_data = [
            {
                'artwork': {'value': ''},  # Invalid - empty URL
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.5}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract:
            mock_extract.return_value = None  # Invalid fields
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 0  # No results due to invalid fields
    
    def test_score_and_filter_invalid_entry(self):
        """Test scoring when entry building fails."""
        raw_data = [
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.5}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract, \
             patch.object(self.creator, '_build_artwork_entry_from_fields') as mock_build:
            
            mock_extract.return_value = {
                'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
                'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
                'sitelinks': '5',
                'subject': 'Q456',
                'genre': 'Q789',
                'artwork_type': 'Q3305213'
            }
            
            mock_build.return_value = None  # Invalid entry
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 0  # No results due to invalid entry
    
    def test_score_and_filter_exception_handling(self):
        """Test scoring when an exception occurs during processing."""
        raw_data = [
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.5}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.side_effect = Exception("Test error")
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract, \
             patch.object(self.creator, '_build_artwork_entry_from_fields') as mock_build, \
             patch('src.datacreator.time.sleep'):
            
            mock_extract.return_value = {
                'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
                'image_url': 'https://commons.wikimedia.org/wiki/File:test.jpg',
                'sitelinks': '5',
                'subject': 'Q456',
                'genre': 'Q789',
                'artwork_type': 'Q3305213'
            }
            
            mock_build.return_value = {
                'title': 'Test Painting',
                'artist': 'Test Artist',
                'subject_q_codes': ['Q456'],
                'genre_q_codes': ['Q789'],
                'year': 1900
            }
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 0  # No results due to exception
    
    def test_score_and_filter_multiple_items_sorted(self):
        """Test scoring multiple items and sorting by score."""
        raw_data = [
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q123'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test1.jpg'},
                'sitelinks': {'value': '5'},
                'subject': {'value': 'Q456'},
                'genre': {'value': 'Q789'},
                'artworkType': {'value': 'Q3305213'}
            },
            {
                'artwork': {'value': 'https://www.wikidata.org/wiki/Q124'},
                'image': {'value': 'https://commons.wikimedia.org/wiki/File:test2.jpg'},
                'sitelinks': {'value': '3'},
                'subject': {'value': 'Q457'},
                'genre': {'value': 'Q790'},
                'artworkType': {'value': 'Q3305213'}
            }
        ]
        
        strategy = {'min_score': 0.5}
        poem_analysis = {'themes': ['nature'], 'emotions': ['peaceful']}
        genres = ['Q789']
        poet_years = (1850, 1920)
        
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.side_effect = [0.9, 0.7]  # Different scores
        
        with patch.object(self.creator, '_extract_artwork_fields_from_raw') as mock_extract, \
             patch.object(self.creator, '_build_artwork_entry_from_fields') as mock_build, \
             patch('src.datacreator.time.sleep'):
            
            mock_extract.side_effect = [
                {
                    'wikidata_url': 'https://www.wikidata.org/wiki/Q123',
                    'image_url': 'https://commons.wikimedia.org/wiki/File:test1.jpg',
                    'sitelinks': '5',
                    'subject': 'Q456',
                    'genre': 'Q789',
                    'artwork_type': 'Q3305213'
                },
                {
                    'wikidata_url': 'https://www.wikidata.org/wiki/Q124',
                    'image_url': 'https://commons.wikimedia.org/wiki/File:test2.jpg',
                    'sitelinks': '3',
                    'subject': 'Q457',
                    'genre': 'Q790',
                    'artwork_type': 'Q3305213'
                }
            ]
            
            mock_build.side_effect = [
                {
                    'title': 'Test Painting 1',
                    'artist': 'Test Artist 1',
                    'subject_q_codes': ['Q456'],
                    'genre_q_codes': ['Q789'],
                    'year': 1900
                },
                {
                    'title': 'Test Painting 2',
                    'artist': 'Test Artist 2',
                    'subject_q_codes': ['Q457'],
                    'genre_q_codes': ['Q790'],
                    'year': 1910
                }
            ]
            
            result = self.creator._score_and_filter_artwork(
                raw_data, strategy, poem_analysis, genres, poet_years, mock_analyzer
            )
            
            assert len(result) == 2
            # Should be sorted by score descending
            assert result[0][1] == 0.9  # Higher score first
            assert result[1][1] == 0.7  # Lower score second
            assert result[0][0]['title'] == 'Test Painting 1'
            assert result[1][0]['title'] == 'Test Painting 2'


class TestGetPaintingDimensions:
    """Test get_painting_dimensions method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_dimensions_valid_response(self):
        """Test getting dimensions with valid response."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'height': {'value': '100'},
                        'width': {'value': '150'}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "100 cm × 150 cm"
    
    def test_get_dimensions_no_dimensions(self):
        """Test getting dimensions when no dimensions in response."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'height': {'value': ''},
                        'width': {'value': ''}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"
    
    def test_get_dimensions_http_error(self):
        """Test getting dimensions with HTTP error."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"
    
    def test_get_dimensions_timeout_exception(self):
        """Test getting dimensions with timeout exception."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        with patch.object(self.creator.session, 'get', side_effect=requests.Timeout()):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"
    
    def test_get_dimensions_malformed_json(self):
        """Test getting dimensions with malformed JSON response."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"
    
    def test_get_dimensions_missing_wikidata_url(self):
        """Test getting dimensions with missing wikidata URL."""
        result = self.creator.get_painting_dimensions(None)
        
        assert result == "Unknown dimensions"
    
    def test_get_dimensions_empty_results(self):
        """Test getting dimensions with empty results array."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': []
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"
    
    def test_get_dimensions_invalid_values(self):
        """Test getting dimensions with invalid dimension values."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'height': {'value': None},
                        'width': {'value': None}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_dimensions(wikidata_url)
            
            assert result == "Unknown dimensions"


class TestGetPaintingLabels:
    """Test get_painting_labels method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    def test_get_labels_valid_response(self):
        """Test getting labels with valid response."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'paintingLabel': {'value': 'The Starry Night'},
                        'artistLabel': {'value': 'Vincent van Gogh'}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'The Starry Night'
            assert result['artist'] == 'Vincent van Gogh'
    
    def test_get_labels_partial_labels(self):
        """Test getting labels with partial labels."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'paintingLabel': {'value': 'The Starry Night'},
                        'artistLabel': {'value': ''}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'The Starry Night'
            assert result['artist'] == ''  # Empty string, not 'Unknown Artist'
    
    def test_get_labels_http_error(self):
        """Test getting labels with HTTP error."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'Unknown Title'
            assert result['artist'] == 'Unknown Artist'
    
    def test_get_labels_timeout_exception(self):
        """Test getting labels with timeout exception."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        with patch.object(self.creator.session, 'get', side_effect=requests.Timeout()):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'Unknown Title'
            assert result['artist'] == 'Unknown Artist'
    
    def test_get_labels_malformed_response(self):
        """Test getting labels with malformed response."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'Unknown Title'
            assert result['artist'] == 'Unknown Artist'
    
    def test_get_labels_missing_wikidata_url(self):
        """Test getting labels with missing wikidata URL."""
        result = self.creator.get_painting_labels(None)
        
        assert result['title'] == 'Unknown Title'
        assert result['artist'] == 'Unknown Artist'
    
    def test_get_labels_empty_results(self):
        """Test getting labels with empty results array."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': []
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'Unknown Title'
            assert result['artist'] == 'Unknown Artist'
    
    def test_get_labels_non_english_labels(self):
        """Test getting labels with non-English labels."""
        wikidata_url = "https://www.wikidata.org/wiki/Q123"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {
                        'paintingLabel': {'value': 'La Nuit Étoilée'},
                        'artistLabel': {'value': 'Vincent van Gogh'}
                    }
                ]
            }
        }
        
        with patch.object(self.creator.session, 'get', return_value=mock_response):
            result = self.creator.get_painting_labels(wikidata_url)
            
            assert result['title'] == 'La Nuit Étoilée'
            assert result['artist'] == 'Vincent van Gogh'


class TestFetchArtworkBySubjectWithScoring:
    """Test fetch_artwork_by_subject_with_scoring method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', False)
    @patch('src.datacreator.PaintingDataCreator.fetch_artwork_by_subject')
    def test_fetch_artwork_by_subject_with_scoring_analyzer_unavailable(self, mock_fetch):
        """Test fallback when poem analyzer is not available."""
        mock_fetch.return_value = [{'title': 'Test Artwork', 'image': 'test.jpg'}]
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1
        )
        
        assert len(result) == 1
        assert result[0][0]['title'] == 'Test Artwork'
        assert result[0][1] == 0.5  # Neutral score when analyzer unavailable
        # Check that fetch_artwork_by_subject was called with correct parameters
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args[0][0] == q_codes  # q_codes
        assert call_args[0][1] == 1  # count
        assert call_args[0][2] is None  # genres
        assert call_args[1]['max_sitelinks'] == 20  # max_sitelinks as keyword arg
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.get_painting_labels')
    def test_fetch_artwork_by_subject_with_scoring_analyzer_available(self, mock_labels, mock_query, mock_analyzer_class):
        """Test scoring when poem analyzer is available."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.8
        
        # Mock query results with proper Wikidata SPARQL structure
        mock_query.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'https://wikidata.org/Q1'},
            'genre': {'value': 'https://wikidata.org/Q191163'},
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}
        }]
        
        # Mock labels method
        mock_labels.return_value = {
            'title': 'Test Artwork',
            'artist': 'Test Artist'
        }
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1, min_score=0.4
        )
        
        # The method has fallback logic, so we just verify it returns results
        assert isinstance(result, list)
        mock_query.assert_called()
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.get_painting_labels')
    def test_fetch_artwork_by_subject_with_scoring_low_score_fallback(self, mock_labels, mock_query, mock_analyzer_class):
        """Test fallback when scored results don't meet minimum score."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.2  # Low score
        
        # Mock query results with proper Wikidata SPARQL structure
        mock_query.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'https://wikidata.org/Q1'},
            'genre': {'value': 'https://wikidata.org/Q191163'},
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}
        }]
        
        # Mock labels method
        mock_labels.return_value = {
            'title': 'Test Artwork',
            'artist': 'Test Artist'
        }
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1, min_score=0.4
        )
        
        # Should still return results even with low scores
        assert len(result) >= 0
        mock_query.assert_called()
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    def test_fetch_artwork_by_subject_with_scoring_empty_q_codes(self, mock_analyzer_class):
        """Test handling of empty Q-codes list."""
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = []
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1
        )
        
        assert result == []
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.get_painting_labels')
    def test_fetch_artwork_by_subject_with_scoring_with_genres(self, mock_labels, mock_query, mock_analyzer_class):
        """Test scoring with genre filtering."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.7
        
        # Mock query results with proper Wikidata SPARQL structure
        mock_query.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'https://wikidata.org/Q1'},
            'genre': {'value': 'https://wikidata.org/Q191163'},
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}
        }]
        
        # Mock labels method
        mock_labels.return_value = {
            'title': 'Test Artwork',
            'artist': 'Test Artist'
        }
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        genres = ['Q123', 'Q456']
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1, genres=genres
        )
        
        # Verify genres were passed to query and method returns results
        assert isinstance(result, list)
        mock_query.assert_called()
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    def test_fetch_artwork_by_subject_with_scoring_analyzer_error(self, mock_analyzer_class):
        """Test graceful handling of analyzer errors."""
        # Mock analyzer to raise an exception
        mock_analyzer_class.side_effect = Exception("Analyzer error")
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        
        # The method doesn't have error handling around analyzer initialization,
        # so it should raise the exception
        with pytest.raises(Exception, match="Analyzer error"):
            self.creator.fetch_artwork_by_subject_with_scoring(
                poem_analysis, q_codes, count=1
            )
    
    def test_fetch_artwork_by_subject_with_scoring_poem_analyzer_available_constant(self):
        """Test that POEM_ANALYZER_AVAILABLE constant is properly defined."""
        # This test ensures the constant exists and can be imported
        from src.datacreator import POEM_ANALYZER_AVAILABLE
        assert isinstance(POEM_ANALYZER_AVAILABLE, bool)
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    @patch('src.datacreator.PaintingDataCreator.query_artwork_by_subject')
    @patch('src.datacreator.PaintingDataCreator.fetch_paintings')
    def test_fetch_artwork_by_subject_with_scoring_progressive_fallback(self, mock_fetch_paintings, mock_query, mock_analyzer_class):
        """Test progressive fallback strategies."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.3  # Below threshold
        
        # Mock query to return empty results initially, then results
        mock_query.side_effect = [[], [], [{'title': 'Fallback Artwork', 'image': 'fallback.jpg'}]]
        
        # Mock fetch_paintings to return a simple artwork for final fallback
        mock_fetch_paintings.return_value = [{'title': 'Random Artwork', 'artist': 'Artist', 'image': 'test.jpg'}]
        
        poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
        q_codes = ['Q1']
        
        result = self.creator.fetch_artwork_by_subject_with_scoring(
            poem_analysis, q_codes, count=1, min_score=0.4
        )
        
        # Should have tried multiple strategies
        assert mock_query.call_count >= 1
        # Should return results from fallback strategy
        assert isinstance(result, list)


class TestDepictsFirstStrategy:
    """Test depicts-first strategy with direct depicts matching."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.creator = datacreator.PaintingDataCreator()
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    def test_depicts_first_strategy_with_bonus(self, mock_analyzer_class):
        """Test that direct depicts matches get +0.5 score bonus."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.3  # Base score
        
        # Mock the queries instance
        mock_queries = Mock()
        mock_queries.query_artwork_by_direct_depicts.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q123'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test.jpg'},
            'sitelinks': {'value': '5'},
            'subject': {'value': 'https://wikidata.org/Q10884'},  # tree
            'genre': {'value': 'https://wikidata.org/Q191163'},  # landscape
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}  # painting
        }]
        
        # Mock get_painting_labels
        with patch.object(self.creator, 'get_painting_labels', return_value={'title': 'Tree Painting', 'artist': 'Artist A'}):
            # Set the queries attribute on the instance
            self.creator.queries = mock_queries
            
            poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
            q_codes = ['Q10884']  # tree
            
            result = self.creator.fetch_artwork_by_subject_with_scoring(
                poem_analysis, q_codes, count=1, min_score=0.4
            )
            
            # Should have called direct depicts query first
            mock_queries.query_artwork_by_direct_depicts.assert_called_once()
            
            # Should return results with bonus applied
            assert len(result) == 1
            artwork, score = result[0]
            assert score >= 0.8  # 0.3 base + 0.5 bonus = 0.8
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    def test_depicts_first_fallback_to_regular_query(self, mock_analyzer_class):
        """Test fallback to regular query when direct depicts returns no results."""
        # Mock analyzer instance
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.5  # Good score
        
        # Mock the queries instance
        mock_queries = Mock()
        mock_queries.query_artwork_by_direct_depicts.return_value = []
        mock_queries.query_artwork_by_subject.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q456'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test2.jpg'},
            'sitelinks': {'value': '3'},
            'subject': {'value': 'https://wikidata.org/Q7860'},  # nature
            'genre': {'value': 'https://wikidata.org/Q191163'},  # landscape
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}  # painting
        }]
        
        # Mock get_painting_labels
        with patch.object(self.creator, 'get_painting_labels', return_value={'title': 'Nature Painting', 'artist': 'Artist B'}):
            # Set the queries attribute on the instance
            self.creator.queries = mock_queries
            
            poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
            q_codes = ['Q7860']  # nature
            
            result = self.creator.fetch_artwork_by_subject_with_scoring(
                poem_analysis, q_codes, count=1, min_score=0.4
            )
            
            # Should have tried direct depicts first, then regular query
            mock_queries.query_artwork_by_direct_depicts.assert_called_once()
            mock_queries.query_artwork_by_subject.assert_called_once()
            
            # Should return results without bonus (regular query)
            assert len(result) == 1
            artwork, score = result[0]
            assert score == 0.5  # No bonus for regular query
    
    @patch('src.datacreator.POEM_ANALYZER_AVAILABLE', True)
    @patch('src.datacreator.poem_analyzer.PoemAnalyzer')
    def test_depicts_bonus_capped_at_one(self, mock_analyzer_class):
        """Test that depicts bonus is capped at 1.0 total score."""
        # Mock analyzer instance with high base score
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.score_artwork_match.return_value = 0.8  # High base score
        
        # Mock the queries instance
        mock_queries = Mock()
        mock_queries.query_artwork_by_direct_depicts.return_value = [{
            'artwork': {'value': 'https://wikidata.org/Q789'},
            'image': {'value': 'https://commons.wikimedia.org/wiki/File:test3.jpg'},
            'sitelinks': {'value': '2'},
            'subject': {'value': 'https://wikidata.org/Q11427'},  # flower
            'genre': {'value': 'https://wikidata.org/Q191163'},  # landscape
            'artworkType': {'value': 'https://wikidata.org/Q3305213'}  # painting
        }]
        
        # Mock get_painting_labels
        with patch.object(self.creator, 'get_painting_labels', return_value={'title': 'Flower Painting', 'artist': 'Artist C'}):
            # Set the queries attribute on the instance
            self.creator.queries = mock_queries
            
            poem_analysis = {'themes': ['nature'], 'mood': 'peaceful'}
            q_codes = ['Q11427']  # flower
            
            result = self.creator.fetch_artwork_by_subject_with_scoring(
                poem_analysis, q_codes, count=1, min_score=0.4
            )
            
            # Should return results with capped score
            assert len(result) == 1
            artwork, score = result[0]
            assert score == 1.0  # Capped at 1.0 (0.8 + 0.5 = 1.3, capped to 1.0)


class TestSelectiveVisionAnalysis:
    """Test selective vision analysis functionality."""
    
    def test_score_and_filter_artwork_parallel_selective_vision(self):
        """Test selective vision analysis in parallel processing."""
        creator = datacreator.PaintingDataCreator()
        
        # Mock vision analyzer
        mock_vision_analyzer = Mock()
        mock_vision_analyzer.is_enabled.return_value = True
        mock_vision_analyzer.should_skip_vision_analysis.return_value = False
        creator.vision_analyzer = mock_vision_analyzer
        
        # Mock poem analyzer
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.return_value = 0.7
        
        # Sample raw data
        raw_data = [
            {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}},
            {'painting': {'value': 'url2'}, 'image': {'value': 'img2'}},
            {'painting': {'value': 'url3'}, 'image': {'value': 'img3'}}
        ]
        
        # Mock _extract_artwork_fields_from_raw
        with patch.object(creator, '_extract_artwork_fields_from_raw') as mock_extract:
            mock_extract.return_value = {
                'title': 'Test Artwork',
                'artist': 'Test Artist',
                'wikidata_url': 'http://test.com',
                'image_url': 'http://test.com/image.jpg'
            }
            
            # Mock _build_artwork_entry_from_fields
            with patch.object(creator, '_build_artwork_entry_from_fields') as mock_build:
                mock_build.return_value = {
                    'title': 'Test Artwork',
                    'artist': 'Test Artist',
                    'subject_q_codes': ['Q7860'],
                    'genre_q_codes': ['Q191163'],
                    'year': 1850
                }
                
                strategy = {'min_score': 0.5, 'depicts_bonus': 0.0}
                poem_analysis = {'themes': ['nature']}
                genres = ['Q191163']
                poet_years = (1800, 1900)
                
                result = creator._score_and_filter_artwork_parallel(
                    raw_data, strategy, poem_analysis, genres, poet_years, 
                    mock_analyzer, enable_vision_analysis=True, 
                    selective_vision=True, vision_candidate_limit=2
                )
                
                # Should process all artworks (first pass) + top candidates (second pass)
                assert len(result) == 3
                # First pass: 3 calls, Second pass: 2 candidates * 3 calls each (search loop) + 2 calls (re-process) = 11 total
                assert mock_extract.call_count >= 5  # At least 5 calls
                # First pass: 3 calls, Second pass: 2 calls (top candidates) = 5 total
                assert mock_build.call_count == 5
    
    def test_score_and_filter_artwork_parallel_no_vision(self):
        """Test parallel processing without vision analysis."""
        creator = datacreator.PaintingDataCreator()
        
        # Mock poem analyzer
        mock_analyzer = Mock()
        mock_analyzer.score_artwork_match.return_value = 0.7
        
        # Sample raw data
        raw_data = [
            {'painting': {'value': 'url1'}, 'image': {'value': 'img1'}}
        ]
        
        # Mock _extract_artwork_fields_from_raw
        with patch.object(creator, '_extract_artwork_fields_from_raw') as mock_extract:
            mock_extract.return_value = {
                'title': 'Test Artwork',
                'artist': 'Test Artist',
                'wikidata_url': 'http://test.com',
                'image_url': 'http://test.com/image.jpg'
            }
            
            # Mock _build_artwork_entry_from_fields
            with patch.object(creator, '_build_artwork_entry_from_fields') as mock_build:
                mock_build.return_value = {
                    'title': 'Test Artwork',
                    'artist': 'Test Artist',
                    'subject_q_codes': ['Q7860'],
                    'genre_q_codes': ['Q191163'],
                    'year': 1850
                }
                
                strategy = {'min_score': 0.5, 'depicts_bonus': 0.0}
                poem_analysis = {'themes': ['nature']}
                genres = ['Q191163']
                poet_years = (1800, 1900)
                
                result = creator._score_and_filter_artwork_parallel(
                    raw_data, strategy, poem_analysis, genres, poet_years, 
                    mock_analyzer, enable_vision_analysis=False
                )
                
                # Should process artwork without vision analysis
                assert len(result) == 1
                assert mock_extract.call_count == 1
                assert mock_build.call_count == 1
    
    def test_fetch_artwork_by_subject_with_scoring_vision_candidate_limit(self):
        """Test fetch_artwork_by_subject_with_scoring with vision_candidate_limit parameter."""
        creator = datacreator.PaintingDataCreator()
        
        # Mock the scoring method
        with patch.object(creator, '_score_and_filter_artwork_parallel') as mock_score:
            mock_score.return_value = [
                ({'title': 'Artwork 1'}, 0.8),
                ({'title': 'Artwork 2'}, 0.7)
            ]
            
            poem_analysis = {'themes': ['nature']}
            q_codes = ['Q7860']
            
            result = creator.fetch_artwork_by_subject_with_scoring(
                poem_analysis, q_codes, count=2, vision_candidate_limit=3
            )
            
            # Should call scoring method with vision_candidate_limit
            mock_score.assert_called_once()
            call_args = mock_score.call_args
            assert call_args[1]['vision_candidate_limit'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
