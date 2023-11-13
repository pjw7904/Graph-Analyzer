from DistributedAlgorithm import DistributedAlgorithm
from queue import PriorityQueue
import networkx as nx

class LSA(DistributedAlgorithm):
    def __init__(self, name, id, data):
        # Node identifers
        self.name = name
        self.id = id

        # Additional node data
        self.neighbors = data["neighbors"]
        self.isRoot = data["isRoot"] # all nodes are root, but used for validation
        self.tree = data["tree"]

        # Initial graph data, add node and it's neighbors
        self.graph = nx.Graph()
        self.addNodeAndEdges(self.name, self.neighbors)

        # Holds distance and parent values
        self.result = None

    def processMessage(self, message) -> bool:
        hasUpdate = False

        if(nx.utils.graphs_equal(self.graph, message)):
            return hasUpdate
        else:
            self.graph = nx.compose(self.graph, message)
            self.runDijkstra()
            hasUpdate = True

        return hasUpdate

    def runDijkstra(self):
        EDGE_COST = 1
        dist = {self.name: 0}
        parent = {}

        unvisited = PriorityQueue()
        unvisited.put((dist[self.name], self.name))

        for node in self.graph:
            if node != self.name:
                dist[node] = float('inf')
            parent[node] = None

        while not unvisited.empty():
            (k, u) = unvisited.get(timeout=5) # THIS IS CAUSING AN ISSUE
            
            if(k == dist[u]):
                for v in self.graph.neighbors(u):
                    alt = dist[u] + EDGE_COST

                    if(alt < dist[v]):
                        dist[v] = alt
                        parent[v] = u
                        unvisited.put((dist[v], v))

                        # validation and output, not part of algorithm
                        if(self.isRoot):
                            self.tree.addParent(u, v)

        # For validation and output
        self.result = (dist, parent)

        return

    def addNodeAndEdges(self, source, neighbors):
        for neighbor in neighbors:
            self.graph.add_edge(source, neighbor)

        return

    def messageToSend(self):
        return self.graph

    def __str__(self) -> str:
        dist = self.result[0]
        parent = self.result[1]

        resultOutput = ""
        for node in sorted(self.graph.nodes):
            resultOutput += f"{node}\n\tParent: {parent[node]}\n\tDistance: {dist[node]}\n"

        resultOutput += "=========\n"

        return resultOutput