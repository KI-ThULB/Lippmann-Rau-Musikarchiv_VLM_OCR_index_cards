#!/bin/bash
# Setup script for Lippmann-Rau Archive OCR

echo "🎵 Lippmann-Rau Archive OCR - Setup"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip
echo "Checking pip..."
python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "❌ pip not found. Please install pip."
    exit 1
fi

echo "✅ Python and pip found"
echo ""

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "📁 Creating output directories..."
mkdir -p output_batches/csv
mkdir -p output_batches/json
mkdir -p output_batches/analysis

echo "✅ Output directories created"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit Lippmann-Rau_VLM_OCR_MultiBatch.py"
echo "   - Set BASE_INPUT_DIR (line 22)"
echo "   - Set BATCH_PATTERN (line 27)"
echo "   - Choose MODEL_NAME (line 34)"
echo ""
echo "2. Run the script:"
echo "   python3 Lippmann-Rau_VLM_OCR_MultiBatch.py"
echo ""
echo "3. After processing, analyze results:"
echo "   python3 analyze_results.py"
echo ""
echo "📖 For more information, see README_GITHUB.md"
