from django.urls import path
from rest_framework import routers

from api.schema_views import get_schema_version_view, version_view
from ocr.views.api_views import OcrPageTextViewSet, OcrViewSet, OcrBoxTextViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('ocr', OcrViewSet, basename='ocr')
router.register('ocr_page_text', OcrPageTextViewSet, basename='ocr_page_text')
router.register('ocr_box_text', OcrBoxTextViewSet, basename='ocr_box_text')

schema_view = get_schema_version_view(version='v1')

urlpatterns = [
    path(r'swagger(<format>\.json|\.yaml)/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'__version__/', version_view, name='version-json'),
]

urlpatterns += router.urls
