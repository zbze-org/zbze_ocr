import concurrent
import hashlib
import os
import random
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

from .const import FONT_SIZE, TEXT_LINES_MAX_COUNT


def calculate_image_size(text, img_font):
    temp_image = Image.new("RGB", (1, 1), color=(255, 255, 255))
    temp_draw = ImageDraw.Draw(temp_image)

    text_bbox = temp_draw.textbbox((0, 0), text, font=img_font)

    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    return text_width, text_height


def draw_text(text, img_font, background=(255, 255, 255)):
    padding = img_font.size // 2
    text_width, text_height = calculate_image_size(text, img_font)
    image = Image.new("RGB", (text_width + padding, text_height + padding), color=background)
    draw = ImageDraw.Draw(image)
    draw.text((0, -img_font.size / 10), text, font=img_font, fill=(0, 0, 0))
    return image


def apply_aging_effect(image, aging_factor=(0.5, 0.1, 0.005)):
    image = image.convert("L")
    black_factor, gray_factor, white_factor = aging_factor

    pixel_data = list(image.getdata())
    for i in range(len(pixel_data)):
        pixel_value = pixel_data[i]

        if pixel_value < 85:
            if random.random() > black_factor:
                continue
            new_value = pixel_value - random.randint(0, 15) * 10
        elif pixel_value < 170:
            if random.random() > gray_factor:
                continue
            new_value = pixel_value + random.randint(-15, 15) * 10
        else:
            if random.random() > white_factor:
                continue
            new_value = pixel_value - random.randint(0, 15) * 10

        pixel_data[i] = new_value

    image.putdata(pixel_data)
    return image


def generate_file_name(text, img_font):
    text_md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
    font_name = img_font.path.split("/")[-1].split(".")[0]
    font_md5 = hashlib.md5(font_name.encode("utf-8")).hexdigest()
    return f"{font_md5}_{text_md5}", font_name, text_md5


class GroupByEnum(Enum):
    NO_GROUP = 0
    FONT = 1
    TEXT = 2


class AgeingFactorEnum(Enum):
    LOW = (0.5, 0.1, 0.005)
    MEDIUM = (0.5, 0.3, 0.02)
    HIGH = (0.5, 0.4, 0.05)


def generate_image(
    text,
    img_font,
    output_dir,
    group_by=GroupByEnum.NO_GROUP,
    group_by_factor=0,
    aging_factor=(0.3, 0.3, 0.01),
):
    file_name, font_name, text_name = generate_file_name(text, img_font)

    if group_by == GroupByEnum.FONT:
        prefix_dir = f"by_font/{font_name}"
    elif group_by == GroupByEnum.TEXT:
        if group_by_factor == 0:
            prefix_dir = f"by_text/{text_name[0]}"
        else:
            prefix_dir = str(int(text_name[0], 16) % group_by_factor)
    else:
        prefix_dir = ""

    os.makedirs(os.path.join(output_dir, prefix_dir), exist_ok=True)
    if os.path.exists(os.path.join(output_dir, prefix_dir, f"{file_name}.png")):
        return

    image = draw_text(text, img_font)
    image = apply_aging_effect(image, aging_factor)
    image.save(os.path.join(output_dir, prefix_dir, f"{file_name}.png"))
    with open(os.path.join(output_dir, prefix_dir, f"{file_name}.gt.txt"), "w") as f:
        f.write(text)

    return os.path.join(output_dir, prefix_dir)


def load_fonts(font_dir, font_size=FONT_SIZE):
    fonts_files = [f"{font_dir}/{font}" for font in sorted(os.listdir(font_dir)) if font.endswith(".ttf")]
    fonts = []
    for font_f in fonts_files:
        try:
            img_font = ImageFont.truetype(font_f, font_size)
            fonts.append(img_font)
        except OSError:
            print(f"Error loading font {font_f}")
            continue

    return fonts


def load_text(text_filepath, max_lines=TEXT_LINES_MAX_COUNT, min_line_len=20, max_line_len=120):
    with open(text_filepath, "r") as f:
        lines = f.read().split("\n")

    text_lines = list(set([line for line in lines if min_line_len < len(line) < max_line_len]))
    text_lines = text_lines[:max_lines]
    random.shuffle(text_lines)
    return text_lines


def generate_images(
    text_filepath,
    font_dir,
    output_dir,
    font_size=FONT_SIZE,
    max_lines=TEXT_LINES_MAX_COUNT,
    par_factor=4,
    group_by=GroupByEnum.NO_GROUP,
    group_by_factor=0,
    font_per_line=5,
):
    text_lines = load_text(text_filepath, max_lines=max_lines)
    fonts = load_fonts(font_dir, font_size=font_size)

    output_subdirs = set()

    with tqdm(total=font_per_line * len(text_lines)) as pbar, ThreadPoolExecutor(max_workers=par_factor) as executor:
        futures = [
            executor.submit(
                generate_image,
                text=text_line,
                img_font=random.choice(fonts),
                output_dir=output_dir,
                group_by=group_by,
                group_by_factor=group_by_factor,
            )
            for text_line in text_lines
            for _ in range(font_per_line)
        ]
        count = 0
        for future in concurrent.futures.as_completed(futures):
            if count % 100 == 0:
                pbar.update(100)
            try:
                result = future.result()
                if result:
                    output_subdirs.add(result)

                count += 1
            except Exception as e:
                print(f"Ошибка: {e}")

    return output_subdirs
