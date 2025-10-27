# Enhanced Poem-Artwork Matching System

## Overview

The **complementary mode** (`--complementary` flag) is a sophisticated AI-powered feature that intelligently pairs poems with artwork based on concrete element analysis, thematic matching, and emotional resonance. This enhanced system represents a major evolution of the Daily Culture Bot, using GPT-4 for deep poem analysis, GPT-4 Vision for artwork image analysis, multi-pass matching, and comprehensive explainability to create highly precise poem-artwork pairings.

## Installation Requirements

### Dependencies

The enhanced matching system requires additional dependencies:

```bash
pip install -r requirements.txt
```

Key new dependencies:
- `spacy>=3.7.0` - For concrete noun extraction and NLP processing
- `openai>=1.0.0` - For GPT-4 and GPT-4 Vision API integration

### spaCy Language Model

The system requires the English language model for spaCy:

```bash
python -m spacy download en_core_web_sm
```

This downloads approximately 12.8 MB of language data for English text processing.

### Environment Variables

Ensure you have the following environment variables set:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Cost Estimation

Based on comprehensive testing with GPT-4 and GPT-4 Vision APIs:

### GPT-4 Poem Analysis
- **Average cost per poem analysis**: ~$0.002
- **Tokens used**: ~800 tokens per analysis
- **Model**: GPT-4 (gpt-4)

### GPT-4 Vision Artwork Analysis
- **Average cost per artwork analysis**: ~$0.015
- **Tokens used**: ~1,200 tokens per analysis (including image processing)
- **Model**: GPT-4 Vision (gpt-4o)

### Projected Costs for Different Scales
- **Small scale (10 poems + 10 artworks)**: ~$0.17
- **Medium scale (100 poems + 100 artworks)**: ~$1.70
- **Large scale (1000 poems + 1000 artworks)**: ~$17.00

### Cost Optimization Features
- **Vision analysis caching**: Avoids redundant API calls for the same artwork
- **Optional vision analysis**: Can be disabled with `--no-vision` flag
- **Multi-pass optimization**: Fetches candidates first, then uses AI selection
- **Cost tracking**: Built-in monitoring and warnings for budget management

The vision analysis is optional and can be disabled with the `--no-vision` flag to reduce costs by ~90%.

## How Complementary Mode Works

### 1. Enhanced Multi-Pass Workflow

When you use `--complementary` mode, the system follows this sophisticated workflow:

1. **Fetches poems first** from PoetryDB API
2. **Analyzes poems** using GPT-4 to extract themes, emotions, concrete elements, and visual suggestions
3. **Extracts concrete nouns** using spaCy NLP for precise object matching
4. **Maps analysis to Wikidata Q-codes** (entity identifiers) using comprehensive mappings
5. **First Pass**: Fetches candidate artworks (3x more than needed) using direct depicts matching
6. **Second Pass**: Uses GPT-4 to intelligently select best matches from candidates
7. **Vision Analysis**: Analyzes artwork images using GPT-4 Vision (optional)
8. **Generates explanations** for each match with detailed reasoning
9. **Falls back gracefully** if no good matches are found

### 2. AI Analysis Process

The system uses **OpenAI's GPT-4** model to analyze poems with a sophisticated prompt designed specifically for visual art pairing:

```json
You are an expert in analyzing poetry for visual art pairing. Analyze this poem and return ONLY a JSON object with the following structure:

{
  "primary_emotions": ["emotion1", "emotion2"],  // Top 2-3 dominant emotions
  "secondary_emotions": ["emotion3"],  // Supporting emotions
  "emotional_tone": "playful|serious|ironic|melancholic|celebratory|contemplative",
  "themes": ["theme1", "theme2"],  // Core subjects
  "narrative_elements": {
    "has_protagonist": true/false,
    "protagonist_type": "human|animal|abstract|none",
    "setting": "indoor|outdoor|abstract|urban|rural|seascape|celestial",
    "time_of_day": "dawn|day|dusk|night|ambiguous",
    "season": "spring|summer|autumn|winter|timeless",
    "human_presence": "central|peripheral|absent|implied",
    "weather": "clear|stormy|rainy|snowy|foggy|ambiguous"
  },
  "concrete_elements": {
    "natural_objects": ["specific nature elements"],
    "man_made_objects": ["specific objects, buildings, tools"],
    "living_beings": ["people, animals mentioned"],
    "abstract_concepts": ["love, death, time, etc."]
  },
  "symbolic_objects": ["objects with symbolic meaning"],
  "spatial_qualities": "enclosed|open|vertical|horizontal|centered|dispersed",
  "movement_energy": "static|flowing|explosive|rhythmic|stagnant",
  "color_references": ["explicit color words in poem"],
  "visual_aesthetic": {...existing structure...}
}

Poem:
[poem text here]

Return ONLY valid JSON with no additional text.
```

### 3. Dual Analysis System

The system uses a **hybrid approach** for robust analysis:

- **Primary**: OpenAI AI analysis (if API key is available)
- **Fallback**: Keyword-based analysis using predefined theme mappings
- **Combined**: Merges both approaches for comprehensive coverage

This ensures the system works even without OpenAI API access, gracefully degrading to keyword-based analysis.

### 4. Artwork Matching & Scoring Algorithm

The system scores artwork matches using a sophisticated **weighted scoring algorithm** with multiple factors:

#### Scoring Components:

1. **Concrete Elements Match (35% weight)**
   - Direct noun matches: 20%
   - Setting/narrative elements: 10%
   - Spatial/compositional alignment: 5%

2. **Theme/Subject Match (30% weight)**
   - Matches artwork subjects to detected poem themes
   - Uses Wikidata Q-code mappings for precise matching

3. **Emotional Tone Match (25% weight)**
   - Primary emotions: 15%
   - Secondary emotions: 10%

4. **Genre Alignment (10% weight)**
   - Maps emotional tone to appropriate artwork genres

#### Specificity Bonuses:
- Direct noun match (rose in poem + rose in artwork): +0.2
- Setting match (ocean in poem + seascape): +0.15
- Time of day match (night poem + nocturne): +0.1
- Season match (spring poem + spring scene): +0.1
- Color palette match: +0.05

### 5. Era-Based Matching

The system includes **temporal matching** that considers the poet's lifetime and artwork creation date:

- **Perfect Match**: Artwork created during poet's lifetime = 1.0 score
- **Buffer Zone**: ±50 years from poet's lifetime with linear decay
- **Outside Buffer**: 0.0 score for artworks too far temporally

This creates historically appropriate pairings when poet dates are available.

### 6. New Enhanced Features

#### Concrete Element Extraction
- **spaCy Integration**: Extracts concrete nouns, objects, and settings from poems
- **Categorization**: Automatically categorizes objects as natural, man-made, living beings, or settings
- **Q-code Mapping**: Maps extracted objects to Wikidata entities for precise matching

#### GPT-4 Vision Analysis
- **Image Analysis**: Analyzes artwork images to detect objects, colors, composition, and mood
- **Caching**: Intelligent caching system to avoid redundant API calls
- **Cost Control**: Optional feature that can be disabled to reduce costs

#### Multi-Pass Analysis
- **Candidate Selection**: Fetches 3x more candidates than needed for better selection
- **AI-Driven Selection**: Uses GPT-4 to intelligently choose best matches from candidates
- **Fallback Logic**: Graceful degradation if AI selection fails

#### Match Explanations
- **Detailed Reasoning**: Generates human-readable explanations for each match
- **Specific Connections**: Identifies concrete connections between poem and artwork
- **Conflict Detection**: Highlights potential tensions or mismatches
- **Multiple Output Formats**: Available in console, email, and JSON output

#### Two-Stage Matching
- **Hard Constraints**: Filters out incompatible artwork (e.g., war scenes for peaceful poems)
- **Soft Conflicts**: Reduces scores for minor mismatches (e.g., indoor vs outdoor)
- **Conflict Mappings**: Comprehensive rules for avoiding inappropriate pairings

#### Direct Depicts Matching
- **P180 Property**: Prioritizes artworks that directly depict objects mentioned in poems
- **Score Bonuses**: +0.5 bonus for direct depicts matches
- **Precision**: More accurate than broader subject matching

### 7. Usage Examples

```bash
# Basic complementary mode with all enhanced features
python daily_culture_bot.py --complementary --email user@example.com

# With custom matching parameters
python daily_culture_bot.py --complementary --min-match-score 0.6 --max-fame-level 15

# Fast mode for testing
python daily_culture_bot.py --complementary --fast --count 1

# Multiple poems with complementary matching
python daily_culture_bot.py --complementary --poem-count 3 --count 3

# Disable vision analysis to reduce costs
python daily_culture_bot.py --complementary --no-vision

# Disable multi-pass analysis for faster processing
python daily_culture_bot.py --complementary --no-multi-pass

# Enable detailed match explanations
python daily_culture_bot.py --complementary --explain-matches

# Custom candidate count for multi-pass analysis
python daily_culture_bot.py --complementary --candidate-count 30

# Combined flags for cost-effective operation
python daily_culture_bot.py --complementary --no-vision --no-multi-pass --explain-matches
```

### 8. Technical Implementation Details

#### Files Involved:
- `src/daily_paintings.py` - Main workflow orchestration
- `src/poem_analyzer.py` - Enhanced poem analysis and scoring
- `src/openai_analyzer.py` - AI-driven artwork selection and analysis
- `src/poem_themes.py` - Extended object mappings and conflict rules
- `src/datacreator.py` - Enhanced artwork fetching with vision analysis
- `src/wikidata_queries.py` - Direct depicts queries and SPARQL integration
- `src/concrete_element_extractor.py` - Concrete noun extraction and Q-code mapping
- `src/vision_analyzer.py` - GPT-4 Vision artwork analysis with caching
- `src/match_explainer.py` - Human-readable match explanation generation
- `src/two_stage_matcher.py` - Hard constraints and weighted scoring
- `src/wikidata_config.py` - Configuration management

#### Error Handling:
- Graceful fallback to keyword analysis if OpenAI fails
- Retry logic for API calls with exponential backoff
- Comprehensive error messages and user guidance
- Fallback to random artwork if no matches found

#### Performance Considerations:
- Query caching to prevent redundant Wikidata calls (50-entry LRU cache)
- Connection pooling with `requests.Session()` for efficient HTTP requests
- Q-code limiting (max 8) to prevent overly complex queries
- Timeout management for Wikidata SPARQL queries
- Vision analysis caching to avoid redundant API calls

### 9. Match Status Tracking

The system tracks match quality for each artwork:
- **"Matched"** - High-quality thematic/emotional match found
- **"Fallback (Random)"** - No good matches found, using random artwork
- **"Sample"** - Using sample data in fast mode

### 10. Future Enhancements

The complementary mode is designed for extensibility:
- Additional AI models can be integrated
- More sophisticated scoring algorithms can be added
- Enhanced era-based matching with cultural context
- Multi-modal analysis (text + image) for even better pairings

## Conclusion

The complementary mode represents a sophisticated AI-driven approach to cultural content curation, combining modern AI analysis with structured knowledge graphs to create meaningful poem-artwork pairings. It demonstrates how AI can enhance cultural discovery by finding unexpected but meaningful connections between different forms of artistic expression.
