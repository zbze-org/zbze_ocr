# zbze_ocr

<div align="center">

**Tesseract Training Infrastructure for Kabardian Language**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tesseract](https://img.shields.io/badge/tesseract-5.0+-green.svg)](https://github.com/tesseract-ocr/tesseract)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](LICENSE)

[Features](#features) • [Quick Start](#quick-start) • [Training](#training-workflow) • [Related Projects](#related-projects) • [Documentation](#documentation)

---

🌐 **[Документация на русском](docs/main.md)** | English

</div>

## Overview

`zbze_ocr` is the **training infrastructure and development repository** for Tesseract OCR models supporting the Kabardian language (kbd). This repository contains the complete toolchain for training, fine-tuning, evaluating, and deploying high-quality OCR models.

### What This Repository Provides

- 🎓 **Complete Training Pipeline** - Automated Airflow DAGs for model training
- 📊 **Data Preparation Tools** - Corpus cleaning, wordlist generation, image synthesis
- 📓 **Jupyter Notebooks** - Interactive workflows for experimentation
- 🔬 **Model Evaluation** - Quality metrics, CER/WER analysis, comparison tools
- 🏗️ **Legacy CLI Tools** - PDF preprocessing (superseded by zbze_ocr_cli)

## Project Ecosystem

This repository is part of a three-project ecosystem:

```
zbze_ocr (this repo)              → Training Infrastructure
    ├── Models & Configs           ↓
    └── Training Scripts      tesseract-kbd-model → Distributable Models
                                   ↓
                              zbze_ocr_cli → Production OCR Tool
```

### Related Projects

| Project | Purpose | When to Use | Repository |
|---------|---------|-------------|------------|
| **zbze_ocr** (this) | Training infrastructure, notebooks, development tools | Want to train models, experiment with training data | This repository |
| **tesseract-kbd-model** | Distributable Tesseract models for Kabardian | Just need the models | [zbze-org/tesseract-kbd-model](https://github.com/zbze-org/tesseract-kbd-model) |
| **zbze_ocr_cli** | Production-ready OCR CLI tool | Need to process documents with OCR | [zbze-org/zbze_ocr_cli](https://github.com/zbze-org/zbze_ocr_cli) |

## Features

### Training Infrastructure

- **Automated Training Pipeline (Airflow)**
  - Complete model training workflow with DAGs
  - Automated ground truth generation
  - Model evaluation and deployment
  - Version tracking and checkpointing

- **Data Preparation Tools**
  - Text corpus cleaning (`dags/src/text_cleaner.py`)
  - Synthetic training image generation (`dags/src/image_generator.py`)
  - Ground truth preparation (box/LSTMF files)
  - Wordlist and bigram extraction from corpora

- **Interactive Notebooks (Jupyter)**
  - `01_create_wlist_for_tesseract.ipynb` - Wordlist generation
  - `00_extract_collocation.ipynb` - Bigram extraction
  - `02_generate_image.ipynb` - Image generation pipeline
  - `12_test_tesseract_models.ipynb` - Model evaluation
  - Plus 20+ more notebooks for experimentation

### Trained Models

Two production-ready models (exported to [tesseract-kbd-model](https://github.com/zbze-org/tesseract-kbd-model)):

| Model | Size | Accuracy | CER | WER | Best For |
|-------|------|----------|-----|-----|----------|
| kbd.traineddata | 16 MB | 93.8% | 6.2% | 11.8% | Modern texts, general purpose |
| kbd_finetuned.traineddata | 26 MB | 95.9% | 4.1% | 8.3% | Historical documents, newspapers |

### Training Strategy

- **Base Model Training**
  - Transfer learning from Russian (rus) base model
  - 100,000 iterations (~2-3 days on 8+ core CPU)
  - Learning rate: 0.0001
  - Training corpus: 600K+ words, 25K lines

- **Fine-tuning**
  - Start from kbd base model
  - 50,000 iterations (~1-2 days)
  - Learning rate: 0.00005 (half the base rate)
  - Specialized corpus: historical texts, newspapers

## Quick Start

### Setup Environment

```bash
# Clone repository
git clone https://github.com/zbze-org/zbze_ocr.git
cd zbze_ocr

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Install External Tools

**macOS:**
```bash
brew install tesseract imagemagick unpaper
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr imagemagick unpaper
```

**Verify Installation:**
```bash
tesseract --version  # Should be 5.0+
convert --version    # ImageMagick 7.1.1+
unpaper --version    # 7.0.0+
```

### Train Your First Model

```bash
# Navigate to tesstrain directory
cd tesseract/tesstrain

# Train base model (this will take 2-3 days)
nohup gmake training \
  MODEL_NAME=kbd \
  START_MODEL=rus \
  MAX_ITERATIONS=100000 \
  TESSDATA=/opt/homebrew/share/tessdata \
  WORDLIST_FILE=kbd.wordlist \
  NUMBERS_FILE=kbd.numbers \
  PUNC_FILE=kbd.punc \
  | ts '[%Y-%m-%d %H:%M:%S]' | tee plot/output.log &

# Monitor training progress
tail -f plot/output.log

# Look for: "New best BCER" to see improvements
grep "New best" plot/output.log
```

See detailed training guide: [tesseract/tesstrain/kbd/docs/training.md](tesseract/tesstrain/kbd/docs/training.md)

### Use Training Notebooks

```bash
# Launch Jupyter
cd notebooks
jupyter notebook

# Open notebooks for:
# - Wordlist generation (01_create_wlist_for_tesseract.ipynb)
# - Bigram extraction (00_extract_collocation.ipynb)
# - Training image generation (02_generate_image.ipynb)
# - Model evaluation (12_test_tesseract_models.ipynb)
```

## Training Workflow

### Complete End-to-End Process

#### 1. Data Preparation

```bash
# Step 1: Clean text corpus
python dags/src/text_cleaner.py --input corpus.txt --output cleaned.txt

# Step 2: Generate wordlist (use Jupyter notebook)
jupyter notebook notebooks/01_create_wlist_for_tesseract.ipynb
# Output: kbd.wordlist (10K most frequent words)

# Step 3: Extract bigrams (use Jupyter notebook)
jupyter notebook notebooks/00_extract_collocation.ipynb
# Output: kbd.bigrams (common word pairs)

# Step 4: Generate synthetic training images
python dags/src/image_generator.py \
    --text cleaned.txt \
    --fonts fonts/ \
    --output ground_truth/

# Step 5: Prepare ground truth (box + lstmf files)
python dags/src/prepare_tessdata.py --dir ground_truth/
```

#### 2. Model Training

```bash
cd tesseract/tesstrain

# Train base model
gmake training \
  MODEL_NAME=kbd \
  START_MODEL=rus \
  MAX_ITERATIONS=100000

# Convert checkpoint to traineddata
gmake traineddata MODEL_NAME=kbd

# Install to system tessdata
cp data/kbd.traineddata /opt/homebrew/share/tessdata/
```

#### 3. Model Evaluation

```bash
# Use evaluation notebook
jupyter notebook notebooks/12_test_tesseract_models.ipynb

# Or use lstmeval command line tool
lstmeval --model data/kbd/kbd.lstm \
         --eval_listfile data/test.txt \
         --verbosity 2
# Output: Character Error Rate (CER), Word Error Rate (WER)
```

#### 4. Model Distribution

Export trained models to [tesseract-kbd-model](https://github.com/zbze-org/tesseract-kbd-model):

```bash
# Copy trained models
cp tesseract/trained_data/kbd.traineddata \
   ../tesseract-kbd-model/trained_data/

cp tesseract/trained_data/kbd_finetuned.traineddata \
   ../tesseract-kbd-model/trained_data/

# Copy configuration files
cp tesseract/tesstrain/kbd/configs/* \
   ../tesseract-kbd-model/configs/

# Generate checksums
cd ../tesseract-kbd-model/trained_data
sha256sum *.traineddata > checksums.txt
```

## Repository Structure

```
zbze_ocr/
├── dags/                       # Airflow DAGs for automation
│   ├── 00_train_tesseract.py   # Complete training workflow
│   ├── 00_image_generate.py    # Ground truth generation
│   └── src/                    # Python modules
│       ├── text_cleaner.py     # Corpus cleaning
│       ├── image_generator.py  # Synthetic image generation
│       └── prepare_tessdata.py # Ground truth preparation
│
├── notebooks/                  # Jupyter notebooks (25+)
│   ├── 01_create_wlist_for_tesseract.ipynb
│   ├── 00_extract_collocation.ipynb
│   ├── 02_generate_image.ipynb
│   ├── 12_test_tesseract_models.ipynb
│   └── ... (20+ more)
│
├── tesseract/                  # Models and training workspace
│   ├── trained_data/           # Production models
│   │   ├── kbd.traineddata
│   │   └── kbd_finetuned.traineddata
│   └── tesstrain/kbd/          # Active training directory
│       ├── configs/            # Tesseract configurations
│       ├── docs/               # Training documentation
│       └── fonts/              # 48 fonts for training
│
├── cli/                        # Legacy PDF preprocessing (use zbze_ocr_cli instead)
├── docs/                       # Documentation (Russian: main.md)
└── data/                       # Working directory (gitignored)
```

## Documentation

### Getting Started

- **[Main Guide (Russian)](docs/main.md)** - Complete setup and usage guide
- **[Training Guide](tesseract/tesstrain/kbd/docs/training.md)** - Step-by-step training instructions
- **[Quality Metrics](tesseract/tesstrain/kbd/docs/quality-metrics.md)** - Model performance analysis

### Training Resources

- **[Tesstrain Commands](docs/tesseract/tesstrain/readme.md)** - Training commands reference
- **[Model History](docs/tesseract/trained_data/model_history.md)** - Model versions and evolution
- **Jupyter Notebooks** - Interactive workflows in `notebooks/`

### For Model Users

If you just want to **use** the Kabardian OCR models:
- 📦 **Download models:** [tesseract-kbd-model](https://github.com/zbze-org/tesseract-kbd-model)
- 🔧 **Process documents:** [zbze_ocr_cli](https://github.com/zbze-org/zbze_ocr_cli)

## Airflow Integration

### Setup Airflow

```bash
# Copy configuration template
cp airflow.cfg.template airflow/airflow.cfg

# Edit configuration as needed
vim airflow/airflow.cfg

# Initialize database
airflow db init

# Start scheduler
airflow scheduler

# Start webserver (in another terminal)
airflow webserver
```

### Available DAGs

- **`train_tesseract_kbd`** - Complete training pipeline
- **`generate_training_images`** - Automated image generation

Access Airflow UI at http://localhost:8080

## Model Performance

### Benchmark Results

| Document Type | kbd.traineddata | kbd_finetuned.traineddata |
|---------------|-----------------|---------------------------|
| Modern books (2000-2020) | 4.5% CER | 2.9% CER |
| Historical texts (1960-1990) | 7.8% CER | 5.2% CER |
| Newspapers | 6.9% CER | 4.8% CER |
| Degraded scans | ~12% CER | ~9% CER |

### Training Data Statistics

- **Total corpus:** ~600,000 words
- **Unique words:** ~85,000
- **Training lines:** ~25,000
- **Validation lines:** ~3,000
- **Data sources:**
  - Web corpora (oshamaho.ru, adyghepsale.ru)
  - Digital books (1960-2020)
  - Manual transcriptions of historical documents

## Contributing

Contributions are welcome! This is a development repository for training infrastructure.

### How to Contribute

**Training Data:**
- Share cleaned Kabardian text corpora
- Provide manual transcriptions of documents
- Report issues with training data quality

**Model Improvements:**
- Experiment with training parameters
- Test different learning rates or iteration counts
- Share results and findings

**Tools & Scripts:**
- Improve data preparation scripts
- Add new Jupyter notebooks
- Enhance automation workflows

**Documentation:**
- Add guides and tutorials
- Translate documentation
- Share training experiences

### Contribution Guidelines

1. **For model distribution improvements** → contribute to [tesseract-kbd-model](https://github.com/zbze-org/tesseract-kbd-model)
2. **For OCR tool improvements** → contribute to [zbze_ocr_cli](https://github.com/zbze-org/zbze_ocr_cli)
3. **For training infrastructure** → contribute to this repository

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Tesseract OCR team** for the excellent OCR engine and training tools
- **tesstrain framework** for simplified training workflow
- **Kabardian language community** for corpus data and validation
- **Web sources:** oshamaho.ru, adyghepsale.ru for corpus materials

## Contact & Support

- **Issues:** [GitHub Issues](https://github.com/zbze-org/zbze_ocr/issues)
- **Author:** Adam Panagov
- **Email:** a.panagoa@gmail.com
- **Organization:** [zbze-org](https://github.com/zbze-org)

---

<div align="center">

**Part of the zbze-org initiative to preserve and digitize Kabardian language materials**

[⬆ Back to Top](#zbze_ocr)

</div>
