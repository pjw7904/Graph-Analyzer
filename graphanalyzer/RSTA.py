from DistributedAlgorithm import DistributedAlgorithm
from queue import PriorityQueue
from collections import namedtuple, defaultdict

# Vector that is exchanged between vertices to determine tree structure
RSTAVector = namedtuple("RSTA_Vector", "RPC VID")

DESIGNATED_ROLE = "D"
ROOT_ROLE = "R"
ALTERNATE_ROLE = "A"
UNDEFINED_ROLE = "U"

class RSTA(DistributedAlgorithm):
    def __init__(self, name, id, data):
        # Node identifers
        self.name = name
        self.id = id

        # Additional node data
        self.isRoot = data["isRoot"]
        self.tree = data["tree"]

        # Define the initial RSTA Vector (RV) and data structures
        if(self.isRoot):
            self.rv = RSTAVector(0, self.id)
            self.root = self.rv
        else:
            self.rv = RSTAVector(float('inf'), self.id)
            self.root = self.rv

        self.neighbor = {}
        self.role = defaultdict(lambda: UNDEFINED_ROLE)
        self.AVPQ = PriorityQueue()

    def processMessage(self, message) -> bool:
        hasUpdate = False
        EDGE_COST = 1

        # If the neighbor has been seen before, but their RV is the same as the last one sent, nothing to do.
        if(message.VID in self.neighbor and self.neighbor[message.VID] == message):
            return hasUpdate

        hasUpdate = True

        # Update RPC = RPC + weight(edge)
        updatedMessage = RSTAVector(message.RPC + EDGE_COST, message.VID)
        neighborWasRoot = True if self.role[updatedMessage.VID] == ROOT_ROLE else False

        # d[v] = min{ d[v], d[u] + c(u, v) }, min is d[v] in this case
        if(self.root < updatedMessage):
            if(message < self.rv):
                self.setAlternate(updatedMessage)
            else:
                self.setDesignated(updatedMessage)

            if(neighborWasRoot):
                self.getNewRoot()
        
        # min is d[u] + c(u, v) in this case
        else:
            if(self.root):
                self.setAlternate(self.root)

            self.setRoot(updatedMessage)


        # Store the updated RV from the neighbor 
        self.neighbor[message.VID] = message

        return hasUpdate

    def setRoot(self, message):
        self.role[message.VID] = ROOT_ROLE
        self.root = message
        self.rv = RSTAVector(message.RPC, self.rv.VID)

        self.tree.addParent(message.VID, self.id)

        return

    def updateRoot(self, messageRV):
        self.setAlternate(messageRV) # Throw it back into the AVPQ and see if it pops back out
        self.getNewRoot()

        return

    def setAlternate(self, altRV):
        self.role[altRV.VID] = ALTERNATE_ROLE
        self.AVPQ.put(altRV)

        return
    
    def setDesignated(self, desRV):
        self.role[desRV.VID] = DESIGNATED_ROLE

        return

    def getNewRoot(self):
        if(self.AVPQ.empty()):
            self.rv = RSTAVector(float('inf'), self.id)
        else:
            self.setRoot(self.AVPQ.get(timeout=5))

        return

    def messageToSend(self):
        return self.rv

    def __str__(self) -> str:
        resultOutput = f"{self.name} ({self.id}) - {self.rv}\n"

        for neighbor in self.neighbor:
            resultOutput += f"\t{neighbor} - {self.neighbor[neighbor]} | Role: {self.role[neighbor]}\n"

        return resultOutput