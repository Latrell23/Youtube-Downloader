from modules.youtube.models import VideoModel, ChannelModel, SearchResults
from typing import Dict
from modules.youtube.templates import Searcher, Parser
from core.settings import VIDEO_OPTIONS, VIDEO_OPTIONS_DETAILED, MAX_RESULTS
import yt_dlp
from core.logging import YoutubeLogger, Logger
from modules.youtube.queue import SearchTask

class QuickSearch(Searcher):
    def __init__(self, video_parser:Parser, channel_parser:Parser, logger: Logger =None, debug=False):
        self.options = VIDEO_OPTIONS
        self.logger = logger
        self.debug = debug
        self.video_parser = video_parser
        self.channel_parser = channel_parser
        
        if self.logger is None and self.debug is True:
                print('[Error]: QuickSearch was set to debug but a logger was not provided')
                raise ValueError
        
    def search(self, task:SearchTask, max_results=MAX_RESULTS) -> SearchTask:
        query = f'ytsearch{max_results}:{task.term}'
        
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(query, download=False)
            data = info.get('entries', [])
            
            for entry in data:
                if entry.get('id') == entry.get('channel_id'):
                    channel :ChannelModel = self.channel_parser.parse(entry)
                    channels = task.results.get('channels')
                    
                    if channel.id not in channels:
                        channels[channel.id] = channel
                
                else:
                    
                    video: VideoModel = self.video_parser.parse(entry)
                    videos = task.results.get('videos')
                    
                    if video.id not in videos:
                        videos[video.id] = video
            
            if self.debug:
                self.logger.log(task.model_dump_json())
                
                
            task.cycle += 1
            return task
        
                        
class DetailedSearch(Searcher):
    def __init__(self, video_parser:Parser, options=VIDEO_OPTIONS_DETAILED, debug=False, logger: Logger = None):
        self.video_parser = video_parser
        self.options = options
        self.debug = debug
        self.logger = logger
        
        if self.logger is None and self.debug is True:
                print('[Error]: DetailedSearch was set to debug but a logger was not provided')
                raise ValueError     
            
    def search(self, video_id) -> SearchResults:
        url = f'https://www.youtube.com/watch?v={video_id}'
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(url, download=False)
            video:VideoModel = self.video_parser.parse(info, full=True)
            
            results = SearchResults(query=video_id, videos=[video], )
                 
            if self.debug:
                self.logger.log({results.model_dump_json()})
            return results
        

if __name__ == "__main__":
    from modules.youtube.parsers import VideoParser, ChannelParser
    from core.logging import Logger
    
    logger = YoutubeLogger()
    video_parser = VideoParser()
    channel_parser = ChannelParser()
    
    search = QuickSearch(video_parser, channel_parser, logger, debug=True)
    
    print(search.search("cart", MAX_RESULTS))
    
    full_search = DetailedSearch(video_parser, debug=True, logger=logger)
    
    print(full_search.search("rH9bZTehm_I"))
    