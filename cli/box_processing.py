import click

from logic.cli_utils import get_files_to_process, generic_file_processor, validate_input_file_path_and_dir_params
from logic.box_processing import extract_box_images


@click.command()
@click.option('--input-file-path', '-i', default=None, help='Path to the input file')
@click.option('--input-dir', '-d', default=None, help='Path to the input directory')
@click.option('--output-dir', '-o', default=None, help='Output directory path for the split images')
@click.option('--file-mask', '-m', default='*.jpg', help='File mask')
def box_processing(input_file_path, input_dir, output_dir, file_mask):
    if not validate_input_file_path_and_dir_params(input_file_path, input_dir):
        return

    files_to_process = get_files_to_process(input_file_path, input_dir, file_mask)
    generic_file_processor(extract_box_images, files_to_process, output_dir, lang='kbd')


if __name__ == '__main__':
    box_processing()
