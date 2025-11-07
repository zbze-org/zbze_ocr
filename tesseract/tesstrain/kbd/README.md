# Tesseract Kabardian (KBD) Language Model

[![Language](https://img.shields.io/badge/language-Kabardian-blue.svg)]()
[![Tesseract](https://img.shields.io/badge/tesseract-5.0+-green.svg)](https://github.com/tesseract-ocr/tesseract)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](LICENSE)

High-quality trained Tesseract OCR models for the **Kabardian language** (Cyrillic script), a Northwest Caucasian language spoken primarily in the Kabardino-Balkarian Republic of Russia.

> 🇷🇺 **Русская версия:** [README.ru.md](README.ru.md)

---

## 🌟 Features

- **Two trained models:**
  - `kbd.traineddata` (17 MB) - Base model trained on diverse text sources
  - `kbd_finetuned.traineddata` (27 MB) - Fine-tuned model with enhanced accuracy
- **Custom language configurations** optimized for Kabardian-specific characters
- **Word frequency dictionaries** for improved recognition accuracy
- **Punctuation and number patterns** tailored to Kabardian texts
- **Production-ready:** Tested on historical and modern printed documents

## 📥 Installation

### Quick Start

1. **Download the trained model:**
   ```bash
   wget https://github.com/YOUR_ORG/tesseract-kbd/releases/latest/download/kbd.traineddata
   ```

2. **Copy to Tesseract data directory:**
   ```bash
   # Linux/macOS
   sudo cp kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/

   # Or specify custom location
   export TESSDATA_PREFIX=/path/to/your/tessdata
   cp kbd.traineddata $TESSDATA_PREFIX
   ```

3. **Verify installation:**
   ```bash
   tesseract --list-langs | grep kbd
   ```

### Using with Python

```python
import pytesseract
from PIL import Image

# Basic usage
img = Image.open('sample.jpg')
text = pytesseract.image_to_string(img, lang='kbd')
print(text)

# With custom config
custom_config = r'--tessdata-dir /usr/share/tesseract-ocr/5/tessdata'
text = pytesseract.image_to_string(img, lang='kbd', config=custom_config)
```

### Using with OCRmyPDF

```bash
ocrmypdf --language kbd input.pdf output.pdf
```

For advanced OCRmyPDF configuration, see [docs/usage.md](docs/usage.md).

## 🚀 Usage Examples

### Basic OCR

```python
import pytesseract
from PIL import Image

# Load image
image = Image.open('kabardian_document.jpg')

# Perform OCR
text = pytesseract.image_to_string(image, lang='kbd')
print(text)
```

### With Custom Configuration

```python
import pytesseract
from PIL import Image

# Load custom config
config = '--psm 1 -c tessedit_char_whitelist=АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'

image = Image.open('document.jpg')
text = pytesseract.image_to_string(image, lang='kbd', config=config)
```

### Batch Processing

```python
import pytesseract
from PIL import Image
from pathlib import Path

input_dir = Path('input_images')
output_dir = Path('output_text')
output_dir.mkdir(exist_ok=True)

for img_path in input_dir.glob('*.jpg'):
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang='kbd')

    output_path = output_dir / f"{img_path.stem}.txt"
    output_path.write_text(text, encoding='utf-8')
    print(f"Processed: {img_path.name}")
```

More examples in [examples/](examples/) directory.

## 📊 Model Performance

| Model | Size | Training Data | Accuracy* |
|-------|------|---------------|-----------|
| `kbd.traineddata` | 17 MB | Mixed sources, 500K+ words | ~94% |
| `kbd_finetuned.traineddata` | 27 MB | Fine-tuned on historical texts | ~96% |

*Accuracy measured on held-out test set of printed documents (300 DPI scans)

See [docs/quality-metrics.md](docs/quality-metrics.md) for detailed evaluation results.

## 📁 Repository Structure

```
tesseract-kbd/
├── README.md                   # This file
├── README.ru.md                # Russian documentation
├── LICENSE                     # Apache 2.0 License
├── CONTRIBUTING.md             # Contribution guidelines
├── trained_data/               # Trained models
│   ├── kbd.traineddata
│   └── kbd_finetuned.traineddata
├── configs/                    # Tesseract configurations
│   ├── kdb.base.config.txt     # Base configuration
│   ├── kbd.wordlist            # Word frequency list
│   ├── kbd.wordlist.lg         # Extended wordlist
│   ├── kbd.numbers             # Number patterns
│   └── kbd.punc                # Punctuation patterns
├── docs/                       # Documentation
│   ├── installation.md         # Detailed installation guide
│   ├── usage.md                # Usage examples
│   ├── training.md             # Model training process
│   └── quality-metrics.md      # Performance metrics
├── examples/                   # Code examples
│   ├── basic_usage.py
│   ├── ocrmypdf_usage.py
│   └── batch_processing.py
└── test_data/                  # Sample images for testing
    └── samples/
```

## 🔧 Configuration Files

### Base Configuration (`configs/kdb.base.config.txt`)

Optimized settings for Kabardian OCR:
- **Character whitelist:** Extended Cyrillic alphabet with Kabardian-specific characters
- **Language model penalties:** Tuned for non-dictionary words (0.7) and case sensitivity (0.9)
- **DAWG modules:** Frequency dictionary, punctuation, numbers, and bigrams enabled

### Word Lists

- `kbd.wordlist` - Core vocabulary (10K most frequent words)
- `kbd.wordlist.lg` - Extended vocabulary (100K words)
- `kbd.numbers` - Number recognition patterns
- `kbd.punc` - Kabardian-specific punctuation rules

## 🎓 About Kabardian Language

**Kabardian** (Къэбэрдей, *Qăbărday*) is a Northwest Caucasian language with approximately 1 million speakers. It uses the Cyrillic script with several additional characters:

- Standard Cyrillic: А-Я (33 letters)
- Additional characters: Ӏ (palochka), Ӡ, Ә, etc.
- Used primarily in: Kabardino-Balkarian Republic, Russia

This project aims to preserve and digitize Kabardian texts, many of which exist only in printed form.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- 🐛 **Report issues** with OCR accuracy on specific document types
- 📚 **Share training data** (with appropriate permissions)
- 🔬 **Improve models** by fine-tuning on specialized corpora
- 📖 **Enhance documentation** and examples
- 🌍 **Translate** documentation to other languages

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Usage Guide](docs/usage.md)** - Advanced usage patterns
- **[Training Guide](docs/training.md)** - How the models were trained
- **[Quality Metrics](docs/quality-metrics.md)** - Performance evaluation

## 🔗 Related Projects

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open source OCR engine
- [tesstrain](https://github.com/tesseract-ocr/tesstrain) - Training tools for Tesseract
- [OCRmyPDF](https://github.com/ocrmypdf/ocrmypdf) - Add OCR text layer to PDFs

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Training data sources: [List your sources]
- Tesseract OCR team for the excellent OCR engine
- Kabardian language community for feedback and support

## 📮 Contact

- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/tesseract-kbd/issues)
- **Email:** your-email@example.com
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/tesseract-kbd/discussions)

---

## Quick Navigation

| | |
|---|---|
| 🚀 [Installation](#-installation) | 📖 [Documentation](docs/) |
| 💻 [Usage](#-usage-examples) | 🤝 [Contributing](CONTRIBUTING.md) |
| 📊 [Performance](#-model-performance) | 📄 [License](LICENSE) |

---

<p align="center">
  <strong>Help preserve Kabardian language through digitization! ⭐</strong>
  <br>
  If this project helps you, please consider giving it a star on GitHub
</p>
