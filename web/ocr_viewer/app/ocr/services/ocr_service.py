import functools
import hashlib
import io
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import pytesseract
from PIL import Image
from django.conf import settings
from django.core.files.base import File

from ocr.models import OcrBoxImage, OcrPage, OcrBoxText, OcrPageText

logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('ocr_service.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logging.getLogger('').addHandler(file_handler)


def timing_and_logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        # logging.info(f'Function {func.__name__} executed in {execution_time} seconds')
        return result

    return wrapper


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


def clean_text(text):
    text = re.sub(r'(?<=)13(?=[а-я].+)', r'Iэ', text)  #
    text = re.sub(r'(?<=)1(?=[а-я])', r'I', text)
    text = re.sub(r'(?<=)!(?=[а-я].+)', r'I', text)
    text = re.sub(r'(?<=(к|л|п|т|ф|ц|щ))([\[|!1Г}{]+)(?=[а-я])', r'I', text)
    return text


@timing_and_logging_decorator
def cv2_image_2_pil_image_bytestream(cv2_image, image_format='JPEG'):
    pil_image = Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    image_bytes = io.BytesIO()
    pil_image.save(image_bytes, format=image_format)
    image_bytes.seek(0)
    return image_bytes


@timing_and_logging_decorator
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


class DbManager:
    def __init__(self, page_index=None, project_id=None, orig_page_id=None, filter_factors=None):
        self.page_index = page_index
        self.project_id = project_id
        self.orig_page_id = orig_page_id
        self.ocr_page_id = None
        self.filter_factors = filter_factors

    @staticmethod
    @timing_and_logging_decorator
    def get_orig_page_id(project_id, page_index):
        orig_page_id = OcrPage.objects.filter(
            ocr_project_id=project_id,
            page_index=page_index,
            image_filter_factor__slug='original',
        ).values_list('id', flat=True).first() or None
        return orig_page_id

    @timing_and_logging_decorator
    def get_or_create_ocr_page(self, image_path):
        image = cv2.imread(image_path)
        image_md5 = hashlib.md5(image.tobytes()).hexdigest()
        try:
            ocr_page = OcrPage.objects.get(image_md5=image_md5)
        except OcrPage.DoesNotExist:
            ocr_page = OcrPage.objects.create(
                image_md5=image_md5,
                width=image.shape[1],
                height=image.shape[0],
                page_index=self.page_index,
                ocr_project_id=self.project_id,
                orig_page_id=self.orig_page_id,
                image_filter_factor=self.filter_factors,
            )
            ocr_page.image.save(
                name=os.path.basename(image_path),
                content=File(cv2_image_2_pil_image_bytestream(image)),
            )
            ocr_page.save()

        return ocr_page

    @staticmethod
    @timing_and_logging_decorator
    def save_box_to_database(ocr_page, box_data, image, resized_image):
        image_md5 = hashlib.md5(image.tobytes()).hexdigest()

        ocr_box_image, created = OcrBoxImage.objects.update_or_create(
            image_md5=image_md5,
            ocr_page=ocr_page,
            defaults=dict(
                # image=ImageFile(BytesIO(image.tobytes()), name=orig_name),
                # resized_image=ImageFile(BytesIO(resized_image_data.tobytes()), name=resized_name),
                image_md5=image_md5,
                level=box_data.level,
                page_num=box_data.page_num,
                block_num=box_data.block_num,
                par_num=box_data.par_num,
                line_num=box_data.line_num,
                word_num=box_data.word_num,
                left=box_data.coordinates.left,
                top=box_data.coordinates.top,
                width=box_data.coordinates.width,
                height=box_data.coordinates.height,
                is_line=box_data.is_line,
                image_filter_factor=ocr_page.image_filter_factor,
            )
        )

        orig_name = f'{box_data.box_name}.orig.jpg'
        resized_name = f'{box_data.box_name}.resized.jpg'

        ocr_box_image.image.save(orig_name, File(cv2_image_2_pil_image_bytestream(image)))
        ocr_box_image.resized_image.save(resized_name, File(cv2_image_2_pil_image_bytestream(resized_image)))

        OcrBoxText.objects.get_or_create(
            ocr_box_image=ocr_box_image,
            md5_hash=hashlib.md5(box_data.text.encode('utf-8')).hexdigest(),
            defaults=dict(
                text=box_data.text,
                confidence=box_data.confidence,
                image_filter_factor=ocr_page.image_filter_factor,
            )
        )

        return ocr_box_image

    @classmethod
    @timing_and_logging_decorator
    def update_ocr_page_text(cls, ocr_page, text):
        OcrPageText.objects.update_or_create(
            ocr_page=ocr_page,
            md5_hash=hashlib.md5(text.encode('utf-8')).hexdigest(),
            defaults=dict(
                text=text,
                image_filter_factor=ocr_page.image_filter_factor,
            )
        )


class ImageProcessor:
    def __init__(self, image_path, db_manager=None):
        self.image = cv2.imread(image_path)
        self.image_path = image_path
        self.ocr_page = None
        self.db_manager = db_manager

    @timing_and_logging_decorator
    def create_cropped_image(self, image, box_data, resize_factor=4):
        cropped = image[
                  box_data.coordinates.top:box_data.coordinates.top + box_data.coordinates.height,
                  box_data.coordinates.left:box_data.coordinates.left + box_data.coordinates.width,
                  ]

        height, width = cropped.shape[:2]
        new_width, new_height = width // resize_factor, height // resize_factor
        if new_width == 0 or new_height == 0:
            return

        resized_cropped = cv2.resize(cropped, (new_width, new_height), interpolation=cv2.INTER_AREA)

        if self.db_manager:
            self.db_manager.save_box_to_database(ocr_page=self.ocr_page, box_data=box_data,
                                                 image=cropped, resized_image=resized_cropped)
        else:
            cv2.imwrite(os.path.join(settings.MEDIA_ROOT, f'{box_data.box_name_hash}.orig.jpg'), cropped)
            cv2.imwrite(os.path.join(settings.MEDIA_ROOT, f'{box_data.box_name_hash}.resized.jpg'), resized_cropped)

    @timing_and_logging_decorator
    def extract_df(self):
        result_df = pytesseract.image_to_data(
            self.image,
            lang=settings.TESSERACT_LANG,
            output_type=pytesseract.Output.DATAFRAME,
            config=os.path.join(settings.BASE_DIR, 'ocr/src/tesseract.kdb.base.config')
        )
        return result_df

    def extract_hocr(self):
        hocr = pytesseract.image_to_pdf_or_hocr(
            self.image,
            lang=settings.TESSERACT_LANG,
            # config=os.path.join(settings.BASE_DIR, 'ocr/src/tesseract.kdb.base.config'),
            extension='hocr',
        )
        return hocr

    @timing_and_logging_decorator
    def _process_df_by_box(self, image, result_df):
        for row in result_df.itertuples():
            box_data = tesseract_df_2_box_data(row)
            self.create_cropped_image(image, box_data=box_data)

    @timing_and_logging_decorator
    def _process_df_by_line(self, image, result_df):
        result_df['text'].fillna('', inplace=True)
        grouped_df = result_df.groupby(['block_num', 'par_num', 'line_num'])
        lines_box_data_map = {}
        for i, (group_name, group_data) in enumerate(grouped_df):
            self._process_df_by_box(image, group_data)

            box_data = grouped_tesseract_df_2_box_data(group_name=group_name, group_data=group_data)
            lines_box_data_map[group_name] = box_data

        combined_text_df = grouped_df['text'].apply(lambda x: ' '.join(x)).reset_index()
        combined_text_df.index = combined_text_df.index + 1
        combined_text_df.to_html(f'{self.image_path}.combined.html', encoding='utf-8')

        for row in combined_text_df.itertuples():
            line = row.Index
            line_box_data = lines_box_data_map[(row.block_num, row.par_num, row.line_num)]
            line_box_data.box_name = f'grouped.{row.block_num}.{row.par_num}.{row.line_num}.line.{line}'
            line_box_data.box_name_hash = hashlib.md5(line_box_data.box_name.encode('utf-8')).hexdigest()
            self.create_cropped_image(image, box_data=line_box_data)

        full_text = '\n'.join(combined_text_df['text'].tolist())
        return full_text

    @timing_and_logging_decorator
    def process_dataframe(self, image, result_df):
        image_dir = os.path.join(Path(self.image_path).parent, "images")
        os.makedirs(image_dir, exist_ok=True)

        # self._process_df_by_box(image, result_df)
        full_text = self._process_df_by_line(image, result_df)
        return full_text

    @timing_and_logging_decorator
    def process_image(self):
        if self.db_manager:
            self.ocr_page = self.db_manager.get_or_create_ocr_page(image_path=self.image_path)

        result_df = self.extract_df()
        full_text = self.process_dataframe(image=self.image, result_df=result_df)

        if self.db_manager:
            self.db_manager.update_ocr_page_text(ocr_page=self.ocr_page, text=full_text)
        return full_text
