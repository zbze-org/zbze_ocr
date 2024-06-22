import logging
import os.path
import shlex
import shutil
import subprocess

import cv2
import numpy as np

from .cv.detectors import find_outliers_contours_on_image
from .cv.drawing import fill_contours_on_image
from .cv.io import load_grayscale_image, save_image
from .cv.modifications import apply_gaussian_blur_and_threshold

log = logging.getLogger(__name__)

SMOOTH_GAUSSIAN_BLUR_SIZE = (21, 5)


# def create_debug_images(contours, debug_dir, binary_image, mask, inverted_mask, contoured_image, output_image, ext):
#     os.makedirs(debug_dir, exist_ok=True)
#     for idx, contour in enumerate(contours, start=1):
#         contour_i = binary_image.copy()
#         cv2.drawContours(contour_i, [contour], -1, 255, thickness=cv2.FILLED)
#         save_image(contour_i, filepath=os.path.join(debug_dir, f'{idx:02d}_contour.{ext}'))
#     save_image(binary_image, filepath=os.path.join(debug_dir, f'00_f_binary_image.{ext}'))
#     save_image(mask, filepath=os.path.join(debug_dir, f'01_f_mask.{ext}'))
#     save_image(inverted_mask, filepath=os.path.join(debug_dir, f'02_f_inverted_mask.{ext}'))
#     save_image(contoured_image, filepath=os.path.join(debug_dir, f'03_f_contoured_image.{ext}'))
#     save_image(output_image, filepath=os.path.join(debug_dir, f'04_f_output_image.{ext}'))


def smooth_contours(file_path, output_dir, debug=True, **kwargs):
    gray_image = load_grayscale_image(file_path)
    _, binary_image = apply_gaussian_blur_and_threshold(gray_image=gray_image, blur_size=SMOOTH_GAUSSIAN_BLUR_SIZE)
    outliers_contours = find_outliers_contours_on_image(binary_image)

    mask = np.zeros_like(gray_image)
    cv2.drawContours(mask, outliers_contours, -1, 255, thickness=cv2.FILLED)
    inverted = cv2.bitwise_not(mask)
    inverted_contours = find_outliers_contours_on_image(inverted)

    output_image = fill_contours_on_image(gray_image, inverted_contours, inplace=False)

    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    smoothed_img_path = os.path.join(output_dir, f"{name}_smoothed{ext}")

    save_image(output_image, filepath=smoothed_img_path)
    return smoothed_img_path


def unpaper_processing(file_path, output_dir, debug=False, **kwargs):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy(file_path, output_dir)
        file_path = os.path.join(output_dir, os.path.basename(file_path))

    commands = [
        f"convert -density 300 -resize 2481x3507 -depth 8 -colorspace Gray -sharpen 0x2.7 {file_path} {file_path}",
        f"convert -black-threshold 35% -white-threshold 75% {file_path} {file_path}.pnm",
        f"unpaper --layout single --black-threshold 0.1 -ni 8 {file_path}.pnm {file_path}.unpaper.pnm",
        f"convert {file_path}.unpaper.pnm {file_path}"
    ]

    for cmd in commands:
        try:
            if debug:
                logging.debug(f"Executing command: {cmd}")

            result = subprocess.run(
                shlex.split(cmd),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )

            if debug and result.stderr:
                logging.debug(f"Command output: {result.stderr}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Error during command execution: {e.stderr}"
            logging.error(error_msg)
            raise Exception(error_msg)

    os.remove(f"{file_path}.pnm")
    os.remove(f"{file_path}.unpaper.pnm")