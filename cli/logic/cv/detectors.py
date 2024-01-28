import cv2

from . import const
from .filters import filter_contours_by_std, filter_largest_contours
from .modifications import apply_gaussian_blur


def detect_edges(gray_image, blur_size=const.GAUSSIAN_BLUR_SIZE):
    blurred_image = apply_gaussian_blur(gray_image=gray_image, blur_size=blur_size)
    edges = cv2.Canny(blurred_image, const.CANNY_THRESHOLD_LOW, const.CANNY_THRESHOLD_HIGH)
    return edges


def detect_lines(edges):
    lines = cv2.HoughLinesP(edges, const.HOUGH_LINES_RHO, const.HOUGH_LINES_THETA,
                            threshold=const.HOUGH_LINES_THRESHOLD,
                            minLineLength=const.HOUGH_LINES_MIN_LENGTH,
                            maxLineGap=const.HOUGH_LINES_MAX_GAP)
    return lines


def find_center_line(lines, width, height):
    if not lines:
        # Если линий нет, мы создаем линию-заглушку точно посередине изображения.
        # Эта линия охватывает от верха до низа изображения.
        fallback_coords = width // 2, 0, width // 2, height
        return fallback_coords
    else:
        center_line = min(lines, key=lambda l: abs(l[0][0] - width / 2))
        return center_line[0]


def find_contours(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def find_primary_contour(image):
    contours = find_contours(image)
    primary_contours = filter_largest_contours(contours,
                                               area_threshold=const.CONTOUR_AREA_THRESHOLD,
                                               largest_limit_count=const.NUM_LARGEST_CONTOURS)
    return primary_contours[0] if primary_contours else None


def correct_rotation_angle(angle):
    if abs(angle - 90) <= 3:
        return angle - 90
    elif abs(angle) <= 3:
        return angle
    else:
        return 0


def determine_rotation_angle(contour):
    hull = cv2.convexHull(contour, clockwise=True, returnPoints=True)
    rect = cv2.minAreaRect(hull)
    (center, (width, height), angle) = rect
    if width < height:
        angle += 90
    corrected_angle = correct_rotation_angle(angle)
    rotation_matrix = cv2.getRotationMatrix2D(center, corrected_angle, 1.0)
    return rotation_matrix, rect


def find_outliers_contours_on_image(image):
    contours = find_contours(image)
    outliers_contours = filter_contours_by_std(contours)
    return outliers_contours
