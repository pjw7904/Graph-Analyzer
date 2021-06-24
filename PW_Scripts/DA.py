'''===========================
DIJKSTRA'S ALGORITHM
==========================='''
from networkx import get_node_attributes

# Location/name of the log file
LOG_FILE = "DA_Output.txt"

def DA(Graph, source):
    Graph.graph["DA"] = 0 # count number of iterations needed
    Graph.graph["DA_recv"] = 0

    logFile = open(LOG_FILE, "w")

    EDGE_COST = 1 # graphs are unweighted, all edges have a cost of 1

    Graph.nodes[source]["dist"] = 0 # Assign the root/source the distance value 0 because you don't need to go anyway to get to it (you start there)
    Graph.nodes[source]["parent"] = "NONE"

    for node in Graph:
        if node != source:
            Graph.nodes[node]["dist"] = float('inf') # All other nodes in the graph are given the place-holder distance of infinity
            Graph.nodes[node]["parent"] = "udef"

    Q = get_node_attributes(Graph, "dist") # unvisited set

    # while Q is not empty, meaning there are still more nodes that haven't been discovered/marked
    while Q:
        Graph.graph["DA"] += 1

        # get the node with the lowest distance value, which starts with the root/source
        v = min(Q, key=Q.get)

        logDAEvent("---------\n({0}) Visted Node: {1} | Distance: {2}\n".format(Graph.graph["DA"], v, Q[v]), logFile)    

        # Now that the node has been "visted", it is deleted from the unvisited set
        del Q[v]

        # For each neighbor of v, update the distance from the root if it is lower than the previous distance
        for u in Graph.neighbors(v):
            neighborInfo = "\t{0} [distance: {1} | parent: {2}]: ".format(u, Graph.nodes[u]["dist"], Graph.nodes[u]["parent"])
            
            if u in Q:
                alt = Graph.nodes[v]["dist"] + EDGE_COST # distance = distance of v + 1 (unweighted edge cost)
                
                if alt < Graph.nodes[u]["dist"]:
                    Graph.nodes[u]["dist"] = alt
                    Graph.nodes[u]["parent"] = v # parent node is now v, as that it how it gets back to root
                    Q[u] = alt
                    neighborInfo += "distance ---> {0} | parent ---> {1}\n".format(alt, v)

                    Graph.graph["DA_recv"] += 1
                
                else:
                    neighborInfo += "no change, higher cost path\n"
            else:
                neighborInfo += "already visited\n"
            
            logDAEvent(neighborInfo, logFile)


    # log the resulting SPT and its associated data (node distance + parent)
    result = getNodeInfo(Graph)
    logDAEvent("\n=====RESULT=====\n" + result, logFile)

    logFile.close()

    return


def getNodeInfo(Graph):
    output = ""

    for node in Graph:
        output += "{0}\n\tparent: {1}\n\tdistance from root: {2}\n".format(node, Graph.nodes[node]["parent"], Graph.nodes[node]["dist"])
    
    return output


# Log a given DA event
def logDAEvent(eventMsg, logFile):
    logFile.write(eventMsg)

    return