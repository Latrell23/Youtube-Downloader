from abc import ABC, abstractmethod

class Searcher(ABC):
    @abstractmethod
    def __init__(self, logger=None, debug=False):
        pass
    
    @abstractmethod
    def search(self, term):
        pass

class Parser(ABC):
    @abstractmethod
    def parse(self, entry):
        pass
  