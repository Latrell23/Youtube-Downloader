from pydantic import BaseModel
from typing import Optional, List, Dict, Union



class ChannelModel(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

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
 
class SearchResults(BaseModel):
    query: str
    videos: List[VideoModel] = []
    channels: List[ChannelModel] = []

class SearchTask(BaseModel):
    client_id: str
    term: str
    results: Dict[str, Dict[str, Union[ChannelModel, VideoModel]]] = {"videos": {} #{video_id: {VideoModel}}
                                                                      ,"channels": {}} #{channel_id: {ChannelModel}}
    cycle: int = 0
    
    
    
    
    