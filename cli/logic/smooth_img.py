import logging
import os.path

import cv2
import numpy as np

from .cv.modifications import apply_gaussian_blur_and_threshold
from .cv.drawing import fill_contours_on_image
from .cv.detectors import find_outliers_contours_on_image
from .cv.io import load_grayscale_image, save_image

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


# @pysnooper.snoop()
def smooth_contours(file_path, output_dir, debug=True):
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
    smoothed_img_path = os.path.join(output_dir, f'{name}_smoothed{ext}')

    save_image(output_image, filepath=smoothed_img_path)
    return smoothed_img_path
