import os
import uuid

import aiohttp_jinja2
from aiohttp import web

from const import UPLOAD_FOLDER
from ocr_processor import process_file


async def index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})


async def upload(request):
    data = await request.post()
    file = data['file']
    task_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}.pdf')
    with open(input_path, 'wb') as f:
        f.write(file.file.read())

    task_manager = request.app['app'].task_manager
    task = task_manager.create_task(process_file(task_manager, task_id), task_id)
    return web.json_response({'task_id': task.get_name()})


async def download(request):
    file_id = request.match_info['file_id']
    output_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.ocr.pdf')
    return web.FileResponse(
        output_path,
        headers={'Content-Disposition': f'attachment; filename="{file_id}.ocr.pdf"'}
    )


async def pdf(request):
    file_id = request.match_info['file_id']
    return aiohttp_jinja2.render_template('pdf.html', request, {'file_id': file_id})
