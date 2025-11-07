# Usage Guide

Comprehensive guide for using Tesseract KBD language models.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Configuration Options](#configuration-options)
- [Image Preprocessing](#image-preprocessing)
- [Advanced Techniques](#advanced-techniques)
- [OCRmyPDF Integration](#ocrmypdf-integration)
- [Best Practices](#best-practices)

---

## Basic Usage

### Command Line

```bash
# Basic OCR
tesseract input.jpg output -l kbd

# With custom config
tesseract input.jpg output -l kbd --psm 1

# Output formats
tesseract input.jpg output -l kbd txt pdf hocr tsv
```

### Python - pytesseract

```python
import pytesseract
from PIL import Image

# Basic OCR
image = Image.open('document.jpg')
text = pytesseract.image_to_string(image, lang='kbd')
print(text)

# Get detailed data
data = pytesseract.image_to_data(image, lang='kbd', output_type=pytesseract.Output.DICT)
print(data['text'])

# Get bounding boxes
boxes = pytesseract.image_to_boxes(image, lang='kbd')
print(boxes)
```

---

## Configuration Options

### Page Segmentation Modes (PSM)

```python
import pytesseract
from PIL import Image

# PSM modes:
# 0 = Orientation and script detection (OSD) only
# 1 = Automatic page segmentation with OSD (default)
# 3 = Fully automatic page segmentation, but no OSD
# 6 = Assume a single uniform block of text
# 11 = Sparse text. Find as much text as possible

image = Image.open('document.jpg')

# Single column text
config = '--psm 6'
text = pytesseract.image_to_string(image, lang='kbd', config=config)

# Sparse text (headlines, captions)
config = '--psm 11'
text = pytesseract.image_to_string(image, lang='kbd', config=config)
```

### OCR Engine Mode (OEM)

```python
# OEM modes:
# 0 = Legacy engine only
# 1 = Neural nets LSTM engine only (default)
# 2 = Legacy + LSTM engines
# 3 = Default, based on what is available

config = '--oem 1 --psm 3'
text = pytesseract.image_to_string(image, lang='kbd', config=config)
```

### Using Custom Configuration Files

```python
import pytesseract
from PIL import Image

# Custom config file path
custom_config = r'-c /path/to/kdb.base.config.txt --psm 1'

image = Image.open('document.jpg')
text = pytesseract.image_to_string(image, lang='kbd', config=custom_config)
```

### Character Whitelist

```python
# Limit recognition to specific characters
cyrillic_only = r'--psm 6 -c tessedit_char_whitelist=АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'

text = pytesseract.image_to_string(image, lang='kbd', config=cyrillic_only)
```

---

## Image Preprocessing

### Using OpenCV

```python
import cv2
import pytesseract
from PIL import Image

def preprocess_image(image_path):
    # Read image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    return denoised

# Preprocess and OCR
processed = preprocess_image('input.jpg')
text = pytesseract.image_to_string(Image.fromarray(processed), lang='kbd')
print(text)
```

### Contrast Enhancement

```python
from PIL import Image, ImageEnhance
import pytesseract

def enhance_image(image_path):
    # Open image
    img = Image.open(image_path)

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)

    return img

# Process and OCR
enhanced = enhance_image('input.jpg')
text = pytesseract.image_to_string(enhanced, lang='kbd')
```

### Deskewing

```python
import cv2
import numpy as np
from PIL import Image
import pytesseract

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

# Load, deskew, and OCR
img = cv2.imread('skewed.jpg', 0)
deskewed = deskew(img)
text = pytesseract.image_to_string(Image.fromarray(deskewed), lang='kbd')
```

---

## Advanced Techniques

### Batch Processing with Progress Bar

```python
import pytesseract
from PIL import Image
from pathlib import Path
from tqdm import tqdm

def batch_ocr(input_dir, output_dir, lang='kbd'):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    image_files = list(input_path.glob('*.jpg')) + list(input_path.glob('*.png'))

    for img_file in tqdm(image_files, desc="Processing images"):
        try:
            img = Image.open(img_file)
            text = pytesseract.image_to_string(img, lang=lang)

            output_file = output_path / f"{img_file.stem}.txt"
            output_file.write_text(text, encoding='utf-8')
        except Exception as e:
            print(f"Error processing {img_file}: {e}")

# Usage
batch_ocr('input_images/', 'output_texts/', lang='kbd')
```

### Multi-Language OCR

```python
import pytesseract
from PIL import Image

# Combine KBD and Russian
image = Image.open('mixed_language.jpg')
text = pytesseract.image_to_string(image, lang='kbd+rus')
print(text)
```

### Confidence Scores

```python
import pytesseract
from PIL import Image

image = Image.open('document.jpg')

# Get word-level confidence scores
data = pytesseract.image_to_data(image, lang='kbd', output_type=pytesseract.Output.DICT)

# Filter low-confidence words
for i, word in enumerate(data['text']):
    if int(data['conf'][i]) > 60:  # Confidence threshold
        print(f"{word}: {data['conf'][i]}%")
```

### Region-specific OCR

```python
import pytesseract
from PIL import Image

image = Image.open('document.jpg')

# Define region (left, top, width, height)
region = image.crop((100, 100, 500, 300))

# OCR only this region
text = pytesseract.image_to_string(region, lang='kbd')
print(text)
```

---

## OCRmyPDF Integration

### Basic PDF OCR

```bash
# Add OCR layer to PDF
ocrmypdf --language kbd input.pdf output.pdf

# Force OCR (ignore existing text layer)
ocrmypdf --force-ocr --language kbd input.pdf output.pdf

# Skip pages with existing text
ocrmypdf --skip-text --language kbd input.pdf output.pdf
```

### Advanced OCRmyPDF

```bash
# High quality output
ocrmypdf \
    --language kbd \
    --deskew \
    --clean \
    --rotate-pages \
    --optimize 3 \
    input.pdf output.pdf

# Fast processing (lower quality)
ocrmypdf \
    --language kbd \
    --fast-web-view 1 \
    --optimize 1 \
    input.pdf output.pdf

# Custom config for KBD
ocrmypdf \
    --language kbd \
    --tesseract-config /path/to/kdb.base.config.txt \
    input.pdf output.pdf
```

### Python API

```python
import ocrmypdf

# Basic usage
ocrmypdf.ocr('input.pdf', 'output.pdf', language='kbd')

# Advanced options
ocrmypdf.ocr(
    'input.pdf',
    'output.pdf',
    language='kbd',
    deskew=True,
    clean=True,
    rotate_pages=True,
    remove_background=False,
    optimize=3,
    jobs=4  # Parallel processing
)
```

---

## Best Practices

### 1. Image Quality

- **Minimum DPI:** 300 DPI for printed text
- **Format:** Use PNG or TIFF for lossless quality
- **Color:** Grayscale is sufficient for text; reduces processing time

### 2. Preprocessing Pipeline

```python
import cv2
import numpy as np
from PIL import Image
import pytesseract

def optimal_preprocessing(image_path):
    # Read image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize if DPI is too low (upscale small images)
    height, width = gray.shape
    if height < 1000:
        scale = 1000 / height
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Deskew
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = thresh.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

# Use pipeline
processed = optimal_preprocessing('input.jpg')
text = pytesseract.image_to_string(Image.fromarray(processed), lang='kbd', config='--psm 1')
```

### 3. Choosing the Right Model

| Document Type | Recommended Model | PSM Mode |
|---------------|-------------------|----------|
| Modern printed books | `kbd.traineddata` | 1 or 3 |
| Historical texts | `kbd_finetuned.traineddata` | 1 |
| Single column article | Either | 6 |
| Newspaper (multi-column) | `kbd_finetuned.traineddata` | 1 or 3 |
| Sparse text (signs, captions) | `kbd.traineddata` | 11 |

### 4. Performance Optimization

```python
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def ocr_single_image(image_path, lang='kbd'):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang=lang)

def parallel_ocr(image_dir, max_workers=4):
    image_paths = list(Path(image_dir).glob('*.jpg'))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(ocr_single_image, image_paths)

    return list(results)

# Process multiple images in parallel
texts = parallel_ocr('images/', max_workers=8)
```

---

## Troubleshooting

### Poor Recognition Quality

1. **Check image quality:** Minimum 300 DPI
2. **Preprocess images:** Apply denoising, thresholding, deskewing
3. **Try fine-tuned model:** Use `kbd_finetuned.traineddata`
4. **Adjust PSM:** Experiment with different page segmentation modes
5. **Use custom config:** Apply `kdb.base.config.txt` for optimized settings

### Memory Issues with Large PDFs

```python
import ocrmypdf

# Process with limited memory
ocrmypdf.ocr(
    'large.pdf',
    'output.pdf',
    language='kbd',
    use_threads=True,
    jobs=2,  # Reduce parallel jobs
    optimize=1  # Lower optimization level
)
```

---

## Next Steps

- **[Quality Metrics](quality-metrics.md)** - Understanding model accuracy
- **[Training Guide](training.md)** - How models were trained
- **[Examples](../examples/)** - More code samples

---

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/tesseract-kbd/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/tesseract-kbd/discussions)
