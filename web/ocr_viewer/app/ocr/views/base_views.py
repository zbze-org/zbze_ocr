from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from django_filters.views import FilterView

from ocr.filters import OcrPageFilter
from ocr.models import OcrPage, OcrPageText, OcrBoxImage, OcrProject, OcrBoxText
from ocr.services.ocr_service import ImageProcessor
from ocr.services.spell_check_service import SpellCheckService
from ocr.tables import OcrTable, OcrPageTable, OcrProjectTable


def get_maps(df):
    data = df.to_dict('records')
    box_data_map = [
        ('_'.join(map(str, [word['left'], word['top'], word['width'], word['height']])), word)
        for word in data
    ]
    word_box_map = [
        (data['text'], box_key)
        for box_key, data in box_data_map
    ]
    return box_data_map, word_box_map


class OcrProjectListView(ListView):
    template_name = 'ocr/base.html'
    queryset = OcrProject.objects.all()

    def get_queryset(self):
        return self.queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['table'] = OcrProjectTable(self.object_list)

        return context


class OcrProjectDetailView(TemplateView):
    template_name = 'ocr/project_detail.html'

    def get(self, request, pk):
        ocr_project = get_object_or_404(OcrProject, pk=pk)
        ocr_pages = OcrPage.objects.filter(ocr_project=ocr_project).order_by('page_index')

        context = {
            'ocr_project': ocr_project,
            'ocr_pages': ocr_pages,
        }

        return render(request, self.template_name, context)


class OcrPageListView(FilterView):
    template_name = 'ocr/base.html'
    queryset = OcrPage.objects.all()
    filterset_class = OcrPageFilter

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['table'] = OcrPageTable(self.object_list)

        return context


class OcrPageDetailView(TemplateView):
    template_name = 'ocr/base_editor.html'

    def get(self, request, pk):
        ocr_page = get_object_or_404(OcrPage, pk=pk)
        ocr_page_text = OcrPageText.objects.filter(ocr_page=ocr_page).last()

        latest_version = ocr_page_text.history.latest('history_id')
        prev_version = latest_version.prev_record

        result_df = ImageProcessor(image_path=ocr_page.image.path).extract_df()
        result_df['text'].fillna('', inplace=True)

        base_image = OcrBoxImage.objects.get(
            ocr_page=ocr_page,
            level=1,
            page_num=1,
            block_num=0,
            par_num=0,
            line_num=0,
            word_num=0,
        )

        # todo delete this shit
        markers = SpellCheckService().check(text=latest_version.text)

        context = {
            'full_text': prev_version.text if prev_version else latest_version.text,
            'full_text_cleaned': latest_version.text,
            'ocr_project': ocr_page.ocr_project,
            'ocr_page': ocr_page,
            'ocr_page_text': ocr_page_text,
            'markers': markers,
            'base_image_url': base_image.image.url,
            'prev_url': reverse('ocr_page_detail', args=(ocr_page.id - 1,)),
            'next_url': reverse('ocr_page_detail', args=(ocr_page.id + 1,)),
        }

        return render(request, self.template_name, context)


class OcrTesseractDataView(TemplateView):
    template_name = 'ocr/base_table.html'

    @staticmethod
    def get_image_lines(row, orc_page):
        try:
            box_image = OcrBoxImage.objects.get(
                ocr_page=orc_page,
                level=row.level,
                page_num=row.page_num,
                block_num=row.block_num,
                par_num=row.par_num,
                line_num=row.line_num,
                word_num=row.word_num,
            )
        except OcrBoxImage.DoesNotExist:
            return None

        return box_image

    def get(self, request, pk):
        ocr_page = get_object_or_404(OcrPage, pk=pk)

        result_df = ImageProcessor(image_path=ocr_page.image.path).extract_df()
        hocr = ImageProcessor(image_path=ocr_page.image.path).extract_hocr()

        soup = BeautifulSoup(hocr, 'html.parser')
        ocr_page_div = soup.find('div', {'class': 'ocr_page'})

        result_df['text'].fillna('', inplace=True)
        grouped_df = result_df.groupby(['block_num', 'par_num', 'line_num'])
        combined_text_df = grouped_df['text'].apply(lambda x: ' '.join(x)).reset_index()
        combined_text_df.index = combined_text_df.index + 1
        full_text = '\n'.join(combined_text_df['text'].tolist())

        lines_box_map = {}
        for i, (group_name, group_data) in enumerate(grouped_df, start=1):
            lines_box_map[group_name] = i

        result_df['line_idx'] = result_df.apply(
            lambda row: lines_box_map.get((row.block_num, row.par_num, row.line_num)),
            axis=1
        )

        result_df['box_image'] = result_df.apply(lambda row: self.get_image_lines(row, orc_page=ocr_page), axis=1)

        table_data = result_df.to_dict('records')
        for row in table_data:
            if row['box_image'] is None:
                continue

            row['box_image_id'] = row['box_image'].id
            row['image'] = row['box_image'].image.url
            row['text'] = OcrBoxText.objects.filter(ocr_box_image=row['box_image']).last().text

        table = OcrTable(table_data)
        context = {
            'ocr_page_id': ocr_page.id,
            'full_text': full_text,
            'table': table,
            'ocr_page_div': ocr_page_div,
            'prev_url': reverse('ocr_page_table', args=(ocr_page.id - 1,)),
            'next_url': reverse('ocr_page_table', args=(ocr_page.id + 1,)),
        }

        return render(request, self.template_name, context)
