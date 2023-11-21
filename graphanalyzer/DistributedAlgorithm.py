from abc import ABC, abstractmethod

class DistributedAlgorithm(ABC):
    @abstractmethod
    def __init__(self, name, id, data):
        pass

    @abstractmethod
    def processMessage(self, message) -> bool:
        pass

    @abstractmethod
    def processFailure(self, failedEdge):
        pass

    @abstractmethod
    def messageToSend(self):
        pass

    @abstractmethod
    def sendingCleanup(self):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass