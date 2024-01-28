import os

from PIL import Image
from django.test import TestCase

from cli.logic.apply_img_filters import GroupEnum, save_original_image
from cli.logic.base import convert_to_grayscale


class ImageUtilsTestCase(TestCase):
    def setUp(self):
        self.image_path = "path/to/temp/image.jpg"
        self.image = Image.new("RGB", (100, 100), color="red")
        self.image.save(self.image_path)

    def tearDown(self):
        os.remove(self.image_path)

    def test_group_enum_values(self):
        self.assertEqual(GroupEnum.NONE.value, 0)
        self.assertEqual(GroupEnum.BY_STEP.value, 1)
        self.assertEqual(GroupEnum.BY_PAGE.value, 2)

    def test_convert_to_grayscale(self):
        grayscale_image = convert_to_grayscale(self.image)
        self.assertEqual(grayscale_image.mode, "L")

    def test_save_original_image(self):
        output_dir = "path/to/output"
        file_name = "image.jpg"

        orig_path = save_original_image(self.image, output_dir, file_name)

        self.assertTrue(os.path.exists(orig_path))
        self.assertEqual(os.path.basename(orig_path), f"orig.{file_name.split('.')[-1]}")
