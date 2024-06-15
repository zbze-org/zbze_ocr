import asyncio
from collections import defaultdict

from aiohttp import web


class WSConnectionManager:

    def __init__(self):
        self.connections = set()

    async def connect(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.connections.add(ws)
        return ws

    async def disconnect(self, ws):
        self.connections.remove(ws)
        await ws.close()

    async def broadcast(self, message):
        for connection in self.connections:
            await connection.send_json(message)


class TaskManager:

    def __init__(self):
        self.tasks = {}
        self.task_ws_map = defaultdict(set)

    def create_task(self, coro, task_id):
        task = asyncio.create_task(coro, name=task_id)
        self.add_task(task.get_name(), task)
        return task

    def add_task(self, task_id, task):
        self.tasks[task_id] = task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def add_ws_to_task(self, task_id, ws):
        self.task_ws_map[task_id].add(ws)

    def remove_ws_from_task(self, task_id, ws):
        self.task_ws_map[task_id].remove(ws)

    async def send_message_to_task(self, task_id, message):
        # set of websocket connections on task (another browser tabs or clients)
        task_ws_set = self.task_ws_map.get(task_id)
        if task_ws_set:
            for ws in task_ws_set:
                await ws.send_json(message)
