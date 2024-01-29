import hashlib
import os
from dataclasses import dataclass

import cv2
import pytesseract

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESSERACT_CONFIG = os.path.join(PROJECT_DIR, 'tesseract', 'kdb.base.config.txt')


@dataclass
class BoxCoordinates:
    left: int
    top: int
    width: int
    height: int


@dataclass
class TesseractBoxData:
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int

    confidence: float
    text: str

    coordinates: BoxCoordinates

    box_name: str
    box_name_hash: str
    is_line: bool


def tesseract_df_2_box_data(row):
    box_coordinates = BoxCoordinates(
        left=row.left,
        top=row.top,
        width=row.width,
        height=row.height
    )
    text_hash = hashlib.md5(row.text.encode('utf-8')).hexdigest()
    box_name = f'{row.page_num}_{row.block_num}_{row.par_num}_{row.line_num}_{row.word_num}_{text_hash}'
    box_name_hash = hashlib.md5(box_name.encode('utf-8')).hexdigest()

    box_data = TesseractBoxData(
        level=row.level,
        page_num=row.page_num,
        block_num=row.block_num,
        par_num=row.par_num,
        line_num=row.line_num,
        word_num=row.word_num,
        confidence=row.conf,
        text=row.text,
        coordinates=box_coordinates,
        is_line=False,

        box_name=box_name,
        box_name_hash=box_name_hash
    )

    return box_data


def grouped_tesseract_df_2_box_data(group_name, group_data):
    box_coords = BoxCoordinates(
        left=group_data['left'].min(),
        top=group_data['top'].min(),
        width=group_data['width'].max(),
        height=group_data['height'].max(),
    )
    text = ' '.join(group_data['text'].tolist())
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    box_name = f'group_{group_name}_{text_hash}'
    box_name_hash = hashlib.md5(box_name.encode('utf-8')).hexdigest()

    box_data = TesseractBoxData(
        block_num=group_data['block_num'].mean(),
        page_num=group_data['page_num'].mean(),
        line_num=group_data['line_num'].mean(),
        level=group_data['level'].mean(),
        par_num=group_data['par_num'].mean(),
        word_num=group_data['word_num'].mean(),
        confidence=None,
        text=text,
        coordinates=box_coords,
        is_line=True,

        box_name=box_name,
        box_name_hash=box_name_hash
    )

    return box_data

def create_cropped_image(image, box_data, output_dir):
    cropped = image[
              box_data.coordinates.top:box_data.coordinates.top + box_data.coordinates.height,
              box_data.coordinates.left:box_data.coordinates.left + box_data.coordinates.width,
              ]

    cv2.imwrite(os.path.join(output_dir, f'{box_data.box_name}.jpg'), cropped)
    with open(os.path.join(output_dir, f'{box_data.box_name}.txt'), 'w') as f:
        f.write(box_data.text)


def process_df_by_box(image, result_df, output_dir):
    for row in result_df.itertuples():
        box_data = tesseract_df_2_box_data(row)
        create_cropped_image(image, box_data=box_data, output_dir=output_dir)


def process_df_by_line(image, result_df, output_dir):
    result_df['text'].fillna('', inplace=True)
    grouped_df = result_df.groupby(['block_num', 'par_num', 'line_num'])
    lines_box_data_map = {}
    for i, (group_name, group_data) in enumerate(grouped_df):
        # box processing
        process_df_by_box(image, group_data, output_dir=output_dir)

        # prepare for line processing
        box_data = grouped_tesseract_df_2_box_data(group_name=group_name, group_data=group_data)
        lines_box_data_map[group_name] = box_data

    combined_text_df = grouped_df['text'].apply(lambda x: ' '.join(x)).reset_index()
    combined_text_df.index = combined_text_df.index + 1

    for row in combined_text_df.itertuples():
        line = row.Index
        line_box_data = lines_box_data_map[(row.block_num, row.par_num, row.line_num)]
        line_box_data.box_name = f'grouped.{row.block_num}.{row.par_num}.{row.line_num}.line.{line}'
        line_box_data.box_name_hash = hashlib.md5(line_box_data.box_name.encode('utf-8')).hexdigest()
        # line processing
        create_cropped_image(image, box_data=line_box_data, output_dir=output_dir)


def extract_df(image, lang, tess_config_path):
    result_df = pytesseract.image_to_data(
        image,
        lang=lang,
        output_type=pytesseract.Output.DATAFRAME,
        config=tess_config_path
    )
    return result_df


def extract_box_images(file_path, output_dir, **kwargs):
    lang = kwargs.get('lang', 'kbd')
    tess_config_path = kwargs.get('tess_config_path', TESSERACT_CONFIG)
    page = kwargs.get('page', None)
    if page is not None:
        page = f'page_{page}'
        output_dir = f'{output_dir}/{page}/'
        os.makedirs(output_dir, exist_ok=True)

    image = cv2.imread(file_path)
    result_df = extract_df(image, lang=lang, tess_config_path=tess_config_path)
    result_df.fillna('', inplace=True)

    process_df_by_line(image, result_df, output_dir=output_dir)
