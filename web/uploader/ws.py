import os

import aiohttp

from const import UPLOAD_FOLDER

STATUS_PROCESSING = 'processing'
STATUS_COMPLETE = 'complete'


def create_ws_message(task_id, status, progress):
    return {
        'task_id': task_id,
        'status': status,
        'progress': progress,
    }


async def handle_ws_message(request, ws, msg_data):
    task_id = msg_data.get('task_id')
    if task_id:
        request.app['app'].task_manager.add_ws_to_task(task_id, ws)
        task = request.app['app'].task_manager.get_task(task_id)
        if task:
            if not task.done():
                out_msg = create_ws_message(task_id, STATUS_PROCESSING, 15)
                await request.app['app'].task_manager.send_message_to_task(task_id, out_msg)
            else:
                out_msg = create_ws_message(task_id, STATUS_COMPLETE, 100)
                await request.app['app'].task_manager.send_message_to_task(task_id, out_msg)
        if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{task_id}.ocr.pdf')):
            out_msg = create_ws_message(task_id, STATUS_COMPLETE, 100)
            await request.app['app'].task_manager.send_message_to_task(task_id, out_msg)


async def websocket_handler(request):
    ws = await request.app['app'].ws_manager.connect(request)

    async for in_msg in ws:
        in_msg: aiohttp.WSMessage
        if in_msg.type == aiohttp.WSMsgType.TEXT:
            msg_data = in_msg.json()
            await handle_ws_message(request, ws, msg_data)

    await request.app['app'].ws_manager.disconnect(ws)
    return ws
