<!-- 45d143c4-48d1-46d6-8fd5-e1d5107ca368 a18493d9-425d-40b0-8be5-4f1077b774b1 -->
# Refactor Codebase for Smaller, Focused Files

## Current State

**Large files identified:**

- `src/datacreator.py` - 1081 lines (20 methods in PaintingDataCreator class)
- `src/poem_analyzer.py` - 656 lines (15 methods in PoemAnalyzer class)
- `tests/test_email_sender.py` - 823 lines
- `tests/test_poem_analyzer.py` - 801 lines
- `tests/test_datacreator.py` - 766 lines
- `src/poem_fetcher.py` - 582 lines
- `src/email_sender.py` - 541 lines

**Target:** Break files into modules with 200-400 lines each for better maintainability.

## Refactoring Strategy

### 1. Split `datacreator.py` (1081 lines → 3-4 files)

**Create `src/wikidata_config.py` (~150 lines):**

- Extract style mappings dictionary (lines 47-65)
- Extract medium mappings dictionary
- Extract all Q-code constants and lookup tables
- Extract SPARQL query templates as constants

**Create `src/wikidata_queries.py` (~300 lines):**

- Move SPARQL query building methods
- `query_artwork_by_subject()` method
- `query_wikidata_paintings()` method
- Query caching logic
- Move `_get_cache_key()` and `_manage_cache_size()`

**Create `src/artwork_processor.py` (~300 lines):**

- Move data processing methods
- `process_painting_data()` method
- `get_artwork_inception_date()` method
- `get_painting_dimensions()` method
- `get_painting_labels()` method
- `clean_text()` utility
- `_get_medium_from_type()` utility

**Keep in `src/datacreator.py` (~330 lines):**

- Main `PaintingDataCreator` class with orchestration logic
- `__init__()` method
- High-level fetch methods: `fetch_paintings()`, `fetch_artwork_by_subject()`, `fetch_artwork_by_subject_with_scoring()`
- `create_sample_paintings()` method
- `get_daily_painting()` method
- JSON save methods
- Import and use the new modules

### 2. Split `poem_analyzer.py` (656 lines → 3 files)

**Create `src/poem_themes.py` (~200 lines):**

- Extract all `theme_mappings` dictionary (~100 lines)
- Extract all `emotion_mappings` dictionary (~100 lines)
- These are pure configuration data

**Create `src/openai_analyzer.py` (~200 lines):**

- Move OpenAI-specific logic
- `analyze_poem_with_ai()` method
- OpenAI client initialization
- Prompt building logic
- Response parsing

**Keep in `src/poem_analyzer.py` (~250 lines):**

- Main `PoemAnalyzer` class
- `__init__()` method
- `analyze_poem()` orchestration method
- `_analyze_with_keywords()` method
- Theme matching methods
- `analyze_multiple_poems()` method
- `score_artwork_match()` method
- Import themes from `poem_themes.py`
- Import OpenAI analyzer if available

### 3. Split Test Files (Optional but Recommended)

**For `tests/test_datacreator.py` (766 lines → 2-3 files):**

- `tests/test_wikidata_queries.py` - Test query building
- `tests/test_artwork_processor.py` - Test data processing
- `tests/test_datacreator.py` - Test main orchestration (keep existing)

**For `tests/test_poem_analyzer.py` (801 lines → 2 files):**

- `tests/test_openai_analyzer.py` - Test OpenAI integration
- `tests/test_poem_analyzer.py` - Test main analysis logic (keep existing)

**For `tests/test_email_sender.py` (823 lines → 2 files):**

- `tests/test_email_builder.py` - Test email content building
- `tests/test_email_sender.py` - Test email sending logic (keep existing)

### 4. Extract Utilities (Optional)

**Create `src/utils.py` (~100 lines):**

- Common utility functions used across modules
- Text cleaning functions
- URL validation
- Date parsing helpers
- Constants shared across modules

## Implementation Order

1. **Phase 1: Extract Configuration** (Lowest Risk)

- Create `poem_themes.py` with theme/emotion mappings
- Create `wikidata_config.py` with style/medium mappings
- Update imports in existing files
- Run tests to verify no breakage

2. **Phase 2: Extract Queries** (Medium Risk)

- Create `wikidata_queries.py` with SPARQL logic
- Update `datacreator.py` to use new module
- Update tests
- Run full test suite

3. **Phase 3: Extract Processing** (Medium Risk)

- Create `artwork_processor.py` with data processing
- Create `openai_analyzer.py` with AI logic
- Update main modules
- Update tests
- Run full test suite

4. **Phase 4: Split Tests** (Optional)

- Split large test files if desired
- Ensure all tests still pass

## Benefits

1. **Maintainability**: Easier to find and modify specific functionality
2. **Testability**: Smaller, focused modules are easier to test
3. **Readability**: 200-400 line files are much easier to understand
4. **Reusability**: Extracted utilities can be reused across modules
5. **Collaboration**: Smaller files reduce merge conflicts
6. **Performance**: Faster IDE indexing and navigation

## Files to Create

**New modules:**

- `src/wikidata_config.py` - Configuration data
- `src/wikidata_queries.py` - SPARQL query logic
- `src/artwork_processor.py` - Artwork data processing
- `src/poem_themes.py` - Theme/emotion mappings
- `src/openai_analyzer.py` - OpenAI integration
- `src/utils.py` (optional) - Shared utilities

**New test files (optional):**

- `tests/test_wikidata_queries.py`
- `tests/test_artwork_processor.py`
- `tests/test_openai_analyzer.py`
- `tests/test_email_builder.py`

## Files to Modify

**Source files:**

- `src/datacreator.py` - Reduce from 1081 to ~330 lines
- `src/poem_analyzer.py` - Reduce from 656 to ~250 lines
- `src/daily_paintings.py` - Update imports if needed
- `src/email_sender.py` - Potentially split if desired

**Test files:**

- Update imports in all test files
- Optionally split large test files

## Success Criteria

1. All files under 500 lines (target 200-400 lines)
2. Clear separation of concerns (config, queries, processing, orchestration)
3. All existing tests pass without modification (except imports)
4. No functional changes - pure refactoring
5. Import structure remains clean and logical
6. Documentation updated to reflect new module structure

## Testing Strategy

After each phase:

1. Run full test suite: `pytest`
2. Test basic functionality: `python daily_culture_bot.py --fast --count 1`
3. Test complementary mode: `python daily_culture_bot.py --complementary --fast`
4. Check no import errors or circular dependencies
5. Verify code coverage remains the same or improves

### To-dos

- [ ] Create src/poem_themes.py with theme_mappings and emotion_mappings extracted from poem_analyzer.py
- [ ] Create src/wikidata_config.py with style_mappings and medium_mappings extracted from datacreator.py
- [ ] Update src/poem_analyzer.py to import from poem_themes.py
- [ ] Update src/datacreator.py to import from wikidata_config.py
- [ ] Run all tests to verify Phase 1 refactoring (configuration extraction)
- [ ] Create src/wikidata_queries.py with SPARQL query methods from datacreator.py
- [ ] Create src/openai_analyzer.py with OpenAI integration logic from poem_analyzer.py
- [ ] Create src/artwork_processor.py with data processing methods from datacreator.py
- [ ] Refactor src/datacreator.py to use extracted modules (queries, processor, config)
- [ ] Refactor src/poem_analyzer.py to use extracted modules (themes, openai)
- [ ] Run all tests to verify Phase 2-3 refactoring (logic extraction)
- [ ] Update README.md and docstrings to reflect new module structure