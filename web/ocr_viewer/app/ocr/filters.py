import django_filters

from ocr.models import OcrPage


class OcrPageFilter(django_filters.FilterSet):
    class Meta:
        model = OcrPage
        fields = {
            'ocr_project': ['exact'],
        }
