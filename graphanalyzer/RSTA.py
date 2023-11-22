from DistributedAlgorithm import DistributedAlgorithm
from queue import PriorityQueue
from collections import namedtuple, defaultdict
import copy

# Vector that is exchanged between vertices to determine tree structure
RSTAVector = namedtuple("RSTA_Vector", "RPC VID")

DESIGNATED_ROLE = "D"
ROOT_ROLE = "R"
ALTERNATE_ROLE = "A"
UNDEFINED_ROLE = "U"
BROKEN_LINK = "B"

UNDEFINED_COST = -2
BROKEN_COST = -1

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

        # To hold alternates
        self.AVPQ = PriorityQueue()
        self.AVDist = defaultdict(lambda: UNDEFINED_COST)

    def processMessage(self, message) -> bool:
        hasUpdate = False
        EDGE_COST = 1

        oldRole = copy.deepcopy(self.role[message.VID])
        sameMessage = True if message.VID in self.neighbor and self.neighbor[message.VID] == message else False
        updatedMessage = RSTAVector(message.RPC + EDGE_COST, message.VID)
        neighborWasRoot = True if self.role[updatedMessage.VID] == ROOT_ROLE else False

        # d[v] = min{ d[v], d[u] + c(u, v) }, min is d[v] in this case
        if(self.root < updatedMessage):
            if(message < self.rv):
                if(self.AVDist[message.VID] != updatedMessage.RPC):
                    self.setAlternate(updatedMessage)
            else:
                self.setDesignated(updatedMessage)

            if(neighborWasRoot and not sameMessage):
                self.getNewRoot()

        # min is d[u] + c(u, v) in this case
        else:
            if(not sameMessage or not neighborWasRoot):
                self.setRoot(updatedMessage)

        # Store the updated RV from the neighbor 
        self.neighbor[message.VID] = message

        if(not sameMessage or self.role[message.VID] != oldRole):
            hasUpdate = True

        return hasUpdate

    def processFailure(self, failedEdge):
        failedNeighbor = failedEdge[0] if self.id != failedEdge[0] else failedEdge[1]

        if(self.role[failedNeighbor] == ROOT_ROLE):
            self.getNewRoot()

            # If there is no alternate, you need to start over and figure out who will be the new root.
            if(self.root == self.rv):
                self.neighbor = {}
                self.role = defaultdict(lambda: UNDEFINED_ROLE)
                self.AVPQ = PriorityQueue()
                self.AVDist = {}

        elif(self.role[failedNeighbor] == ALTERNATE_ROLE):
            self.AVDist[failedNeighbor] = BROKEN_COST

        self.neighbor[failedNeighbor] = RSTAVector(BROKEN_COST, failedNeighbor)
        self.role[failedNeighbor] = BROKEN_LINK

        return

    def setRoot(self, rootRV):
        if(self.root and self.root.VID != self.id):
            self.setAlternate(self.root)

        self.role[rootRV.VID] = ROOT_ROLE
        self.root = rootRV
        self.rv = RSTAVector(rootRV.RPC, self.rv.VID)

        self.tree.addParent(rootRV.VID, self.id)

        return

    def setAlternate(self, altRV):
        self.role[altRV.VID] = ALTERNATE_ROLE
        self.AVPQ.put(altRV)
        self.AVDist[altRV.VID] = altRV.RPC

        return
    
    def setDesignated(self, desRV):
        self.role[desRV.VID] = DESIGNATED_ROLE

        return

    def getNewRoot(self):
        rootHasNotBeenChosen = True

        while(rootHasNotBeenChosen):
            if(self.AVPQ.empty()):
                #if(self.root.VID != self.id):
                #    pass
                self.rv = RSTAVector(float('inf'), self.id)
                self.root = self.rv
                rootHasNotBeenChosen = False                    

            else:
                newRoot = self.AVPQ.get(timeout=5)

                if(self.role[newRoot.VID] == ALTERNATE_ROLE and newRoot.RPC == self.AVDist[newRoot.VID]): # D issue here
                    self.setRoot(newRoot)
                    rootHasNotBeenChosen = False

        return

    def messageToSend(self):
        return self.rv

    def sendingCleanup(self):
        # Nothing to do for RSTA, only one type of message
        return

    def __str__(self) -> str:
        resultOutput = f"{self.name} ({self.id}) - {self.rv}\n"

        for neighbor in self.neighbor:
            resultOutput += f"\t{neighbor} - {self.neighbor[neighbor]} | Role: {self.role[neighbor]}\n"

        return resultOutput