from modules.youtube.templates import Parser, Searcher
from concurrent.futures import ThreadPoolExecutor
import asyncio
from core.logging import YoutubeLogger
from modules.youtube.parsers import VideoParser, ChannelParser
from modules.youtube.search import QuickSearch, DetailedSearch

class YouTubeService:
    def __init__(self, quick_searcher:Searcher, detailed_searcher:Searcher,  video_parser:Parser, channel_parser:Parser, debug=False, logger=None):
        self.logger = logger
        self.quick_searcher = quick_searcher
        self.detailed_searcher = detailed_searcher
        self.channel_parser = channel_parser
        self.video_parser = video_parser
        self.debug = debug
        
        if self.logger is None and self.debug is True:
                print('[Error]: YouTubeService did not recieve a logger')
                raise ValueError
            
        
    async def quick_search_stream(self, term):
        ''' Concurently searches YouTube for the term to stream back to Client '''
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as pool:
            tasks = [loop.run_in_executor(pool, self.quick_searcher.search, term) for x in range(2)]
            for task in asyncio.as_completed(tasks):
                result = await task
                self.logger.log(f'Streaming {result}')
                yield result
            
    async def detailed_search(self, video_id):
        ''' Concurently searches a video to retrieve its full details '''
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            tasks = loop.run_in_executor(pool, self.detailed_searcher.search, video_id)
            for task in asyncio.all_tasks(tasks):
                result = await task
                return result
        
        


