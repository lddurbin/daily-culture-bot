<!-- 4cdc2a3e-ad40-4370-bad4-bad50c4f60bf 1b2b9182-6528-4232-a5c2-aafd9f968c26 -->
# Comprehensive Test Coverage Improvement Plan

## Overview

Implement systematic testing improvements to prevent issues like the OpenAI client initialization bug and match explainer list handling error from reaching production. Target: 85%+ coverage across all modules.

## Step 1: Add Integration Tests (Priority: High)

### 1.1 Create Integration Test for OpenAI Client Passing

**File:** `tests/test_integration_workflow.py` (new)

Add test to verify OpenAI client is properly passed between components:

- Test that `poem_analyzer_instance.openai_client` is correctly used (not `creator.openai_client`)
- Test the full workflow: PoemAnalyzer → OpenAIAnalyzer → AI selection
- Use optional skip condition when API key unavailable
- Mock OpenAI responses to avoid actual API calls

### 1.2 Add Integration Test for Complete Complementary Mode Flow

**File:** `tests/test_integration_workflow.py`

Add end-to-end test for complementary mode:

- Test poem fetching → analysis → artwork matching → explanation generation
- Verify all components connect correctly
- Test with and without vision analysis
- Test fallback behavior when OpenAI unavailable

### 1.3 Update Existing Integration Tests

**File:** `tests/test_complementary_mode_integration.py`

Improve existing tests:

- Keep skip conditions but add fallback mocked versions
- Add assertions for client initialization
- Test error paths and fallbacks

**Estimated Lines:** ~200 lines of new tests

## Step 2: Add Edge Case Tests (Priority: High)

### 2.1 Match Explainer Edge Cases

**File:** `tests/test_match_explainer.py`

Add tests for:

- Nested lists in themes: `[['nature', 'night'], 'love']`
- Nested lists in emotions: `[['melancholy'], 'peace']`
- Nested lists in concrete elements: `[['tree', 'moon'], 'sky']`
- Mixed list/string types throughout
- Empty nested lists: `[[]]`
- Deeply nested structures: `[[['item']]]`

Test class: `TestMatchExplainerEdgeCases`

### 2.2 Poem Analysis Edge Cases

**File:** `tests/test_poem_analyzer.py`

Add tests for:

- Malformed AI responses
- Unexpected data structures from OpenAI
- Missing required fields in analysis
- Type mismatches in analysis results

Test class: `TestPoemAnalysisEdgeCases`

### 2.3 Data Structure Validation Tests

**File:** `tests/test_data_validation.py` (new)

Add tests to validate:

- Poem analysis data structure consistency
- Artwork data structure consistency
- Vision analysis data structure consistency
- Add schema validation using dataclasses or pydantic

**Estimated Lines:** ~150 lines of new tests

## Step 3: Add Real Data Tests (Priority: Medium)

### 3.1 Capture Real Data Samples

**File:** `tests/fixtures/real_data_samples.json` (new)

Create fixture file with real data from successful runs:

- Real poem analysis results (with nested lists)
- Real artwork data structures
- Real vision analysis results
- Real match explanations

### 3.2 Add Real Data Replay Tests

**File:** `tests/test_real_data_scenarios.py` (new)

Add tests using real captured data:

- Test match explainer with real poem analysis data
- Test artwork matching with real data structures
- Test full workflow with historical successful runs
- Test previously failing scenarios (nested lists, etc.)

Test class: `TestRealDataScenarios`

**Estimated Lines:** ~100 lines of tests + fixtures

## Step 4: Add GitHub Actions Simulation Tests (Priority: Medium)

### 4.1 Create GitHub Actions Environment Simulator

**File:** `tests/test_github_actions_workflow.py` (new)

Add test that simulates GitHub Actions environment:

- Mock environment variables (API keys, etc.)
- Test with same parameters used in `.github/workflows/daily-email-optimized.yml`
- Test fallback behavior when API unavailable
- Verify error handling and graceful degradation

### 4.2 Add Workflow Configuration Tests

**File:** `tests/test_workflow_config.py` (new)

Validate workflow configurations:

- Test CLI arguments match workflow YAML
- Test required environment variables are documented
- Test fallback strategies work correctly

**Estimated Lines:** ~120 lines of new tests

## Step 5: Improve Test Coverage to 85%+ (Priority: High)

### 5.1 Analyze Current Coverage Gaps

Run coverage analysis to identify specific untested lines:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Focus on modules below 85%:

- `daily_paintings.py`: 58% → 85%+ (need ~97 more lines)
- `two_stage_matcher.py`: 65% → 85%+ (need ~50 more lines)
- `datacreator.py`: 73% → 85%+ (need ~66 more lines)
- `match_explainer.py`: 75% → 85%+ (need ~16 more lines)
- `poem_fetcher.py`: 78% → 85%+ (need ~15 more lines)

### 5.2 Add Tests for daily_paintings.py

**File:** `tests/test_daily_paintings.py`

Add missing coverage:

- Test error paths in main()
- Test OpenAI client initialization check
- Test all command-line argument combinations
- Test match explanation generation loop
- Test fallback scenarios
- Test email sending with match explanations

Target: Add ~50 new test cases

### 5.3 Add Tests for two_stage_matcher.py

**File:** `tests/test_two_stage_matcher.py`

Add missing coverage:

- Test all scoring methods with edge cases
- Test hard constraints with various inputs
- Test soft conflicts detection
- Test era scoring calculations
- Test emotion mapping edge cases

Target: Add ~30 new test cases

### 5.4 Add Tests for datacreator.py

**File:** `tests/test_datacreator.py`

Add missing coverage:

- Test selective vision analysis edge cases
- Test error handling in parallel processing
- Test cache management edge cases
- Test fallback strategies
- Test timeout handling

Target: Add ~40 new test cases

### 5.5 Add Tests for Other Modules

**Files:** Various test files

- `poem_fetcher.py`: Test timeout handling, retry logic
- `match_explainer.py`: Test _generate_summary edge cases
- `vision_analyzer.py`: Test cache invalidation, error recovery

Target: Add ~25 new test cases

**Estimated Lines:** ~600 lines of new tests

## Implementation Order

1. **Phase 1 (Days 1-2):** Steps 1 & 2 - Integration and Edge Case Tests

   - Prevents the specific bugs we just encountered
   - Immediate value for production stability

2. **Phase 2 (Day 3):** Step 3 - Real Data Tests

   - Captures real-world scenarios
   - Builds on integration tests

3. **Phase 3 (Day 4):** Step 4 - GitHub Actions Simulation

   - Validates CI/CD workflow
   - Ensures production parity

4. **Phase 4 (Days 5-7):** Step 5 - Systematic Coverage Improvement

   - Methodical approach to 85%+ coverage
   - Fill remaining gaps

## Success Criteria

- All new tests passing
- Overall coverage ≥ 85%
- No module below 85% coverage
- Integration tests verify component connections
- Edge cases for nested data structures covered
- GitHub Actions workflow validated
- CI/CD pipeline remains green

## Step 6: Refactor Large Files (Priority: Medium)

### 6.1 Refactor datacreator.py (1,298 lines → ~400 lines)

**Current Structure Issues:**

- Single monolithic class with too many responsibilities
- Mixes query logic, data processing, scoring, and caching
- Hard to test individual components

**Refactoring Strategy:**

Split into multiple focused modules:

1. **`src/artwork_fetcher.py`** (new, ~250 lines)

   - Handle Wikidata queries and raw data fetching
   - Move: `fetch_paintings()`, `query_artwork_by_subject()`, `get_daily_painting()`
   - Class: `ArtworkFetcher`

2. **`src/artwork_scorer.py`** (new, ~300 lines)

   - Handle scoring and filtering logic
   - Move: `_score_and_filter_artwork_parallel()`, `fetch_artwork_by_subject_with_scoring()`
   - Class: `ArtworkScorer`

3. **`src/datacreator.py`** (refactored, ~400 lines)

   - Orchestrate fetcher and scorer
   - Keep: initialization, sample data creation, JSON operations
   - Use composition to delegate to fetcher and scorer

**Test Files:**

- Create `tests/test_artwork_fetcher.py` (~400 lines)
- Create `tests/test_artwork_scorer.py` (~500 lines)
- Refactor `tests/test_datacreator.py` (2,194 → ~800 lines)

### 6.2 Refactor poem_analyzer.py (797 lines → ~300 lines)

**Current Issues:**

- Mixes pattern matching, AI integration, and scoring
- Large methods difficult to test in isolation

**Refactoring Strategy:**

Split functionality:

1. **Keep in `src/poem_analyzer.py`** (~300 lines)

   - Main `PoemAnalyzer` class
   - Keyword-based analysis
   - Theme detection

2. **Already extracted:** `src/openai_analyzer.py` (279 lines) ✓

   - AI integration is already separate

3. **Move scoring to:** `src/artwork_scorer.py`

   - Move: `score_artwork_match()`, `_calculate_era_score()`, `_calculate_specificity_bonus()`
   - Consolidate all scoring logic in one place

**Test Files:**

- Refactor `tests/test_poem_analyzer.py` (1,157 → ~500 lines)
- Tests for scoring moved to `test_artwork_scorer.py`

### 6.3 Refactor daily_paintings.py (590 lines → ~350 lines)

**Current Issues:**

- Long main() function (300+ lines)
- Mixes CLI parsing, workflow orchestration, and output formatting

**Refactoring Strategy:**

Extract modules:

1. **`src/workflow_orchestrator.py`** (new, ~250 lines)

   - Move workflow logic from main()
   - Class: `WorkflowOrchestrator` with methods for each mode
   - Handle complementary mode, fast mode, email mode

2. **Keep in `src/daily_paintings.py`** (~350 lines)

   - CLI argument parsing
   - Entry point main()
   - Output formatting
   - Use orchestrator for workflow

**Test Files:**

- Create `tests/test_workflow_orchestrator.py` (~300 lines)
- Refactor `tests/test_daily_paintings.py` (621 → ~350 lines)

### 6.4 Refactor poem_fetcher.py (590 lines → ~400 lines)

**Current Issues:**

- Mixed concerns: fetching, filtering, date enrichment

**Refactoring Strategy:**

1. **Keep core fetching** (~400 lines)

   - Poem fetching logic
   - Basic filtering

2. **Already separate:** Date fetching is cohesive

   - Keep `get_poet_dates()` in this file

**Test Files:**

- Refactor `tests/test_poem_fetcher.py` (774 → ~500 lines)
- Split by functionality

### 6.5 Refactor email_sender.py (541 lines → ~350 lines)

**Current Issues:**

- Long HTML/text building methods

**Refactoring Strategy:**

1. **`src/email_templates.py`** (new, ~200 lines)

   - Move HTML/text template building
   - Class: `EmailTemplateBuilder`

2. **Keep in `src/email_sender.py`** (~350 lines)

   - Email sending logic
   - Configuration
   - Use template builder

**Test Files:**

- Create `tests/test_email_templates.py` (~150 lines)
- Refactor `tests/test_email_sender.py` (841 → ~500 lines)

### 6.6 Refactor two_stage_matcher.py (506 lines → ~400 lines)

**Current Issues:**

- Can be streamlined

**Refactoring Strategy:**

Move scoring methods to `artwork_scorer.py`:

- Consolidate all scoring in one place
- Keep matching logic in two_stage_matcher

**Test Files:**

- Refactor `tests/test_two_stage_matcher.py` (545 → ~350 lines)

**Estimated Refactoring Impact:**

- 6 new focused modules created
- ~2,000 lines of code reorganized
- Improved testability and maintainability
- Each module < 400 lines, focused on single responsibility

## Files to Create/Modify

**New Files (Refactoring):**

- `src/artwork_fetcher.py` (~250 lines)
- `src/artwork_scorer.py` (~300 lines)
- `src/workflow_orchestrator.py` (~250 lines)
- `src/email_templates.py` (~200 lines)
- `tests/test_artwork_fetcher.py` (~400 lines)
- `tests/test_artwork_scorer.py` (~500 lines)
- `tests/test_workflow_orchestrator.py` (~300 lines)
- `tests/test_email_templates.py` (~150 lines)

**New Files (Testing):**

- `tests/test_integration_workflow.py` (~200 lines)
- `tests/test_data_validation.py` (~150 lines)
- `tests/test_real_data_scenarios.py` (~100 lines)
- `tests/test_github_actions_workflow.py` (~120 lines)
- `tests/test_workflow_config.py` (~100 lines)
- `tests/fixtures/real_data_samples.json`

**Refactored Files (Reduced Size):**

- `src/datacreator.py` (1,298 → ~400 lines, -898)
- `src/poem_analyzer.py` (797 → ~300 lines, -497)
- `src/daily_paintings.py` (590 → ~350 lines, -240)
- `src/poem_fetcher.py` (590 → ~400 lines, -190)
- `src/email_sender.py` (541 → ~350 lines, -191)
- `src/two_stage_matcher.py` (506 → ~400 lines, -106)
- `tests/test_datacreator.py` (2,194 → ~800 lines, -1,394)
- `tests/test_poem_analyzer.py` (1,157 → ~500 lines, -657)
- `tests/test_daily_paintings.py` (621 → ~350 lines, -271)
- `tests/test_email_sender.py` (841 → ~500 lines, -341)
- `tests/test_poem_fetcher.py` (774 → ~500 lines, -274)
- `tests/test_two_stage_matcher.py` (545 → ~350 lines, -195)

**Modified Files (Testing):**

- `tests/test_match_explainer.py` (add ~100 lines)
- `tests/test_complementary_mode_integration.py` (add ~50 lines)
- `pytest.ini` (if coverage thresholds need adjustment)

**Total Estimated Code Changes:**

- New test code: ~1,170 lines
- New refactored modules: ~1,000 lines
- Code reorganization: ~2,000 lines moved
- Net reduction in file sizes: ~4,800 lines (better organization)

### To-dos

- [ ] Add integration tests for OpenAI client passing and complementary mode flow
- [ ] Add edge case tests for nested lists and mixed data types in match explainer
- [ ] Create real data fixtures and replay tests
- [ ] Add GitHub Actions workflow simulation tests
- [ ] Improve daily_paintings.py coverage from 58% to 85%+
- [ ] Improve two_stage_matcher.py coverage from 65% to 85%+
- [ ] Improve datacreator.py coverage from 73% to 85%+
- [ ] Improve remaining modules to 85%+ coverage
- [ ] Run final coverage report and verify 85%+ across all modules