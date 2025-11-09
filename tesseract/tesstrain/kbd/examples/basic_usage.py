#!/usr/bin/env python3
"""
Basic usage examples for Tesseract KBD language model.

This script demonstrates simple OCR operations using pytesseract
with the Kabardian language model.
"""

import pytesseract
from PIL import Image


def basic_ocr(image_path: str, lang: str = 'kbd') -> str:
    """
    Perform basic OCR on an image.

    Args:
        image_path: Path to the image file
        lang: Language code (default: 'kbd')

    Returns:
        Extracted text as string
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    return text


def ocr_with_config(image_path: str, psm: int = 3) -> str:
    """
    OCR with custom page segmentation mode.

    Args:
        image_path: Path to the image file
        psm: Page segmentation mode (0-13)

    Returns:
        Extracted text as string
    """
    image = Image.open(image_path)
    config = f'--psm {psm}'
    text = pytesseract.image_to_string(image, lang='kbd', config=config)
    return text


def ocr_with_confidence(image_path: str) -> list:
    """
    Get OCR results with confidence scores.

    Args:
        image_path: Path to the image file

    Returns:
        List of tuples (word, confidence)
    """
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, lang='kbd', output_type=pytesseract.Output.DICT)

    results = []
    for i, word in enumerate(data['text']):
        if word.strip():  # Skip empty strings
            confidence = int(data['conf'][i])
            results.append((word, confidence))

    return results


def ocr_with_bounding_boxes(image_path: str) -> list:
    """
    Get OCR results with bounding box coordinates.

    Args:
        image_path: Path to the image file

    Returns:
        List of tuples (word, x, y, width, height, confidence)
    """
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, lang='kbd', output_type=pytesseract.Output.DICT)

    results = []
    for i, word in enumerate(data['text']):
        if word.strip():
            x = data['left'][i]
            y = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]
            confidence = int(data['conf'][i])
            results.append((word, x, y, width, height, confidence))

    return results


def main():
    """Demonstrate basic usage examples."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python basic_usage.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Example 1: Basic OCR
    print("=" * 50)
    print("Example 1: Basic OCR")
    print("=" * 50)
    text = basic_ocr(image_path)
    print(text)

    # Example 2: OCR with custom PSM
    print("\n" + "=" * 50)
    print("Example 2: OCR with PSM=6 (single block)")
    print("=" * 50)
    text = ocr_with_config(image_path, psm=6)
    print(text)

    # Example 3: OCR with confidence scores
    print("\n" + "=" * 50)
    print("Example 3: Words with confidence scores")
    print("=" * 50)
    results = ocr_with_confidence(image_path)
    for word, conf in results[:10]:  # Show first 10 words
        print(f"{word:<20} {conf:>3}%")

    # Example 4: OCR with bounding boxes
    print("\n" + "=" * 50)
    print("Example 4: Words with bounding boxes")
    print("=" * 50)
    boxes = ocr_with_bounding_boxes(image_path)
    for word, x, y, w, h, conf in boxes[:5]:  # Show first 5 words
        print(f"{word:<15} x={x:<4} y={y:<4} w={w:<3} h={h:<3} conf={conf}%")


if __name__ == '__main__':
    main()
