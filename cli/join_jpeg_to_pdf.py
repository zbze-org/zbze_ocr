import os
import click
from PIL import Image
from pypdf import PdfWriter
from io import BytesIO
from tqdm import tqdm


@click.command()
@click.option("--input-dir", "-d", help="Path to the input directory")
@click.option(
    "--output-file-path",
    "-o",
    help="Output file path for the joined PDF",
)
def join_images_to_pdf(input_dir, output_file_path):
    if input_dir is None:
        click.echo("Please provide an input directory path.")
        return

    if output_file_path is None:
        click.echo("Please provide an output file path.")
        return

    input_image_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    pdf_writer = PdfWriter()

    with tqdm(total=len(input_image_files), desc="Processing images") as pbar:
        for image_file in input_image_files:
            image_path = os.path.join(input_dir, image_file)

            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PDF')
                img_byte_arr.seek(0)

                # Append the page bytes to the PDF
                pdf_writer.append(img_byte_arr)

            pbar.update(1)

    # Write the PDF to the output file
    with open(output_file_path, 'wb') as output_file:
        pdf_writer.write(output_file)

    click.echo(f"PDF created successfully: {output_file_path}")


if __name__ == "__main__":
    join_images_to_pdf()