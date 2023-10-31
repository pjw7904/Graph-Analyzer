from abc import ABC, abstractmethod

class DistributedAlgorithm(ABC):
    @abstractmethod
    def __init__(self, name, id, isRoot):
        pass

    @abstractmethod
    def processMessage(self, message) -> bool:
        pass

    @abstractmethod
    def messageToSend(self):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass