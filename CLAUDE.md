# DPDP Act Compliance Checker - Architecture Documentation

## Project Overview

This is a **DPDP Act (Digital Personal Data Protection Act, India) Compliance Checker** web application that evaluates privacy policies of AI service providers against Indian data protection regulations.

**Purpose**: Automatically analyze privacy policies to check compliance with DPDP Act requirements and generate detailed scoring reports.

**Tech Stack**: Flask (Python), Groq LLM API, ReportLab (PDF generation)

---

## Architecture Philosophy

This codebase is designed with two core principles:

### 1. Readability
- Clear separation of concerns with dedicated modules
- Descriptive naming conventions
- Self-documenting code structure
- Consistent patterns across policy implementations

### 2. Scalability
- Easy to add new policy categories (follows plug-and-play pattern)
- Centralized configuration management
- Modular AI function implementations
- Extensible scoring system

---

## Folder Structure

```
DPDP_ACT_UIDD/
│
├── app.py                          # Flask application entry point
├── checker.py                      # Orchestrates all compliance checks
├── scorer.py                       # Centralized scoring engine
│
├── all_policies/                   # Policy check implementations
│   ├── __init__.py                 # Registry of all policy groups
│   ├── a_notice.py                 # Notice & Transparency checks
│   ├── b_consent.py                # Consent Management checks
│   ├── c_retention.py              # Retention checks
│   ├── d_deletion.py               # Deletion checks
│   └── e_data_minimization.py      # Data Minimization checks
│
├── models/                         # AI/LLM integration layer
│   ├── llm_client.py               # Groq API client & utilities
│   ├── prompts.yaml                # All LLM prompts & model config
│   └── ai_functions/               # AI-powered evaluation functions
│       ├── a_lang_clarity.py       # Language clarity evaluation
│       ├── b_consent_verify.py     # Consent mechanism verification
│       ├── c_retention_verify.py   # Retention policy verification
│       ├── d_deletion_verify.py    # Deletion rights verification
│       └── e_data_min_verify.py    # Data minimization verification
│
├── utils/                          # Shared utilities
│   ├── policies.py                 # Policy URL mappings
│   ├── utils.py                    # Policy document loading
│   ├── pdf_generator.py            # PDF report generation
│   ├── message_formatter.py        # Standardized message formatting
│   └── vector_store/               # Vector embeddings & search
│       ├── build_index.py          # FAISS index builder
│       ├── query_index.py          # VectorStore query interface
│       ├── chunker.py              # Policy text chunking
│       ├── embedder.py             # Sentence embeddings
│       └── index/                  # FAISS index files
│           ├── policy_index.faiss  # Vector index
│           └── policy_metadata.pkl # Chunk metadata
│
├── templates/                      # Flask HTML templates
│   ├── index.html                  # Landing page
│   └── report.html                 # Compliance report display
│
├── static/                         # Frontend assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript
│   └── assets/                     # Images, icons, etc.
│
├── policies_txt/                   # Stored privacy policy documents
│   ├── open_ai.md
│   ├── claude.md
│   ├── gemini.md
│   └── grok.md
│
├── data/                           # Runtime data (if needed)
├── .env                            # Environment variables (GROQ_API_KEY)
├── pyproject.toml                  # Project dependencies
└── README.md                       # Project documentation
```

---

## Module Details

### Core Application Flow

**app.py** - Main Flask application
- Route `/`: Landing page for policy selection
- Route `/send_number`: Main processing endpoint
  1. Receives policy ID from frontend
  2. Loads policy document
  3. Runs all compliance checks
  4. Calculates scoring report
  5. Renders results with tabular view
- Route `/download_pdf`: Generates downloadable PDF report

**checker.py** - Check orchestration
- Function: `run_all_checks(policy_doc)`
- Iterates through all registered policy groups from `all_policies/__init__.py`
- Executes each check function
- Returns unified results array with structure:
  ```python
  {
      "group": str,        # e.g., "notice", "consent"
      "id": str,           # e.g., "clear_language"
      "section": str,      # e.g., "Notice"
      "description": str,  # Check description
      "passed": bool,      # True/False
      "score": float,      # 0.0 to 1.0
      "message": str       # Detailed explanation
  }
  ```

**scorer.py** - Centralized scoring engine
- Configuration: `DPDP_CONFIG` dict contains:
  - Total DPDP categories (5 implemented)
  - Category weight: 20% each (100/5)
  - Category-to-group mappings
  - Check metadata (labels, weights)
  - Grading thresholds (HIGH: 75+, MODERATE: 60+)
- Function: `calculate_compliance_score(check_results)`
  - Groups results by category
  - Calculates weighted scores (each category contributes 20 points max)
  - Determines overall grade and status
  - Returns structured scoring report
- Helper: `add_policy_category()` for easy category addition

---

### Policy Check Modules (all_policies/)

Each policy module follows a consistent pattern:

#### Structure:
```python
# 1. Documentation block
"""
Category description and requirements
"""

# 2. CHECKS array - metadata for each check
CHECKS = [
    {
        "id": "check_identifier",
        "section": "Category Name",
        "description": "What this check validates"
    },
    # ... more checks
]

# 3. Check implementation functions
def run_check_name(doc):
    """
    Args:
        doc (dict): Policy document with 'text', 'provider', etc.

    Returns:
        (score: float, passed: bool, message: str)
    """
    # Implementation logic
    return score, passed, message

# 4. IMPLEMENTATIONS mapping
IMPLEMENTATIONS = {
    "check_identifier": run_check_name,
    # ... more mappings
}
```

#### Current Implementations:

**a_notice.py** - Notice & Transparency
- Checks: `privacy_policy_exists`, `clear_language`, `indian_languages`
- Uses both rule-based and AI evaluation
- Weight: 1/3 per check (equal distribution)

**b_consent.py** - Consent Management
- Checks: `opt_in_or_opt_out`, `consent_for_training`
- **Vector Embeddings + AI**: Semantic search → Rule-based → AI final score
- Validates explicit consent mechanisms
- Verifies separate consent for AI training
- Weight: 1/2 per check

**c_retention.py** - Retention
- Checks: `retention_period`, `specific_timeframe`
- **Vector Embeddings + AI**: Semantic search → Rule-based → AI final score
- Searches for retention periods, timeframes, deletion conditions
- Validates presence of specific time-bound commitments
- Weight: 1/2 per check

**d_deletion.py** - Deletion
- Checks: `deletion_doc`, `offers_deletion`
- **Vector Embeddings + AI**: Semantic search → Rule-based → AI final score
- Searches for deletion rights, account deletion, data erasure
- Verifies documented deletion procedures and user options
- Weight: 1/2 per check

**e_data_minimization.py** - Data Minimization
- Check: `data_min`
- **Vector Embeddings + AI**: Semantic search → Rule-based → AI final score
- Searches for data collection practices, minimization principles
- Validates necessity-based collection vs excessive language
- Weight: 1.0 (single check category)

#### Adding New Policy Categories:

1. Create new file: `all_policies/f_your_category.py`
2. Define `CHECKS` array with check metadata
3. Implement check functions returning `(score, passed, message)`
4. Create `IMPLEMENTATIONS` dict mapping check IDs to functions
5. Register in `all_policies/__init__.py`:
   ```python
   from . import f_your_category

   ALL_CHECK_GROUPS = {
       "notice": a_notice,
       "consent": b_consent,
       "retention": c_retention,
       "deletion": d_deletion,
       "data_minimization": e_data_minimization,
       "your_category": f_your_category,  # Add this
   }
   ```
6. Update `scorer.py` `DPDP_CONFIG`:
   ```python
   # Add to all_categories list
   "all_categories": [
       "Notice & Transparency",
       "Consent Management",
       "Data Minimization",
       "Retention",
       "Deletion",
       "Your Category Name"  # Add this
   ],

   # Add to category_to_group mapping
   "category_to_group": {
       "Your Category Name": "your_category",
   },

   # Add check metadata
   "check_metadata": {
       "your_category": {
           "check_id": {
               "label": "Display Label",
               "weight": 0.5  # Adjust based on importance
           }
       }
   }
   ```
7. Update `checker.py` `GROUP_DISPLAY_NAMES`:
   ```python
   GROUP_DISPLAY_NAMES = {
       "your_category": "Your Category Name",
   }
   ```
8. Update `total_categories` in scorer.py to 6 and recalculate weights

---

### AI/LLM Integration (models/)

**llm_client.py** - LLM client utilities
- `get_groq_client()`: Singleton Groq API client
- `get_prompt(name)`: Load prompt from YAML by name
- `get_model_name(purpose)`: Get configured model for task
- `_chunk_text(text, max_words)`: Split large texts for processing
- `_call_groq(chunk, cfg)`: Execute LLM call with prompt config

**prompts.yaml** - Centralized prompt management
- Structure:
  ```yaml
  models:
    clarity:
      provider: groq
      model: llama-3.1-8b-instant

  prompts:
    prompt_name:
      system: |
        System instructions
      user_template: |
        User prompt with {{placeholders}}
  ```
- Current prompts:
  - `clear_language`: Evaluates policy clarity score
  - `consent_opt_in_review`: Reviews consent mechanisms
  - `consent_training_review`: Verifies AI training consent

**ai_functions/** - AI-powered evaluations
- Each function follows pattern:
  ```python
  def evaluate_something(text: str) -> Tuple[bool, str, Dict[str, Any]]:
      """
      Returns: (passed, message, metadata)
      """
      # 1. Chunk text if needed
      # 2. Call LLM for each chunk
      # 3. Aggregate results
      # 4. Return structured output
  ```
- `a_lang_clarity.py`: Chunks policy, evaluates clarity per chunk, averages scores
- `b_consent_verify.py`: Hybrid rule+AI approach for consent validation

#### Adding New AI Functions:

1. Create function in `models/ai_functions/`
2. Add prompt to `models/prompts.yaml`
3. Use `_call_groq(text, cfg="your_prompt_name")` for evaluation
4. Return `(passed: bool, message: str, meta: dict)`

---

### Utilities (utils/)

**policies.py**
- Maps policy IDs to URLs
- Currently supports: OpenAI, Anthropic, Google Gemini, X.AI

**utils.py**
- `get_policy_doc(policy_id, url)`: Loads policy from markdown files
- Returns structured document dict with text, provider, title, etc.

**pdf_generator.py**
- `generate_compliance_pdf(results, provider)`: Creates PDF report
- Uses ReportLab library
- Formats check results into professional report

---

## Data Flow (with Real-Time Progress & Vector Search)

```
1. User selects policy (ID) on frontend
   ↓
2. Frontend shows progress modal with elapsed timer (0:00, 0:01, 0:02...)
   ↓
3. POST to /send_number → Returns session_id
   ↓
4. Frontend connects to /progress/<session_id> via Server-Sent Events (SSE)
   ↓
5. POST to /run_checks with session_id starts processing
   ↓
6. Backend processing (with progress callbacks):
   │
   ├─ utils.policies.get_policy() retrieves URL
   │
   ├─ utils.utils.get_policy_doc() loads policy text
   │
   ├─ checker.run_all_checks_with_progress() validates policy
   │  │
   │  ├─ For each of 5 categories (Notice, Consent, Data Minimization, Retention, Deletion):
   │  │  ├─ Callback: category_start → SSE → Frontend shows "Checking [Category]..."
   │  │  │
   │  │  ├─ For each check in category:
   │  │  │  ├─ 🔍 Vector Search: VectorStore.query() retrieves top 5 relevant chunks
   │  │  │  ├─ 📏 Rule-Based: Keyword analysis on retrieved context
   │  │  │  ├─ 🤖 AI Review: Extract policy quotes + generate final score (60% rule + 40% AI)
   │  │  │  └─ 📝 Format: DPDP + Policy + Evidence + Score
   │  │  │
   │  │  └─ Callback: category_complete → SSE → Frontend shows "[Category] completed ✓"
   │  │
   │  └─ Returns unified results array with evidence
   │
   ├─ scorer.calculate_compliance_score() processes results
   │  ├─ Groups by category
   │  ├─ Calculates weighted scores (20% per category)
   │  ├─ Determines grade (HIGH/MODERATE/LOW)
   │  └─ Returns structured scoring report
   │
   └─ Callback: complete with scoring_data → SSE → Frontend navigates to report
   ↓
7. Timer stops, report page loads data from sessionStorage
   ↓
8. Frontend displays interactive tabular report with dynamic category tabs
   ↓
9. User can:
   - Switch between category breakdowns using tabs
   - View detailed check results with DPDP requirements, policy quotes, and evidence
   - See top 3 retrieved chunks that led to each conclusion
   - Download PDF via /download_pdf
```

---

## Key Design Patterns

### 1. Plugin Architecture (all_policies/)
- Each policy category is a self-contained module
- Registry pattern in `__init__.py` for auto-discovery
- Zero code changes needed in checker.py when adding categories

### 2. Configuration-Driven Scoring (scorer.py)
- All scoring logic in centralized `DPDP_CONFIG`
- Easy to adjust weights, thresholds, categories
- Single source of truth for compliance rules

### 3. Hybrid AI Evaluation
- Rule-based pre-filtering for efficiency
- AI review for nuanced interpretation
- Example: b_consent.py combines keyword matching + LLM validation

### 4. Separation of Concerns
- Checks: Define what to validate
- Scorer: Define how to calculate scores
- LLM Client: Handle API communication
- App: Handle web routing and presentation

### 5. Declarative Metadata
- CHECKS arrays describe validation rules
- IMPLEMENTATIONS map IDs to functions
- prompts.yaml centralizes all LLM instructions

### 6. Real-Time Progress with Server-Sent Events (SSE)
- Backend streams progress updates to frontend during processing
- No polling required - efficient one-directional communication
- User sees live status: "Checking Notice...", "Notice completed ✓"
- Progress stored in session-based `progress_store` dict
- Clean separation: session creation → SSE connection → background processing

### 7. Dynamic Category Breakdown UI
- Tab-based interface for detailed check results
- Automatically generates tabs for all implemented categories
- Click-to-switch between Notice, Consent, and future categories
- No hardcoded category sections - fully dynamic rendering
- Breakdown data stored in frontend global variable for instant tab switching

---

## Feature Highlights

### Real-Time Progress Tracking with Timer

**User Experience:**
When a user clicks a provider, they immediately see:
```
Running DPDP Compliance Checks

Elapsed Time: 0:15

- Checking Notice & Transparency...
- Notice & Transparency completed ✓
- Checking Consent Management...
- Consent Management completed ✓
- Checking Data Minimization...
- Data Minimization completed ✓
- Checking Retention...
- Retention completed ✓
- Checking Deletion...
- Deletion completed ✓
- All checks completed! Loading report...
```

The timer displays elapsed time in MM:SS format and updates every second.

**Technical Implementation:**
1. **Frontend (script.js)**:
   - Shows progress modal on click with timer display
   - `startTimer()`: Starts elapsed time counter (updates every 1s)
   - `stopTimer()`: Stops timer when modal closes or navigates away
   - Connects to SSE endpoint `/progress/<session_id>`
   - Listens for progress events and updates UI
   - Stores final data in sessionStorage
   - Navigates to report page

2. **Timer Display (style.css)**:
   - Blue monospace digits for easy reading (0:00, 0:15, 1:23...)
   - Centered in gray background above progress messages
   - Auto-stops on completion or error

3. **Backend (app.py)**:
   - `/send_number`: Creates session, returns session_id
   - `/progress/<session_id>`: SSE stream for progress updates
   - `/run_checks`: Executes checks with progress callbacks
   - Progress stored in `progress_store` dict

4. **Checker (checker.py)**:
   - `run_all_checks_with_progress()` accepts callback function
   - Fires `category_start` and `category_complete` events for all 5 categories
   - Passes updates through callback to progress store

**Benefits:**
- No page refresh or blind waiting
- User knows exactly what's happening AND how long it's taking
- Better perceived performance
- Timer provides feedback even if progress updates are slow
- Easy to debug processing flow

### Dynamic Category Breakdowns

**User Experience:**
Report page shows tabs for all 5 implemented categories:
```
[Notice & Transparency] [Consent Management] [Data Minimization] [Retention] [Deletion]
```
Click any tab to see detailed breakdown of that category's checks.

**Technical Implementation:**
- `renderCategoryTabs()`: Creates tabs from categories array
- `renderCategoryBreakdown()`: Displays checks for selected category
- `switchCategoryBreakdown()`: Handles tab clicks
- Data stored globally: `window._currentScoringData`

**Benefits:**
- Automatically scales as new categories are added
- No template changes needed for new categories
- Clean, organized presentation of complex data
- Better user navigation through results

---

## DPDP Act Categories

The system currently evaluates 5 core DPDP Act compliance categories:

1. **Notice & Transparency** [IMPLEMENTED] - all_policies/a_notice.py
   - Privacy policy existence (1/3 weight)
   - Clear, plain language (1/3 weight)
   - Indian language availability (1/3 weight)
   - **Category contribution**: 20% of total score

2. **Consent Management** [IMPLEMENTED] - all_policies/b_consent.py
   - Opt-in vs opt-out mechanisms (1/2 weight)
   - Separate consent for AI training (1/2 weight)
   - **Category contribution**: 20% of total score

3. **Data Minimization** [IMPLEMENTED] - all_policies/e_data_minimization.py
   - Only necessary data collected (1.0 weight)
   - Proportionality check
   - **Category contribution**: 20% of total score

4. **Retention** [IMPLEMENTED] - all_policies/c_retention.py
   - Clear retention periods (1/2 weight)
   - Specific timeframe documentation (1/2 weight)
   - **Category contribution**: 20% of total score

5. **Deletion** [IMPLEMENTED] - all_policies/d_deletion.py
   - Deletion mechanism documented (1/2 weight)
   - User-facing deletion options (1/2 weight)
   - **Category contribution**: 20% of total score

**Overall Scoring**: Each category contributes 20 points maximum (100/5). Final grade determined by:
- **HIGH (75+)**: COMPLIANT
- **MODERATE (60-74)**: NEEDS IMPROVEMENT
- **LOW (<60)**: NEEDS IMPROVEMENT

**Future Categories**: Additional DPDP requirements can be added following the established pattern (Purpose Limitation, User Rights, Cross-Border Transfer, etc.)

---

## Environment Variables

Required in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Dependencies

See `pyproject.toml` for full list. Key dependencies:
- **flask**: Web framework
- **groq**: LLM API client
- **pyyaml**: Configuration management
- **reportlab**: PDF generation
- **beautifulsoup4**: HTML parsing (if scraping policies)
- **python-dotenv**: Environment variable management

---

## Running the Application

```bash
# Install dependencies
uv sync

# Set environment variables
# Create .env with GROQ_API_KEY=xxx

# Build FAISS vector index (REQUIRED - first time only)
python -m utils.vector_store.build_index

# Run Flask app
python app.py

# Access at http://localhost:5000
```

**Important**: You must build the FAISS index before running the app for the first time. The index is built from policy files in `policies_txt/` and enables semantic search for all checks.

---

## Testing Privacy Policies

The system includes pre-loaded policies in `policies_txt/`:
- **1**: OpenAI (ChatGPT)
- **2**: Anthropic (Claude)
- **3**: Google (Gemini)
- **4**: X.AI (Grok)

Add new policies by:
1. Creating markdown file in `policies_txt/`
2. Adding entry to `utils/policies.py` `get_policy()`
3. Adding entry to `utils/utils.py` `POLICY_FILES`

---

## Best Practices for Extension

### Adding a New Check to Existing Category:
1. Add check metadata to `CHECKS` array
2. Implement check function
3. Add mapping to `IMPLEMENTATIONS`
4. Update `scorer.py` check_metadata with label and weight

### Adding a New Category:
1. Create module in `all_policies/`
2. Register in `all_policies/__init__.py`
3. Update `scorer.py` DPDP_CONFIG with category mapping and metadata

### Adding a New AI Function:
1. Create function in `models/ai_functions/`
2. Add prompt configuration to `models/prompts.yaml`
3. Use consistent return signature: `(bool, str, dict)`

### Modifying Scoring Logic:
1. All changes go in `scorer.py` `DPDP_CONFIG`
2. Never hardcode scores in check functions
3. Use weights to balance importance

---

## Future Enhancements

- [ ] Implement additional DPDP categories (Purpose Limitation, User Rights, Cross-Border Transfer)
- [ ] Add policy scraping automation (currently uses pre-saved files)
- [ ] Multi-language support for report generation (currently English only)
- [ ] Detailed remediation suggestions per failing check
- [ ] Historical tracking of policy changes over time
- [ ] Comparative analysis across multiple providers
- [ ] Export to additional formats (JSON, CSV, HTML)
- [ ] Progress persistence across browser refresh
- [ ] Enhanced AI evaluation for more nuanced policy interpretation
- [ ] Custom weighting per category based on organization priorities

---

## Changelog

### Version 2.0 - 2025-12-19
**MAJOR UPGRADE: Vector Embeddings + AI for ALL Categories**

**🎯 Core Enhancement:**
- ✅ **ALL 5 Categories Now Use Vector Embeddings + AI**
  - Consent Management: Vector search + Rule + AI
  - Retention: Vector search + Rule + AI
  - Deletion: Vector search + Rule + AI
  - Data Minimization: Vector search + Rule + AI
  - Notice: Hybrid approach (existing AI for clarity)

**🔍 Intelligent Context Retrieval:**
- FAISS vector store with sentence-transformers embeddings
- Semantic search retrieves top 5 relevant policy chunks per check
- Policy-specific filtering ensures accurate context
- Evidence chunks displayed to user for full transparency

**🤖 Enhanced AI Analysis:**
- New prompts for retention, deletion, and data minimization
- AI extracts exact policy quotes for comparison
- Structured output: DPDP Requirement + Provider's Policy + Evidence + Score
- Conservative scoring: 60% rule-based + 40% AI for reliability

**📊 Improved Message Format:**
- **DPDP Requirement** (Blue): What the law mandates
- **Provider's Policy** (Purple): Exact quotes from policy
- **Retrieved Evidence** (Green): Top 3 matching chunks from vector search
- **Compliance Score** (Color-coded): Visual high/medium/low indicators

**New Files Created:**
- `utils/vector_store/build_index.py`: Builds FAISS index from policies
- `utils/vector_store/query_index.py`: VectorStore class for semantic search
- `utils/vector_store/chunker.py`: Splits policies into searchable chunks
- `utils/vector_store/embedder.py`: Generates embeddings with sentence-transformers
- `utils/message_formatter.py`: Standardized message formatting across all checks
- `models/ai_functions/c_retention_verify.py`: AI review for retention
- `models/ai_functions/d_deletion_verify.py`: AI review for deletion
- `models/ai_functions/e_data_min_verify.py`: AI review for data minimization

**Updated Files:**
- `models/prompts.yaml`: Added retention_review, deletion_review, data_minimization_review prompts
- `all_policies/b_consent.py`: Uses vector search + AI (2 checks)
- `all_policies/c_retention.py`: Uses vector search + AI (2 checks)
- `all_policies/d_deletion.py`: Uses vector search + AI (2 checks)
- `all_policies/e_data_minimization.py`: Uses vector search + AI (1 check)
- `all_policies/a_notice.py`: Updated to use message formatter
- `static/css/report.css`: Enhanced styling for evidence display

**Technical Architecture:**
```
Check Flow (Applied to ALL categories):
1. Vector Search → Semantic retrieval of top 5 chunks
2. Rule-Based → Keyword analysis on retrieved context
3. AI Analysis → Extract policy quotes + generate final score
4. Display → Show DPDP + Policy + Evidence + Score
```

**Dependencies Added:**
- `faiss-cpu>=1.13.1`: Vector similarity search
- `sentence-transformers>=5.2.0`: Text embeddings

### Version 1.2 - 2025-12-17
**Major Updates:**
- ✅ **5 DPDP Categories Fully Implemented**
  - All core categories now operational: Notice & Transparency, Consent Management, Data Minimization, Retention, Deletion
  - Each category contributes 20% to overall score (100/5)
  - Balanced scoring system with equal weighting

- ✅ **New Policy Categories Added**
  - `c_retention.py`: Validates retention periods and specific timeframes
  - `d_deletion.py`: Checks deletion mechanism documentation and user options
  - `e_data_minimization.py`: Evaluates data collection minimization practices

- ✅ **Elapsed Timer in Progress Modal**
  - Real-time timer showing MM:SS format (0:00, 0:15, 1:23...)
  - Updates every second during processing
  - Auto-stops on completion or error
  - Provides feedback even if progress updates are slow

### Version 1.1 - 2025-12-17
**New Features:**
- ✅ Real-time progress tracking with Server-Sent Events (SSE)
  - Live status updates: "Checking [Category]...", "[Category] completed ✓"
  - Progress modal with animated status messages
  - Session-based progress tracking
  - Clean SSE streaming implementation

- ✅ Dynamic category breakdown tabs
  - Auto-generated tabs for all implemented categories
  - Click-to-switch between category details
  - No hardcoded sections - fully scalable
  - Smooth animations and transitions

**Technical Improvements:**
- Added `/progress/<session_id>` SSE endpoint
- Modified `/send_number` to return session_id instead of HTML
- Added `/run_checks` endpoint for background processing
- Updated `checker.py` with `run_all_checks_with_progress()` callback support
- Enhanced frontend with progress modal UI
- sessionStorage for report data persistence
- Comprehensive debug logging throughout stack

**Files Modified:**
- `app.py`: Added SSE endpoints, session management
- `checker.py`: Added progress callback support
- `static/js/script.js`: SSE connection, progress modal
- `static/js/report.js`: Dynamic tabs, category switching
- `templates/report.html`: Dynamic breakdown section, sessionStorage loading
- `static/css/style.css`: Progress modal styles
- `static/css/report.css`: Tab styles

### Version 1.0 - 2025-12-15
**Initial Release:**
- Notice & Transparency compliance checks
- Consent Management compliance checks
- AI-powered clarity evaluation
- Tabular scoring report
- PDF export functionality
- Centralized scoring engine

---

## Contact & Contribution

For questions about this architecture or to contribute:
- Follow the patterns established in existing modules
- Maintain the readability and scalability principles
- Document new categories and checks clearly
- Update this CLAUDE.md when making structural changes

**Development Tips:**
- Use browser console to track frontend progress
- Check terminal output for backend debug logs
- Progress updates appear in real-time during processing
- All 5 category tabs auto-generate - no template changes needed
- Timer provides visual feedback of processing duration

---

**Last Updated**: 2025-12-19
**Architecture Version**: 2.0
**Python Version**: 3.12+
**Status**: All 5 core DPDP categories with Vector Embeddings + AI fully operational
