# Examples

This directory contains example scripts demonstrating how to use the Tesseract KBD language model.

## Available Examples

### 1. `basic_usage.py`

Demonstrates fundamental OCR operations:
- Basic text extraction
- Custom configuration (PSM modes)
- Confidence scores
- Bounding box detection

**Usage:**
```bash
python basic_usage.py image.jpg
```

### 2. `batch_processing.py`

Shows how to process multiple files efficiently:
- Parallel image processing
- Batch PDF conversion
- Image preprocessing pipeline
- Progress tracking with tqdm
- Error handling and reporting

**Usage:**
```bash
# Process images
python batch_processing.py ./input_images ./output_texts 4

# The script auto-detects whether to process images or PDFs
python batch_processing.py ./input_pdfs ./output_pdfs 2
```

### 3. `ocrmypdf_usage.py`

Comprehensive OCRmyPDF examples:
- Basic PDF OCR
- High-quality processing
- Fast processing mode
- Custom configurations
- Image preprocessing
- Batch directory processing

**Usage:**
```bash
# Basic OCR
python ocrmypdf_usage.py basic input.pdf output.pdf

# High quality with preprocessing
python ocrmypdf_usage.py high scan.pdf clean.pdf

# Fast processing
python ocrmypdf_usage.py fast input.pdf output.pdf

# Batch process directory
python ocrmypdf_usage.py batch ./input_pdfs ./output_pdfs
```

## Installation

Install required dependencies:

```bash
pip install pytesseract Pillow opencv-python ocrmypdf tqdm
```

## Prerequisites

1. **Tesseract OCR** must be installed on your system
2. **KBD language model** must be installed in tessdata directory
3. For PDF processing: **OCRmyPDF** and dependencies

See [installation guide](../docs/installation.md) for detailed instructions.

## Common Use Cases

### Single Image OCR
```python
import pytesseract
from PIL import Image

img = Image.open('document.jpg')
text = pytesseract.image_to_string(img, lang='kbd')
print(text)
```

### Batch Processing with Preprocessing
```python
from examples.batch_processing import batch_process_with_preprocessing

stats = batch_process_with_preprocessing(
    input_dir='./images',
    output_dir='./texts',
    lang='kbd',
    apply_preprocessing=True
)
```

### PDF OCR
```python
import ocrmypdf

ocrmypdf.ocr(
    'input.pdf',
    'output.pdf',
    language='kbd',
    deskew=True,
    clean=True
)
```

## Tips

1. **For best results:**
   - Use images with 300 DPI or higher
   - Apply preprocessing for poor quality scans
   - Choose appropriate PSM mode for your document layout

2. **For faster processing:**
   - Use parallel processing with multiple workers
   - Reduce optimization level in OCRmyPDF
   - Skip preprocessing if images are already clean

3. **For higher accuracy:**
   - Use the fine-tuned model (`kbd_finetuned.traineddata`)
   - Apply image preprocessing (denoising, deskewing)
   - Use custom configuration files

## More Information

- [Usage Guide](../docs/usage.md) - Detailed usage instructions
- [Installation Guide](../docs/installation.md) - Setup instructions
- [Quality Metrics](../docs/quality-metrics.md) - Model performance details
