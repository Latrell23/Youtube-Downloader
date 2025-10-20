from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from modules.youtube.service import YouTubeService ,VideoParser, ChannelParser, QuickSearch, DetailedSearch, SearchQueue, SearchTask
from contextlib import asynccontextmanager
from core.logging import AsyncLogger




@asynccontextmanager
async def lifespan(app: FastAPI):
    vp = VideoParser()
    vp_2 = VideoParser()
    cp = ChannelParser()
    q_search = QuickSearch(vp, cp)
    f_search = DetailedSearch(vp_2)
    fs_queue = SearchQueue()
    qs_queue = SearchQueue()
    
    app.state.client_queues = {} #connected clients will add their task queue {client_id: asyncio.Queue}    
    app.state.youtube_service = YouTubeService(callback=add_task,qs_queue=qs_queue, fd_queue=fs_queue, quick_searcher=q_search, detailed_searcher=f_search, debug=False, logger=AsyncLogger())
    app.state.worker = asyncio.create_task(app.state.youtube_service.start_workers())
    
    yield
    
    app.state_worker.cancel()
    
app = FastAPI(lifespan=lifespan)

async def add_task(task:SearchTask):
    client_queue:asyncio.Queue = app.state.client_queues.get(task.client_id)
    if client_queue:
        await client_queue.put(task)
        
@app.get('/api.search/{term}')
async def search(request:Request, term:str, client_id:str):
    service:YouTubeService = app.state.youtube_service
    response_queue = asyncio.Queue()
    app.state.client_queues[client_id] = response_queue 
    
    await service.quick_search(term, client_id) #waits until task has been added to queue
    
    async def stream_results():
        try:
            while True: #gathers data from client queue until they disconnects and send them results as they appear
                if await request.is_disconnected():
                    break
                
                task_result:SearchTask = await response_queue.get()
                yield f'result : {task_result.model_dump_json()}\n\n'
        
        except asyncio.CancelledError:
            print("Stream cancelled.")
            queues:dict = app.state.client_queues
            queue = queues.pop(client_id)
            del queue
            raise
        
    #stream that will return the values of yield stream results
    return StreamingResponse(stream_results(), media_type='text/event-stream')    
    
@app.get('/api.full-search/{video_id}')
async def search(request:Request, video_id:str, client_id:str):
    service:YouTubeService = app.state.youtube_service
    response_queue = asyncio.Queue()
    app.state.client_queues[client_id] = response_queue
    
    await service.full_search(video_id, client_id)
    
    async def stream_results():
        try:
            while True: #gathers data from client queue until they disconnects and send them results as they appear
                if await request.is_disconnected():
                    break
                
                task_result:SearchTask = await response_queue.get()
                data = await asyncio.to_thread(task_result.model_dump_json)
                yield f'result : {data}\n\n'
        
        except asyncio.CancelledError:
            print("Stream cancelled.")
            queues:dict = app.state.client_queues
            queue = queues.pop(client_id)
            del queue
            raise
        
    #stream that will return the values of yield stream results
    return StreamingResponse(stream_results(), media_type='text/event-stream')
           
    
    
    