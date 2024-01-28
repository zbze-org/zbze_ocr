import cv2
import numpy as np
from PIL import ImageEnhance

from .const import GAUSSIAN_BLUR_SIZE


class ImageNotGrayscaleError(Exception):
    pass


def check_image_is_grayscale(image):
    if not image.ndim == 2:
        raise ImageNotGrayscaleError("Image is not grayscale")


def convert_to_grayscale(image):
    if isinstance(image, np.ndarray):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image.convert("L")

    return image


def apply_blur(gray_image, blur_size=(20, 5)):
    return cv2.blur(gray_image, blur_size)


def apply_gaussian_blur(gray_image, blur_size=GAUSSIAN_BLUR_SIZE):
    return cv2.GaussianBlur(gray_image, blur_size, 0)


def apply_threshold(gray_image):
    _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_TRIANGLE)
    return binary_image


def apply_gaussian_blur_and_threshold(gray_image, blur_size=GAUSSIAN_BLUR_SIZE):
    check_image_is_grayscale(gray_image)
    blurred_image = apply_gaussian_blur(gray_image=gray_image, blur_size=blur_size)
    binary_image = apply_threshold(blurred_image)
    return blurred_image, binary_image


def split_image(image, line):
    x1, y1, x2, y2 = line
    left_image = image[:, :x1]
    right_image = image[:, x1:]
    return left_image, right_image


def apply_enhancement(image, enhancement_name, enhancement_factor):
    enhancer = getattr(ImageEnhance, enhancement_name)(image)
    processed_image = enhancer.enhance(enhancement_factor)
    return processed_image


def apply_rotate(orig_image, rotation_matrix, rect):
    rotated_image = cv2.warpAffine(orig_image, rotation_matrix, orig_image.shape[1::-1], flags=cv2.INTER_LINEAR)
    rotated_box = cv2.boxPoints(rect).astype('int')
    return rotated_image, rotated_box
