from DistributedAlgorithm import DistributedAlgorithm
import heapq
import networkx as nx
import copy

class LSA(DistributedAlgorithm):
    def __init__(self, name, id, data):
        # Node identifers
        self.name = name
        self.id = id

        # Additional node data
        self.neighbors = data["neighbors"]
        self.isRoot = data["isRoot"] # all nodes are root, but used for validation
        self.tree = data["tree"]
        self.failurePropagation = None # If an edge fails and needs to be propagated

        # Initial graph data, add node and it's neighbors
        self.graph = nx.Graph()
        self.addNodeAndEdges(self.name, self.neighbors)

        # Holds distance and parent values
        self.result = None

    def processMessage(self, message) -> bool:
        hasUpdate = False

        if(isinstance(message, nx.classes.graph.Graph)):
            if(nx.utils.graphs_equal(self.graph, message)):
                return hasUpdate
            else:
                self.graph = nx.compose(self.graph, message)
                self.runDijkstra()
                hasUpdate = True
        else:
            if(self.graph.has_edge(*message)):
                self.edgeRemovalUpdate(message)
                hasUpdate = True

        return hasUpdate
    
    def edgeRemovalUpdate(self, edge):
        self.graph.remove_edge(*edge)
        self.runDijkstra()
        self.failurePropagation = edge

        return

    def runDijkstra(self):
        EDGE_COST = 1
        dist = {self.name: 0}
        parent = {}

        unvisited = []
        heapq.heappush(unvisited, (dist[self.name], self.name))

        for node in self.graph:
            if node != self.name:
                dist[node] = float('inf')
            parent[node] = None

        while unvisited:
            (k, u) = heapq.heappop(unvisited)
            
            if(k == dist[u]):
                for v in self.graph.neighbors(u):
                    alt = dist[u] + EDGE_COST

                    if(alt < dist[v]):
                        dist[v] = alt
                        parent[v] = u
                        heapq.heappush(unvisited, (dist[v], v))

                        # validation and output, not part of algorithm
                        if(self.isRoot):
                            self.tree.addParent(u, v)

        # For validation and output
        self.result = (dist, parent)

        return

    def processFailure(self, failedEdge):
        if(self.graph.has_edge(*failedEdge)):
            self.edgeRemovalUpdate(failedEdge)

        return

    def addNodeAndEdges(self, source, neighbors):
        for neighbor in neighbors:
            self.graph.add_edge(source, neighbor)

        return

    def messageToSend(self):
        if(self.failurePropagation is not None):
            message = copy.deepcopy(self.failurePropagation)
        else:
            message = self.graph

        return message

    def sendingCleanup(self):
        if(self.failurePropagation is not None):
            self.failurePropagation = None

        return

    def __str__(self) -> str:
        dist = self.result[0]
        parent = self.result[1]

        resultOutput = ""
        for node in sorted(self.graph.nodes):
            resultOutput += f"{node}\n\tParent: {parent[node]}\n\tDistance: {dist[node]}\n"

        resultOutput += "=========\n"

        return resultOutput