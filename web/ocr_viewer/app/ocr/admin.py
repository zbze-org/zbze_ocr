from django import forms
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from ocr.models import (
    OcrProject, OcrPage, OcrBoxImage, OcrPageText, OcrBoxText, ImageFilterFactor
)


@admin.register(ImageFilterFactor)
class ImageFilterFactorAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'slug',
        'brightness',
        'contrast',
        'sharpness',
    ]
    list_filter = ['brightness', 'contrast', 'sharpness']
    search_fields = ['id', 'slug']
    readonly_fields = ['slug']


@admin.register(OcrProject)
class OcrProjectAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'created_at',
        'updated_at',
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['id', 'uid', 'name']


@admin.register(OcrPage)
class OcrPageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image',
        'image_md5',
        'width',
        'height',
        'created_at',
        'updated_at',
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['id', 'image_md5']


class OcrBoxTextForm(forms.ModelForm):
    class Meta:
        model = OcrBoxText
        fields = [
            'text',
            'is_cleaned',
            'extraction_method',
            'image_filter_factor',
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
            'extraction_config_context': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
        }


class OcrBoxTextInline(admin.TabularInline):
    model = OcrBoxText
    form = OcrBoxTextForm
    extra = 0
    fk_name = 'ocr_box_image'


@admin.register(OcrBoxImage)
class OcrBoxImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'ocr_page',
        'image',
        'resized_image',
        'resized_image_width',
        'resized_image_height',
        'image_md5',
        'level',
        'page_num',
        'block_num',
        'par_num',
        'line_num',
        'word_num',
        'left',
        'top',
        'width',
        'height',
        'is_line',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'ocr_page__page_index',
        'is_line',
        'created_at',
        'updated_at'
    ]
    search_fields = ['id', 'image_md5']
    inlines = [OcrBoxTextInline]


class OcrPageTextForm(forms.ModelForm):
    class Meta:
        model = OcrPageText
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'rows': 80, 'cols': 80}),
        }


@admin.register(OcrPageText)
class OcrPageTextAdmin(SimpleHistoryAdmin):
    form = OcrPageTextForm
    list_display = [
        'id',
        'ocr_page',
        'md5_hash',
        'is_cleaned',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'ocr_page__page_index',
        'is_cleaned',
        'created_at',
        'updated_at'
    ]
    search_fields = ['id', 'md5_hash']


@admin.register(OcrBoxText)
class OcrBoxTextAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'ocr_box_image',
        'text',
        'md5_hash',
        'is_cleaned',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'ocr_box_image__ocr_page__page_index',
        'is_cleaned',
        'created_at',
        'updated_at'
    ]
    search_fields = ['id', 'md5_hash', 'text']
    readonly_fields = ['ocr_box_image', 'md5_hash']
