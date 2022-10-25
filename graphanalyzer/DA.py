#!/usr/bin/env python
'''
===========================
DIJKSTRA'S ALGORITHM
===========================
'''
from networkx import get_node_attributes
from timeit import default_timer as timer # Get elasped time of execution
from os.path import join as getFile
import logging

#
# Constants
#
LOG_FILE = "{}DA_Output.log"
LOG_FILE_BATCH = "{}batch_test.csv"

def init(Graph, root, logFilePath, batch=False, testName=None):
    #setLoggingLevel(logFilePath, batch, testName)

    Graph.graph["DA"] = 0 # count number of iterations needed
    Graph.graph["DA_recv"] = 0
    Graph.graph["step"] = 0
    Graph.graph["DA_time"] = 0 # Elasped algorithm simulation execution time

    EDGE_COST = 1 # graphs are unweighted, all edges have a cost of 1

    Graph.nodes[root]["dist"] = 0 # Assign the root the distance value 0 because you don't need to go anyway to get to it (you start there)
    Graph.nodes[root]["parent"] = "NONE"

    for node in Graph:
        if node != root:
            Graph.nodes[node]["dist"] = float('inf') # All other nodes in the graph are given the place-holder distance of infinity
            Graph.nodes[node]["parent"] = "udef"

    Q = get_node_attributes(Graph, "dist") # unvisited set

    # START TIMER
    startTime = timer()

    # while Q is not empty, meaning there are still more nodes that haven't been discovered/marked
    while Q:
        Graph.graph["DA"] += 1

        # get the node with the lowest distance value, which starts with the root
        v = min(Q, key=Q.get)
        Graph.graph["step"] += 1

        logging.warning("---------\n({0}) Visted Node: {1} | Distance: {2}\n".format(Graph.graph["DA"], v, Q[v]))    

        # Now that the node has been "visted", it is deleted from the unvisited set
        del Q[v]

        # For each neighbor of v, update the distance from the root if it is lower than the previous distance
        for u in Graph.neighbors(v):
            neighborInfo = "\t({0})[distance: {1} | parent: {2}]: ".format(u, Graph.nodes[u]["dist"], Graph.nodes[u]["parent"])
            
            Graph.graph["step"] += 1 # For each neighbor check

            if u in Q:
                alt = Graph.nodes[v]["dist"] + EDGE_COST # distance = distance of v + 1 (unweighted edge cost)

                if alt < Graph.nodes[u]["dist"]:
                    Graph.nodes[u]["dist"] = alt
                    Graph.nodes[u]["parent"] = v # parent node is now v, as that it how it gets back to root
                    Q[u] = alt
                    neighborInfo += "({0})distance ---> {1} | parent ---> {2}\n".format(Graph.graph["step"], alt, v)

                    Graph.graph["DA_recv"] += 1
                
                else:
                    neighborInfo += "({0})no change, higher cost path\n".format(Graph.graph["step"])
            else:
                neighborInfo += "already visited\n"

            Graph.graph["step"] += 1 # For each Q check
            
            logging.warning(neighborInfo)

    # STOP TIMER
    endTime = timer()

    # For batch testing
    logging.error("{0},{1},{2}".format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"]*Graph.number_of_nodes()))

    # log the resulting SPT and its associated data (node distance + parent)
    result = getNodeInfo(Graph)
    logging.warning("\n=====RESULT=====\n" + result)

    logging.warning("\nTime to execute: {0}".format(endTime - startTime))
    Graph.graph["DA_time"] = endTime - startTime

    logging.warning("steps: {}".format(Graph.graph["step"]))

    return


def getNodeInfo(Graph):
    output = ""

    for node in Graph:
        output += "{0}\n\tparent: {1}\n\tdistance from root: {2}\n".format(node, Graph.nodes[node]["parent"], Graph.nodes[node]["dist"])
    
    return output

def setLoggingLevel(logFilePath, batch, testName):
    if(testName):
        testName = testName + "_"
    else:
        testName = ""

    if(batch):
        logging.basicConfig(format='%(message)s', filename=getFile(logFilePath, LOG_FILE_BATCH.format(testName)), filemode='a', level=logging.ERROR) 
    else:
        logging.basicConfig(format='%(message)s', filename=getFile(logFilePath, LOG_FILE.format(testName)), filemode='w', level=logging.WARNING)

    return