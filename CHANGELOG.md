# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-30

### Added
- Initial release of multi-batch OCR processing system
- Support for 86 batch folders with ~500 cards each
- Parallel processing with configurable worker threads
- Two-level checkpoint system (file and batch level)
- Automatic CSV merging into master file
- Comprehensive analysis tools (`analyze_results.py`)
- Manual CSV merge utility (`merge_csvs.py`)
- Support for Qwen3-VL and Qwen2.5-VL models
- Exponential backoff retry logic for API calls
- Detailed error logging
- Progress tracking with ETA calculation
- Batch-specific JSON organization
- Field completeness validation
- Signature format validation

### Features
- **Multi-Batch Processing**: Automatically processes all batch folders
- **Checkpoint Recovery**: Resume from any interruption point
- **Quality Analysis**: Built-in statistics and quality metrics
- **Flexible Configuration**: Easy adaptation to different archive structures
- **Error Resilience**: Robust error handling with detailed logging

## [Unreleased]

### Planned
- Web interface for quality control
- Export to MARC and Dublin Core formats
- Integration with archive management systems
- Fine-tuning support for archive-specific models
- Docker containerization
- REST API for batch processing
- Real-time progress dashboard

### Ideas
- OCR confidence scoring
- Duplicate card detection
- Batch similarity analysis
- Multi-model ensemble processing
- Automatic image preprocessing

## Migration Guide

### From Single-Batch Script to Multi-Batch

If you're migrating from the single-batch version:

1. **Configuration Changes**
   - Old: `INPUT_DIR` → New: `BASE_INPUT_DIR`
   - Old: `CSV_OUT` → New: `CSV_OUT_BASE` + `FINAL_CSV`
   - New: `BATCH_PATTERN` configuration required

2. **Output Structure**
   - Old: Single `metadata_vlm.csv`
   - New: `output_batches/csv/Batch_XXX.csv` + `metadata_vlm_complete.csv`

3. **Checkpoint System**
   - Old: File-level only
   - New: File + Batch level checkpoints

4. **Process**
   - Old: Manual batch switching
   - New: Fully automated multi-batch processing

See `CHANGES.md` for detailed migration instructions.

---

## Version History

### [1.0.0] - 2025-10-30
- First stable release
- Production-ready for large-scale digitization projects
- Tested with 43,000+ archive cards

---

**Note**: For detailed changes in each version, see individual release notes on GitHub.
