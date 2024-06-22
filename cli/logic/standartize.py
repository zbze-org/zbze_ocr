import os

from PIL import Image

STANDARD_WIDTH = 2481


def standardize_img_width(file_path, output_dir=None, standard_width=STANDARD_WIDTH, *args, **kwargs):
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)

    try:
        image = Image.open(file_path)
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")
        return

    width, height = image.size

    if width < standard_width:
        # add white background to the left and right of the image
        new_image = Image.new('RGB', (standard_width, height), color='white')
        offset = (standard_width - width) // 2
        new_image.paste(image, (offset, 0))
    elif width > standard_width:
        # crop the image
        offset = (width - standard_width) // 2
        new_image = image.crop((offset, 0, offset + standard_width, height))
    else:
        new_image = image

    output_path = os.path.join(output_dir, os.path.basename(file_path))
    new_image.save(output_path)
