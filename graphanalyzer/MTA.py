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

        if(self.isRoot):
            self.preferred = MTAVector(0, self.id)
            self.pathBundle = [MTAVector(0, self.id)]
        else:
            self.preferred = None
            self.pathBundle = []

        self.remedyPaths = []

    def processMessage(self, message) -> bool:
        hasUpdate = False

        # If you're the root, ignore all messages, nothing to do.
        if(self.isRoot):
            return hasUpdate

        # For each incoming path that does not include your ID, add it to path bundle
        for path in message:
            if self.id not in path.path:
                heapq.heappush(self.remedyPaths, MTAVector(path.cost + 1, path.path + self.id))

        # Add the current preferred path to see if it is still the best path
        if(self.preferred is not None):
            self.preferred = heapq.heappushpop(self.remedyPaths, self.preferred)
        else:
            self.preferred = heapq.heappop(self.remedyPaths)

        # Define additional bundles
        tempBundle = [self.preferred]
        greatBundle = copy.deepcopy(self.remedyPaths)

        # Define a deletion set (deletions that will break the path)
        S = self.getPathEdgeSet(self.preferred.path)

        while(greatBundle and S):
            Q = heapq.heappop(greatBundle)

            # T contains the edges in P that Q will remedy
            remedySet = self.getPathEdgeSet(Q.path)
            T = [edge for edge in S if edge not in remedySet]

            if(T):
                tempBundle.append(Q)
                # S now contains the remaining edges still in need of a remedy
                S = [edge for edge in S if edge not in T]

        if tempBundle != self.pathBundle:
            self.pathBundle = copy.deepcopy(tempBundle)
            self.tree.addParent(self.preferred.path[-2], self.id)
            hasUpdate = True

        return hasUpdate

    def messageToSend(self):
        return self.pathBundle

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
    
    def __str__(self) -> str:
        resultOutput = f"{self.name} ({self.id})\n"

        for path in self.pathBundle:
            resultOutput += f"\t{path}\n"

        return resultOutput