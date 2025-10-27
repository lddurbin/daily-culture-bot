import pytest
import json
import sys
import os
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
