import click

from logic.smooth_img import unpaper_processing
from logic.cli_utils import generic_file_processor, get_files_to_process, validate_input_file_path_and_dir_params


@click.command()
@click.option("--input-file-path", "-i", default=None, help="Path to the input file")
@click.option("--input-dir", "-d", default=None, help="Path to the input directory")
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Output directory path for the split images",
)
@click.option("--file-mask", "-m", default="*.jpg", help="File mask")
def unpaper_img(input_file_path, input_dir, output_dir, file_mask):
    if not validate_input_file_path_and_dir_params(input_file_path, input_dir):
        return

    files_to_process = get_files_to_process(input_file_path, input_dir, file_mask)
    generic_file_processor(unpaper_processing, files_to_process, output_dir)


if __name__ == "__main__":
    unpaper_img()
