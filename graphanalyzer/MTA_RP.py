#!/usr/bin/env python
import logging

from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
import copy # Get the ability to perform a deep copy

#
# Constants
#
TOP_NODE = 0
LOG_FILE = "results/log_results/MTA_RP_Output.log"

def init(Graph, root, loggingStatus):
    # Startup tasks
    setLoggingLevel(loggingStatus)
    defineMetrics(Graph)
    setVertexLabels(Graph, root)

    # Non-root vertices are assigned an empty path bundle
    for vertex in Graph:
        if vertex != root: # 
            Graph.nodes[vertex]['pathBundle'] = []
            logging.debug("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        # The root vertex is given a path bundle of itself, which is the only path it will contain
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logging.debug("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        Graph.nodes[vertex]['updateCounter'] = 0 # Counts the number of times a node has to send an update to a neighbor
        Graph.nodes[vertex]['children'] = [] # mark children on the given node
        Graph.nodes[vertex]['parent'] = "None" # mark the parent of the given node (root will not have one) 

    sendQueue = [root]
    v = sendQueue[TOP_NODE] # v is the top node in the sending queue
    
    queueCounter = 0 # count the number of times the queue has popped an entry

    # Start elapsed time timer
    startTime = timer()

    # Simulate message passing to allow the distributed algorithm to run in a serial manner
    send(v, Graph, root, sendQueue, queueCounter)

    # Stop elapsed time timer
    endTime = timer()

    # Log the resulting path bundles from each node
    resultOutput = logPathBundles(Graph)

    logging.debug("\n=====RESULT=====\n" + resultOutput)
    logging.debug("\nTime to execute: {0}".format(endTime - startTime))
    Graph.graph["MTA_time"] = endTime - startTime

    return

def MTA_reconverge(Graph, brokenVertex1, brokenVertex2):
    # Define a send queue for VID removal propogation. As long as a vertex has a VID to remove, it will continue to propogate that removal
    sendQueue = []

    logging.debug("\n\n=====REMOVED EDGE=====\n")

    # To determine the right order, I can always look at each preferred path and determine which is longer by one symbol than the other
    # For now, I'm considering the second vertex to be the downstream node where the VID lives
    # Define the edge that has been removed
    removedEdge = Graph.nodes[brokenVertex1]["ID"] + Graph.nodes[brokenVertex2]["ID"]
    logging.debug("Removed edge: {0}\n".format(removedEdge))
    logging.debug("Nodes Attached to removed edge: {0}, {1}\n".format(brokenVertex1, brokenVertex2))

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

    resultOutput = logPathBundles(Graph)
    logging.debug("{0}\n{1}".format("\n=====RESULT=====", resultOutput))

    logging.debug("\nTime to remove edge: {0}".format(format(endTime - startTime, '.8f')))

    logging.debug("\n\n=====RE-CONVERGENCE=====\n")

    # Once everything is fixed with the primary paths, have the vertex downstream of the edge removal kick off the reconvergence process
    sendQueue = [brokenVertex2]
    v = sendQueue[TOP_NODE] # v is the top node in the sending queue

    # Mark the vertex downstream of the edge removal as the new root
    queueCounter = 0 # count the number of times the queue has popped an entry
    send(v, Graph, brokenVertex2, sendQueue, queueCounter)

    resultOutput = logPathBundles(Graph)
    logging.debug("{0}\n{1}".format("\n=====RESULT=====", resultOutput))

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

def send(v, Graph, root, sendQueue, queueCounter):
    # Update meta-information about algorithm sending queue
    Graph.graph["MTA"] += 1
    queueCounter += 1
    logging.debug("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendQueue))
    logging.debug("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))

    # For each neighbor x of the vertex currently sending an update (vertex v), send them the path bundle
    for x in Graph.neighbors(v):
        if x != root:
            # Update the log file about the neighbors current situation
            logging.debug("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))
            logging.debug("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

            # Delete any path that already contains the local label L(v) and append L(v) to the rest of them
            pathsReceived = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
            validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates
            
            Graph.graph["MTA_step"] += 1
            logging.debug("\t{0} Valid paths received: {1}\n".format(Graph.graph["MTA_step"], validPaths))

            # The receiving node now processes the valid paths in the bundle it has collected
            isChild = processBundle(x, v, Graph, validPaths, sendQueue)

            if(isChild and x not in Graph.nodes[v]['children']):
                Graph.nodes[v]['children'].append(x)

    # Dequeue v from the send queue and then check to see if there is another node to send data
    s = sendQueue.pop(TOP_NODE)
    if sendQueue:
        send(s, Graph, root, sendQueue, queueCounter)

    return

def processBundle(x, v, Graph, validPaths, sendQueue):
    # Determine if this vertex who is processing the bundle is a child of the sender
    isChild = False

    # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
    greatBundle = list(merge(Graph.nodes[x]['pathBundle'], validPaths, key=lambda x: (len(x), x)))

    Graph.graph["MTA_step"] += 1
    logging.debug("\t{0} Great bundle post-merge: {1}\n".format(Graph.graph["MTA_step"], greatBundle))

    # Remove the preferred path and create a new path bundle with it.
    P = copy.deepcopy(greatBundle[0])
    del greatBundle[0]

    Graph.nodes[x]['newPathBundle'] = [P] # the new path bundle with the preferred path

    logging.debug("\tNew path bundle created for step 4: {0}\n".format(Graph.nodes[x]['newPathBundle']))
    # WATCH OUT FOR SHALLOW COPYING HERE AND BELOW

    # Define a deletion set (deletions that will break the path)
    S = getPathEdgeSet(P)

    logging.debug("\tDeletion set ( S = E(P) ): {0}\n".format(S))

    # Process as many of the remaining paths in the great bundle as possible
    while(greatBundle and S):
         # First path remaining in the great bundle, remove it from great bundle
        Q = copy.deepcopy(greatBundle[0])
        del greatBundle[0]

        logging.debug("\tFirst path remaining in great bundle: {0}\n".format(Q))

        # T contains the edges in P that Q will remedy
        remedySet = getPathEdgeSet(Q)
        T = [edge for edge in S if edge not in remedySet]

        Graph.graph["MTA_step"] += 1
        logging.debug("\t{0} Remedy Set ( T = s - E(Q) ): {1}\n".format(Graph.graph["MTA_step"], T))

        if(T):
            Graph.nodes[x]['newPathBundle'].append(Q)

            logging.debug("\tAdding new path: {0}\n".format(Q))

            # S now contains the remaining edges still in need of a remedy
            S = [edge for edge in S if edge not in T]

            Graph.graph["MTA_step"] += 1
            logging.debug("\t{0} Updated S for remaining edges in need of a remedy: {1}\n".format(Graph.graph["MTA_step"], S))

    # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
    if Graph.nodes[x]['newPathBundle'] != Graph.nodes[x]['pathBundle']:
        Graph.nodes[x]['pathBundle'] = Graph.nodes[x]['newPathBundle'] # WATCH FOR SHALLOW COPIES

        # If this vertex is now a child of the sender, mark that for the sender to update
        if(Graph.nodes[x]['pathBundle'][0][:-1] == Graph.nodes[v]['pathBundle'][0]):
            isChild = True

            # Remove the old parent, if necessary
            previousParent = Graph.nodes[x]['parent']
            if(previousParent != "None" and previousParent != v):
                Graph.nodes[previousParent]['children'].remove(x)

            Graph.nodes[x]['parent'] = v

        logging.debug("\tOfficial new path bundle for node: {0}\n".format(Graph.nodes[x]['pathBundle']))
        Graph.graph["MTA_recv"] += 1 # node received updated information that it used

        if(x not in sendQueue):
            sendQueue.append(x)

    return isChild

def defineMetrics(Graph):
    Graph.graph["MTA"] = 0      # count number of iterations needed
    Graph.graph["MTA_recv"] = 0 # count number of times a node receives important information
    Graph.graph["MTA_step"] = 0 # count the number of times a node processes ingress information
    Graph.graph["MTA_time"] = 0 # Elasped algorithm simulation execution time

    return

def setVertexLabels(G, root):
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)
    
        if(node == root):
            logging.debug("Root node is {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        else:
            logging.debug("Non-Root node {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        IDCount += 1

    logging.debug("---------\n")

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

def logPathBundles(Graph):
    resultOutput = ""

    # Log the resulting path bundles from each node
    resultOutput = ""
    for node in Graph:
        resultOutput += "{0}\n".format(node)

        for path in Graph.nodes[node]['pathBundle']:
            resultOutput += "\t{0}\n".format(path)

        resultOutput += "\t---\n\tchildren: "
        if(Graph.nodes[node]['children']):
            for child in Graph.nodes[node]['children']:
                resultOutput += "{0} ".format(child)
        else:
            resultOutput += "NONE"

        resultOutput += "\n\tparent: {0}".format(Graph.nodes[node]['parent'])
        resultOutput += "\n\t---\n"

    return resultOutput

def setLoggingLevel(requiresLogging):
    if(requiresLogging):
        logging.basicConfig(format='%(message)s', filename=LOG_FILE, filemode='w', level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    return

def validateInitConvergence(G, root):
    for v in G:
        if(v != root):
            if(G.nodes[v]['parent'] == "None"):
                return False
            
            parent = G.nodes[v]['parent']
            if(v not in G.nodes[parent]["children"]):
                return False


        for child in G.nodes[v]['children']:
            if(G.nodes[child]['parent'] != v):
                return False

    return True