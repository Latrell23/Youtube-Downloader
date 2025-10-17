import yt_dlp
from pydantic import BaseModel
from typing import Optional, Dict, List
from pprint import pprint
from datetime import datetime

DEBUG = True

OPTIONS = {
    "skip_download": True,
    "extract_flat": True,
    "quiet": True,
}

OPTIONS_DETAILED = {
    "skip_download": True,
    "extract_flat": False,
    "quiet": True,
}

class VideoModel(BaseModel):
    id: str
    title: str
    full_detailed: bool = False
    channel: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    upload_date: Optional[str] = None
    thumbnail_url: Optional[str] = None
    view_count: Optional[int] = None
    
class ChannelModel(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
class SearchResults(BaseModel):
    query: str
    videos: List[VideoModel]
    channels: List[ChannelModel]
    


class Search:
    def __init__(self, query, options=OPTIONS, max_results=10, debug=False):
        self.options = options
        self.query = f"ytsearch{max_results}:{query}"
        self.debug = debug
        self.result = SearchResults(query=query, videos=[], channels=[])
        
        
    def search(self):
        ''' uses yt_dlp to do a quick search of metadata from youtube '''
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(self.query, download=False)
            results = info.get('entries', [])
            for result in results:
                if result.get('id') == result.get('channel_id'):
                    channel = self.parse_channel(result)
                    self.result.channels.append(channel)
                
                else:
                    
                    video = self.parse_video(result)
                    self.result.videos.append(video)
                    
            if self.debug:
                self.log(f'Search Result: (\n   Videos:\n {" ".join([f'   {x.title}:{x.id}\n' for x in self.result.videos])} \n   Channels:\n {" ".join([f'   {x.title}:{x.id}\n' for x in self.result.channels])} \n)')
                
            
    def parse_video(self, entry:Dict) -> VideoModel:
        ''' Uses the returned data from ytdlp and turns it into VideoModel'''
        id = entry.get('id')
        title = entry.get('title')
        channel = entry.get('channel')
        description = entry.get('description')
        thumbnail_url = entry.get('thumbnails', [{}])[-1].get("url")
        
        video = VideoModel(id=id,
                           title=title,
                           channel=channel,
                           description=description,
                           thumbnail_url=thumbnail_url)
        
        if self.debug:
            self.log(f'Parsed Video {title} with id of {id}')
            
        return video
        
        
    def parse_channel(self, entry:Dict) -> ChannelModel:
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
            self.log(f'Parsed Channel {title} with id of {id}')
            
        return channel
    
        
    def log(self, event):
        ''' takes in the event and logs it into logs.txt with event time '''
        with open("logs.txt", "a") as f:
            f.writelines(f'{datetime.now().isoformat()} - {event}\n')
            
class DetailedSearch:
    def __init__(self, video_id:str, options=OPTIONS_DETAILED, debug=False):
        self.video_id = video_id
        self.result: List[VideoModel] = []
        self.options = options
        self.debug = debug
        
        
    def search(self):
        with yt_dlp.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={self.video_id}', download=False)
            pprint(self.parse_video(info))
        
            
    def parse_video(self, entry:Dict) -> VideoModel:
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
                           full_detailed=True)
        
        if self.debug:
            self.log(f'Parsed Video (Full) {title} with id of {id}')
            
        return video
    
    
    def log(self, event):
        ''' takes in the event and logs it into logs.txt with event time '''
        with open("logs.txt", "a") as f:
            f.writelines(f'{datetime.now().isoformat()} - {event}\n')
            
                    
DetailedSearch(video_id='VcRc2DHHhoM', debug=True).search()

        
        
