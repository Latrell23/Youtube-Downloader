from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
from modules.youtube.service import YouTubeService, YoutubeLogger, VideoParser, ChannelParser, QuickSearch, DetailedSearch

app = FastAPI()


@app.get('/search')
async def search(q: str):
    pass
    
    
    

