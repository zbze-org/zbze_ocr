import os
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management import BaseCommand
from tqdm import tqdm

from ocr.models import ImageFilterFactor
from ocr.services.ocr_service import ImageProcessor, DbManager


class Command(BaseCommand):
    help = 'OCR test'

    html_base_path = os.path.join(settings.BASE_DIR, 'ocr/templates/ocr/base_ocr.html')
    html_result_path = os.path.join(settings.BASE_DIR, 'ocr/services/tests/result_src/ocr_result.html')

    def add_arguments(self, parser):
        parser.add_argument(
            '-path',
            '--path',
            action='store',
        )
        parser.add_argument(
            '-p_id',
            '--project_id',
            action='store',
        )
        parser.add_argument(
            '-n',
            '--njobs',
            type=int,
            default=4,  # Количество параллельных задач по умолчанию
            help='Number of parallel jobs',
        )

    def process_image(self, image_path, page_i, db_manager, progress_bar=None):
        image_name = os.path.basename(image_path)
        progress_bar.set_description(f'Processing {page_i} {image_name}')

        ocr_page_id = db_manager.get_or_create_ocr_page(image_path=image_path)
        ocr_original_page_id = db_manager.get_orig_page_id(project_id=db_manager.project_id, page_index=page_i)

        db_manager.ocr_page_id = ocr_page_id
        db_manager.page_index = page_i
        db_manager.ocr_original_page_id = ocr_original_page_id

        processor = ImageProcessor(
            image_path=image_path,
            html_base_path=self.html_base_path,
            html_result_path=self.html_result_path,
            db_manager=db_manager
        )
        processor.process_image()

        if progress_bar is not None:
            progress_bar.update(1)

    def handle(self, *args, **options):
        path = os.path.join(settings.MEDIA_ROOT, options['path'])
        project_id = options['project_id']
        njobs = options['njobs']

        processing_steps = ImageFilterFactor.dir_name_to_processing_steps(dir_name=path)
        filter_factors = ImageFilterFactor.get_or_create_from_processing_steps(processing_steps=processing_steps)
        db_manager = DbManager(
            project_id=project_id,
            filter_factors=filter_factors,
        )

        image_list = sorted([f for f in os.listdir(path) if f.endswith('.jpg')])

        progress_bar = tqdm(image_list, desc='Processing', unit='job')

        with ThreadPoolExecutor(max_workers=njobs) as executor:
            futures = []
            for page_i, image_name in enumerate(image_list):
                image_path = os.path.join(path, image_name)
                future = executor.submit(self.process_image, image_path, page_i, db_manager, progress_bar)
                futures.append(future)

            for future in futures:
                future.result()
