import cv2
import numpy as np

from .const import ANGLE_TOLERANCE, WIDTH_RATIO


def sort_contours_by_area(filtered_contours, reverse=True):
    return sorted(filtered_contours, key=cv2.contourArea, reverse=reverse)


def find_outliers(areas, std_area):
    return [a for a in areas if abs(a - std_area) > std_area]


def filter_vertical_lines(lines):
    if lines is None:
        return []

    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        if 90 - ANGLE_TOLERANCE < np.abs(angle) < 90 + ANGLE_TOLERANCE:
            vertical_lines.append(line)
    return vertical_lines


def filter_lines_near_center(vertical_lines, width):
    filtered_lines = []
    for line in vertical_lines:
        x1, y1, x2, y2 = line[0]
        # определяем, две линии 1/3 и 2/3 ширины изображения, нас интересуют только линии между ними
        if width * WIDTH_RATIO < x1 < width * (1 - WIDTH_RATIO):
            filtered_lines.append(line)
    return filtered_lines


def calculate_areas_from_contours(contours):
    return [cv2.contourArea(cnt) for cnt in contours]


def calculate_areas_stats(areas):
    areas_mean = np.mean(areas)
    areas_std = np.std(areas)
    return areas_mean, areas_std


def filter_contours_by_std(contours, areas_std=None):
    if areas_std is None:
        areas = calculate_areas_from_contours(contours)
        _, areas_std = calculate_areas_stats(areas)

    return [cnt for cnt in contours if abs(cv2.contourArea(cnt) - areas_std) > areas_std]


def filter_contours_by_threshold(contours, area_threshold):
    return [cnt for cnt in contours if cv2.contourArea(cnt) > area_threshold]


def filter_largest_contours(contours, area_threshold, largest_limit_count=1):
    filtered_contours = filter_contours_by_threshold(contours, area_threshold)
    return sorted(filtered_contours, key=cv2.contourArea, reverse=True)[:largest_limit_count]
