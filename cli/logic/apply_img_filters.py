import os
from enum import Enum

from PIL import Image

from .cv.modifications import convert_to_grayscale, apply_enhancement


class GroupEnum(Enum):
    NONE = 0
    BY_STEP = 1
    BY_PAGE = 2


def save_original_image(image, output_dir, file_name):
    orig_path = os.path.join(output_dir, f'orig.{file_name.split(".")[-1]}')
    image.save(orig_path)
    return orig_path


def save_image_debug_step(output_dir, file_name, processed_images):
    for index, (processed_image, step_name, step_factor) in enumerate(processed_images, start=1):
        processed_image.save(
            os.path.join(
                output_dir,
                f'{index:02d}_p_{step_name.lower()}_{step_factor}_{file_name}'
            )
        )


def create_output_file_path(output_dir, steps_to_name_prefix, file_name, group_steps):
    if group_steps == GroupEnum.BY_STEP.value:
        subdir = os.path.join(output_dir, steps_to_name_prefix)
        os.makedirs(subdir, exist_ok=True)
        output_file_path = os.path.join(subdir, file_name)
    elif group_steps == GroupEnum.BY_PAGE.value:
        subdir = os.path.join(output_dir, file_name)
        os.makedirs(subdir, exist_ok=True)
        output_file_path = os.path.join(subdir, f'{steps_to_name_prefix}.{file_name.split(".")[-1]}')
    else:
        output_file_path = os.path.join(
            output_dir,
            f'{steps_to_name_prefix}.{file_name}'
        )
    return output_file_path


def apply_image_filters(file_path, output_dir, processing_steps=None, group_steps=GroupEnum.NONE, debug=False,
                        **kwargs):
    path, file_name = os.path.split(file_path)
    os.makedirs(output_dir, exist_ok=True)

    image = Image.open(file_path)
    image = convert_to_grayscale(image)

    if not processing_steps:
        processing_steps = [
            ("Contrast", 1.0),
            ("Brightness", 1.0),
            ("Sharpness", 1.0)
        ]

    processed_images = []

    for step_name, step_factor in processing_steps:
        processed_image = apply_enhancement(image, step_name, step_factor)
        processed_images.append((processed_image.copy(), step_name, step_factor))
        image = processed_image

    if debug:
        debug_dir = f'{output_dir}__debug'
        os.makedirs(debug_dir, exist_ok=True)
        save_image_debug_step(debug_dir, file_name, processed_images)

    steps_to_name_prefix = '__'.join([f'{p[0]}{c}' for p, c in processing_steps])
    output_file_path = create_output_file_path(output_dir, steps_to_name_prefix, file_name, group_steps)
    image.save(output_file_path)

    return output_file_path
