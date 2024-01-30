import os

import cv2
import matplotlib.pyplot as plt

from .cv.detectors import determine_rotation_angle, find_primary_contour
from .cv.drawing import draw_circle_on_image, draw_contours_on_image
from .cv.io import load_image, save_image
from .cv.modifications import apply_gaussian_blur_and_threshold, apply_rotate, convert_to_grayscale

ROTATE_GAUSSIAN_BLUR_SIZE = (51, 51)


def draw_lines_on_image(image, box):
    drawn_image = image.copy()
    draw_contour(drawn_image, box)
    draw_lines(drawn_image, box)
    return drawn_image


def draw_contour(image, box):
    contour_color = (255, 0, 0)  # Контур: Синий
    circle_color = (0, 255, 0)  # Круги: Зеленый
    draw_contours_on_image(image, [box], color=contour_color, thickness=5)
    for x, y in box:
        draw_circle_on_image(image, (x, y), 10, color=circle_color, thickness=5, inplace=True)


def draw_lines(image, box):
    line_mapping = {
        (0, 1): (0, 255, 0),  # Верхняя горизонтальная линия: Зеленый
        (1, 2): (0, 255, 0),  # Правая вертикальная линия: Зеленый
        (2, 3): (0, 255, 0),  # Нижняя горизонтальная линия: Зеленый
        (3, 0): (0, 255, 0),  # Левая вертикальная линия: Зеленый
        (0, 2): (0, 0, 255),  # Главная диагональная линия: Красный
        (1, 3): (0, 0, 255),  # Побочная диагональная линия: Красный
    }

    for (idx1, idx2), color in line_mapping.items():
        cv2.line(image, tuple(box[idx1]), tuple(box[idx2]), color, 2)


def rotate_image(file_path, output_dir, plot=False):
    image = load_image(file_path)
    blurred_image, binary_image = apply_gaussian_blur_and_threshold(
        gray_image=convert_to_grayscale(image), blur_size=ROTATE_GAUSSIAN_BLUR_SIZE
    )
    primary_contour = find_primary_contour(binary_image)

    if primary_contour is not None:
        rotation_matrix, rect = determine_rotation_angle(primary_contour)
        rotated_image, rotated_box = apply_rotate(image, rotation_matrix=rotation_matrix, rect=rect)
        drawn_image = draw_lines_on_image(rotated_image, rotated_box)

        if plot:
            show_rotation_steps(image, blurred_image, rotated_image, drawn_image)

        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        rotated_img_path = os.path.join(output_dir, f"{name}_rotated{ext}")

        save_image(rotated_image, filepath=rotated_img_path)
        return rotated_image


def show_image(subplot, title, image):
    subplot.imshow(image, cmap="gray")
    subplot.set_title(title)


def show_rotation_steps(original, blur, rotated, drawn):
    fig, axs = plt.subplots(1, 4, figsize=(20, 20))
    show_image(axs[0], "Исходное изображение", original)
    show_image(axs[1], "Бинаризация и размытие", blur)
    show_image(axs[2], "Повернутое изображение", rotated)
    show_image(axs[3], "Повернутое изображение с линиями", drawn)
    plt.show()
