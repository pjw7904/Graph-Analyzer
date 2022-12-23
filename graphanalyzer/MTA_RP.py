#!/usr/bin/env python
'''
===========================
MESHED TREE ALGORITHM - REMEDY PATHS
===========================
'''
from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
from os.path import join as getFile
from TreeAnalyzer import TreeValidator
from MTP_NPaths import failureRecovery
import logging
import copy # Get the ability to perform a deep copy

#
# Constants
#
TOP_NODE = 0
LOG_FILE = "{}MTA_RP_Output.log"
LOG_FILE_BATCH = "{}batch_test.csv"

def defineMetrics(Graph):
    Graph.graph["step"] = 0     # count the number of times a node processes ingress information
    Graph.graph["MTA_time"] = 0 # Elasped algorithm simulation execution time
    Graph.graph["queueCounter"] = 0 # Count the number of times the queue has popped an entry

    return

def init(Graph, root, logFilePath, batch=False, removal=None, testName=None):
    # Startup tasks
    #setLoggingLevel(logFilePath, batch, testName)
    defineMetrics(Graph)
    treeValidator = TreeValidator(Graph.nodes, root) 

    # Non-root vertices are assigned an empty path bundle
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = []
            logging.warning("{0} path bundle = {1}".format(vertex, Graph.nodes[vertex]['pathBundle']))

        # The root vertex is given a path bundle of itself, which is the only path it will contain
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logging.warning("{0} path bundle = {1}".format(vertex, Graph.nodes[vertex]['pathBundle'])) 

    # Get the send queue ready to go
    sendQueue = []
    v = root

    # Simulate message passing to allow the distributed algorithm to run in a serial manner
    send(v, Graph, root, sendQueue, treeValidator)

    # Single test result collection
    logMTAInfo(Graph, treeValidator, "INIT RESULTS")

    # If an edge is to be removed and the resulting tree studied
    if(removal):
        recoveryTreeValidator = failureRecovery(Graph, root, removal[0], removal[1])
        logMTAInfo(Graph, recoveryTreeValidator, "RECOVERY RESULTS")

        failureReconvergence(Graph, root, recoveryTreeValidator)

    elif(batch):
        # Batch testing result collection
        logging.error("{0},{1},{2}".format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"]))

    return


def send(v, Graph, root, sendQueue, treeValidator):
    # Update meta-information about algorithm sending queue
    Graph.graph["queueCounter"] += 1
    logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(Graph.graph["queueCounter"], sendQueue))
    logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))

    # For each neighbor x of the vertex currently sending an update (vertex v), send them the path bundle
    for x in Graph.neighbors(v):
        # Update the log file about the neighbors current situation
        logging.warning("NEIGHBOR: {0} ({1})".format(x, Graph.nodes[x]['ID']))
        logging.warning("\tCurrent path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

        # Delete any path that already contains the local label L(v) and append L(v) to the rest of them
        pathsReceived = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
        validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates
        
        Graph.graph["step"] += 1 # 12/8: validation is two steps for each path in path bundle
        logging.warning("\t{0} Valid paths received: {1}".format(Graph.graph["step"], validPaths))

        # The receiving node now processes the valid paths in the bundle it has collected
        isChild = processBundle(x, v, Graph, validPaths, sendQueue)
        if(isChild):
            treeValidator.addParent(v, x)

    # Dequeue v from the send queue and then check to see if there is another node to send data
    s = sendQueue.pop(TOP_NODE)
    if sendQueue:
        send(s, Graph, root, sendQueue, treeValidator)

    return

def processBundle(x, v, Graph, validPaths, sendQueue):
    # Determine if this vertex who is processing the bundle is a child of the sender
    isChild = False

    # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
    greatBundle = list(merge(Graph.nodes[x]['pathBundle'], validPaths, key=lambda x: (len(x), x)))
    Graph.graph["step"] += 1
    logging.warning("\t{0} Great bundle post-merge: {1}".format(Graph.graph["step"], greatBundle))

    # Remove the preferred path and create a new path bundle with it.
    P = copy.deepcopy(greatBundle[0])
    del greatBundle[0]

    Graph.nodes[x]['newPathBundle'] = [P] # the new path bundle with the preferred path

    logging.warning("\tNew path bundle created for step 4: {0}".format(Graph.nodes[x]['newPathBundle']))
    # WATCH OUT FOR SHALLOW COPYING HERE AND BELOW

    # Define a deletion set (deletions that will break the path)
    S = getPathEdgeSet(P)

    logging.warning("\tDeletion set ( S = E(P) ): {0}".format(S))

    # Process as many of the remaining paths in the great bundle as possible
    while(greatBundle and S):
         # First path remaining in the great bundle, remove it from great bundle
        Q = copy.deepcopy(greatBundle[0])
        del greatBundle[0]

        logging.warning("\tFirst path remaining in great bundle: {0}".format(Q))

        # T contains the edges in P that Q will remedy
        remedySet = getPathEdgeSet(Q)
        T = [edge for edge in S if edge not in remedySet]

        Graph.graph["step"] += 1
        logging.warning("\t{0} Remedy Set ( T = s - E(Q) ): {1}".format(Graph.graph["step"], T))

        if(T):
            Graph.nodes[x]['newPathBundle'].append(Q)

            logging.warning("\tAdding new path: {0}".format(Q))

            # S now contains the remaining edges still in need of a remedy
            S = [edge for edge in S if edge not in T]

            Graph.graph["step"] += 1
            logging.warning("\t{0} Updated S for remaining edges in need of a remedy: {1}".format(Graph.graph["step"], S))

    # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
    if Graph.nodes[x]['newPathBundle'] != Graph.nodes[x]['pathBundle']:
        Graph.nodes[x]['pathBundle'] = Graph.nodes[x]['newPathBundle'] # WATCH FOR SHALLOW COPIES

        # If this vertex is now a child of the sender, mark that for the sender to update
        if(Graph.nodes[x]['pathBundle'][0][:-1] == Graph.nodes[v]['pathBundle'][0]):
            isChild = True

        logging.warning("\tOfficial new path bundle for node: {0}".format(Graph.nodes[x]['pathBundle']))

        if(x not in sendQueue):
            sendQueue.append(x)

    return isChild

def failureReconvergence(Graph, root, treeValidator: TreeValidator):
    # The ol' send queue, it needs to be the neighbors of the fallen brothers
    sendingQueue = []

    for vertex in treeValidator.getStrandedVertices():
        for neighbor in Graph.neighbors(vertex):
            sendingQueue.append(neighbor)

    if(not sendingQueue):
        logging.warning(f"\n=====RECONVERGENCE RESULTS=====\n")
        logging.warning("No stranded vertices, no change to bundles.")
        
        return

    else:
        s = sendingQueue.pop(0)
        send(s, Graph, root, sendingQueue, treeValidator)
        logMTAInfo(Graph, treeValidator, "RECONVERGENCE RESULTS")

    return

def getPathEdgeSet(path):
    edgeSet = []

    if path:
        if len(path) <= 2:
            edgeSet = [path]
        else:
            vertexSet = list(path)
            for currentEdge in range(1,len(vertexSet)):
                edgeSet.append(vertexSet[currentEdge-1] + vertexSet[currentEdge])

    return edgeSet

def logMTAInfo(Graph, treeValidator, title):
    # Log the resulting path bundles from each node
    resultOutput = ""
    for node in sorted(Graph.nodes):
        resultOutput += "{0}\n".format(node)

        for path in Graph.nodes[node]['pathBundle']:
            resultOutput += "\t{0}\n".format(path)

        resultOutput += "\t---\n\tchildren: "

        children = treeValidator.getChildren(node)
        if(children):
            for child in children:
                resultOutput += "{0} ".format(child)
        else:
            resultOutput += "None"

        resultOutput += "\n\tparent: {0}".format(treeValidator.getParent(node))
        resultOutput += "\n\t---\n"

    logging.warning(f"\n====={title}=====\n" + resultOutput)
    logging.warning("steps: {}".format(Graph.graph["step"]))
    logging.warning("Result is a tree: {0}".format(treeValidator.isTree()))

    return