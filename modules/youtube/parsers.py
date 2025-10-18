from modules.youtube.models import ChannelModel, VideoModel
from typing import Dict
from modules.youtube.templates import Parser

class ChannelParser(Parser):
    def __init__(self, debug=False, logger=None):
        self.debug = debug
        self.logger = logger
        
        if self.logger is None and self.debug is True:
                print('[Error]: ChannelParser was set to debug but a logger was not provided')
                raise ValueError
    
    def parse(self, entry:Dict) -> ChannelModel:
            ''' Uses the returned data from ytdlp and turns it into ChannelModel '''
            id = entry.get("id")
            title = entry.get("title")
            description = entry.get("description")
            thumbnail_url = entry.get('thumbnails', [{}])[-1].get("url")
            
            channel = ChannelModel(id=id,
                            title=title,
                            description=description,
                            thumbnail_url=thumbnail_url)
            
            if self.debug:
                self.logger.log(f'Parsed Channel {title} with id of {id}')
                
            return channel
        

class VideoParser(Parser):
    def __init__(self, debug=False, logger=None):
        self.debug = debug
        self.logger = logger
        
        if self.logger is None and self.debug is True:
                print('[Error]: VideoParser was set to debug but a logger was not provided')
                raise ValueError
        
        
    def parse(self, entry:Dict, full=False) -> VideoModel:
        ''' Uses the returned data from ytdlp and turns it into VideoModel'''
        id = entry.get('id')
        title = entry.get('title')
        channel = entry.get('channel')
        description = entry.get('description')
        duration = entry.get('duration_string')
        thumbnail_url = entry.get('thumbnails', [{}])[-1].get("url")
        view_count = entry.get('view_count')
        upload_date = entry.get('upload_date')
        
        video = VideoModel(id=id,
                           title=title,
                           channel=channel,
                           description=description,
                           duration=duration,
                           thumbnail_url=thumbnail_url,
                           view_count=view_count,
                           upload_date=upload_date,
                           full_detailed=full)
        
        if self.debug:
            self.logger.log(f'Parsed Video (Full) {title} with id of {id}')
            
        return video
        