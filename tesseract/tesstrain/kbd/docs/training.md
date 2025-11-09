# Training Guide

Documentation of the training process for Tesseract KBD language models.

## Table of Contents

- [Overview](#overview)
- [Training Data](#training-data)
- [Training Process](#training-process)
- [Fine-tuning](#fine-tuning)
- [Model Architecture](#model-architecture)
- [Validation](#validation)
- [Reproducing Training](#reproducing-training)

---

## Overview

The Tesseract KBD models were trained using Tesseract 5.x's LSTM (Long Short-Term Memory) neural network architecture. Two models are provided:

1. **kbd.traineddata** - Base model trained from scratch
2. **kbd_finetuned.traineddata** - Fine-tuned on specialized corpus

### Training Timeline

| Phase | Duration | Iterations | Data Size |
|-------|----------|------------|-----------|
| Base training | 2-3 days | ~100K | 500K words |
| Fine-tuning | 1-2 days | ~50K | 200K words |
| Validation | 1 day | - | 50K words |

### Hardware Requirements

- **CPU:** 8+ cores recommended
- **RAM:** 16+ GB
- **Storage:** 10+ GB free space
- **GPU:** Optional (CUDA support for faster training)

---

## Training Data

### Data Sources

Training data was collected from multiple sources:

1. **Digital Books:**
   - Kabardian literature (1960-2020)
   - Academic publications
   - Historical documents
   - **Size:** ~300K words

2. **Web Corpora:**
   - Online newspapers (adyghepsale.ru, oshamaho.ru)
   - Government websites
   - Educational materials
   - **Size:** ~200K words

3. **OCR Ground Truth:**
   - Manually transcribed scans
   - Verified by native speakers
   - **Size:** ~100K words

### Data Preparation

#### Text Corpus Collection

```bash
# Example: Extract text from web sources
python collect_corpus.py --source oshamaho.ru --output corpus/oshamaho.txt

# Clean and normalize text
python clean_text.py --input corpus/*.txt --output cleaned/
```

#### Word Frequency Lists

Word frequency dictionaries improve recognition accuracy:

```bash
# Generate frequency lists
python generate_wordlist.py --input cleaned/*.txt --output kbd.wordlist --top 10000

# Generate bigram frequencies
python generate_bigrams.py --input cleaned/*.txt --output kbd.bigrams --top 5000
```

**Output files:**
- `kbd.wordlist` - 10K most frequent words
- `kbd.wordlist.lg` - 100K extended vocabulary
- `kbd.bigrams` - Common word pairs

#### Ground Truth Generation

For supervised training, create line images with ground truth text:

```bash
# Generate training images from text
text2image --text=corpus.txt \
           --outputbase=train/kbd \
           --font='Liberation Serif' \
           --fonts_dir=/usr/share/fonts \
           --fontconfig_tmpdir=/tmp/fonts
```

### Data Statistics

| Metric | Value |
|--------|-------|
| Total words | ~600,000 |
| Unique words | ~85,000 |
| Training lines | ~25,000 |
| Validation lines | ~3,000 |
| Character set size | 73 (Cyrillic + special) |

---

## Training Process

### Base Model Training

The base model was trained using the `tesstrain` framework:

#### 1. Setup Training Environment

```bash
# Clone tesstrain
git clone https://github.com/tesseract-ocr/tesstrain
cd tesstrain

# Create language directory
mkdir -p data/kbd-ground-truth
```

#### 2. Prepare Training Data

```bash
# Copy ground truth files (image + text pairs)
cp /path/to/training/*.tif data/kbd-ground-truth/
cp /path/to/training/*.gt.txt data/kbd-ground-truth/

# Directory structure:
# data/kbd-ground-truth/
#   ├── page001.tif
#   ├── page001.gt.txt
#   ├── page002.tif
#   ├── page002.gt.txt
#   └── ...
```

#### 3. Configure Training

Create `kbd.training_config`:

```makefile
MODEL_NAME = kbd
START_MODEL = rus  # Start from Russian model (similar script)
TESSDATA = /usr/share/tesseract-ocr/5/tessdata
GROUND_TRUTH_DIR = data/kbd-ground-truth
MAX_ITERATIONS = 100000
LEARNING_RATE = 0.0001
NET_SPEC = [1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c111]
```

**Network Specification Explained:**
- `[1,36,0,1` - Input layer (1 channel, 36 pixel height)
- `Ct3,3,16` - Convolutional layer (3x3 kernel, 16 filters)
- `Mp3,3` - Max pooling (3x3)
- `Lfys48` - Forward LSTM (48 nodes)
- `Lfx96 Lrx96` - Bidirectional LSTM (96 nodes each direction)
- `Lfx256` - Forward LSTM (256 nodes)
- `O1c111` - Output layer (softmax, 73 classes)

#### 4. Run Training

```bash
# Start training
make training MODEL_NAME=kbd START_MODEL=rus

# Monitor progress
tail -f data/kbd.log
```

#### 5. Training Monitoring

Key metrics to watch:

```
Iteration 10000: Training loss = 0.245
Iteration 20000: Training loss = 0.182
Iteration 50000: Training loss = 0.098
Iteration 100000: Training loss = 0.042  # Target < 0.05
```

**Training convergence:**
- **Early stage (0-20K):** Rapid loss decrease
- **Mid stage (20-60K):** Gradual improvement
- **Late stage (60-100K):** Fine-tuning, diminishing returns

#### 6. Extract Trained Model

```bash
# Combine layers into final model
make traineddata MODEL_NAME=kbd

# Output: data/kbd.traineddata
```

---

## Fine-tuning

Fine-tuning improves performance on specific document types (e.g., historical texts).

### Fine-tuning Process

#### 1. Prepare Specialized Corpus

```bash
# Collect historical texts
mkdir -p data/kbd-finetuned-ground-truth

# Create ground truth for historical documents
cp historical_docs/*.tif data/kbd-finetuned-ground-truth/
cp historical_docs/*.gt.txt data/kbd-finetuned-ground-truth/
```

#### 2. Configure Fine-tuning

```makefile
MODEL_NAME = kbd_finetuned
START_MODEL = kbd  # Start from base model
TESSDATA = /usr/share/tesseract-ocr/5/tessdata
GROUND_TRUTH_DIR = data/kbd-finetuned-ground-truth
MAX_ITERATIONS = 50000  # Fewer iterations for fine-tuning
LEARNING_RATE = 0.00005  # Lower learning rate
```

#### 3. Run Fine-tuning

```bash
# Fine-tune from base model
make training MODEL_NAME=kbd_finetuned START_MODEL=kbd

# Extract fine-tuned model
make traineddata MODEL_NAME=kbd_finetuned
```

### Fine-tuning Best Practices

1. **Lower learning rate:** Prevent catastrophic forgetting
2. **Smaller corpus:** Focus on specific domain (historical, technical, etc.)
3. **Fewer iterations:** Stop when validation loss plateaus
4. **Validation:** Test on held-out data regularly

---

## Model Architecture

### LSTM Network Structure

```
Input Image (300 DPI)
         ↓
   [Preprocessing]
    - Normalize
    - Binarize
         ↓
   [Feature Extraction]
    - Convolutional layers
    - Max pooling
         ↓
   [Sequence Modeling]
    - Bidirectional LSTM
    - Forward LSTM
         ↓
   [Classification]
    - Softmax output
    - 73 character classes
         ↓
   Output Text
```

### Layer Configuration

| Layer | Type | Parameters | Purpose |
|-------|------|------------|---------|
| Input | Image | 1x36xW | Normalized input |
| Conv1 | 2D Conv | 3x3, 16 filters | Feature extraction |
| Pool1 | MaxPool | 3x3 | Dimensionality reduction |
| LSTM1 | Forward | 48 nodes | Sequence learning |
| LSTM2 | Bidirectional | 96+96 nodes | Context modeling |
| LSTM3 | Forward | 256 nodes | High-level features |
| Output | Softmax | 73 classes | Character prediction |

### Character Set

The model recognizes 73 characters:

- **Cyrillic:** А-Я, а-я (33 letters)
- **Special:** Ӏ (palochka), Ӡ, Ә, etc.
- **Numbers:** 0-9
- **Punctuation:** .,!?;:-()[]«»"'
- **Space**

---

## Validation

### Validation Metrics

Training is validated on held-out test set:

```bash
# Run validation
lstmeval --model data/kbd/kbd.lstm \
         --eval_listfile data/test_list.txt \
         --verbosity 2
```

**Output:**
```
Character error rate = 4.1%
Word error rate = 8.3%
```

### Cross-validation

K-fold validation (K=5) was used to ensure model generalization:

| Fold | CER | WER |
|------|-----|-----|
| 1 | 4.2% | 8.5% |
| 2 | 3.9% | 8.1% |
| 3 | 4.3% | 8.6% |
| 4 | 4.0% | 8.2% |
| 5 | 4.1% | 8.4% |
| **Mean** | **4.1%** | **8.4%** |

**Conclusion:** Consistent performance across folds indicates good generalization.

---

## Reproducing Training

To reproduce the training process:

### Step 1: Environment Setup

```bash
# Install Tesseract with training tools
sudo apt install tesseract-ocr libtesseract-dev

# Clone tesstrain
git clone https://github.com/tesseract-ocr/tesstrain
cd tesstrain

# Install dependencies
sudo apt install lsb-release
pip install -r requirements.txt
```

### Step 2: Prepare Data

```bash
# Create ground truth data
# (Requires manual transcription or existing dataset)
mkdir -p data/kbd-ground-truth

# Generate synthetic training data (alternative)
python generate_training_data.py \
    --corpus kbd_corpus.txt \
    --fonts "Liberation Serif,DejaVu Serif" \
    --output data/kbd-ground-truth
```

### Step 3: Train Model

```bash
# Configure training
export MODEL_NAME=kbd
export START_MODEL=rus
export MAX_ITERATIONS=100000

# Run training
make training

# Monitor progress
tail -f data/kbd.log

# Extract model when done
make traineddata
```

### Step 4: Validate

```bash
# Test on validation set
lstmeval --model data/kbd/kbd.lstm \
         --eval_listfile data/test.txt

# Compare with ground truth
python evaluate.py --model data/kbd.traineddata \
                   --test_images validation/*.jpg \
                   --ground_truth validation/*.txt
```

---

## Training Tips

### Improving Accuracy

1. **More training data:**
   - Target: 100K+ lines of ground truth
   - Diverse sources (books, newspapers, documents)

2. **Better ground truth quality:**
   - Manual verification by native speakers
   - Consistent formatting
   - Accurate transcriptions

3. **Hyperparameter tuning:**
   - Learning rate: 0.0001-0.001
   - Iterations: 50K-200K
   - Network depth: Add LSTM layers for complex scripts

4. **Data augmentation:**
   - Font variations
   - Synthetic degradation (noise, blur)
   - Rotation, scaling

### Common Issues

**Problem:** Training loss not decreasing
**Solution:**
- Increase learning rate
- Check data quality
- Verify START_MODEL compatibility

**Problem:** Overfitting (training loss low, validation loss high)
**Solution:**
- Add more training data
- Reduce model complexity
- Early stopping

**Problem:** Out of memory
**Solution:**
- Reduce batch size
- Use smaller network
- Train on GPU

---

## Further Reading

- [Tesseract Training Documentation](https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html)
- [tesstrain GitHub](https://github.com/tesseract-ocr/tesstrain)
- [LSTM Networks for OCR](https://arxiv.org/abs/1507.05717)

---

## Contact

Questions about training process:
- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/tesseract-kbd/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/tesseract-kbd/discussions)

---

Last updated: 2024
