from modules.youtube.templates import Parser, Searcher
from concurrent.futures import ThreadPoolExecutor
import asyncio
from core.logging import AsyncLogger
from core.settings import MAX_WORKERS, MAX_CYCLES,MAX_THREADS
from modules.youtube.parsers import VideoParser, ChannelParser
from modules.youtube.search import QuickSearch, DetailedSearch
from modules.youtube.models import SearchTask
from modules.youtube.queue import QuickSearchQueue, Queue

class YouTubeService:
    def __init__(self,qs_queue:Queue, quick_searcher:Searcher, detailed_searcher:Searcher, debug=False, logger=None):
        self.quick_searcher = quick_searcher
        self.detailed_searcher = detailed_searcher
        self.debug = debug
        self.logger = logger
        self.qs_queue = qs_queue
        self.running = True
        self.thread_pool = ThreadPoolExecutor(MAX_THREADS)
        self.results = asyncio.Queue()
        
        if self.logger is None and self.debug is True:
                print('[Error]: YouTubeService did not recieve a logger')
                raise ValueError
    
    
    async def search(self, term, client_id):
        task = SearchTask(client_id=client_id, term=term)
        await self.qs_queue.enqueue(task)
            
    async def workers(self, on_result):
        ''' Continues to gather tasks from queue and executes them in their own thread '''
        loop = asyncio.get_running_loop()
        while self.running:
            task:SearchTask = await self.qs_queue.get_task()
            
            try:
                executed_task:SearchTask = await loop.run_in_executor(self.thread_pool, self.quick_searcher.search, task)
                await on_result(executed_task)
            except Exception as e:
                print(e)
                continue
            
            if executed_task.cycle != MAX_CYCLES:
                #need to add function to check if client still active
                asyncio.create_task(self.qs_queue.enqueue(executed_task))
                
    async def handle_results(self, task):
        await asyncio.to_thread(print, f'Completed {task}')
               
    async def start_workers(self, num_workers:int = MAX_WORKERS):
        workers = [
            asyncio.create_task(self.workers(self.handle_results))
            for i in range(num_workers)
        ]
        await asyncio.gather(*workers)
                
if __name__ == "__main__":
    import random
    logger = AsyncLogger()
    channel_parser = ChannelParser()
    video_parser = VideoParser()
    quick_searcher = QuickSearch(channel_parser, video_parser)
    queue = QuickSearchQueue(debug=True, logger=logger)
    detail_searcher = DetailedSearch(video_parser)
    youtube_service = YouTubeService(qs_queue=queue, quick_searcher=quick_searcher, detailed_searcher=video_parser)
    
    async def aprint(*args, **kwargs):
        await asyncio.to_thread(print, *args, **kwargs)
    
    async def print_task():
        search_task:SearchTask
        async for search_task in youtube_service.start_workers(num_workers=MAX_WORKERS):
            await aprint(search_task)
            
    async def queue_task():
        while True:
            id = random.randint(1,100)
            await asyncio.sleep(1)
            await youtube_service.search(client_id='Tester', term=f'carti{id}')
            
    async def main():
        await asyncio.gather(
            youtube_service.start_workers(num_workers=5),
            queue_task())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting Down")
        
    
                
            
            
            
            
        
            
    
    
            
        


