from DistributedAlgorithm import DistributedAlgorithm
from collections import namedtuple
import heapq
import copy # Get the ability to perform a deep copy

MTAVector = namedtuple("MTA_Vector", "cost path")

class MTA(DistributedAlgorithm):
    def __init__(self, name, id, data):
        # Node identifers
        self.name = name
        self.id = id

        # Additional node data
        self.isRoot = data["isRoot"]
        self.tree = data["tree"]
        self.neighbor = {}
        self.failurePropagation = None

        if(self.isRoot):
            self.preferred = MTAVector(0, self.id)
            self.pathBundle = {MTAVector(0, self.id)}
        else:
            self.preferred = None
            self.pathBundle = set()

        self.remedyPaths = []

    def processMessage(self, message) -> bool:
        hasUpdate = False

        if(self.isRoot): # If you're the root, ignore all messages, nothing to do.
            return hasUpdate
        
        elif(isinstance(message, MTAVector) and message.cost == -1): # Failed Edge.
            hasUpdate = self.removePaths(message.path)

        else: # Add valid paths to the bundle. 0 = sender ID, 1 = their sent path bundle
            senderID = message[0]
            senderBundle = message[1]

            if(senderID in self.neighbor):
                validPaths = senderBundle.difference(self.neighbor[senderID])
            else:
                validPaths = senderBundle

            hasUpdate = self.addPaths(validPaths)
            self.neighbor[senderID] = senderBundle

        return hasUpdate

    def addPaths(self, receivedBundle):
        hasUpdate = False

        for path in receivedBundle: 
            if self.id not in path.path:
                heapq.heappush(self.remedyPaths, MTAVector(path.cost + 1, path.path + self.id))

        # Add the current preferred path to see if it is still the best path
        if(self.preferred is not None):
            self.preferred = heapq.heappushpop(self.remedyPaths, self.preferred)
        else:
            self.preferred = heapq.heappop(self.remedyPaths)

        # Define additional bundles
        tempBundle = {self.preferred}

        if(self.remedyPaths is not None):
            # Define a deletion set (deletions that will break the path)
            S = self.getPathEdgeSet(self.preferred.path)

            while(self.remedyPaths and S):
                Q = heapq.heappop(self.remedyPaths)

                # T contains the edges in P that Q will remedy
                remedySet = self.getPathEdgeSet(Q.path)
                T = [edge for edge in S if edge not in remedySet]

                if(T):
                    tempBundle.add(Q) # O(1)
                    # S now contains the remaining edges still in need of a remedy
                    S = [edge for edge in S if edge not in T]

        if tempBundle != self.pathBundle:
            self.pathBundle = copy.deepcopy(tempBundle)
            self.tree.addParent(self.preferred.path[-2], self.id)
            hasUpdate = True

        tempBundle.remove(self.preferred)
        self.remedyPaths = list(tempBundle) # O(n)
        heapq.heapify(self.remedyPaths) # O(n)

        return hasUpdate

    def removePaths(self, failedEdge):
        noPreferred = True
        hasUpdate = False

        if(self.isRoot):
            noPreferred = False

        while(noPreferred):
            if failedEdge in self.preferred.path:
                self.pathBundle.remove(self.preferred)

                if(not self.remedyPaths):
                    self.preferred = None
                    noPreferred = False
                else:
                    self.preferred = heapq.heappop(self.remedyPaths)
                    #self.pathBundle.remove(self.preferred)
                    self.tree.addParent(self.preferred.path[-2], self.id)

                self.failurePropagation = MTAVector(-1, failedEdge)

                hasUpdate = True
            else:
                noPreferred = False

        return hasUpdate
    
    def processFailure(self, failedEdge):
        failedEdge = failedEdge[0] + failedEdge[1]
        self.removePaths(failedEdge)

        return

    def messageToSend(self):
        if(self.failurePropagation is not None):
            message = copy.deepcopy(self.failurePropagation)
        else:
            message = (self.id, self.pathBundle)

        return message

    def sendingCleanup(self):
        if(self.failurePropagation is not None):
            self.failurePropagation = None

        return
    
    def __str__(self) -> str:
        resultOutput = f"{self.name} ({self.id})\n"

        outputPathBundle = sorted(list(self.pathBundle))
        outputRemedyBundle = sorted(list(self.remedyPaths))

        resultOutput += f"\tPreferred path \n\t\t{self.preferred}\n\tRemedy Paths\n"

        for path in outputRemedyBundle:
            resultOutput += f"\t\t{path}\n"

        resultOutput += f"\tPath Bundle\n"

        for path in outputPathBundle:
            resultOutput += f"\t\t{path}\n"

        return resultOutput

    def getPathEdgeSet(self, path):
        edgeSet = []

        if path:
            if len(path) <= 2:
                edgeSet = [path]
            else:
                vertexSet = list(path)
                for currentEdge in range(1,len(vertexSet)):
                    edgeSet.append(vertexSet[currentEdge-1] + vertexSet[currentEdge])

        return edgeSet