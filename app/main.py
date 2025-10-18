from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
from modules.youtube.service import YouTubeService, YoutubeLogger, VideoParser, ChannelParser, QuickSearch, DetailedSearch

app = FastAPI()


@app.get('/search')
async def search(q: str):
    logger = YoutubeLogger()
    video_parser = VideoParser(debug=False, logger=logger)
    channel_parser = ChannelParser(debug=False, logger=logger)
    quick_searcher = QuickSearch(video_parser, channel_parser, logger=logger, debug=False)
    detail_searcher = DetailedSearch(video_parser=video_parser, debug=False, logger=logger)
    ServiceYouTube = YouTubeService(quick_searcher, detail_searcher, video_parser, channel_parser, debug=True, logger=logger)

    async def event_stream():
        
        async for result in ServiceYouTube.quick_search_stream(q):
            yield f"data: {json.dumps(result)}\n\n"
            
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
    
    
    

