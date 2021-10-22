#!/usr/bin/env python

from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
import copy # Get the ability to perform a deep copy

#
# Constants
#
TOP_NODE = 0

def MTA_init(Graph, root):
    # Startup tasks
    defineMetrics(Graph)
    setVertexLabels(Graph, root)

    # Write updates to specified log file
    logFile = open("results/log_results/MTA_Output.txt", "a")
    
    # Non-root vertices are assigned an empty path bundle
    for vertex in Graph:
        if vertex != root: # 
            Graph.nodes[vertex]['pathBundle'] = []
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        # The root vertex is given a path bundle of itself, which is the only path it will contain
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        Graph.nodes[vertex]['updateCounter'] = 0 # Counts the number of times a node has to send an update to a neighbor

    sendQueue = [root]
    v = sendQueue[TOP_NODE] # v is the top node in the sending queue
    
    queueCounter = 0 # count the number of times the queue has popped an entry

    # Start elapsed time timer
    startTime = timer()

    # Simulate message passing to allow the distributed algorithm to run in a serial manner
    send(v, Graph, root, sendQueue, logFile, queueCounter)

    # Stop elapsed time timer
    endTime = timer()

    # Log the resulting path bundles from each node
    resultOutput = ""
    for node in Graph:
        resultOutput += "{0}\n".format(node)
        for path in Graph.nodes[node]['pathBundle']:
            resultOutput += "\t{0}\n".format(path)

    logFile.write("\n=====RESULT=====\n" + resultOutput)
    logFile.write("\nTime to execute: {0}".format(endTime - startTime))
    Graph.graph["MTA_time"] = endTime - startTime

    # Close the log file
    logFile.close()    

    return

def send(v, Graph, root, sendQueue, logFile, queueCounter):
    # Update meta-information about algorithm sending queue
    Graph.graph["MTA"] += 1
    queueCounter += 1
    logFile.write("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendQueue))
    logFile.write("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))

    # For each neighbor x of the vertex currently sending an update (vertex v), send them the path bundle
    for x in Graph.neighbors(v):
        if x != root:
            # Update the log file about the neighbors current situation
            logFile.write("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))
            logFile.write("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

            # Delete any path that already contains the local label L(v) and append L(v) to the rest of them
            pathsReceived = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
            validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates
            
            Graph.graph["MTA_step"] += 1
            logFile.write("\t{0} Valid paths received: {1}\n".format(Graph.graph["MTA_step"], validPaths))

            # The receiving node now processes the valid paths in the bundle it has collected
            processBundle(x, Graph, validPaths, sendQueue, logFile)

    # Dequeue v from the send queue and then check to see if there is another node to send data
    s = sendQueue.pop(TOP_NODE)
    if sendQueue:
        send(s, Graph, root, sendQueue, logFile, queueCounter)

    return

def processBundle(x, Graph, validPaths, sendQueue, logFile):
    # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
    greatBundle = list(merge(Graph.nodes[x]['pathBundle'], validPaths, key=lambda x: (len(x), x)))

    Graph.graph["MTA_step"] += 1
    logFile.write("\t{0} Great bundle post-merge: {1}\n".format(Graph.graph["MTA_step"], greatBundle))

    # Remove the preferred path and create a new path bundle with it.
    P = copy.deepcopy(greatBundle[0])
    del greatBundle[0]

    Graph.nodes[x]['newPathBundle'] = [P] # the new path bundle with the preferred path

    logFile.write("\tNew path bundle created for step 4: {0}\n".format(Graph.nodes[x]['newPathBundle']))
    # WATCH OUT FOR SHALLOW COPYING HERE AND BELOW

    # Define a deletion set (deletions that will break the path)
    S = getPathEdgeSet(P)

    logFile.write("\tDeletion set ( S = E(P) ): {0}\n".format(S))

    # Process as many of the remaining paths in the great bundle as possible
    while(greatBundle and S):
         # First path remaining in the great bundle, remove it from great bundle
        Q = copy.deepcopy(greatBundle[0])
        del greatBundle[0]

        logFile.write("\tFirst path remaining in great bundle: {0}\n".format(Q))

        # T contains the edges in P that Q will remedy
        remedySet = getPathEdgeSet(Q)
        T = [edge for edge in S if edge not in remedySet]

        Graph.graph["MTA_step"] += 1
        logFile.write("\t{0} Remedy Set ( T = s - E(Q) ): {1}\n".format(Graph.graph["MTA_step"], T))

        if(T):
            Graph.nodes[x]['newPathBundle'].append(Q)

            logFile.write("\tAdding new path: {0}\n".format(Q))

            # S now contains the remaining edges still in need of a remedy
            S = [edge for edge in S if edge not in T]

            Graph.graph["MTA_step"] += 1
            logFile.write("\t{0} Updated S for remaining edges in need of a remedy: {1}\n".format(Graph.graph["MTA_step"], S))

    # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
    if Graph.nodes[x]['newPathBundle'] != Graph.nodes[x]['pathBundle']:
        Graph.nodes[x]['pathBundle'] = Graph.nodes[x]['newPathBundle'] # WATCH FOR SHALLOW COPIES

        logFile.write("\tOfficial new path bundle for node: {0}\n".format(Graph.nodes[x]['pathBundle']))
        Graph.graph["MTA_recv"] += 1 # node received updated information that it used

        if(x not in sendQueue):
            sendQueue.append(x)

    return

def defineMetrics(Graph):
    Graph.graph["MTA"] = 0      # count number of iterations needed
    Graph.graph["MTA_recv"] = 0 # count number of times a node receives important information
    Graph.graph["MTA_step"] = 0 # count the number of times a node processes ingress information
    Graph.graph["MTA_time"] = 0 # Elasped algorithm simulation execution time

    return

def setVertexLabels(G, root):
    logFile = open("results/log_results/MTA_Output.txt", "w")
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)
    
        if(node == root):
            logFile.write("Root node is {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        else:
            logFile.write("Non-Root node {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        IDCount += 1

    logFile.write("---------\n\n")
    logFile.close()

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