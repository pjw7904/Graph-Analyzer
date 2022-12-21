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

    return

def init(Graph, root, logFilePath, batch=False, testName=None):
    # Startup tasks
    #setLoggingLevel(logFilePath, batch, testName)
    defineMetrics(Graph)
    treeValidator = TreeValidator(Graph.nodes, root) 

    # Non-root vertices are assigned an empty path bundle
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = []
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        # The root vertex is given a path bundle of itself, which is the only path it will contain
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle'])) 

    # Get the send queue ready to go
    sendQueue = []
    v = root
    
    # Count the number of times the queue has popped an entry
    queueCounter = 0

    # Start elapsed time timer
    startTime = timer()

    # Simulate message passing to allow the distributed algorithm to run in a serial manner
    send(v, Graph, root, sendQueue, queueCounter, treeValidator)

    # Stop elapsed time timer
    endTime = timer()

    # Single test result collection
    resultOutput = getMTAInfo(Graph, treeValidator)

    logging.warning("\n=====RESULT=====\n" + resultOutput)
    logging.warning("\nTime to execute: {0}".format(endTime - startTime))
    logging.warning("steps: {}".format(Graph.graph["step"]))
    Graph.graph["MTA_time"] = endTime - startTime

    # Batch testing result collection
    logging.error("{0},{1},{2}".format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"]))

    return

def MTA_reconverge(Graph, brokenVertex1, brokenVertex2):
    # Define a send queue for VID removal propogation. As long as a vertex has a VID to remove, it will continue to propogate that removal
    sendQueue = []

    logging.warning("\n\n=====REMOVED EDGE=====\n")

    # To determine the right order, I can always look at each preferred path and determine which is longer by one symbol than the other
    # For now, I'm considering the second vertex to be the downstream node where the VID lives
    # Define the edge that has been removed
    removedEdge = Graph.nodes[brokenVertex1]["ID"] + Graph.nodes[brokenVertex2]["ID"]
    logging.warning("Removed edge: {0}\n".format(removedEdge))
    logging.warning("Nodes Attached to removed edge: {0}, {1}\n".format(brokenVertex1, brokenVertex2))

    # The downstream vertex attached to the removed edge is the first node to register the change
    sendQueue.append(brokenVertex2)

    # Start elapsed time timer
    startTime = timer()

    # Continue to propogate removal until finished
    while(sendQueue):
        sendingVertex = sendQueue.pop(TOP_NODE)
        # Determine what VIDs need to be removed from the two nodes that lost their shared edge
        if(sendingVertex == brokenVertex1 or hasRemovedVIDs(Graph, sendingVertex, removedEdge)):
            for x in Graph.nodes[sendingVertex]['children']:
                sendQueue.append(x)

    endTime = timer()

    resultOutput = getMTAInfo(Graph)
    logging.warning("{0}\n{1}".format("\n=====RESULT=====", resultOutput))

    logging.warning("\nTime to remove edge: {0}".format(format(endTime - startTime, '.8f')))

    logging.warning("\n\n=====RE-CONVERGENCE=====\n")

    # Once everything is fixed with the primary paths, have the vertex downstream of the edge removal kick off the reconvergence process
    sendQueue = [brokenVertex2]
    v = sendQueue[TOP_NODE] # v is the top node in the sending queue

    # Mark the vertex downstream of the edge removal as the new root
    queueCounter = 0 # count the number of times the queue has popped an entry
    send(v, Graph, brokenVertex2, sendQueue, queueCounter)

    resultOutput = getMTAInfo(Graph)
    logging.warning("{0}\n{1}".format("\n=====RESULT=====", resultOutput))

    return

'''
Return a boolean depending on if any VIDs were removed
'''
def hasRemovedVIDs(Graph, vertex, edge):
    VIDsRemoved = False
    VIDsToRemove = []

    # For every path that contains the broken edge, remove it
    for path in Graph.nodes[vertex]['pathBundle']:
        if edge in path:
            VIDsToRemove.append(path)
            VIDsRemoved = True

    for path in VIDsToRemove:
        Graph.nodes[vertex]['pathBundle'].remove(path)

    return VIDsRemoved

def send(v, Graph, root, sendQueue, queueCounter, treeValidator):
    # Update meta-information about algorithm sending queue
    queueCounter += 1
    logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendQueue))
    logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))

    # For each neighbor x of the vertex currently sending an update (vertex v), send them the path bundle
    for x in Graph.neighbors(v):
        # Update the log file about the neighbors current situation
        logging.warning("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))
        logging.warning("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

        # Delete any path that already contains the local label L(v) and append L(v) to the rest of them
        pathsReceived = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
        validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates
        
        Graph.graph["step"] += 1 # 12/8: validation is two steps for each path in path bundle
        logging.warning("\t{0} Valid paths received: {1}\n".format(Graph.graph["step"], validPaths))

        # The receiving node now processes the valid paths in the bundle it has collected
        isChild = processBundle(x, v, Graph, validPaths, sendQueue)
        if(isChild):
            treeValidator.addParent(v, x)

    # Dequeue v from the send queue and then check to see if there is another node to send data
    s = sendQueue.pop(TOP_NODE)
    if sendQueue:
        send(s, Graph, root, sendQueue, queueCounter, treeValidator)

    return

def processBundle(x, v, Graph, validPaths, sendQueue):
    # Determine if this vertex who is processing the bundle is a child of the sender
    isChild = False

    # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
    greatBundle = list(merge(Graph.nodes[x]['pathBundle'], validPaths, key=lambda x: (len(x), x)))
    Graph.graph["step"] += 1
    logging.warning("\t{0} Great bundle post-merge: {1}\n".format(Graph.graph["step"], greatBundle))

    # Remove the preferred path and create a new path bundle with it.
    P = copy.deepcopy(greatBundle[0])
    del greatBundle[0]

    Graph.nodes[x]['newPathBundle'] = [P] # the new path bundle with the preferred path

    logging.warning("\tNew path bundle created for step 4: {0}\n".format(Graph.nodes[x]['newPathBundle']))
    # WATCH OUT FOR SHALLOW COPYING HERE AND BELOW

    # Define a deletion set (deletions that will break the path)
    S = getPathEdgeSet(P)

    logging.warning("\tDeletion set ( S = E(P) ): {0}\n".format(S))

    # Process as many of the remaining paths in the great bundle as possible
    while(greatBundle and S):
         # First path remaining in the great bundle, remove it from great bundle
        Q = copy.deepcopy(greatBundle[0])
        del greatBundle[0]

        logging.warning("\tFirst path remaining in great bundle: {0}\n".format(Q))

        # T contains the edges in P that Q will remedy
        remedySet = getPathEdgeSet(Q)
        T = [edge for edge in S if edge not in remedySet]

        Graph.graph["step"] += 1
        logging.warning("\t{0} Remedy Set ( T = s - E(Q) ): {1}\n".format(Graph.graph["step"], T))

        if(T):
            Graph.nodes[x]['newPathBundle'].append(Q)

            logging.warning("\tAdding new path: {0}\n".format(Q))

            # S now contains the remaining edges still in need of a remedy
            S = [edge for edge in S if edge not in T]

            Graph.graph["step"] += 1
            logging.warning("\t{0} Updated S for remaining edges in need of a remedy: {1}\n".format(Graph.graph["step"], S))

    # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
    if Graph.nodes[x]['newPathBundle'] != Graph.nodes[x]['pathBundle']:
        Graph.nodes[x]['pathBundle'] = Graph.nodes[x]['newPathBundle'] # WATCH FOR SHALLOW COPIES

        # If this vertex is now a child of the sender, mark that for the sender to update
        if(Graph.nodes[x]['pathBundle'][0][:-1] == Graph.nodes[v]['pathBundle'][0]):
            isChild = True

        logging.warning("\tOfficial new path bundle for node: {0}\n".format(Graph.nodes[x]['pathBundle']))

        if(x not in sendQueue):
            sendQueue.append(x)

    return isChild

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

def getMTAInfo(Graph, treeValidator):
    resultOutput = ""

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

    return resultOutput