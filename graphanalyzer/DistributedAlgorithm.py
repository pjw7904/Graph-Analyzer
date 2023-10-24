from abc import ABC, abstractmethod

class DistributedAlgorithm(ABC):
    @abstractmethod
    def __init__(self, isRoot):
        pass

    @abstractmethod
    def processMessage(self, message):
        pass

    @abstractmethod
    def messageToSend(self):
        pass