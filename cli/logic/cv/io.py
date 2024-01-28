import cv2


def load_image(filepath):
    return cv2.imread(filepath)


def load_grayscale_image(file_path):
    return cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)


def save_image(image, filepath):
    cv2.imwrite(filepath, image)
