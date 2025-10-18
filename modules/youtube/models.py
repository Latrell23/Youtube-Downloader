from pydantic import BaseModel
from typing import Optional, List

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
    videos: List[VideoModel]
    channels: List[ChannelModel]
