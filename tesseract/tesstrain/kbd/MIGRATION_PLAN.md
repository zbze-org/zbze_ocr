# Migration Plan: Extracting tesseract-kbd to Separate Repository

This document outlines the plan and steps for extracting the Tesseract Kabardian (KBD) language model from the `zbze_ocr` project into a standalone repository.

## Table of Contents

- [Rationale](#rationale)
- [Repository Structure](#repository-structure)
- [Migration Steps](#migration-steps)
- [Post-Migration Setup](#post-migration-setup)
- [Integration with zbze_ocr](#integration-with-zbze_ocr)
- [Release Strategy](#release-strategy)

---

## Rationale

### Why Extract to Separate Repository?

1. **🔍 Discoverability**
   - Makes the KBD model easily findable through search engines and GitHub
   - Attracts contributors working with Caucasian languages
   - Enables independent citations in academic work

2. **♻️ Reusability**
   - Other projects can use the model without cloning entire zbze_ocr
   - Can be distributed via GitHub Releases
   - Potential for PyPI package distribution

3. **🌍 Community Building**
   - Dedicated space for KBD-specific issues and discussions
   - Lower barrier to entry for contributors
   - Focused documentation for language model users

4. **🔧 Maintainability**
   - Independent versioning
   - Separate CI/CD pipeline
   - Cleaner issue tracking

---

## Repository Structure

The new repository will have this structure:

```
tesseract-kbd/
├── README.md                       # Main documentation (EN)
├── README.ru.md                    # Russian documentation
├── LICENSE                         # Apache 2.0
├── CONTRIBUTING.md                 # Contribution guidelines
├── .gitignore                      # Git ignore rules
├── .github/                        # GitHub specific files
│   ├── workflows/
│   │   ├── release.yml            # Automated releases
│   │   └── validate.yml           # Model validation CI
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── trained_data/                   # Pre-trained models
│   ├── kbd.traineddata            # Base model (17 MB)
│   ├── kbd_finetuned.traineddata  # Fine-tuned model (27 MB)
│   └── checksums.txt              # SHA256 checksums
├── configs/                        # Tesseract configurations
│   ├── kdb.base.config.txt        # Base configuration
│   ├── kdb.ocrmypdf.config.txt    # OCRmyPDF config
│   ├── kbd.wordlist               # Word frequency list (10K)
│   ├── kbd.wordlist.lg            # Extended wordlist (100K)
│   ├── kbd.numbers                # Number patterns
│   ├── kbd.punc                   # Punctuation patterns
│   └── README.md                  # Config documentation
├── docs/                           # Documentation
│   ├── installation.md            # Installation guide
│   ├── usage.md                   # Usage examples
│   ├── training.md                # Training documentation
│   ├── quality-metrics.md         # Performance metrics
│   └── api-reference.md           # API reference
├── examples/                       # Code examples
│   ├── README.md                  # Examples overview
│   ├── basic_usage.py             # Basic OCR examples
│   ├── batch_processing.py        # Batch processing
│   ├── ocrmypdf_usage.py          # PDF processing
│   └── requirements.txt           # Example dependencies
├── test_data/                      # Sample test images
│   ├── samples/                   # Test images
│   │   ├── modern_text.jpg
│   │   ├── historical_text.jpg
│   │   └── newspaper.jpg
│   └── expected_output/           # Ground truth
│       ├── modern_text.txt
│       ├── historical_text.txt
│       └── newspaper.txt
├── train_data/                     # Training data info (optional)
│   ├── README.md                  # Training data documentation
│   └── frequency_lists/           # Word frequency data
│       ├── bigrams_freq.txt
│       └── unigrams_freq.txt
└── scripts/                        # Utility scripts
    ├── install.sh                 # Installation script
    ├── validate_model.py          # Model validation
    └── generate_checksums.sh      # Generate SHA256 sums
```

---

## Migration Steps

### Phase 1: Prepare Current Repository (zbze_ocr)

This branch already contains the prepared structure in `tesseract/tesstrain/kbd/`.

#### ✅ Completed:
- [x] Created comprehensive README (EN + RU)
- [x] Added LICENSE (Apache 2.0)
- [x] Created documentation (installation, usage, training, quality metrics)
- [x] Added examples (basic, batch, OCRmyPDF)
- [x] Organized configs and trained models
- [x] Written migration plan (this document)

#### Next Steps in zbze_ocr:

```bash
# 1. Review all files in tesseract/tesstrain/kbd/
cd tesseract/tesstrain/kbd
ls -la

# 2. Commit changes to this branch
git add .
git commit -m "Prepare KBD model for extraction to separate repository"
git push origin claude/refactor-separate-component-011CUtFevBsVtdd3Hnczc15u

# 3. The directory is now ready for extraction
```

### Phase 2: Extract to New Repository

#### Option A: Using Git Subtree (Preserves History)

```bash
# In zbze_ocr repository
git subtree split --prefix=tesseract/tesstrain/kbd --branch kbd-extraction

# Create new repository on GitHub: tesseract-kbd

# Push to new repository
git push git@github.com:YOUR_ORG/tesseract-kbd.git kbd-extraction:main

# Clean up
git branch -D kbd-extraction
```

#### Option B: Fresh Repository (Recommended - Cleaner History)

```bash
# 1. Create new repository on GitHub
# GitHub > New Repository > tesseract-kbd

# 2. Copy files to new repository
cd /tmp
git clone git@github.com:YOUR_ORG/tesseract-kbd.git
cd tesseract-kbd

# 3. Copy all files from zbze_ocr/tesseract/tesstrain/kbd/
cp -r /path/to/zbze_ocr/tesseract/tesstrain/kbd/* .

# 4. Initialize and commit
git add .
git commit -m "Initial commit: Tesseract KBD language model

Extracted from zbze_ocr project.
Includes:
- Pre-trained models (base + fine-tuned)
- Configuration files
- Documentation (EN + RU)
- Examples and test data
"

# 5. Push to GitHub
git push origin main

# 6. Create initial release (v1.0.0)
git tag v1.0.0
git push origin v1.0.0
```

### Phase 3: Post-Migration Setup

#### 1. GitHub Repository Settings

```bash
# Configure repository
- Description: "Tesseract OCR trained model for Kabardian language (Cyrillic script)"
- Topics: tesseract, ocr, kabardian, circassian, minority-languages, nlp, caucasian-languages
- Website: (link to docs if deployed)
- License: Apache-2.0
```

#### 2. Create GitHub Releases

```bash
# Create release with model files
gh release create v1.0.0 \
    trained_data/kbd.traineddata \
    trained_data/kbd_finetuned.traineddata \
    --title "Release v1.0.0" \
    --notes "Initial release of Tesseract KBD models

**Models:**
- kbd.traineddata (17 MB) - Base model
- kbd_finetuned.traineddata (27 MB) - Fine-tuned model

**Accuracy:**
- Base: ~94% accuracy on mixed corpus
- Fine-tuned: ~96% accuracy

**Installation:**
See README.md for installation instructions.
"
```

#### 3. Setup CI/CD (GitHub Actions)

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate checksums
        run: |
          cd trained_data
          sha256sum *.traineddata > checksums.txt

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            trained_data/kbd.traineddata
            trained_data/kbd_finetuned.traineddata
            trained_data/checksums.txt
          body_path: CHANGELOG.md
```

#### 4. Add Sample Test Data

```bash
# Add a few sample images for testing
mkdir -p test_data/samples
mkdir -p test_data/expected_output

# Copy or create sample images
# Add corresponding ground truth text files
```

---

## Integration with zbze_ocr

After extraction, update `zbze_ocr` to use the external repository:

### Option 1: Git Submodule

```bash
# In zbze_ocr repository
cd tesseract/tesstrain
git rm -r kbd
git commit -m "Remove kbd directory (extracted to separate repo)"

# Add as submodule
git submodule add https://github.com/YOUR_ORG/tesseract-kbd.git kbd
git commit -m "Add tesseract-kbd as submodule"

# Update documentation
echo "KBD models are now maintained in: https://github.com/YOUR_ORG/tesseract-kbd" > tesseract/tesstrain/README.md
```

### Option 2: Download on Demand

Create `tesseract/tesstrain/download_kbd.sh`:

```bash
#!/bin/bash
# Download KBD models from GitHub releases

VERSION="v1.0.0"
BASE_URL="https://github.com/YOUR_ORG/tesseract-kbd/releases/download/$VERSION"

echo "Downloading KBD models..."
mkdir -p kbd/trained_data

wget -O kbd/trained_data/kbd.traineddata \
    "$BASE_URL/kbd.traineddata"

wget -O kbd/trained_data/kbd_finetuned.traineddata \
    "$BASE_URL/kbd_finetuned.traineddata"

echo "Download complete!"
```

### Option 3: Package Dependency (Future)

When ready, publish to PyPI:

```bash
pip install tesseract-kbd
```

Then in zbze_ocr:

```python
# requirements.txt
tesseract-kbd>=1.0.0

# In code
from tesseract_kbd import get_model_path

model_path = get_model_path('kbd_finetuned')
```

---

## Release Strategy

### Initial Release (v1.0.0)

**Contents:**
- Base model (kbd.traineddata)
- Fine-tuned model (kbd_finetuned.traineddata)
- Complete documentation
- Examples
- Configuration files

**Announcement Channels:**
- GitHub Release notes
- Tesseract OCR community forums
- Reddit: r/MachineLearning, r/OCR
- Twitter/X: Tag @tesseract_ocr
- Minority languages forums

### Version Numbering

Follow Semantic Versioning (semver):

- **Major (X.0.0):** Breaking changes, model architecture changes
- **Minor (1.X.0):** New features, improved models, backward compatible
- **Patch (1.0.X):** Bug fixes, documentation updates

### Future Releases

**v1.1.0 (Planned):**
- Improved fine-tuned model
- Extended test coverage
- Additional examples

**v2.0.0 (Future):**
- Tesseract 6.x compatibility
- Transformer-based model
- Multi-script support

---

## Post-Migration Checklist

### In New Repository (tesseract-kbd)

- [ ] Verify all files are present
- [ ] Test model installation locally
- [ ] Run examples to ensure they work
- [ ] Create initial GitHub Release (v1.0.0)
- [ ] Setup GitHub Topics and description
- [ ] Configure branch protection rules
- [ ] Add CODEOWNERS file
- [ ] Setup GitHub Actions for CI/CD
- [ ] Add contribution guidelines
- [ ] Create issue templates

### In Original Repository (zbze_ocr)

- [ ] Remove or archive kbd directory
- [ ] Update documentation references
- [ ] Add link to new repository
- [ ] Update installation instructions
- [ ] Test integration (submodule or download script)
- [ ] Update CI/CD pipelines
- [ ] Announce migration to users

### Community

- [ ] Announce on Tesseract forums
- [ ] Post on relevant Reddit communities
- [ ] Share on social media
- [ ] Contact Kabardian language communities
- [ ] Update Tesseract wiki with KBD model link
- [ ] Notify academic collaborators

---

## Rollback Plan

If issues arise during migration:

1. **Keep original branch:**
   ```bash
   # The kbd directory remains in this branch
   git checkout claude/refactor-separate-component-011CUtFevBsVtdd3Hnczc15u
   ```

2. **Restore from backup:**
   ```bash
   # Before deletion, create backup branch
   git checkout -b kbd-backup
   ```

3. **Revert changes:**
   ```bash
   git revert <commit-hash>
   ```

---

## Timeline

**Week 1:**
- ✅ Prepare structure in current repository
- ✅ Create all documentation
- ✅ Add examples and tests
- 🔄 Review and commit

**Week 2:**
- Create new GitHub repository
- Extract and push files
- Setup CI/CD
- Create initial release

**Week 3:**
- Update zbze_ocr integration
- Test integration
- Update documentation

**Week 4:**
- Announce to community
- Monitor initial feedback
- Fix any issues

---

## Contact

Questions about migration:
- **GitHub Issues:** [zbze_ocr issues](https://github.com/YOUR_ORG/zbze_ocr/issues)
- **Email:** your-email@example.com

---

## References

- [Git Subtree Documentation](https://www.atlassian.com/git/tutorials/git-subtree)
- [GitHub Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**Status:** ✅ Ready for extraction

**Last Updated:** 2024-11-07
