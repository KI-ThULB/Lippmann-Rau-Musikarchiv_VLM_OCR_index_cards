# Example Configuration for Lippmann-Rau Archive OCR System
# Copy this file to config.py and adjust settings

# ============================================================================
# INPUT/OUTPUT CONFIGURATION
# ============================================================================

# Base directory containing all batch folders
# Example: "/Users/username/Desktop/Karteikarten/JPEG"
BASE_INPUT_DIR = "/path/to/your/JPEG/folders"

# Pattern to match batch folders
# Examples:
#   "Batch_*"     - Matches: Batch_001, Batch_002, etc.
#   "[0-9][0-9][0-9]" - Matches: 001, 002, 003, etc.
#   "*"           - Matches all subdirectories
BATCH_PATTERN = "Batch_*"

# Output base directory (created automatically)
OUTPUT_BASE = "output_batches"

# ============================================================================
# API CONFIGURATION
# ============================================================================

# API endpoint URL
# Examples:
#   OpenWebUI: "https://your-server.com/api/v1/chat/completions"
#   Ollama:    "http://localhost:11434/api/chat"
API_URL = "https://openwebui.test.uni-jena.de/api/v1/chat/completions"

# Model selection
# Recommended options:
#   "qwen3-vl:8b"      - Best OCR, fast, 32 languages (RECOMMENDED)
#   "qwen2.5vl:32b"    - Very accurate, slower
#   "qwen3-vl:32b"     - Highest quality, slowest
MODEL_NAME = "qwen3-vl:8b"

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Number of parallel API calls
# Recommendations:
#   Stable connection: 8-10
#   Normal connection: 5-7
#   Slow/unstable:     3-4
MAX_WORKERS = 5

# Number of retry attempts for failed API calls
MAX_RETRIES = 3

# Seconds to wait between retries (exponential backoff applied)
RETRY_DELAY = 2

# Expected number of cards per batch (for progress estimation)
BATCH_SIZE = 500

# ============================================================================
# DATA EXTRACTION FIELDS
# ============================================================================

# Fields to extract from each card
# Add or remove fields as needed for your use case
FIELD_KEYS = [
    "Komponist",      # Composer
    "Signatur",       # Archive signature
    "Titel",          # Title
    "Textanfang",     # Text beginning/incipit
    "Verlag",         # Publisher
    "Material",       # Material type
    "Textdichter",    # Lyricist
    "Bearbeiter",     # Arranger
    "Bemerkungen"     # Remarks
]

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Temperature for API calls (0.0 = deterministic, 1.0 = creative)
TEMPERATURE = 0.1

# Maximum tokens for API response
MAX_TOKENS = 1000

# API timeout in seconds
API_TIMEOUT = 120

# Enable verbose logging
VERBOSE = False

# ============================================================================
# SIGNATURE VALIDATION PATTERNS
# ============================================================================

# Regular expressions for valid signature formats
# Customize based on your archive's signature system
SIGNATURE_PATTERNS = [
    r'^Spez\.\d{1,2}\.\d{3,4}(\s+[a-z])?$',  # e.g., Spez.12.433
    r'^(RTSO|RTOB|TOB)\s+\d{3,4}$'            # e.g., TOB 1728
]

# ============================================================================
# EXAMPLE CONFIGURATIONS
# ============================================================================

# Fast processing (recommended for initial testing)
"""
MAX_WORKERS = 8
MAX_RETRIES = 2
MODEL_NAME = "qwen3-vl:8b"
"""

# High quality (recommended for production)
"""
MAX_WORKERS = 5
MAX_RETRIES = 3
MODEL_NAME = "qwen3-vl:32b"
TEMPERATURE = 0.05
"""

# Slow/unstable connection
"""
MAX_WORKERS = 3
MAX_RETRIES = 5
RETRY_DELAY = 5
API_TIMEOUT = 180
"""

# Large-scale processing (many batches)
"""
MAX_WORKERS = 10
BATCH_SIZE = 500
# Consider running overnight
"""
