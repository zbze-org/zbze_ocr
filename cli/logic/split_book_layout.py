import os

import matplotlib.pyplot as plt

from .cv.detectors import detect_edges, detect_lines, find_center_line
from .cv.filters import filter_lines_near_center, filter_vertical_lines
from .cv.io import load_image, save_image
from .cv.modifications import convert_to_grayscale, split_image


def plot_images(original, detected_line, left, right):
    plt.figure(figsize=(20, 10))

    plt.subplot(1, 3, 1)
    plt.imshow(original, cmap="gray")
    plt.title("Original Image")

    plt.subplot(1, 3, 2)
    plt.imshow(detected_line, cmap="gray")
    plt.title("Detected Line")

    plt.subplot(2, 3, 3)
    plt.imshow(left, cmap="gray")
    plt.title("Left Part")

    plt.subplot(2, 3, 6)
    plt.imshow(right, cmap="gray")
    plt.title("Right Part")

    plt.show()


def split_book_processing(file_path, output_dir=None, plot=False, **kwargs):
    # Save the left and right images
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)

    # Load the image
    img = load_image(file_path)

    width, height = img.shape[0], img.shape[1]
    if width > height:
        orig_img_out_path = os.path.join(output_dir, base_name)
        save_image(img, filepath=orig_img_out_path)
        return

    # Preprocess the image
    edges = detect_edges(gray_image=convert_to_grayscale(img))
    # Detect lines in the image
    lines = detect_lines(edges)
    # Filter out the vertical lines
    vertical_lines = filter_vertical_lines(lines)
    # Filter out the lines near the center of the image
    lines_near_center = filter_lines_near_center(vertical_lines, img.shape[1])
    # Find the line closest to the center of the image
    center_line = find_center_line(lines_near_center, width=img.shape[1], height=img.shape[0])
    # Split the image into a left and right part based on the center line
    left_img, right_img = split_image(img, center_line)

    left_img_path = os.path.join(output_dir, f"{name}_left{ext}")
    right_img_path = os.path.join(output_dir, f"{name}_right{ext}")
    save_image(left_img, filepath=left_img_path)
    save_image(right_img, filepath=right_img_path)

    if plot:
        plot_images(img, edges, left_img, right_img)


# Example usage (uncomment and modify paths as needed):
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 3:
#         print("Usage: python split_book_layout.py <input_image> <output_dir>")
#         sys.exit(1)
#
#     img_filepath = sys.argv[1]
#     output_dir = sys.argv[2]
#     split_book_processing(img_filepath, output_dir=output_dir)
