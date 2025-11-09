#!/usr/bin/env python3
"""
OCRmyPDF usage examples for Kabardian language.

This script demonstrates how to use OCRmyPDF with the KBD language model
for adding searchable text layers to PDF documents.
"""

import sys
from pathlib import Path
import logging

try:
    import ocrmypdf
    from ocrmypdf import PdfMergeFailedError, MissingDependencyError
except ImportError:
    print("Error: ocrmypdf not installed. Install with:")
    print("  pip install ocrmypdf")
    sys.exit(1)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def basic_ocr_pdf(input_pdf: str, output_pdf: str, lang: str = 'kbd') -> bool:
    """
    Add OCR text layer to a PDF with default settings.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF
        lang: Language code

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing {input_pdf}...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language=lang
        )
        logger.info(f"Saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def high_quality_ocr(input_pdf: str, output_pdf: str) -> bool:
    """
    OCR with high quality settings and image processing.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF

    Returns:
        True if successful
    """
    try:
        logger.info("Processing with high quality settings...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            deskew=True,              # Fix page rotation
            clean=True,               # Clean up page images
            remove_background=False,  # Keep background
            rotate_pages=True,        # Auto-rotate pages
            optimize=3,               # Maximum optimization
            output_type='pdfa',       # PDF/A format
            jobs=4                    # Parallel processing
        )
        logger.info(f"High quality PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def fast_ocr(input_pdf: str, output_pdf: str) -> bool:
    """
    Fast OCR with minimal processing for quick results.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF

    Returns:
        True if successful
    """
    try:
        logger.info("Processing with fast settings...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            fast_web_view=1,  # Optimize for web viewing
            optimize=1,       # Light optimization
            jobs=4
        )
        logger.info(f"Fast PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def ocr_with_custom_config(input_pdf: str, output_pdf: str, config_file: str) -> bool:
    """
    OCR with custom Tesseract configuration file.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF
        config_file: Path to Tesseract config file

    Returns:
        True if successful
    """
    try:
        logger.info(f"Processing with custom config: {config_file}")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            tesseract_config=config_file
        )
        logger.info(f"PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def force_ocr_all_pages(input_pdf: str, output_pdf: str) -> bool:
    """
    Force OCR on all pages, even if they already contain text.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF

    Returns:
        True if successful
    """
    try:
        logger.info("Forcing OCR on all pages...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            force_ocr=True,    # OCR even if text exists
            redo_ocr=True      # Replace existing OCR
        )
        logger.info(f"Forced OCR PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def skip_existing_text(input_pdf: str, output_pdf: str) -> bool:
    """
    Skip pages that already contain text.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF

    Returns:
        True if successful
    """
    try:
        logger.info("Skipping pages with existing text...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            skip_text=True  # Skip pages with text
        )
        logger.info(f"Selective OCR PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def ocr_with_image_preprocessing(input_pdf: str, output_pdf: str) -> bool:
    """
    OCR with advanced image preprocessing for poor quality scans.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF

    Returns:
        True if successful
    """
    try:
        logger.info("Processing with advanced preprocessing...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            deskew=True,
            clean=True,
            clean_final=True,
            remove_background=True,
            oversample=300,        # Increase DPI to 300
            rotate_pages=True,
            rotate_pages_threshold=2.0
        )
        logger.info(f"Preprocessed PDF saved to {output_pdf}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def ocr_with_sidecar_text(input_pdf: str, output_pdf: str, sidecar: str) -> bool:
    """
    OCR and save extracted text to a separate sidecar file.

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output PDF
        sidecar: Path to text sidecar file

    Returns:
        True if successful
    """
    try:
        logger.info("Processing with sidecar text output...")
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language='kbd',
            sidecar=sidecar  # Save text to separate file
        )
        logger.info(f"PDF saved to {output_pdf}")
        logger.info(f"Text saved to {sidecar}")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def batch_process_directory(input_dir: str, output_dir: str) -> dict:
    """
    Process all PDFs in a directory.

    Args:
        input_dir: Directory containing input PDFs
        output_dir: Directory for output PDFs

    Returns:
        Dictionary with processing statistics
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_path.glob('*.pdf'))

    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}

    stats = {'total': len(pdf_files), 'success': 0, 'failed': 0}
    failed_files = []

    for pdf_file in pdf_files:
        output_file = output_path / pdf_file.name
        logger.info(f"Processing {pdf_file.name}...")

        try:
            ocrmypdf.ocr(
                str(pdf_file),
                str(output_file),
                language='kbd',
                deskew=True,
                clean=True,
                rotate_pages=True,
                jobs=4
            )
            stats['success'] += 1
            logger.info(f"✓ {pdf_file.name}")
        except Exception as e:
            stats['failed'] += 1
            failed_files.append(pdf_file.name)
            logger.error(f"✗ {pdf_file.name}: {e}")

    logger.info(f"\nProcessing complete:")
    logger.info(f"  Total: {stats['total']}")
    logger.info(f"  Success: {stats['success']}")
    logger.info(f"  Failed: {stats['failed']}")

    if failed_files:
        logger.info(f"\nFailed files: {', '.join(failed_files)}")

    return stats


def main():
    """Demonstrate OCRmyPDF usage examples."""
    if len(sys.argv) < 3:
        print("Usage: python ocrmypdf_usage.py <command> <input_pdf> [output_pdf]")
        print("\nCommands:")
        print("  basic      - Basic OCR with default settings")
        print("  high       - High quality OCR with preprocessing")
        print("  fast       - Fast OCR for quick results")
        print("  force      - Force OCR on all pages")
        print("  skip       - Skip pages with existing text")
        print("  preprocess - Advanced image preprocessing")
        print("  sidecar    - Save text to sidecar file")
        print("  batch      - Process directory of PDFs")
        print("\nExamples:")
        print("  python ocrmypdf_usage.py basic input.pdf output.pdf")
        print("  python ocrmypdf_usage.py high scan.pdf clean.pdf")
        print("  python ocrmypdf_usage.py batch ./input_pdfs ./output_pdfs")
        sys.exit(1)

    command = sys.argv[1]
    input_pdf = sys.argv[2]

    if command == 'batch':
        output_dir = sys.argv[3] if len(sys.argv) > 3 else './output'
        batch_process_directory(input_pdf, output_dir)
        return

    output_pdf = sys.argv[3] if len(sys.argv) > 3 else 'output.pdf'

    commands = {
        'basic': lambda: basic_ocr_pdf(input_pdf, output_pdf),
        'high': lambda: high_quality_ocr(input_pdf, output_pdf),
        'fast': lambda: fast_ocr(input_pdf, output_pdf),
        'force': lambda: force_ocr_all_pages(input_pdf, output_pdf),
        'skip': lambda: skip_existing_text(input_pdf, output_pdf),
        'preprocess': lambda: ocr_with_image_preprocessing(input_pdf, output_pdf),
        'sidecar': lambda: ocr_with_sidecar_text(
            input_pdf, output_pdf, output_pdf.replace('.pdf', '.txt')
        )
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)

    success = commands[command]()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
