import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import click

from cli import (
    apply_img_filters,
    box_processing,
    ocr_text_diff,
    rotate_img,
    run_tesseract_for_page,
    smooth_img,
    split_book_layout,
    split_pdf_to_jpeg,
    unpaper_img,
    standartize_img,
)


@click.group()
def cli():
    pass


cli.add_command(split_pdf_to_jpeg.split_pdf_to_jpeg)
cli.add_command(split_book_layout.split_book_layout)
cli.add_command(rotate_img.rotate_img)
cli.add_command(smooth_img.smooth_img)
cli.add_command(run_tesseract_for_page.run_tesseract_for_page)
cli.add_command(ocr_text_diff.compare_texts)
cli.add_command(box_processing.box_processing)
cli.add_command(unpaper_img.unpaper_img)
cli.add_command(apply_img_filters.apply_filters)
cli.add_command(standartize_img.standartize_img)


if __name__ == "__main__":
    cli()
