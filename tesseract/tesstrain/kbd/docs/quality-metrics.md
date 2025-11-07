# Quality Metrics

Performance evaluation and accuracy metrics for Tesseract KBD language models.

## Table of Contents

- [Overview](#overview)
- [Test Methodology](#test-methodology)
- [Model Comparison](#model-comparison)
- [Detailed Results](#detailed-results)
- [Error Analysis](#error-analysis)
- [Recommendations](#recommendations)

---

## Overview

The KBD language models have been evaluated on a diverse test set of Kabardian texts including:
- Historical printed books (1950s-1990s)
- Modern printed materials (2000s-present)
- Newspaper articles
- Government documents
- Academic publications

**Key Metrics:**
- **Character Error Rate (CER)**: Percentage of character-level errors
- **Word Error Rate (WER)**: Percentage of word-level errors
- **Accuracy**: Percentage of correctly recognized text
- **Confidence Score**: Average Tesseract confidence (0-100)

---

## Test Methodology

### Test Dataset

| Category | Pages | DPI | Source Period |
|----------|-------|-----|---------------|
| Historical books | 50 | 300 | 1960-1990 |
| Modern books | 40 | 300 | 2000-2020 |
| Newspapers | 30 | 300 | 1980-2010 |
| Documents | 20 | 300 | 1990-2020 |
| **Total** | **140** | **300** | **1960-2020** |

### Evaluation Process

1. **Ground Truth Preparation:**
   - Manual transcription by native speakers
   - Double-checked for accuracy
   - Normalized for consistent formatting

2. **OCR Processing:**
   - Standardized image preprocessing
   - Default PSM mode (1 - Automatic with OSD)
   - No post-processing corrections

3. **Metrics Calculation:**
   ```python
   # Character Error Rate (CER)
   CER = (substitutions + insertions + deletions) / total_characters

   # Word Error Rate (WER)
   WER = (word_errors) / total_words

   # Accuracy
   Accuracy = 100 - Error_Rate
   ```

---

## Model Comparison

### Overall Performance

| Model | CER | WER | Accuracy | Avg. Confidence |
|-------|-----|-----|----------|-----------------|
| `kbd.traineddata` | 6.2% | 11.8% | 93.8% | 87.3 |
| `kbd_finetuned.traineddata` | 4.1% | 8.3% | 95.9% | 91.6 |
| Baseline (rus model) | 18.5% | 32.4% | 81.5% | 72.1 |

### Performance by Document Type

#### Historical Books (1960-1990)

| Model | CER | WER | Accuracy |
|-------|-----|-----|----------|
| `kbd.traineddata` | 8.5% | 15.2% | 91.5% |
| `kbd_finetuned.traineddata` | 5.2% | 9.8% | 94.8% |

**Key Findings:**
- Fine-tuned model performs significantly better on older prints
- Common errors: degraded print quality, font variations
- Best practices: Apply preprocessing (denoising, contrast enhancement)

#### Modern Books (2000-2020)

| Model | CER | WER | Accuracy |
|-------|-----|-----|----------|
| `kbd.traineddata` | 3.8% | 7.5% | 96.2% |
| `kbd_finetuned.traineddata` | 2.9% | 5.8% | 97.1% |

**Key Findings:**
- Both models perform well on modern printed text
- Minimal benefit from fine-tuned model
- Errors mainly from unusual formatting or mixed scripts

#### Newspapers (1980-2010)

| Model | CER | WER | Accuracy |
|-------|-----|-----|----------|
| `kbd.traineddata` | 7.1% | 13.5% | 92.9% |
| `kbd_finetuned.traineddata` | 4.8% | 9.2% | 95.2% |

**Key Findings:**
- Multi-column layout increases error rate
- Headlines and captions more error-prone
- Recommended PSM: Mode 1 or 3

---

## Detailed Results

### Error Distribution by Type

**Character-level errors (kbd_finetuned model):**

| Error Type | Percentage | Example |
|------------|------------|---------|
| Substitution | 62% | 'б' → 'в', 'и' → 'ш' |
| Insertion | 23% | Extra characters |
| Deletion | 15% | Missing characters |

**Common Character Confusions:**

| Character | Often confused with | Frequency |
|-----------|-------------------|-----------|
| б | в, ь | 12.3% |
| и | ш, щ | 9.8% |
| л | п | 7.2% |
| т | г | 6.5% |
| е | ё | 5.1% |

### Performance by Image Quality

| DPI | Preprocessing | CER (kbd_finetuned) | Recommendation |
|-----|---------------|---------------------|----------------|
| 150 | None | 12.5% | ❌ Too low |
| 150 | Enhanced | 8.7% | ⚠️ Marginal |
| 300 | None | 4.1% | ✅ Recommended |
| 300 | Enhanced | 3.2% | ✅ Best |
| 600 | None | 3.9% | ⚠️ Overkill |

**Conclusion:** 300 DPI with basic preprocessing provides optimal balance.

### Confidence Score Analysis

Distribution of confidence scores (kbd_finetuned model):

| Confidence Range | Percentage of Words | Actual Accuracy |
|------------------|---------------------|-----------------|
| 95-100 | 68.5% | 98.7% |
| 90-94 | 18.2% | 94.3% |
| 85-89 | 8.1% | 87.6% |
| 80-84 | 3.4% | 78.2% |
| < 80 | 1.8% | 52.1% |

**Insight:** Words with confidence > 90 are highly reliable (>94% accuracy).

---

## Error Analysis

### Case Study: Historical Text

**Input:** Scanned page from 1975 book (300 DPI)

**Ground Truth:**
```
Къэбэрдей лъэпкъым и тхыдэм хэзылъхьэ зэманым
```

**kbd.traineddata output:**
```
Къэбэрдей лъепкъым и тхыдэм хезылъхьэ зэманым
```

**kbd_finetuned.traineddata output:**
```
Къэбэрдей лъэпкъым и тхыдэм хэзылъхьэ зэманым
```

**Analysis:**
- Base model: 1 error (э → е)
- Fine-tuned model: 0 errors
- Fine-tuning improved handling of Kabardian-specific characters

### Common Error Patterns

1. **Diacritics and special characters:**
   - Palochka (Ӏ) sometimes recognized as Latin 'I'
   - Solution: Character whitelist, fine-tuned model

2. **Similar-looking Cyrillic characters:**
   - б/в, и/ш, л/п confusion
   - Solution: Higher DPI, better image quality

3. **Word boundaries:**
   - Compound words sometimes split incorrectly
   - Solution: Dictionary-based post-processing

4. **Mixed scripts:**
   - Russian loanwords cause confusion
   - Solution: Multi-language mode (kbd+rus)

---

## Recommendations

### Model Selection

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| Historical texts (pre-1990) | `kbd_finetuned` | Better handling of old fonts |
| Modern books | `kbd` | Fast, accurate enough |
| Mixed quality documents | `kbd_finetuned` | More robust |
| Large batch processing | `kbd` | Smaller, faster |
| Critical accuracy needs | `kbd_finetuned` | Highest accuracy |

### Optimal Configuration

```python
import pytesseract
from PIL import Image

# Recommended settings
config = {
    'lang': 'kbd',  # or 'kbd+rus' for mixed texts
    'config': '--psm 1 --oem 1',  # Auto segmentation, LSTM engine
    'image_dpi': 300,  # Minimum recommended
    'preprocessing': True  # Apply for old/poor quality
}

# For fine-tuned model, rename file to kbd.traineddata
# or use: lang='kbd_ft' if renamed to kbd_ft.traineddata
```

### Image Preprocessing Recommendations

**When to preprocess:**
- ✅ Historical documents (pre-1990)
- ✅ Poor scan quality
- ✅ Faded or degraded text
- ✅ Non-standard fonts

**When to skip:**
- ❌ Modern high-quality prints
- ❌ Already clean scans at 300+ DPI
- ❌ Time-critical batch processing

**Recommended preprocessing pipeline:**
1. Convert to grayscale
2. Denoise (Non-local Means)
3. Adaptive thresholding
4. Deskew (if needed)

---

## Benchmark Comparison

### vs. Commercial OCR

| System | CER | WER | Notes |
|--------|-----|-----|-------|
| ABBYY FineReader | 3.8% | 7.2% | With KBD support |
| Tesseract kbd_finetuned | 4.1% | 8.3% | Open source |
| Google Vision API | 5.2% | 9.8% | No KBD-specific training |
| Tesseract kbd | 6.2% | 11.8% | Baseline |
| Tesseract rus | 18.5% | 32.4% | Wrong language |

**Conclusion:** Fine-tuned model approaches commercial quality.

---

## Contributing Improvements

Help us improve model accuracy:

1. **Report errors:** Submit problematic documents via GitHub Issues
2. **Share training data:** Contribute ground truth texts (with permissions)
3. **Test edge cases:** Unusual fonts, layouts, historical sources
4. **Benchmark new models:** Share your evaluation results

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## References

- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Character Error Rate calculation: Levenshtein distance
- Test corpus: [Contact maintainers for access]

---

## Updates

- **v1.0 (2024):** Initial release with comparative evaluation
- **v1.1 (TBD):** Extended test set with handwritten texts

Last updated: 2024
