import os
import re
import uuid
from functools import partial

import pysnooper
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords


class OcrProjectStatusEnum(models.IntegerChoices):
    CREATED = 0
    PROCESSED = 1
    ERROR = 2
    IMAGE_PROCESSING = 10
    TEXT_PROCESSING = 20


class OcrProjectTypeEnum(models.IntegerChoices):
    UNKNOWN = 0
    SCAN_LAYOUT_ONE_PAGE = 1
    SCAN_LAYOUT_TWO_PAGES = 2
    CAMERA_SHOT = 3


class TextExtractionMethodEnum(models.IntegerChoices):
    UNKNOWN = 0
    TESSERACT = 1
    OCRMYPDF = 2
    ABBYY = 3
    EASY_OCR = 4
    OCR_LAYER_GRAB = 5
    TEXT_GRAB = 6
    APPLE_OCR = 7


def generate_uid():
    return str(uuid.uuid4())


class UidModelMixin(models.Model):
    uid = models.CharField(max_length=36, unique=True, editable=False, default=generate_uid)

    class Meta:
        abstract = True


class OcrProject(UidModelMixin):
    orig_project = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='child_projects',
                                     null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    status = models.IntegerField(choices=OcrProjectStatusEnum.choices, default=OcrProjectStatusEnum.CREATED)
    type = models.IntegerField(choices=OcrProjectTypeEnum.choices, default=OcrProjectTypeEnum.UNKNOWN)

    pdf_file = models.FileField(upload_to='ocr_projects', null=True, blank=True)
    pdf_file_md5 = models.CharField(max_length=32, unique=True, null=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.id} - {self.name}'


def _get_image_upload_path(instance, filename, base_path, hash_field='image_md5'):
    image_hash = getattr(instance, hash_field)
    directory_path = os.path.join(base_path, image_hash[:2], image_hash[2:4])
    return os.path.join(directory_path, image_hash, filename)


get_ocr_image_upload_path = partial(_get_image_upload_path, base_path='ocr_images', hash_field='image_md5')
get_ocr_box_image_upload_path = partial(_get_image_upload_path, base_path='ocr_box_images', hash_field='image_md5')
get_ocr_box_image_resized_upload_path = partial(_get_image_upload_path,
                                                base_path='ocr_box_images_resized',
                                                hash_field='image_md5')


class ImageFilterFactor(UidModelMixin):
    class FilterEnum(models.TextChoices):
        Brightness = 'brightness'
        Contrast = 'contrast'
        Sharpness = 'sharpness'

    class FilterDirNameEnum(models.TextChoices):
        Brightness = 'B'
        Contrast = 'C'
        Sharpness = 'S'

    contrast = models.FloatField(default=1.0)
    brightness = models.FloatField(default=1.0)
    sharpness = models.FloatField(default=1.0)

    filter_order = ArrayField(models.CharField(max_length=32, choices=FilterEnum.choices), default=list)

    slug = models.CharField(max_length=80, unique=True, null=True, editable=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.id} - {self.slug}'

    @classmethod
    def processing_step_to_dir_name(cls, processing_steps):
        return '__'.join(f'{cls.FilterDirNameEnum[field].value}{factor}' for field, factor in processing_steps)

    @classmethod
    def dir_name_to_processing_steps(cls, dir_name):
        regex_pattern = r'([BCS])(\d+\.\d+)'  # B1.0__C1.0__S1.0
        matches = re.findall(regex_pattern, dir_name)
        factors = [(cls.FilterDirNameEnum(match[0]).name, float(match[1])) for match in matches]
        return factors

    @classmethod
    def get_or_create_from_processing_steps(cls, processing_steps=None):
        if not processing_steps:
            data = {
                'brightness': 1.0,
                'contrast': 1.0,
                'sharpness': 1.0,
                'filter_order': [],
                'slug': 'original'
            }
        else:
            data = {cls.FilterEnum[field]: factor for field, factor in processing_steps}
            data['filter_order'] = [cls.FilterEnum[field] for field, _ in processing_steps]
            data['slug'] = cls._generate_slug_from_processing_steps(processing_steps)

        try:
            img_ff = cls.objects.get(slug=data['slug'])
        except cls.DoesNotExist:
            img_ff = cls.objects.create(**data)
        return img_ff

    @classmethod
    def _generate_slug_from_processing_steps(cls, processing_steps):
        slug = '_'.join(f'{cls.FilterEnum[field]}:{factor}' for field, factor in processing_steps)
        return slug

    @property
    def processing_steps(self):
        return [(self.FilterEnum(field).name, getattr(self, field)) for field in self.filter_order]

    def _generate_slug(self):
        return '_'.join(f'{field}:{getattr(self, field)}' for field in self.filter_order)

    @pysnooper.snoop(watch_explode=['self'])
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = self.slug or self._generate_slug()
        super().save(force_insert, force_update, using, update_fields)


class OcrPage(UidModelMixin):
    ocr_project = models.ForeignKey(OcrProject, on_delete=models.CASCADE, related_name='ocr_pages',
                                    null=True, blank=True)
    orig_page = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='child_pages',
                                  null=True, blank=True)
    page_index = models.IntegerField(null=True, blank=True)

    image = models.ImageField(upload_to=get_ocr_image_upload_path)
    image_md5 = models.CharField(max_length=32, unique=True, null=True, editable=False)

    width = models.IntegerField()
    height = models.IntegerField()

    image_filter_factor = models.ForeignKey(ImageFilterFactor, on_delete=models.CASCADE, related_name='ocr_pages',
                                            null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} - {self.image}'


class OcrBoxImage(UidModelMixin):
    ocr_page = models.ForeignKey(OcrPage, on_delete=models.CASCADE, related_name='ocr_box_images')

    image = models.ImageField(upload_to=get_ocr_box_image_upload_path)
    resized_image = models.ImageField(upload_to=get_ocr_box_image_resized_upload_path, null=True)
    resized_image_width = models.IntegerField(null=True)
    resized_image_height = models.IntegerField(null=True)

    image_md5 = models.CharField(max_length=32, null=True, editable=False)

    # Tesseract data fields
    level = models.IntegerField()
    page_num = models.IntegerField()
    block_num = models.IntegerField()
    par_num = models.IntegerField()
    line_num = models.IntegerField()
    word_num = models.IntegerField()
    left = models.IntegerField()
    top = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    is_line = models.BooleanField(default=False)

    image_filter_factor = models.ForeignKey(ImageFilterFactor, on_delete=models.CASCADE, related_name='ocr_box_images',
                                            null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_url(self):
        return self.image.url

    class Meta:
        ordering = ['-id']
        unique_together = ['ocr_page', 'image_md5']

    def __str__(self):
        return f'{self.id} - {self.image.name}'


class OcrPageText(UidModelMixin):
    ocr_page = models.ForeignKey(OcrPage, on_delete=models.CASCADE, related_name='ocr_page_texts')

    text = models.TextField()
    md5_hash = models.CharField(max_length=32, null=True, editable=False)
    is_cleaned = models.BooleanField(default=False)

    extraction_config_context = models.JSONField(null=True, blank=True)
    extraction_method = models.IntegerField(choices=TextExtractionMethodEnum.choices,
                                            default=TextExtractionMethodEnum.UNKNOWN,
                                            null=True, blank=True)

    image_filter_factor = models.ForeignKey(ImageFilterFactor, on_delete=models.CASCADE, related_name='ocr_page_texts',
                                            null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']
        unique_together = ['ocr_page', 'md5_hash']

    def __str__(self):
        return f'{self.id} - {self.text[:15]}...{self.text[-15:]}'


class OcrBoxText(UidModelMixin):
    ocr_box_image = models.ForeignKey(OcrBoxImage, on_delete=models.CASCADE, related_name='ocr_box_texts')

    text = models.TextField()
    confidence = models.FloatField(null=True, blank=True)
    md5_hash = models.CharField(max_length=32, null=True, editable=False)
    is_cleaned = models.BooleanField(default=False)

    extraction_config_context = models.JSONField(null=True, blank=True)
    extraction_method = models.IntegerField(choices=TextExtractionMethodEnum.choices,
                                            default=TextExtractionMethodEnum.TESSERACT,
                                            null=True, blank=True)

    image_filter_factor = models.ForeignKey(ImageFilterFactor, on_delete=models.CASCADE, related_name='ocr_box_texts',
                                            null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']
        unique_together = ['ocr_box_image', 'md5_hash']

    def __str__(self):
        return f'{self.id} - {self.text[:15]}...{self.text[-15:]}'
