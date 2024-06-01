import asyncio
import logging
import os

import aiohttp_jinja2
import jinja2
import uvloop
from aiohttp import web

from const import UPLOAD_FOLDER
from managers import WSConnectionManager, TaskManager
from views import index, upload, download, pdf
from ws import websocket_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class App:

    def __init__(self):
        # Discourage inheritance from some aiohttp classes
        # https://github.com/aio-libs/aiohttp/issues/2691#issuecomment-360979262
        self.web_app = web.Application(client_max_size=1024 ** 3)  # 1 GB
        self.ws_manager = WSConnectionManager()
        self.task_manager = TaskManager()

        aiohttp_jinja2.setup(self.web_app, loader=jinja2.FileSystemLoader('templates'))
        self.web_app.add_routes([web.get('/', index),
                                 web.post('/upload', upload),
                                 web.get('/download/{file_id}', download),
                                 web.get('/pdf/{file_id}', pdf),
                                 web.get('/ws', websocket_handler)])

        self.web_app['app'] = self

    def run(self):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        web.run_app(self.web_app)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app = App()
    app.run()
