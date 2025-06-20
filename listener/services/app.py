import asyncio
from contextvars import Context
from api.repositories.task_repository import TaskRepository

class ListenerApp:
    def __init__(self, task_repo: TaskRepository):
        self.task_repository = task_repo

    async def do_stuff(self):
        print(f"{asyncio.current_task().get_name()}") # type: ignore
        print(f"{self.task_repository.db._get_wrapped_session()}") # type: ignore
        r = await self.task_repository.get_task_by_id("4d7426c3-b49c-4f59-8142-73dc3f7db2c0","example")
        await self.task_repository.db.close()

    async def start(self):
        while True:
            print("---------------")
            await self.do_stuff()
            asyncio.create_task(self.do_stuff(), context=Context())
            await asyncio.sleep(1)