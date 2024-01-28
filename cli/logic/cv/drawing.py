import cv2


def draw_contours_on_image(image, contours, color=255, thickness=10, inplace=True):
    draw_image = image if inplace else image.copy()
    cv2.drawContours(draw_image, contours, -1, color, thickness=thickness)
    return draw_image


def draw_circle_on_image(image, center, radius, color=255, thickness=10, inplace=True):
    draw_image = image if inplace else image.copy()
    cv2.circle(draw_image, center=center, radius=radius, color=color, thickness=thickness)
    return draw_image


def fill_contours_on_image(image, contours, color=255, inplace=True):
    draw_image = image if inplace else image.copy()
    cv2.drawContours(draw_image, contours, -1, color, thickness=cv2.FILLED)
    return draw_image
