from django.urls import path

from ocr.views.base_views import OcrPageDetailView, OcrTesseractDataView, OcrPageListView, OcrProjectListView, \
    OcrProjectDetailView

urlpatterns = [
    path('ocr_project/', OcrProjectListView.as_view(), name='ocr_project_list'),
    path('ocr_project/<int:pk>/', OcrProjectDetailView.as_view(), name='ocr_project_detail'),
    path('ocr_page/', OcrPageListView.as_view(), name='ocr_page_list'),
    path('ocr_page/<int:pk>/', OcrPageDetailView.as_view(), name='ocr_page_detail'),
    path('ocr_page_table/<int:pk>/', OcrTesseractDataView.as_view(), name='ocr_page_table'),
]
