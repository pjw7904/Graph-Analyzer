from DistributedAlgorithm import DistributedAlgorithm
from heapq import merge # Merge function implemented for path bundle merging
import copy # Get the ability to perform a deep copy

class MTA(DistributedAlgorithm):
    def __init__(self, name, id, data):
        # Node identifers
        self.name = name
        self.id = id

        # Additional node data
        self.isRoot = data["isRoot"]
        self.tree = data["tree"]

        if(self.isRoot):
            self.pathBundle = [id] # The root vertex is given a path bundle of itself, which is the only path it will contain
        else:
            self.pathBundle = [] # Non-root vertices are assigned an empty path bundle

    def processMessage(self, message) -> bool:
        hasUpdate = False

        # Delete any path that already contains the local label L(v) and append L(v) to the rest of them
        pathsReceived = [path + self.id for path in message if self.id not in path]
        validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates

        # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
        greatBundle = list(merge(self.pathBundle, validPaths, key=lambda x: (len(x), x)))

        # Remove the preferred path and create a new path bundle with it.
        P = copy.deepcopy(greatBundle[0])
        del greatBundle[0]

        tempBundle = [P] # the new path bundle with the preferred path

        # WATCH OUT FOR SHALLOW COPYING BELOW

        # Define a deletion set (deletions that will break the path)
        S = self.getPathEdgeSet(P)

        # Process as many of the remaining paths in the great bundle as possible
        while(greatBundle and S):
            # First path remaining in the great bundle, remove it from great bundle
            Q = copy.deepcopy(greatBundle[0])
            del greatBundle[0]

            # T contains the edges in P that Q will remedy
            remedySet = self.getPathEdgeSet(Q)
            T = [edge for edge in S if edge not in remedySet]

            if(T):
                tempBundle.append(Q)

                # S now contains the remaining edges still in need of a remedy
                S = [edge for edge in S if edge not in T]

        # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
        if tempBundle != self.pathBundle:
            self.pathBundle = tempBundle # WATCH FOR SHALLOW COPIES
            self.tree.addParent(self.pathBundle[0][-2], self.id)
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