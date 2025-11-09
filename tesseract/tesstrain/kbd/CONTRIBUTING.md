# Contributing to Tesseract KBD

Thank you for your interest in contributing to the Tesseract Kabardian language model! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Community](#community)

---

## Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### 🐛 Report Bugs

Found an issue with OCR accuracy or a bug in the code?

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title and description
   - Sample image (if OCR-related)
   - Expected vs. actual output
   - System information (OS, Tesseract version)
   - Steps to reproduce

**Template for OCR issues:**
```markdown
**Description:**
Brief description of the problem

**Sample Image:**
[Attach or link to image]

**Expected Output:**
[What text should be recognized]

**Actual Output:**
[What was actually recognized]

**System Info:**
- OS: Ubuntu 22.04
- Tesseract: 5.3.0
- Model: kbd_finetuned.traineddata
- Python: 3.10.5
```

### 📚 Improve Documentation

Documentation is crucial for accessibility:

- Fix typos or unclear explanations
- Add missing examples
- Translate documentation to other languages
- Create tutorials or guides
- Improve code comments

### 🔬 Improve Models

Help make the models more accurate:

1. **Share training data** (with appropriate permissions)
   - Scanned documents with transcriptions
   - Digital texts for word frequency lists
   - Specialized corpora (technical, historical, etc.)

2. **Report accuracy issues**
   - Specific document types where accuracy is poor
   - Systematic error patterns
   - Character confusion matrices

3. **Fine-tune for specific domains**
   - Historical texts
   - Technical documents
   - Handwritten text (future)

### 💻 Contribute Code

Improve tools, examples, or utilities:

- Add new examples or use cases
- Create helper scripts
- Improve preprocessing pipelines
- Build integrations with other tools

### 🧪 Testing

- Test models on your documents
- Validate on different platforms
- Performance benchmarking
- Create test datasets

---

## Getting Started

### Prerequisites

1. **Install Tesseract OCR:**
   ```bash
   # Ubuntu/Debian
   sudo apt install tesseract-ocr

   # macOS
   brew install tesseract
   ```

2. **Install Python dependencies:**
   ```bash
   pip install pytesseract Pillow opencv-python
   ```

3. **Install KBD model:**
   ```bash
   sudo cp trained_data/kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/
   ```

### Fork and Clone

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tesseract-kbd.git
   cd tesseract-kbd
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_ORG/tesseract-kbd.git
   ```

---

## Contribution Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Testing improvements
- `refactor/` - Code refactoring

### 2. Make Changes

- Follow [style guidelines](#style-guidelines)
- Write clear commit messages
- Test your changes

### 3. Commit

```bash
git add .
git commit -m "Brief description of changes

Detailed explanation if needed:
- Point 1
- Point 2
"
```

**Commit message format:**
```
<type>: <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Testing
- `refactor:` - Code refactoring
- `perf:` - Performance improvement

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

**Pull Request Guidelines:**

- Clear title and description
- Reference related issues (`Fixes #123`)
- Include screenshots for visual changes
- Update documentation if needed
- Ensure all tests pass

**PR Template:**
```markdown
## Description
What does this PR do?

## Related Issues
Fixes #123

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Screenshots (if applicable)
```

### 5. Code Review

- Respond to review comments
- Make requested changes
- Update your PR

```bash
# Make changes
git add .
git commit -m "Address review comments"
git push origin feature/your-feature-name
```

---

## Style Guidelines

### Python Code

Follow **PEP 8** style guide:

```python
# Good
def process_image(image_path: str, lang: str = 'kbd') -> str:
    """
    Process an image and extract text.

    Args:
        image_path: Path to the image file
        lang: Language code for OCR

    Returns:
        Extracted text as string
    """
    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang=lang)


# Use type hints
def calculate_accuracy(predicted: str, ground_truth: str) -> float:
    """Calculate character-level accuracy."""
    pass
```

**Guidelines:**
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions
- Include type hints

### Documentation

**Markdown formatting:**
```markdown
# Main Title

## Section

### Subsection

- Use bullet points for lists
- Use `code blocks` for code
- Use **bold** for emphasis
- Use [links](url) for references
```

**Code examples:**
- Include complete, runnable examples
- Add comments explaining key steps
- Show both input and output
- Test examples before submitting

### Commit Messages

**Good:**
```
feat: Add batch processing example

Added batch_processing.py with parallel processing support
using ThreadPoolExecutor. Includes progress tracking with tqdm.

Closes #42
```

**Bad:**
```
update files
```

---

## Testing

### Test Your Changes

1. **For model changes:**
   ```bash
   # Test on sample images
   tesseract test_data/samples/modern_text.jpg output -l kbd
   cat output.txt

   # Compare with ground truth
   diff output.txt test_data/expected_output/modern_text.txt
   ```

2. **For code changes:**
   ```bash
   # Run examples
   python examples/basic_usage.py test_data/samples/modern_text.jpg

   # Test batch processing
   python examples/batch_processing.py test_data/samples/ output/
   ```

3. **For documentation:**
   - Check for typos and broken links
   - Verify code examples work
   - Ensure formatting is correct

### Validation Script

Run the validation script before submitting:

```bash
# Create validation script
python scripts/validate_model.py --model trained_data/kbd.traineddata
```

---

## Contributing Training Data

### Guidelines for Training Data

If you have training data to contribute:

1. **Ensure you have rights** to share the data
2. **Provide clean ground truth:**
   - Accurate transcriptions
   - Consistent formatting
   - Native speaker verification

3. **Document the source:**
   - Source type (book, newspaper, etc.)
   - Time period
   - Quality assessment

4. **Format:**
   - Image files (.jpg, .png, .tiff)
   - Corresponding text files (.txt)
   - Or line images with .gt.txt files

### Privacy Considerations

- Do not contribute personal information
- Do not contribute copyrighted material without permission
- Redact sensitive information from documents

---

## Model Improvement Process

### 1. Identify Issues

- Document specific error patterns
- Collect problematic examples
- Measure current accuracy

### 2. Propose Improvements

- Open an issue describing the problem
- Suggest potential solutions
- Discuss with maintainers

### 3. Implement Changes

- Collect/generate additional training data
- Retrain or fine-tune model
- Validate improvements

### 4. Submit Changes

- Create PR with new model
- Include accuracy comparison
- Document training process
- Provide test results

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and ideas
- **Pull Requests:** Code and model contributions

### Getting Help

- Search existing issues and discussions
- Check documentation thoroughly
- Ask specific, detailed questions
- Provide context and examples

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS file
- Mentioned in release notes
- Credited in academic citations (if applicable)

---

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

## Questions?

- **General questions:** GitHub Discussions
- **Bug reports:** GitHub Issues
- **Security issues:** Email maintainers directly
- **Other inquiries:** Contact information in README

---

## Thank You!

Your contributions help preserve and digitize the Kabardian language. Every contribution, no matter how small, makes a difference!

---

**Useful Resources:**

- [Tesseract Documentation](https://tesseract-ocr.github.io/tessdoc/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Semantic Versioning](https://semver.org/)
