# Testing Documentation

This document describes the testing setup and strategy for the Daily Artwork Bot project.

## Test Suite Overview

The project includes a comprehensive test suite with **45 tests** covering:
- Command-line argument parsing
- Image download functionality
- HTML gallery generation
- Sample data creation
- JSON file operations
- Data processing and cleaning
- API integration (with mocking)
- Error handling
- Edge cases

**Current Coverage**: 73% overall
- `daily_paintings.py`: 89% coverage
- `datacreator.py`: 67% coverage

## Running Tests

### Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test Files
```bash
pytest test_daily_paintings.py
pytest test_datacreator.py
```

### Run Specific Test Classes
```bash
pytest test_daily_paintings.py::TestArgumentParsing
pytest test_datacreator.py::TestCreateSamplePaintings
```

### Run Specific Tests
```bash
pytest test_daily_paintings.py::TestArgumentParsing::test_default_arguments
```

### Run Tests in Parallel (Faster)
```bash
pytest -n auto
```

## Coverage Reports

### Terminal Coverage Report
```bash
pytest --cov=daily_paintings --cov=datacreator --cov-report=term-missing
```

### HTML Coverage Report
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

## Test Files

### `test_daily_paintings.py`
Tests for the main application module:
- **TestArgumentParsing** (6 tests): Command-line argument parsing
- **TestDownloadImage** (4 tests): Image download functionality
- **TestGenerateHTMLGallery** (3 tests): HTML gallery generation
- **TestMain** (3 tests): Main function integration
- **TestFileOperations** (2 tests): File operations and JSON handling

**Total**: 18 tests

### `test_datacreator.py`
Tests for the data creator module:
- **TestPaintingDataCreatorInit** (2 tests): Initialization
- **TestCreateSamplePaintings** (4 tests): Sample data creation
- **TestCleanText** (4 tests): Text cleaning functionality
- **TestGetHighResImageUrl** (4 tests): Image URL processing
- **TestFetchPaintings** (3 tests): Painting fetching
- **TestSaveToJson** (2 tests): JSON saving
- **TestAppendToExistingJson** (2 tests): JSON appending
- **TestProcessPaintingData** (2 tests): Data processing
- **TestGetDailyPainting** (2 tests): Daily painting retrieval
- **TestQueryWikidataPaintings** (2 tests): Wikidata queries

**Total**: 27 tests

## Mocking Strategy

The test suite uses mocking to avoid:
- Actual network requests to Wikidata/Wikimedia APIs
- File I/O operations
- External dependencies

Key mocking approaches:
- `@patch` decorator for patching function calls
- `mock_open` for file operations
- `Mock` objects for API responses
- `side_effect` for simulating errors

## Continuous Integration

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml
```

## Adding New Tests

When adding new features, follow these guidelines:

1. **Create descriptive test names**: Use clear, descriptive test names
2. **Follow Arrange-Act-Assert pattern**: Setup, execute, verify
3. **Mock external dependencies**: Don't make real API calls
4. **Test edge cases**: Include error handling and boundary conditions
5. **Maintain coverage**: Aim for 80%+ coverage on new code

### Example Test Structure
```python
class TestNewFeature:
    """Test suite for new feature."""
    
    def test_new_feature_success(self):
        """Test successful execution of new feature."""
        # Arrange
        test_data = {...}
        
        # Act
        result = function_under_test(test_data)
        
        # Assert
        assert result == expected_value
    
    def test_new_feature_error(self):
        """Test error handling for new feature."""
        # Arrange
        invalid_data = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            function_under_test(invalid_data)
```

## Known Limitations

1. **Limited API Testing**: Tests mock API calls rather than making real requests
2. **File Operations**: File I/O is mocked, not actually performed
3. **Time-dependent Tests**: Some tests may be time-sensitive
4. **Integration Tests**: No integration tests against real APIs

## Future Improvements

- [ ] Add integration tests with actual API calls
- [ ] Add performance/load tests
- [ ] Add property-based tests using Hypothesis
- [ ] Increase coverage to 90%+
- [ ] Add test documentation for complex scenarios
- [ ] Set up automated test runs on CI/CD

## Troubleshooting

### Tests Fail with Import Errors
```bash
# Make sure you're in the project directory
cd /path/to/daily-culture-bot

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Tests Hang or Timeout
- Check for unmocked network calls
- Verify test timeouts are set appropriately
- Run tests individually to identify the culprit

### Coverage Report Not Generating
```bash
# Make sure pytest-cov is installed
pip install pytest-cov

# Run with coverage flags
pytest --cov=. --cov-report=html
```

## Contributing

When contributing tests:
1. Run the full test suite before submitting
2. Ensure new tests follow existing patterns
3. Update this documentation if adding new test categories
4. Aim for clear, readable, maintainable tests

---

For more information, see the main [README.md](README.md) file.
