import os
import subprocess

import click


@click.command()
@click.option('--input-file-path', '-i', default=None, help='Path to the input file')
@click.option('--output-dir', '-o', default=None, help='Output directory path for the processed images')
def split_pdf_to_jpeg(input_file_path, output_dir):
    if input_file_path is None:
        click.echo("Please provide an input file path.")
        return

    if output_dir is None:
        click.echo("Please provide an output directory path.")
        return

    file_name = os.path.basename(input_file_path)
    output_file_path = os.path.join(output_dir, file_name)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_file_path, exist_ok=True)

    # Run the pdftoppm command
    subprocess.run(["pdftoppm", "-jpeg", "-progress", input_file_path, output_file_path])


if __name__ == '__main__':
    split_pdf_to_jpeg()
