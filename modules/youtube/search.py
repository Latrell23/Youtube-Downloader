from modules.youtube.models import VideoModel, ChannelModel, SearchResults
from typing import Dict
from modules.youtube.templates import Searcher, Parser
from core.settings import VIDEO_OPTIONS, VIDEO_OPTIONS_DETAILED
import yt_dlp

class QuickSearch(Searcher):
    def __init__(self, video_parser:Parser, channel_parser:Parser, logger=None, debug=False):
        self.options = VIDEO_OPTIONS
        self.logger = logger
        self.debug = debug
        self.video_parser = video_parser
        self.channel_parser = channel_parser
        
        if self.logger is None and self.debug is True:
                print('[Error]: QuickSearch was set to debug but a logger was not provided')
                raise ValueError
        
    def search(self, term, max_results=10):
        query = f'ytsearch{max_results}:{term}'
        results = SearchResults(query=term, videos=[], channels=[])
        
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(query, download=False)
            data = info.get('entries', [])
            
            for entry in data:
                if entry.get('id') == entry.get('channel_id'):
                    channel :ChannelModel = self.channel_parser.parse(entry)
                    results.channels.append(channel)
                
                else:
                    
                    video: VideoModel = self.video_parser.parse(entry)
                    results.videos.append(video)
                    
            return results.model_dump_json()
                    
        
class DetailedSearch(Searcher):
    def __init__(self, video_parser:Parser, options=VIDEO_OPTIONS_DETAILED, debug=False, logger=None):
        self.video_parser = video_parser
        self.options = options
        self.debug = debug
        self.logger = logger
        
        if self.logger is None and self.debug is True:
                print('[Error]: DetailedSearch was set to debug but a logger was not provided')
                raise ValueError
            
    def search(self, video_id) -> VideoModel:
        url = f'https://www.youtube.com/watch?v={video_id}'
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(url, download=False)
            return self.video_parser.parse(info, full=True)
        
        