# Installation Guide

Complete installation instructions for the Lippmann-Rau Archive OCR system.

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 4 GB (8 GB recommended)
- **Storage**: 10 GB free space
- **Network**: Stable internet connection for API calls

### Recommended Setup
- **OS**: Ubuntu 20.04+ or macOS 12+
- **Python**: 3.10+
- **RAM**: 16 GB
- **Storage**: 50 GB SSD
- **Network**: High-speed connection (for 43k cards)

## 🚀 Quick Installation

### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/lippmann-rau-ocr.git
cd lippmann-rau-ocr

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/your-username/lippmann-rau-ocr.git
cd lippmann-rau-ocr

# Install dependencies
pip3 install -r requirements.txt

# Create output directories
mkdir -p output_batches/csv
mkdir -p output_batches/json
mkdir -p output_batches/analysis
```

## 🔧 Detailed Installation Steps

### Step 1: Install Python

#### On Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### On macOS (with Homebrew)
```bash
brew install python3
```

#### On Windows
Download from [python.org](https://www.python.org/downloads/) and install.

### Step 2: Verify Installation

```bash
python3 --version  # Should show 3.8 or higher
pip3 --version
```

### Step 3: Clone Repository

```bash
# Via HTTPS
git clone https://github.com/your-username/lippmann-rau-ocr.git

# Or via SSH
git clone git@github.com:your-username/lippmann-rau-ocr.git

cd lippmann-rau-ocr
```

### Step 4: Set Up Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pandas>=1.3.0` - Data manipulation
- `requests>=2.26.0` - API calls

### Step 6: Configure the Script

Edit `Lippmann-Rau_VLM_OCR_MultiBatch.py`:

```python
# Line 22-23: Your input directory
BASE_INPUT_DIR = "/path/to/your/JPEG/batches"

# Line 27: Batch folder pattern
BATCH_PATTERN = "Batch_*"

# Line 30: API endpoint
API_URL = "https://your-api-endpoint.com/v1/chat/completions"

# Line 34: Model selection
MODEL_NAME = "qwen3-vl:8b"

# Line 39: Performance
MAX_WORKERS = 5
```

### Step 7: Test Installation

```bash
# Test with Python import
python3 -c "import pandas, requests; print('✅ All dependencies OK')"

# Quick test run (optional)
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# Press Ctrl+C after seeing the API key prompt
```

## 🐳 Docker Installation (Alternative)

### Build Docker Image

```dockerfile
# Dockerfile (create this file)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "Lippmann-Rau_VLM_OCR_MultiBatch.py"]
```

### Build and Run

```bash
# Build image
docker build -t lippmann-rau-ocr .

# Run container
docker run -it \
  -v /path/to/your/data:/data \
  -v $(pwd)/output_batches:/app/output_batches \
  lippmann-rau-ocr
```

## 🔑 API Configuration

### Method 1: Runtime Input (Current)

The script will prompt for your API key:
```bash
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# → API-Key: [enter your key]
```

### Method 2: Environment Variable

```bash
# Linux/macOS
export QWEN_API_KEY="your-api-key-here"

# Windows
set QWEN_API_KEY=your-api-key-here

# Add to script (line ~285)
api_key = os.getenv('QWEN_API_KEY') or getpass.getpass("API-Key: ")
```

### Method 3: Config File

Create `config.py`:
```python
API_KEY = "your-api-key-here"
API_URL = "https://your-endpoint.com/v1/chat/completions"
```

Add to main script:
```python
try:
    from config import API_KEY, API_URL
except ImportError:
    API_KEY = None
```

**⚠️ Important:** Add `config.py` to `.gitignore`!

## 🧪 Verify Installation

### Test 1: Python Dependencies

```bash
python3 << EOF
import pandas as pd
import requests
print("✅ pandas version:", pd.__version__)
print("✅ requests version:", requests.__version__)
EOF
```

### Test 2: Directory Structure

```bash
ls -la
# Should show:
# - Lippmann-Rau_VLM_OCR_MultiBatch.py
# - analyze_results.py
# - merge_csvs.py
# - requirements.txt
# - README_GITHUB.md
```

### Test 3: API Connection (Optional)

```python
# test_api.py
import requests
import json

API_URL = "your-api-url-here"
API_KEY = "your-api-key-here"

response = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"model": "qwen3-vl:8b", "messages": [{"role": "user", "content": "test"}]},
    timeout=10
)
print("Status:", response.status_code)
print("✅ API connection working" if response.status_code == 200 else "❌ API error")
```

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
pip3 install pandas requests --upgrade
```

### Issue: `Permission denied` on setup.sh

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: Python version too old

**Solution:**
```bash
# Install Python 3.10 (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv
```

### Issue: API connection fails

**Solutions:**
1. Check API_URL is correct
2. Verify API key is valid
3. Test network connectivity: `curl -I https://your-api-url.com`
4. Check firewall settings

### Issue: Out of memory

**Solutions:**
1. Reduce `MAX_WORKERS` to 3 or less
2. Process batches one at a time
3. Increase system RAM or use swap

## 📦 Updating

### Update to Latest Version

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Check for changes
git log --oneline -10
```

### Update Dependencies Only

```bash
pip install --upgrade pandas requests
```

## 🗑️ Uninstallation

```bash
# Remove virtual environment
deactivate  # if in venv
rm -rf venv/

# Remove repository
cd ..
rm -rf lippmann-rau-ocr/

# Uninstall system-wide packages (optional)
pip3 uninstall pandas requests
```

## 📞 Support

If you encounter installation issues:

1. Check [GitHub Issues](https://github.com/your-username/lippmann-rau-ocr/issues)
2. Review [Troubleshooting](#-troubleshooting) section
3. Create a new issue with:
   - Your OS and Python version
   - Error message
   - Steps you've tried

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] pip installed
- [ ] Repository cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Output directories created
- [ ] Script configured (BASE_INPUT_DIR, API_URL, MODEL_NAME)
- [ ] API key obtained
- [ ] Test run successful

---

**Ready to start?** → See [README_GITHUB.md](README_GITHUB.md) for usage instructions!
