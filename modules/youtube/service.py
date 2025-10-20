from modules.youtube.templates import Parser, Searcher
from concurrent.futures import ThreadPoolExecutor
import asyncio
from core.logging import AsyncLogger
from core.settings import MAX_WORKERS, RES_COUNT, MAX_THREADS_FULL,MAX_THREADS_QUICK, MAX_CYCLES
from modules.youtube.parsers import VideoParser, ChannelParser
from modules.youtube.search import QuickSearch, DetailedSearch
from modules.youtube.models import SearchTask
from modules.youtube.queue import SearchQueue, Queue
from datetime import datetime

class YouTubeService:
    def __init__(self,callback, qs_queue:Queue,fd_queue:Queue, quick_searcher:Searcher, detailed_searcher:Searcher, debug=False, logger=None):
        self.quick_searcher = quick_searcher
        self.detailed_searcher = detailed_searcher
        self.callback = callback
        self.debug = debug
        self.logger = logger
        self.qs_queue = qs_queue
        self.fd_queue = fd_queue
        self.running = True
        self.quick_pool = ThreadPoolExecutor(MAX_THREADS_QUICK)
        self.full_pool = ThreadPoolExecutor(MAX_THREADS_FULL)
        self.results = asyncio.Queue()
        
        if self.logger is None and self.debug is True:
                print('[Error]: YouTubeService did not recieve a logger')
                raise ValueError
    
    async def quick_search(self, term, client_id):
        task = SearchTask(client_id=client_id, term=term)
        await self.qs_queue.enqueue(task)
            
    async def quick_workers(self, on_result):
        ''' Continues to gather tasks from queue and executes them in their own thread '''
        loop = asyncio.get_running_loop()
        while self.running:
            task:SearchTask = await self.qs_queue.get_task()
            
            try:
                executed_task:SearchTask = await loop.run_in_executor(self.quick_pool, self.quick_searcher.search, task)
                await on_result(executed_task)
            except Exception as e:
                continue
            
            if self.debug:
                self.logger.log(f"{task.client_id} : Task {task.term} has completed res-count {task.res_count} cycle-count {task.cycle_count} created at {datetime.now()}.")
            
            if (executed_task.res_count < RES_COUNT and executed_task.cycle_count <= MAX_CYCLES):
                #need to add function to check if client still active
                asyncio.create_task(self.qs_queue.enqueue(executed_task))
            else:
                del executed_task
              
    async def full_search(self, video_id, client_id):
        task = SearchTask(client_id=client_id, term=video_id)
        await self.fd_queue.enqueue(task)
        
    async def full_workers(self, on_result):
         loop = asyncio.get_running_loop()
         
         while self.running:
            task:SearchTask = await self.fd_queue.get_task()
             
            try:
                executed_task:SearchTask = await loop.run_in_executor(self.full_pool, self.detailed_searcher.search, task)
                await on_result(executed_task)
                
            except Exception as e:
                continue
            
            if self.debug:
                self.logger.log(f"{task.client_id} : Task {task.term} has completed res-count {task.res_count} cycle-count {task.cycle_count} created at {datetime.now()}.")
                
            del executed_task
                                  
    async def handle_results(self, task:SearchTask):
        await self.callback(task)
               
    async def start_workers(self, num_workers:int = MAX_WORKERS):
        quick_workers = [asyncio.create_task(self.quick_workers(self.handle_results)) for i in range(num_workers)]
        full_workers = [asyncio.create_task(self.full_workers(self.handle_results)) for i in range(num_workers)]
        workers = [*quick_workers, *full_workers]
        await asyncio.gather(*workers)
              
                
if __name__ == "__main__":
    import random
    logger = AsyncLogger()
    
    channel_parser = ChannelParser()
    qs_video_parser = VideoParser()
    fd_video_parser = VideoParser()
    
    quick_searcher = QuickSearch(channel_parser, qs_video_parser)
    detail_searcher = DetailedSearch(fd_video_parser)
    
    qs_queue = SearchQueue(debug=False, logger=logger)
    fd_queue = SearchQueue(debug=False, logger=logger)
    youtube_service = YouTubeService(qs_queue=qs_queue,fd_queue=fd_queue, quick_searcher=quick_searcher, detailed_searcher=detail_searcher, debug=True, logger=logger)
           
    async def queue_task():
        while True:
            id = random.randint(1,100)
            await asyncio.sleep(.1)
            
            async with asyncio.TaskGroup() as tasks:
                task1 = tasks.create_task(youtube_service.quick_search(client_id=f'Tester{id}', term=f'pewdiepie'))
                task2 = tasks.create_task(youtube_service.full_search(client_id=f'Tester{id}', video_id=f'OQUV6kEKwlk'))
                
            
    async def main():
        await asyncio.gather(
            youtube_service.start_workers(num_workers=5),
            queue_task())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting Down")
        
    
                
            
            
            
            
        
            
    
    
            
        


