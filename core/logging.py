from datetime import datetime
from threading import Lock
from abc import ABC, abstractmethod

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