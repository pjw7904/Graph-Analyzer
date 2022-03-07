'''===========================
DIJKSTRA'S ALGORITHM
==========================='''
from networkx import get_node_attributes
from timeit import default_timer as timer # Get elasped time of execution
import logging

# Location/name of the log file
LOG_FILE = "results/log_results/DA_Output.log"
LOG_FILE_BATCH = "results/log_results/batch_test.log"

def init(Graph, source, loggingStatus, batch=False):
    setLoggingLevel(loggingStatus, batch)

    Graph.graph["DA"] = 0 # count number of iterations needed
    Graph.graph["DA_recv"] = 0
    Graph.graph["step"] = 0
    Graph.graph["DA_time"] = 0 # Elasped algorithm simulation execution time

    logFile = open(LOG_FILE, "w")

    EDGE_COST = 1 # graphs are unweighted, all edges have a cost of 1

    Graph.nodes[source]["dist"] = 0 # Assign the root/source the distance value 0 because you don't need to go anyway to get to it (you start there)
    Graph.nodes[source]["parent"] = "NONE"

    for node in Graph:
        if node != source:
            Graph.nodes[node]["dist"] = float('inf') # All other nodes in the graph are given the place-holder distance of infinity
            Graph.nodes[node]["parent"] = "udef"

    Q = get_node_attributes(Graph, "dist") # unvisited set

    # START TIMER
    startTime = timer()

    # while Q is not empty, meaning there are still more nodes that haven't been discovered/marked
    while Q:
        Graph.graph["DA"] += 1

        # get the node with the lowest distance value, which starts with the root/source
        v = min(Q, key=Q.get)
        Graph.graph["step"] += 1

        logDAEvent("---------\n({0}) Visted Node: {1} | Distance: {2}\n".format(Graph.graph["DA"], v, Q[v]))    

        # Now that the node has been "visted", it is deleted from the unvisited set
        del Q[v]

        # For each neighbor of v, update the distance from the root if it is lower than the previous distance
        for u in Graph.neighbors(v):
            neighborInfo = "\t({0})[distance: {1} | parent: {2}]: ".format(u, Graph.nodes[u]["dist"], Graph.nodes[u]["parent"])

            if u in Q:
                alt = Graph.nodes[v]["dist"] + EDGE_COST # distance = distance of v + 1 (unweighted edge cost)

                Graph.graph["step"] += 1
                if alt < Graph.nodes[u]["dist"]:
                    Graph.nodes[u]["dist"] = alt
                    Graph.nodes[u]["parent"] = v # parent node is now v, as that it how it gets back to root
                    Q[u] = alt
                    neighborInfo += "({0})distance ---> {1} | parent ---> {2}\n".format(Graph.graph["step"], alt, v)

                    Graph.graph["step"] += 2
                    Graph.graph["DA_recv"] += 1
                
                else:
                    neighborInfo += "({0})no change, higher cost path\n".format(Graph.graph["step"])
            else:
                neighborInfo += "already visited\n"
            
            logDAEvent(neighborInfo)

    # STOP TIMER
    endTime = timer()

    # For batch testing
    logging.error("{0},{1},{2}".format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"]*Graph.number_of_nodes()))

    # log the resulting SPT and its associated data (node distance + parent)
    result = getNodeInfo(Graph)
    logDAEvent("\n=====RESULT=====\n" + result)

    logDAEvent("\nTime to execute: {0}".format(endTime - startTime))
    Graph.graph["DA_time"] = endTime - startTime

    logFile.close()

    return


def getNodeInfo(Graph):
    output = ""

    for node in Graph:
        output += "{0}\n\tparent: {1}\n\tdistance from root: {2}\n".format(node, Graph.nodes[node]["parent"], Graph.nodes[node]["dist"])
    
    return output


# Log a given DA event
def logDAEvent(eventMsg):
    logging.warning(eventMsg)

    return

def setLoggingLevel(requiresLogging, batch):
    if(requiresLogging):
        if(batch):
            logging.basicConfig(format='%(message)s', filename=LOG_FILE_BATCH, filemode='a', level=logging.ERROR) 
        else:
            logging.basicConfig(format='%(message)s', filename=LOG_FILE, filemode='w', level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    return