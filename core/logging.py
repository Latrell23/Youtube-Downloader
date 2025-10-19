from abc import ABC, abstractmethod
import asyncio
import threading
from queue import Queue
from datetime import datetime
from threading import Lock

class Logger(ABC):
    @abstractmethod
    def log(self,event):
        pass

class YoutubeLogger(Logger):
    _lock = Lock()
    
    def log(self, event):
        ''' takes in the event and logs it into logs.txt with event time '''
        with self._lock:
            with open("logs.txt", "a", encoding='utf-8', errors='ignore') as f:
                f.writelines(f'{datetime.now().isoformat()} - {event}\n')
                

class AsyncLogger(Logger):
    def __init__(self, path="logs.txt"):
        self.q = Queue()
        self.path = path
        self.thread = threading.Thread(target=self._writer, daemon=True)
        self.thread.start()

    def _writer(self):
        with open(self.path, "a", encoding="utf-8", errors="ignore") as f:
            while True:
                msg = self.q.get()
                if msg is None:
                    break
                f.write(msg)
                f.flush()

    def log(self, event):
        self.q.put(f"{datetime.now().isoformat()} - {event}\n")

    def close(self):
        self.q.put(None)
        self.thread.join()
