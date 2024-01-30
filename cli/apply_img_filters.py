import itertools

import click

from logic.apply_img_filters import apply_image_filters
from logic.cli_utils import generic_file_processor, get_files_to_process, validate_input_file_path_and_dir_params

DEFAULT_PROCESS_STEPS = [
    ("Brightness", 1.4),
    ("Contrast", 1.7),
    ("Sharpness", 1.4),
]


@click.command()
@click.option("--input-file-path", "-i", default=None, help="Path to the input file")
@click.option("--input-dir", "-d", default=None, help="Path to the input directory")
@click.option("--output-dir", "-o", default=None, help="Output directory path for the HTML file")
@click.option("--file-mask", "-m", default="*.jpg", help="File mask")
@click.option("--group", "-g", default=1, help="Group files")
def apply_img_filters(input_file_path, input_dir, output_dir, file_mask, group):
    if not validate_input_file_path_and_dir_params(input_file_path, input_dir):
        return

    files_to_process = get_files_to_process(input_file_path, input_dir, file_mask)
    process_steps_permutations = list(itertools.permutations(DEFAULT_PROCESS_STEPS))
    for process_steps_p in process_steps_permutations:
        generic_file_processor(
            process_function=apply_image_filters,
            files=files_to_process,
            output_dir=output_dir,
            processing_steps=process_steps_p,
            description_prefix=" ".join([f"{step[0]} {step[1]}" for step in process_steps_p]),
            group_steps=group,
        )


if __name__ == "__main__":
    apply_img_filters()
