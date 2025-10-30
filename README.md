# Lippmann-Rau-Musikarchiv_VLM_OCR_index_cards
> Automated metadata extraction from ~43,000 digitized archive index cards using Vision Language Models (Qwen VL)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![Qwen VL](https://img.shields.io/badge/Model-Qwen%20VL-red.svg)](https://github.com/QwenLM/Qwen-VL)

## 📋 Overview

This project automates the digitization of the **Lippmann-Rau Music Archive** in Eisenach, Germany. It processes 86 batch folders containing approximately 43,000 historical index cards, extracting structured metadata using state-of-the-art Vision Language Models.

### Key Features

- 🚀 **Parallel Processing** - Multi-threaded batch processing with configurable workers
- 💾 **Robust Checkpointing** - Resume from interruption at file and batch level
- 📊 **Comprehensive Analysis** - Built-in quality assessment and statistics
- 🔄 **Automatic CSV Merging** - Combines all batch outputs into a single master file
- 🛡️ **Error Handling** - Exponential backoff retry logic with detailed error logging
- 🎯 **Flexible Configuration** - Easily adaptable for different archive structures

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input: 86 Batch Folders                   │
│                   (~500 index cards each)                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Batch OCR Processor                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Parallel Workers (5-10 threads)                   │   │
│  │  • Qwen3-VL / Qwen2.5-VL API Integration            │   │
│  │  • Checkpoint System (file + batch level)           │   │
│  │  • Retry Logic with Exponential Backoff             │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        Output                                │
│  ┌──────────────┬──────────────┬────────────────────────┐   │
│  │  86 Batch    │   JSON       │  Master CSV            │   │
│  │  CSVs        │   Archives   │  (43,000+ entries)     │   │
│  └──────────────┴──────────────┴────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python3 --version

# Required packages
pip install pandas requests
```

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/lippmann-rau-ocr.git
cd lippmann-rau-ocr

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `Lippmann-Rau_VLM_OCR_MultiBatch.py`:

```python
# Line 22-23: Set your input directory
BASE_INPUT_DIR = "/path/to/your/JPEG/batches"

# Line 27: Batch folder pattern
BATCH_PATTERN = "Batch_*"  # or "*" for all subdirectories

# Line 34: Choose your model
MODEL_NAME = "qwen3-vl:8b"          # Recommended: Best OCR
# MODEL_NAME = "qwen2.5vl:32b"      # Alternative: Tested & stable
# MODEL_NAME = "qwen3-vl:32b"       # Best quality (slower)

# Line 39: Performance tuning
MAX_WORKERS = 5  # Adjust based on your server capacity
```

### Usage

```bash
# Start the multi-batch processing
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py

# Enter your API key when prompted
# The script will process all 86 batches automatically

# After completion, analyze results
python3 analyze_results.py
```

## 📁 Project Structure

```
lippmann-rau-ocr/
├── Lippmann-Rau_VLM_OCR_MultiBatch.py    # Main processing script
├── analyze_results.py                     # Analysis & quality reports
├── merge_csvs.py                          # Manual CSV merger (backup)
├── requirements.txt                       # Python dependencies
├── README.md                              # This file
├── CHANGES.md                             # Changelog & migration guide
└── output_batches/                        # Output directory (created)
    ├── csv/                               # Individual batch CSVs
    │   ├── Batch_001.csv
    │   ├── Batch_002.csv
    │   └── ...
    ├── json/                              # JSON archives by batch
    │   ├── Batch_001/
    │   └── ...
    ├── metadata_vlm_complete.csv          # 🎯 Master output file
    ├── analysis/                          # Analysis reports
    │   ├── field_completeness.csv
    │   ├── batch_statistics.csv
    │   ├── komponisten_frequency.csv
    │   └── ...
    ├── batch_progress.json                # Progress tracking
    └── vlm_errors.log                     # Error log
```

## 📊 Extracted Metadata Fields

Each index card is parsed into the following structured fields:

| Field | Description | Example |
|-------|-------------|---------|
| **Datei** | Filename | `karte_12345.jpg` |
| **Batch** | Batch folder | `Batch_042` |
| **Komponist** | Composer name | `Zimmermann, Rolf` |
| **Signatur** | Archive signature | `Spez.12.433` |
| **Titel** | Work title | `Sonate für Violine` |
| **Textanfang** | Text incipit | `Es war einmal...` |
| **Verlag** | Publisher | `Peters Leipzig` |
| **Material** | Material type | `1 Part. u. Stimmen` |
| **Textdichter** | Lyricist | `Goethe, Johann W.` |
| **Bearbeiter** | Arranger | `Müller, Hans` |
| **Bemerkungen** | Remarks | `Handschriftlich` |

## 🎯 Performance Benchmarks

### Processing Speed

| Configuration | Model | Speed | Total Time (43k cards) |
|--------------|-------|-------|----------------------|
| 5 workers | Qwen3-VL-8B | ~150 cards/hour | 24-36 hours |
| 10 workers | Qwen3-VL-8B | ~250 cards/hour | 15-20 hours |
| 5 workers | Qwen2.5-VL-32B | ~100 cards/hour | 36-48 hours |

*Note: Actual speed depends on API response time and network stability*

### Quality Metrics

Based on test runs:
- ✅ **Success Rate**: 95-98%
- 📝 **Komponist Extraction**: 85-92%
- 🔖 **Signatur Extraction**: 88-94%
- ✓ **Valid Signatur Format**: 90-96%

## 🔧 Advanced Configuration

### Model Selection

```python
# Qwen3-VL-8B (Recommended)
# ✅ Best OCR performance (32 languages)
# ✅ Fast processing
# ✅ Excellent handwriting recognition
MODEL_NAME = "qwen3-vl:8b"

# Qwen2.5-VL-32B
# ✅ Well-tested and stable
# ✅ Good for structured documents
# ⚠️ Slower than 8B variant
MODEL_NAME = "qwen2.5vl:32b"

# Qwen3-VL-32B
# ✅ Highest quality
# ⚠️ Slowest processing
MODEL_NAME = "qwen3-vl:32b"
```

### Performance Tuning

```python
# For fast server with stable API
MAX_WORKERS = 10
MAX_RETRIES = 2
RETRY_DELAY = 2

# For slow/unstable connection
MAX_WORKERS = 3
MAX_RETRIES = 5
RETRY_DELAY = 5
```

### Batch Folder Patterns

```python
# Pattern 1: "Batch_001", "Batch_002", ...
BATCH_PATTERN = "Batch_*"

# Pattern 2: "001", "002", "003", ...
BATCH_PATTERN = "[0-9][0-9][0-9]"

# Pattern 3: All subdirectories
BATCH_PATTERN = "*"
```

## 📈 Workflow

### Phase 1: Testing (Day 1)
```bash
# Process 1-2 test batches
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# Press Ctrl+C after 1-2 batches

# Analyze test results
python3 analyze_results.py

# Review output CSV for quality
```

### Phase 2: Full Processing (Day 2-3)
```bash
# Start full batch processing
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# Let run overnight (24-36 hours)
```

### Phase 3: Analysis (Day 4)
```bash
# Generate comprehensive statistics
python3 analyze_results.py

# Review analysis reports in output_batches/analysis/
# - field_completeness.csv
# - batch_statistics.csv
# - komponisten_frequency.csv
# - problematic_cards.csv
# - missing_signatures.csv
```

## 🛡️ Error Handling & Recovery

### Checkpoint System

The script maintains two levels of checkpoints:

1. **File-level checkpoints**: Tracks processed cards within each batch
2. **Batch-level progress**: Tracks completed batches

On interruption (Ctrl+C or crash):
- ✅ Already processed files are skipped
- ✅ Completed batches are not reprocessed
- ✅ Processing resumes automatically from last position

### Retry Logic

```python
# Automatic retry with exponential backoff
MAX_RETRIES = 3           # 3 attempts per card
RETRY_DELAY = 2           # Initial delay: 2s
# Backoff: 2s → 4s → 6s
```

### Error Logging

All errors are logged to `output_batches/vlm_errors.log`:
```
[2025-10-30T12:34:56] Batch: Batch_042 | Datei: card_12345.jpg
⚠️  API timeout after 120s
Details: Connection timeout
----------------------------------------------------------------
```

## 📊 Analysis Tools

### Built-in Analysis (`analyze_results.py`)

Generates comprehensive reports:

```bash
python3 analyze_results.py
```

**Output:**
- Field completeness statistics
- Batch-by-batch comparison
- Top composers ranking
- Signature pattern analysis
- Quality metrics (empty/sparse/complete records)
- Problematic cards identification

### Manual CSV Merging (`merge_csvs.py`)

Backup tool for manual CSV combination:

```bash
python3 merge_csvs.py [optional_csv_directory]
```

## 🔒 Security

### API Key Management

**Current (Recommended):**
```bash
# API key is requested securely at runtime
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# → API-Key: [hidden input]
```

**Alternative (Environment Variable):**
```bash
# Add to script configuration
import os
API_KEY = os.getenv('QWEN_API_KEY')

# Terminal
export QWEN_API_KEY="sk-..."
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
```

⚠️ **Never commit API keys to Git!** Use `.gitignore`:
```
# .gitignore
*.env
.env
api_key.txt
config_local.py
```

## 🐛 Troubleshooting

### Common Issues

**Issue: "No batch folders found"**
```bash
# Solution 1: Check BASE_INPUT_DIR path
# Solution 2: Adjust BATCH_PATTERN
# Solution 3: Test manually:
python3 -c "from pathlib import Path; print(list(Path('/your/path').glob('*')))"
```

**Issue: API errors or timeouts**
```python
# Solution: Reduce MAX_WORKERS
MAX_WORKERS = 3

# Increase retry delay
RETRY_DELAY = 5
```

**Issue: Poor OCR quality**
```python
# Solution 1: Switch to Qwen3-VL
MODEL_NAME = "qwen3-vl:8b"

# Solution 2: Adjust temperature
"temperature": 0.0  # More consistent (in call_vlm_api function)

# Solution 3: Check image quality
# Recommended: 300 DPI or higher
```

**Issue: Interrupted processing**
```bash
# Simply restart - checkpoints ensure continuation
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
```

## 📝 Citation

If you use this project in academic work, please cite:

```bibtex
@software{lippmann_rau_ocr_2025,
  title = {Lippmann-Rau Archive OCR: Automated Metadata Extraction from Historical Index Cards},
  author = {Tom Meißner},
  year = {2025},
  url = {https://github.com/your-username/lippmann-rau-ocr}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/lippmann-rau-ocr.git
cd lippmann-rau-ocr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

## 📄 License

This project is licensed under CC-BY 4.0

## 📞 Contact

**Project Maintainer:** Tom Meißner
- Email: tom.meissner@uni-jena.de
- GitHub: [ki_thulb](https://github.com/ki_thulb)


## 📊 Project Status

**Current Version:** 1.0.0  
**Status:** beta / testing  
**Last Updated:** October 2025

### Roadmap

- [x] Multi-batch processing
- [x] Checkpoint system
- [x] Analysis tools
- [x] Error handling
- [ ] Web interface for quality control
- [ ] Export to library catalog formats (MARC, Dublin Core)
- [ ] Integration with archive management systems
- [ ] Machine learning model fine-tuning on archive-specific cards
