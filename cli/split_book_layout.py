import click

from logic.cli_utils import get_files_to_process, generic_file_processor, validate_input_file_path_and_dir_params
from logic.split_book_layout import split_book_processing


@click.command()
@click.option('--input-file-path', '-i', default=None, help='Path to the input file')
@click.option('--input-dir', '-d', default=None, help='Path to the input directory')
@click.option('--output-dir', '-o', default=None, help='Output directory path for the split images')
@click.option('--file-mask', '-m', default='*.jpg', help='File mask')
def split_book_layout(input_file_path, input_dir, output_dir, file_mask):
    if not validate_input_file_path_and_dir_params(input_file_path, input_dir):
        return

    files_to_process = get_files_to_process(input_file_path, input_dir, file_mask)
    generic_file_processor(split_book_processing, files_to_process, output_dir)


if __name__ == '__main__':
    split_book_layout()
