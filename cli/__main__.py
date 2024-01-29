import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import click

from cli import (
    split_pdf_to_jpeg,
    split_book_layout,
    rotate_img,
    smooth_img,
    apply_img_filters,
    run_tesseract_for_page,
    ocr_text_diff,
)


@click.group()
def cli():
    pass


cli.add_command(split_pdf_to_jpeg.split_pdf_to_jpeg)
cli.add_command(split_book_layout.split_book_layout)
cli.add_command(rotate_img.rotate_img)
cli.add_command(smooth_img.smooth_img)
cli.add_command(apply_img_filters.apply_img_filters)
cli.add_command(run_tesseract_for_page.run_tesseract_for_page)
cli.add_command(ocr_text_diff.compare_texts)

if __name__ == '__main__':
    cli()
