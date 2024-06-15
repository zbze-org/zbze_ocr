import asyncio
import os

import ocrmypdf

from const import UPLOAD_FOLDER


async def process_file(task_manager, task_id):
    input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}.pdf')
    output_path = os.path.join(UPLOAD_FOLDER, f'{task_id}.ocr.pdf')

    # run ocrmypdf in a separate thread
    await asyncio.to_thread(
        ocrmypdf.ocr,
        input_path,
        output_path,
        force_ocr=True,
        language='kbd',
        # progress_bar=False,
        deskew=True,
        # remove_background=True,
        clean=True,
        clean_final=True,
    )

    message = {
        'task_id': task_id,
        'status': 'complete',
        'progress': 100,
    }
    await task_manager.send_message_to_task(task_id, message)
