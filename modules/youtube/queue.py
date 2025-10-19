import asyncio
from core.settings import MAX_WORKERS, MAX_QUEUE_SIZE
from core.logging import YoutubeLogger, Logger
from concurrent.futures import ThreadPoolExecutor
from modules.youtube.models import SearchTask
from abc import ABC, abstractmethod

class Queue(ABC):
    @abstractmethod
    async def enqueue(self):
        pass
    
    @abstractmethod
    async def get_task(self):
        pass

class QuickSearchQueue(Queue):
    def __init__(self, max_workers = MAX_WORKERS, logger:Logger=None, debug=False):
        self.max_workers = max_workers
        self.logger = logger
        self.debug = debug
        self.queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self.lock = asyncio.Lock()
        
    async def enqueue(self, task:SearchTask):
        await self.queue.put(task)
        
        if self.debug:
            self.logger.log(f"Task {task.term} has been enqueued - 1 of { self.queue.qsize()}.")
            
        return

    async def get_task(self):
        task = await self.queue.get()
        
        if self.debug:
            self.logger.log(f"Task {task.term} is running.")
            
        return task
    
    
            
        
        