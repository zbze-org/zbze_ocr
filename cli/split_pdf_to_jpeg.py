import os

import click
import fitz
from PIL import Image
from tqdm import tqdm


def split_pdf_to_jpeg_processing(input_file_path, output_dir, dpi=300):
    os.makedirs(output_dir, exist_ok=True)

    pdf_document = fitz.open(input_file_path)
    total_pages = len(pdf_document)

    with tqdm(total=total_pages, desc="Converting PDF to JPEG", unit="page") as pbar:
        for page_number in range(total_pages):
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))

            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_path = os.path.join(output_dir, f"page_{page_number + 1:03d}.jpg")
            image.save(image_path, "JPEG", quality=100)

            pbar.update(1)

    pdf_document.close()


@click.command()
@click.option("--input-file-path", "-i", default=None, help="Path to the input file")
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Output directory path for the processed images",
)
def split_pdf_to_jpeg(input_file_path, output_dir):
    if input_file_path is None:
        click.echo("Please provide an input file path.")
        return

    if output_dir is None:
        click.echo("Please provide an output directory path.")
        return

    split_pdf_to_jpeg_processing(input_file_path, output_dir)


if __name__ == "__main__":
    split_pdf_to_jpeg()
