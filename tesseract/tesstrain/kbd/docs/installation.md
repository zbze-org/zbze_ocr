# Installation Guide

Complete installation instructions for Tesseract KBD language model.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installing Tesseract OCR](#installing-tesseract-ocr)
- [Installing KBD Language Model](#installing-kbd-language-model)
- [Python Dependencies](#python-dependencies)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System:** Linux, macOS, or Windows
- **Python:** 3.8 or higher (for Python bindings)
- **Tesseract:** Version 5.0 or higher recommended

### Storage Requirements

- Base model: ~17 MB
- Fine-tuned model: ~27 MB
- Configuration files: <1 MB

---

## Installing Tesseract OCR

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Tesseract 5.x
sudo apt install tesseract-ocr

# Verify installation
tesseract --version
```

### Linux (Fedora/RHEL/CentOS)

```bash
# Install Tesseract
sudo dnf install tesseract

# Verify installation
tesseract --version
```

### macOS

Using Homebrew:

```bash
# Install Tesseract
brew install tesseract

# Verify installation
tesseract --version
```

### Windows

1. Download installer from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Add Tesseract to PATH:
   ```cmd
   set PATH=%PATH%;C:\Program Files\Tesseract-OCR
   ```

---

## Installing KBD Language Model

### Method 1: Manual Installation (Recommended)

1. **Download the model:**

   ```bash
   # Download base model
   wget https://github.com/YOUR_ORG/tesseract-kbd/releases/latest/download/kbd.traineddata

   # Or download fine-tuned model
   wget https://github.com/YOUR_ORG/tesseract-kbd/releases/latest/download/kbd_finetuned.traineddata
   ```

2. **Find your tessdata directory:**

   ```bash
   # Linux/macOS
   tesseract --version | grep "tessdata"
   # Usually: /usr/share/tesseract-ocr/5/tessdata/

   # Or use
   echo $TESSDATA_PREFIX
   ```

   Common locations:
   - **Linux:** `/usr/share/tesseract-ocr/5/tessdata/`
   - **macOS:** `/usr/local/share/tessdata/` or `/opt/homebrew/share/tessdata/`
   - **Windows:** `C:\Program Files\Tesseract-OCR\tessdata\`

3. **Copy the model:**

   ```bash
   # Linux/macOS
   sudo cp kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/

   # If you want both models, rename one
   sudo cp kbd_finetuned.traineddata /usr/share/tesseract-ocr/5/tessdata/kbd_ft.traineddata
   ```

### Method 2: Using Custom Directory

If you don't have sudo access or prefer a custom location:

1. **Create custom tessdata directory:**

   ```bash
   mkdir -p ~/tessdata
   cp kbd.traineddata ~/tessdata/
   ```

2. **Set TESSDATA_PREFIX environment variable:**

   ```bash
   # Temporary (current session)
   export TESSDATA_PREFIX=~/tessdata

   # Permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export TESSDATA_PREFIX=~/tessdata' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Use in commands:**

   ```bash
   tesseract input.jpg output --tessdata-dir ~/tessdata -l kbd
   ```

### Method 3: Install via Git Clone (Development)

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/tesseract-kbd.git
cd tesseract-kbd

# Copy models
sudo cp trained_data/kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/
sudo cp trained_data/kbd_finetuned.traineddata /usr/share/tesseract-ocr/5/tessdata/

# Copy configuration files (optional)
mkdir -p ~/.tesseract/configs
cp configs/*.txt ~/.tesseract/configs/
```

---

## Python Dependencies

### Install pytesseract

```bash
# Using pip
pip install pytesseract Pillow

# Or using conda
conda install -c conda-forge pytesseract pillow
```

### Install OCRmyPDF (Optional)

For PDF processing:

```bash
pip install ocrmypdf
```

### Full Python Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install pytesseract Pillow opencv-python ocrmypdf

# Verify installation
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

---

## Verification

### Test Tesseract Installation

```bash
# List available languages
tesseract --list-langs

# You should see 'kbd' in the list
```

### Test with Python

Create `test_kbd.py`:

```python
import pytesseract
from PIL import Image

# Test Tesseract installation
print("Tesseract version:", pytesseract.get_tesseract_version())

# List available languages
langs = pytesseract.get_languages()
print("Available languages:", langs)

# Check if kbd is available
if 'kbd' in langs:
    print("✓ KBD language model is installed!")
else:
    print("✗ KBD language model not found")
```

Run the test:

```bash
python test_kbd.py
```

### Test OCR on Sample Image

```bash
# Download sample image (create one if needed)
# Then run OCR
tesseract sample.jpg output -l kbd

# View result
cat output.txt
```

---

## Troubleshooting

### Issue: "kbd" language not found

**Solution:**

1. Verify file location:
   ```bash
   find /usr -name "kbd.traineddata" 2>/dev/null
   ```

2. Check tessdata directory:
   ```bash
   tesseract --version | grep tessdata
   ```

3. Set TESSDATA_PREFIX:
   ```bash
   export TESSDATA_PREFIX=/path/to/tessdata
   ```

### Issue: Permission denied when copying

**Solution:**

```bash
# Use sudo
sudo cp kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/

# Or use custom directory without sudo
mkdir -p ~/tessdata
cp kbd.traineddata ~/tessdata/
export TESSDATA_PREFIX=~/tessdata
```

### Issue: Python can't find tesseract

**Solution:**

```bash
# Linux/macOS: Install tesseract via package manager
# Windows: Add to PATH
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"
```

Or specify path in Python:

```python
import pytesseract

# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS (Homebrew)
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

### Issue: Low OCR accuracy

**Possible solutions:**

1. Use fine-tuned model (`kbd_finetuned.traineddata`)
2. Use custom configuration file
3. Preprocess images (see [usage.md](usage.md))
4. Adjust Tesseract parameters (PSM, OEM)

### Issue: OCRmyPDF doesn't recognize kbd language

**Solution:**

```bash
# Verify OCRmyPDF can see the language
ocrmypdf --list-languages | grep kbd

# If not found, set TESSDATA_PREFIX before running
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ocrmypdf --language kbd input.pdf output.pdf
```

---

## Docker Installation (Alternative)

For isolated environment:

```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    python3 \
    python3-pip \
    wget

# Download and install KBD model
RUN wget -O /usr/share/tesseract-ocr/5/tessdata/kbd.traineddata \
    https://github.com/YOUR_ORG/tesseract-kbd/releases/latest/download/kbd.traineddata

# Install Python packages
RUN pip3 install pytesseract Pillow

# Verify installation
RUN tesseract --list-langs | grep kbd
```

Build and run:

```bash
docker build -t tesseract-kbd .
docker run -v $(pwd):/data tesseract-kbd tesseract /data/input.jpg /data/output -l kbd
```

---

## Next Steps

- **[Usage Guide](usage.md)** - Learn how to use the models
- **[Examples](../examples/)** - See code examples
- **[Quality Metrics](quality-metrics.md)** - Understanding model performance

---

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/tesseract-kbd/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/tesseract-kbd/discussions)
