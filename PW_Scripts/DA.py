'''===========================
DIJKSTRA'S ALGORITHM
==========================='''
from networkx import get_node_attributes

def DA(Graph, source):
    EDGE_COST = 1 # graphs are unweighted, all edges have a cost of 1

    Graph.nodes[source]["dist"] = 0 # Assign the root/source the distance value 0 because you don't need to go anyway to get to it (you start there)
    Graph.nodes[source]["parent"] = "NONE"

    for node in Graph:
        if node != source:
            Graph.nodes[node]["dist"] = float('inf') # All other nodes in the graph are given the place-holder distance of infinity
            Graph.nodes[node]["parent"] = "udef"

    Q = get_node_attributes(Graph, "dist")

    # while Q is not empty, meaning there are still more nodes that haven't been discovered/marked
    while Q:
        # get the node with the lowest distance value, which starts with the root/source
        v = min(Q, key=Q.get)

        del Q[v]

        for u in Graph.neighbors(v):
            if u in Q:
                alt = Graph.nodes[v]["dist"] + EDGE_COST
                if alt < Graph.nodes[u]["dist"]:
                    Graph.nodes[u]["dist"] = alt
                    Graph.nodes[u]["parent"] = v
                    Q[u] = alt


    result = getNodeInfo(Graph)
    print(result)

    return


def getNodeInfo(Graph):
    output = ""

    for node in Graph:
        output += "{0}\n\tparent: {1}\n\tdistance from root: {2}\n".format(node, Graph.nodes[node]["parent"], Graph.nodes[node]["dist"])
    
    return output