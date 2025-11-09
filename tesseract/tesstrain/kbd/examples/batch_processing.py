#!/usr/bin/env python3
"""
Batch processing examples for Tesseract KBD language model.

This script demonstrates how to efficiently process multiple images
or PDF files using parallel processing.
"""

import pytesseract
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
from tqdm import tqdm
import json
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_single_image(image_path: Path, lang: str = 'kbd', config: str = '') -> Tuple[Path, str, bool]:
    """
    Process a single image file.

    Args:
        image_path: Path to image file
        lang: Language code
        config: Tesseract config string

    Returns:
        Tuple of (path, text, success)
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        return (image_path, text, True)
    except Exception as e:
        logger.error(f"Error processing {image_path}: {e}")
        return (image_path, str(e), False)


def batch_process_images(
    input_dir: str,
    output_dir: str,
    lang: str = 'kbd',
    config: str = '',
    max_workers: int = 4,
    file_extensions: List[str] = None
) -> dict:
    """
    Process multiple images in parallel.

    Args:
        input_dir: Directory containing images
        output_dir: Directory to save text files
        lang: Language code
        config: Tesseract config string
        max_workers: Number of parallel workers
        file_extensions: List of file extensions to process

    Returns:
        Dictionary with processing statistics
    """
    if file_extensions is None:
        file_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect all image files
    image_files = []
    for ext in file_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))

    if not image_files:
        logger.warning(f"No image files found in {input_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}

    logger.info(f"Found {len(image_files)} images to process")

    # Statistics
    stats = {'total': len(image_files), 'success': 0, 'failed': 0}
    failed_files = []

    # Process images in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_single_image, img, lang, config): img
            for img in image_files
        }

        # Process results as they complete
        with tqdm(total=len(image_files), desc="Processing images") as pbar:
            for future in as_completed(futures):
                img_path, text, success = future.result()

                if success:
                    # Save text to file
                    output_file = output_path / f"{img_path.stem}.txt"
                    output_file.write_text(text, encoding='utf-8')
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
                    failed_files.append(str(img_path))

                pbar.update(1)

    # Save processing report
    report = {
        'statistics': stats,
        'failed_files': failed_files
    }

    report_file = output_path / 'processing_report.json'
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    logger.info(f"Processing complete: {stats['success']} success, {stats['failed']} failed")
    return stats


def batch_process_with_preprocessing(
    input_dir: str,
    output_dir: str,
    lang: str = 'kbd',
    apply_preprocessing: bool = True
) -> dict:
    """
    Batch process images with optional preprocessing.

    Args:
        input_dir: Directory containing images
        output_dir: Directory to save results
        lang: Language code
        apply_preprocessing: Whether to apply image preprocessing

    Returns:
        Processing statistics
    """
    import cv2
    import numpy as np

    def preprocess_image(img_path: Path) -> Optional[np.ndarray]:
        """Apply preprocessing to improve OCR quality."""
        try:
            img = cv2.imread(str(img_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            return thresh
        except Exception as e:
            logger.error(f"Preprocessing error for {img_path}: {e}")
            return None

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect images
    image_files = list(input_path.glob('*.jpg')) + list(input_path.glob('*.png'))

    stats = {'total': len(image_files), 'success': 0, 'failed': 0}

    for img_file in tqdm(image_files, desc="Processing with preprocessing"):
        try:
            if apply_preprocessing:
                processed = preprocess_image(img_file)
                if processed is None:
                    stats['failed'] += 1
                    continue
                img = Image.fromarray(processed)
            else:
                img = Image.open(img_file)

            text = pytesseract.image_to_string(img, lang=lang, config='--psm 1')

            output_file = output_path / f"{img_file.stem}.txt"
            output_file.write_text(text, encoding='utf-8')
            stats['success'] += 1

        except Exception as e:
            logger.error(f"Error processing {img_file}: {e}")
            stats['failed'] += 1

    return stats


def batch_convert_pdf_to_text(
    input_dir: str,
    output_dir: str,
    lang: str = 'kbd',
    max_workers: int = 2
) -> dict:
    """
    Convert multiple PDF files to text.

    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save text files
        lang: Language code
        max_workers: Number of parallel workers

    Returns:
        Processing statistics
    """
    try:
        import ocrmypdf
    except ImportError:
        logger.error("ocrmypdf not installed. Install with: pip install ocrmypdf")
        return {'total': 0, 'success': 0, 'failed': 0}

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_path.glob('*.pdf'))

    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}

    stats = {'total': len(pdf_files), 'success': 0, 'failed': 0}

    def process_pdf(pdf_path: Path) -> Tuple[bool, str]:
        """Process a single PDF."""
        try:
            output_file = output_path / pdf_path.name
            ocrmypdf.ocr(
                pdf_path,
                output_file,
                language=lang,
                force_ocr=True,
                deskew=True,
                clean=True
            )
            return (True, str(pdf_path))
        except Exception as e:
            return (False, str(pdf_path))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, pdf) for pdf in pdf_files]

        with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
            for future in as_completed(futures):
                success, path = future.result()
                if success:
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
                pbar.update(1)

    logger.info(f"PDF processing complete: {stats['success']} success, {stats['failed']} failed")
    return stats


def main():
    """Demonstrate batch processing examples."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python batch_processing.py <input_dir> <output_dir> [max_workers]")
        print("\nExamples:")
        print("  python batch_processing.py ./images ./output 4")
        print("  python batch_processing.py ./pdfs ./texts 2")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    # Check if processing images or PDFs
    input_path = Path(input_dir)
    has_images = any(input_path.glob('*.jpg')) or any(input_path.glob('*.png'))
    has_pdfs = any(input_path.glob('*.pdf'))

    if has_images:
        logger.info("Processing images...")
        stats = batch_process_images(input_dir, output_dir, max_workers=max_workers)
        print(f"\nResults: {stats}")

    if has_pdfs:
        logger.info("Processing PDFs...")
        stats = batch_convert_pdf_to_text(input_dir, output_dir, max_workers=max_workers)
        print(f"\nResults: {stats}")


if __name__ == '__main__':
    main()
