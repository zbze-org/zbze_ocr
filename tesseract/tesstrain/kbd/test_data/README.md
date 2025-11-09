# Test Data

This directory contains sample images and expected outputs for testing the KBD Tesseract models.

## Structure

```
test_data/
├── README.md                    # This file
├── samples/                     # Sample images for testing
│   └── (add your test images here)
└── expected_output/             # Ground truth text files
    └── (corresponding text files)
```

## Usage

### Running Tests

```bash
# Test single image
tesseract test_data/samples/sample.jpg output -l kbd
diff output.txt test_data/expected_output/sample.txt

# Test with Python
python examples/basic_usage.py test_data/samples/sample.jpg
```

### Adding Test Data

When contributing test data:

1. **Add image file** to `samples/`:
   ```bash
   cp your_image.jpg test_data/samples/
   ```

2. **Add ground truth** to `expected_output/`:
   ```bash
   echo "Expected text here" > test_data/expected_output/your_image.txt
   ```

3. **Document the sample:**
   - Source and date
   - Document type
   - Image quality (DPI)
   - Expected accuracy

## Sample Types

Ideal test samples should include:

- **Modern printed text** (2000-2020)
- **Historical documents** (1960-1990)
- **Newspaper articles** (various layouts)
- **Books** (single column)
- **Mixed quality** (degraded, faded, etc.)

## Ground Truth Guidelines

Ground truth text files should:

- Use UTF-8 encoding
- Match the actual text in the image
- Preserve line breaks and formatting
- Include all text, including headers/footers

## Test Coverage

Target coverage areas:

- [ ] Modern printed books
- [ ] Historical texts (pre-1990)
- [ ] Newspapers (multi-column)
- [ ] Government documents
- [ ] Academic publications
- [ ] Mixed script documents (Kabardian + Russian)
- [ ] Poor quality scans
- [ ] Various fonts and sizes

## Validation

Run validation script:

```bash
python scripts/validate_model.py \
    --model trained_data/kbd.traineddata \
    --test_dir test_data/samples \
    --ground_truth test_data/expected_output
```

## Contributing

To contribute test data:

1. Ensure you have rights to share the images
2. Verify ground truth accuracy
3. Submit via Pull Request
4. Include metadata (source, date, type)

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Privacy

⚠️ **Important:**
- Do not include personal information
- Redact sensitive data
- Verify copyright compliance
- Anonymize if necessary
