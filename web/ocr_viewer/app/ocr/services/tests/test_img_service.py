import hashlib
import os

import cv2
from django.conf import settings
from django.core.files import File
from django.test import TestCase

from ocr.models import OcrBoxImage, OcrPage
from ocr.services.img_service import extract_text_from_box_image, load_image
from ocr.services.ocr_service import cv2_image_2_pil_image_bytestream


class ImageServiceTestCase(TestCase):

    def setUp(self):
        self.test_ocr_page = OcrPage.objects.create(
            width=0,
            height=0,
        )
        self.test_box_path = os.path.join(os.path.join(settings.BASE_DIR, 'ocr/services/tests/src/box_imgs'))

    def create_test_box_image(self, image_path, ocr_page_id):
        image = cv2.imread(image_path)
        image_md5 = hashlib.md5(image.tobytes()).hexdigest()

        ocr_box_image, created = OcrBoxImage.objects.update_or_create(
            image_md5=image_md5,
            ocr_page_id=ocr_page_id,
            defaults=dict(
                image_md5=image_md5,
                level=0,
                page_num=0,
                block_num=0,
                par_num=0,
                line_num=0,
                word_num=0,
                left=0,
                top=0,
                width=0,
                height=0,
                is_line=False,
            )
        )

        orig_name = f'{image_md5}.orig.jpg'
        ocr_box_image.image.save(orig_name, File(cv2_image_2_pil_image_bytestream(image)))
        return ocr_box_image

    def test_extract_text_from_box_image__89a968f462c285ce785cca82a0774906(self):
        image_path = os.path.join(self.test_box_path, '89a968f462c285ce785cca82a0774906.jpg')
        bi = self.create_test_box_image(image_path=image_path, ocr_page_id=self.test_ocr_page.id)

        process_steps_text = extract_text_from_box_image(bi)
        self.assertIsInstance(process_steps_text, dict)

        self.assertDictEqual(
            process_steps_text,
            {
                (('Brightness', 1.4), ('Contrast', 1.7), ('Sharpness', 1.4)): 'къьшцэк1ьштэкъым\n',
                (('Brightness', 1.4), ('Sharpness', 1.4), ('Contrast', 1.7)): 'къьшцэк1ьштэкъым\n',
                (('Contrast', 1.7), ('Brightness', 1.4), ('Sharpness', 1.4)): "к'ьыщ13к1Ь1нтэкъым\n",
                (('Contrast', 1.7), ('Sharpness', 1.4), ('Brightness', 1.4)): 'къыщ13к1ьштэкъым\n',
                (('Sharpness', 1.4), ('Brightness', 1.4), ('Contrast', 1.7)): 'къыщ]эк1ынтэкъым\n',
                (('Sharpness', 1.4), ('Contrast', 1.7), ('Brightness', 1.4)): 'къыщЕэкШнтэкъым\n'}
        )

    def test_extract_text_from_box_image__89dd777c81bbedd0c9cf66900347aded(self):
        image_path = os.path.join(self.test_box_path, '89dd777c81bbedd0c9cf66900347aded.jpg')
        bi = self.create_test_box_image(image_path=image_path, ocr_page_id=self.test_ocr_page.id)

        process_steps_text = extract_text_from_box_image(bi)
        self.assertIsInstance(process_steps_text, dict)

        self.maxDiff = None
        self.assertDictEqual(
            process_steps_text,
            {
                (('Brightness', 1.4), ('Contrast', 1.7), ('Sharpness', 1.4)): "Хъэнцсъ'ш\n",
                (('Brightness', 1.4), ('Sharpness', 1.4), ('Contrast', 1.7)): "Хъэнцсъ'ш\n",
                (('Contrast', 1.7), ('Brightness', 1.4), ('Sharpness', 1.4)): "Хъэнцсг'Ы-м\n",
                (('Contrast', 1.7), ('Sharpness', 1.4), ('Brightness', 1.4)): "Хъэнцсг'й-м\n",
                (('Sharpness', 1.4), ('Brightness', 1.4), ('Contrast', 1.7)): 'Хъэнцсгш\n',
                (('Sharpness', 1.4), ('Contrast', 1.7), ('Brightness', 1.4)): "Хъэнцсъ'й-м\n"
            }
        )

    def test_extract_text_from_box_image__0b9d0f5c268e5da26e4bf3a03109b0e8(self):
        image_path = os.path.join(self.test_box_path, '0b9d0f5c268e5da26e4bf3a03109b0e8.jpg')
        bi = self.create_test_box_image(image_path=image_path, ocr_page_id=self.test_ocr_page.id)

        process_steps_text = extract_text_from_box_image(bi)
        self.assertIsInstance(process_steps_text, dict)

        self.maxDiff = None
        self.assertDictEqual(
            process_steps_text,
            {
                (('Brightness', 1.4), ('Contrast', 1.7), ('Sharpness', 1.4)): 'ц1ыхухъу\n',
                (('Brightness', 1.4), ('Sharpness', 1.4), ('Contrast', 1.7)): 'ц1ыхухъу\n',
                (('Contrast', 1.7), ('Brightness', 1.4), ('Sharpness', 1.4)): 'ц1ыхухъу\n',
                (('Contrast', 1.7), ('Sharpness', 1.4), ('Brightness', 1.4)): 'ц1ыхухъу\n',
                (('Sharpness', 1.4), ('Brightness', 1.4), ('Contrast', 1.7)): 'ц1ыхухъу\n',
                (('Sharpness', 1.4), ('Contrast', 1.7), ('Brightness', 1.4)): 'ц1ыхухъу\n'
            }
        )
