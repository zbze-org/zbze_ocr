from django.utils.html import format_html
from django_tables2 import tables, A
from django_tables2.columns import Column, LinkColumn


class ImageColumn(Column):
    def render(self, value):
        return format_html('<img src="{}" style="max-width:300px;"/>', value)


class OcrProjectTable(tables.Table):
    pk = Column()
    name = LinkColumn(viewname='ocr_project_detail', text=lambda record: f'{record.name}', args=[A("pk")])
    description = Column()
    status = Column()
    created_at = Column()
    updated_at = Column()

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'page_index'
        fields = [
            'pk',
            'name',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]


class OcrPageTable(tables.Table):
    pk = Column()
    table_url = LinkColumn(viewname='ocr_page_table', text=lambda record: f'table page {record.pk}', args=[A("pk")])
    editor_url = LinkColumn(viewname='ocr_page_detail', text=lambda record: f'editor page {record.pk}', args=[A("pk")])
    orig_page = Column()
    page_index = Column()
    image_filter_factor = Column()
    created_at = Column()
    updated_at = Column()

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'page_index'
        fields = [
            'pk',
            'table_url',
            'editor_url',
            'orig_page',
            'page_index',
            'image_filter_factor',
            'created_at',
            'updated_at',
        ]


class OcrTable(tables.Table):
    box_image_id = Column(empty_values=(), verbose_name='Box image ID')

    level = Column(verbose_name='Level')
    page_num = Column(verbose_name='Page')
    block_num = Column(verbose_name='Block')
    par_num = Column(verbose_name='Paragraph')
    line_num = Column(verbose_name='Line')
    word_num = Column(verbose_name='Word')
    left = Column(verbose_name='Left')
    top = Column(verbose_name='Top')
    width = Column(verbose_name='Width')
    height = Column(verbose_name='Height')
    line_idx = Column(verbose_name='Line idx')

    conf = Column(verbose_name='Confidence')
    image = ImageColumn()
    text = Column(verbose_name='Text')

    form_column = Column(empty_values=(), verbose_name='Form Column')

    def render_form_column(self, value, record):
        form_id = record.get('box_image_id')
        if not form_id:
            return None

        text = record.get('text')
        form_html = f'''
        <form id={form_id}>
            <input type="text" name="box_text" value="{text}">
            <button >save</button>
        </form>
        '''
        return format_html(form_html)

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        fields = (
            'level',
            'page_num',
            'block_num',
            'par_num',
            'line_num',
            'line_idx',
            'word_num',
            'left',
            'top',
            'width',
            'height',
            'conf',
            'text',
            'image',
            'form_column',
        )
        attrs = {
            'class': 'table table-bordered table-hover table-sm',
            'thead': {
                'class': 'thead-dark',
            },
        }
