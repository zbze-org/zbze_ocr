import os

import pysnooper
from django.conf import settings
from django.test import TestCase

from app.ocr.services.ocr_service import ImageProcessor


@pysnooper.snoop()
class ImageProcessorTestCase(TestCase):
    def setUp(self):
        # Укажите путь к тестовому изображению
        self.test_image_path = os.path.join(settings.BASE_DIR, 'ocr/services/tests/src/ocr_to_html_test.jpg')
        self.html_base_path = os.path.join(settings.BASE_DIR, 'ocr/templates/base_ocr.html')
        self.html_result_path = os.path.join(settings.BASE_DIR, 'ocr/services/tests/result_src/ocr_result.html')

        self.processor = ImageProcessor(
            image_path=self.test_image_path,
            html_base_path=self.html_base_path,
            html_result_path=self.html_result_path,
        )

    def test_clean_text(self):
        # Проверяем, что функция clean_text правильно очищает текст
        text = '13 текст 1 ! 13кот 133 [кот]'
        cleaned_text = self.processor.clean_text(text)
        self.assertEqual(cleaned_text, 'Iэ текст I ! Iэкот Iэ [кот]')

    def test_extract_text(self):
        # Проверяем, что функция extract_text возвращает DataFrame
        result_df = self.processor.extract_df()
        self.assertIsNotNone(result_df)
        self.assertTrue('text' in result_df.columns)

    def test_process_image(self):
        # Проверяем, что функция process_image возвращает ожидаемый результат
        result_text = self.processor.process_image()

        # Укажите ожидаемый результат, который вы ожидаете получить после обработки изображения
        expected_text = "Сыт сэ уи гупсысэм"
        self.assertIn(expected_text, result_text)
