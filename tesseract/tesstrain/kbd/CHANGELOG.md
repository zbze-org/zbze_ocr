# Changelog

All notable changes to the Tesseract KBD language model will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Extended test coverage
- Additional examples for advanced use cases
- Performance benchmarks
- Docker image for easy deployment

## [1.0.0] - 2024-11-07

### Added
- Initial release of Tesseract KBD language models
- Base model (`kbd.traineddata`) - 17 MB
- Fine-tuned model (`kbd_finetuned.traineddata`) - 27 MB
- Comprehensive documentation:
  - Installation guide
  - Usage guide with examples
  - Training documentation
  - Quality metrics and benchmarks
- Configuration files:
  - Base configuration (`kdb.base.config.txt`)
  - OCRmyPDF configuration (`kdb.ocrmypdf.config.txt`)
  - Word frequency lists (10K and 100K)
  - Number and punctuation patterns
- Code examples:
  - Basic usage (`basic_usage.py`)
  - Batch processing (`batch_processing.py`)
  - OCRmyPDF integration (`ocrmypdf_usage.py`)
- Test data samples
- Migration plan from parent project
- Apache 2.0 License
- Contributing guidelines

### Performance
- Base model: ~94% accuracy on mixed corpus
- Fine-tuned model: ~96% accuracy on mixed corpus
- Character Error Rate (CER): 4.1% (fine-tuned)
- Word Error Rate (WER): 8.3% (fine-tuned)

### Documentation
- English README with detailed usage instructions
- Russian README (README.ru.md)
- Complete API documentation
- 40+ pages of comprehensive guides

### Notes
- Extracted from zbze_ocr project for better discoverability
- Trained on 600K+ words of Kabardian text
- Tested on historical (1960-1990) and modern (2000-2020) documents
- Supports Tesseract 5.0+

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| 1.0.0   | 2024-11-07   | Initial release with base and fine-tuned models |

---

## Migration from zbze_ocr

This project was extracted from the [zbze_ocr](https://github.com/YOUR_ORG/zbze_ocr) project to:
- Improve discoverability for users searching for Kabardian OCR solutions
- Enable independent development and versioning
- Make the models easily accessible to other projects
- Build a dedicated community around Kabardian language digitization

The models and configurations remain fully compatible with zbze_ocr.

---

## Upgrade Guide

### From zbze_ocr to standalone

If you were using the models from zbze_ocr:

```bash
# Old path (in zbze_ocr)
/zbze_ocr/tesseract/trained_data/kbd.traineddata

# New location (standalone)
wget https://github.com/YOUR_ORG/tesseract-kbd/releases/latest/download/kbd.traineddata

# Install to system
sudo cp kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/
```

No code changes required - the model name remains `kbd`.

---

## Future Roadmap

### v1.1.0 (Q1 2025)
- [ ] Improved fine-tuned model with extended training data
- [ ] Additional preprocessing utilities
- [ ] Performance optimization for batch processing
- [ ] Extended test suite

### v1.2.0 (Q2 2025)
- [ ] Support for handwritten text (experimental)
- [ ] Specialized models for historical documents
- [ ] Integration examples with popular frameworks

### v2.0.0 (Future)
- [ ] Tesseract 6.x compatibility
- [ ] Transformer-based model architecture
- [ ] Multi-script support (Kabardian + Latin + Arabic)
- [ ] Real-time OCR optimizations

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/tesseract-kbd/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/tesseract-kbd/discussions)
- **Security:** Report security issues to [SECURITY.md](SECURITY.md)

---

[Unreleased]: https://github.com/YOUR_ORG/tesseract-kbd/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_ORG/tesseract-kbd/releases/tag/v1.0.0
