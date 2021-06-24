#!/usr/bin/env python
from heapq import merge # Merge function implemented for path bundle merging
import copy

def createMeshedTreeDatatStructures(G, root):
    logFile = open("MTA_Output.txt", "w")
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)
    
        if(node == root):
            '''
            rootInfo = {
                'isRoot': True,
                'state': "F",
                'ACK(child)': [],
                'ACK(noChild)': [],
                'inBasket': [],
                'pathBundle': [G.nodes[node]['ID']]
            }

            G.nodes[node]['rootInfo'] = rootInfo
            '''
            logFile.write("Root node is {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        else:
            '''
            nodeInfo = {
                'isRoot': False,
                'state': "I",
                'NEXT': False,
                'STOP': False,
                'inBasket': [],
                'pathBundle': []
            }

            G.nodes[node]['nodeInfo'] = nodeInfo
            '''
            logFile.write("Non-Root node {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        IDCount += 1

    logFile.write("---------\n\n")
    logFile.close()

    return


def MTA(Graph, root):
    Graph.graph["MTA"] = 0 # count number of iterations needed
    Graph.graph["MTA_recv"] = 0 # count number of times a node receives important information

    # Startup tasks
    logFile = open("MTA_Output.txt", "a")
    topNode = 0
    createMeshedTreeDatatStructures(Graph, root) # Every vertex is given a single-character ID (starting with 'A')

    # Assign initial path bundles to each vertex
    for vertex in Graph:
        if vertex != root: # Non-root vertices are given an empty path bundle
            Graph.nodes[vertex]['pathBundle'] = []
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        else: # The root vertex is given a path bundle of itself, which is the only path it will contain
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        Graph.nodes[vertex]['updateCounter'] = 0 # Counts the number of times a node has to send an update to a neighbor

    # Queue is based on a list for this implementation test
    sendingQueue = [root]
    queueCounter = 0 # count the number of times the queue has popped an entry

    # Go through the sending process
    while sendingQueue:
        Graph.graph["MTA"] += 1

        v = sendingQueue[topNode] # v is the top node in the sending queue

        # Update meta-information about algorithm sending queue
        queueCounter += 1
        logFile.write("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendingQueue))
        logFile.write("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))

        # For each neighbor (x) of the node currently sending an update, send them the path bundle
        for x in Graph.neighbors(v):
            if x != root:
                # Update the log file about the neighbors current situation
                logFile.write("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))
                logFile.write("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

                # (1) (i) Delete any path that already contains the local label L(v) and (ii) append L(v) to the rest of them
                pathsReceived = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
                validPaths = list(dict.fromkeys(pathsReceived)) # remove duplicates
                logFile.write("\tValid paths received: {0}\n".format(validPaths))

                # (2) Form a great bundle B(v) by merging the path bundle with the paths from (1)
                #greatBundle = mergePathBundles(Graph.nodes[x]['pathBundle'], validPaths)
                greatBundle = list(merge(Graph.nodes[x]['pathBundle'], validPaths, key=lambda x: (len(x), x))) # merge cause duplicates, should I remove them with the same process as above?
                logFile.write("\tGreat bundle post-merge: {0}\n".format(greatBundle))

                # (3) remove the preferred path and create a new path bundle with it. Then define a deletion set (deletions that will break the path)
                preferredPath = greatBundle[0]
                Graph.nodes[x]['newPathBundle'] = [preferredPath] # the new path bundle with the preferred path
                logFile.write("\tNew path bundle created for step 4: {0}\n".format(Graph.nodes[x]['newPathBundle']))
                # WATCH OUT FOR SHALLOW COPYING HERE AND BELOW

                S = getPathEdgeSet(preferredPath)
                logFile.write("\tDeletion set ( S = E(P) ): {0}\n".format(S))

                # (4) process as many of the remaining paths in the great bundle as possible
                processing = True
                while(processing):
                    # (i) if GB = null or not null
                    if greatBundle:
                        Q = greatBundle[0] # First path remaining in the great bundle (if it is not empty)
                        logFile.write("\tFirst path remaining in great bundle: {0}\n".format(Q))
                        remedySet = getPathEdgeSet(Q)
                        T = [edge for edge in S if edge not in remedySet]
                        logFile.write("\tRemedy Set ( T = s - E(Q) ): {0}\n".format(T))

                        # (ii) if T = null or not null
                        if not T:
                            del greatBundle[0]
                        else:
                            Graph.nodes[x]['newPathBundle'].append(Q)
                            logFile.write("\tAdding new path: {0}\n".format(Q))
                            S = [edge for edge in S if edge not in T] # S now contains the remaining edges still in need of a remedy
                            logFile.write("\tUpdated S for remaining edges in need of a remedy: {0}\n".format(S))

                        # (iii) if S = null or not null
                        if not S:
                            processing = False

                    else:
                        processing = False

                # (5) If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
                if Graph.nodes[x]['newPathBundle'] != Graph.nodes[x]['pathBundle']:
                    Graph.nodes[x]['pathBundle'] = Graph.nodes[x]['newPathBundle'] # WATCH FOR SHALLOW COPIES
                    logFile.write("\tOfficial new path bundle for node: {0}\n".format(Graph.nodes[x]['pathBundle']))

                    Graph.graph["MTA_recv"] += 1 # node received updated information that it used

                    if(x not in sendingQueue):
                        sendingQueue.append(x)

        sendingQueue.pop(topNode)
    
    resultOutput = ""
    for node in Graph:
        resultOutput += "{0}\n".format(node)
        for path in Graph.nodes[node]['pathBundle']:
            resultOutput += "\t{0}\n".format(path)
    logFile.write("\n=====RESULT=====\n" + resultOutput)
    
    logFile.close()    

    return


def hamiltonAlgo(Graph, source, NP):
    
    createMeshedTreeDatatStructures(Graph, source) # Every vertex is given a single-character ID (starting with 'A') 

    for vertex in Graph:
        Graph.nodes[vertex]['pathBundle'] = [] # A data structure (list for Python) to hold paths to the vertex from the root
        Graph.nodes[vertex]['inBasket']   = [] # A data structure (list for Python) to hold path bundles send from nbrs to vertex

    Graph.nodes[source]['pathBundle'].append(Graph.nodes[source]['ID']) # source's path bundle contains only the trivial path RID (Root ID)
    
    sending = set([source]) # Sending is the set containing any vertex ready to send its path bundle.

    nextSending = []    # Verticies that need to send a path bundle update to nbrs during the next cycle
    receiving   = set() # Verticies that have received a path bundle update from a nbr

    sendingEvents = []
    sendingEvents2 = []

    while sending: # Convergence happens when sending goes empty
        sendingEvents.append(len(sending))
        sendingEvents2.append((len(sending),sending))

        # Clear structures that keep track of who needs to send path bundles and who has received them
        nextSending.clear()
        receiving.clear()

        for u in sending: # For each vertex u in the sending list
            u_pathBundle = Graph.nodes[u]['pathBundle']
            for v in Graph.neighbors(u): # For each vertex v who is a nbr of vertex u
                v_inBasket = Graph.nodes[v]['inBasket']
                v_inBasket.append(copy.deepcopy(u_pathBundle)) # old way: v_inBasket.extend(u_pathBundle)   # Add the paths in vertex u's path bundle to vertex v's inBasket
                receiving.add(v) # Note that vertex v received a path bundle from a nbr (vertex u)

        for v in list(receiving):
            # Delete any path that already contains vertex v and append the vertex ID to the end of valid paths
            v_grandBundle = mergeBundles(Graph.nodes[v], NP)

            del v_grandBundle[NP:] # Delete paths in the grand bundle until it is has the shortest NP paths

            pbChanges = list(set(v_grandBundle).difference(set(Graph.nodes[v]['pathBundle']))) # Check if the path bundle has been updated

            # If there are updates to the path bundle, the vertex needs to send an update
            if(pbChanges):
                Graph.nodes[v]['pathBundle'] = v_grandBundle
                nextSending.append(v)

            Graph.nodes[v]['inBasket'].clear() # Clear the inBasket for this cycle
    
        sending = nextSending.copy() # Get the new list of verticies that need to send updates

    return sendingEvents, sendingEvents2


def mergeBundles(v, NP):
    finishedMerging = False
    bestPath = 0 # First entry (index 0) is always the current best path
    v_grandBundle = copy.deepcopy(v['pathBundle'])

    while(not finishedMerging):
        # Pythonic representation of a more efficient for loop
        bestPaths = [pathBundle.pop(bestPath) + v['ID'] for pathBundle in v['inBasket'] if pathBundle and v['ID'] not in pathBundle[bestPath]]
        v_grandBundle = list(merge(v_grandBundle, bestPaths, key=len))

        if(len(v_grandBundle) >= NP or not bestPaths):
            finishedMerging = True

    return v_grandBundle


def PanAlgo(Graph, root):
    logFile = open("algoOutput.txt", "a")

    createMeshedTreeDatatStructures(Graph, root) # Every vertex is given a single-character ID (starting with 'A')

    INFINITE = -1 # Representing a hop count value of infinity as a negative hop count value
    topNode = 0 # Representing the first index of the queue

    # Assign the root's hop count value = 0
    Graph.nodes[root]['hopCountValue'] = 0
    logFile.write("root ({0}) hop count value = 0\n".format(root))

    # Counts the number of times a given node is added to the sending queue and sends updates, for complexity calculations
    nodeSendingCount = {}

    # Birds-eye-view sending queue to not send to additional nodes.

    # All other verticies hop count value = INFINITE
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['hopCountValue'] = INFINITE
            logFile.write("{0} hop count value = INFINITE\n".format(vertex))

            # For each vertex v in graph, pathBundle[v] <-- []
            Graph.nodes[vertex]['pathBundle'] = []
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logFile.write("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

        # Checks whether or not a node has reached NP paths
        #Graph.nodes[vertex]['atMaxPaths'] = False
        # Counts the number of times a node has to send an update to a neighbor (decreases as atMaxPaths becomes true)
        Graph.nodes[vertex]['updateCounter'] = 0

        nodeSendingCount[vertex] = 0

    # Define max paths
    maxPaths = 3

    sendingQueue = [root] # Queue being represented as list data structure

    # Count the number of iterations needed to send all updates
    queueCounter = 0

    # Define function sending(v)
    while sendingQueue:
        # Update meta-information about algorithm sending queue
        queueCounter += 1
        logFile.write("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendingQueue))

        # v is the top node in the sending queue
        v = sendingQueue[topNode]
        logFile.write("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))
        nodeSendingCount[v] += 1

        # For each neighbor x of v
        for x in Graph.neighbors(v):
            logFile.write("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))

            if(Graph.nodes[x]['hopCountValue'] == INFINITE):
                Graph.nodes[x]['hopCountValue'] = Graph.nodes[v]['hopCountValue'] + 1
                logFile.write("\tHop count value updated to {0}\n".format(Graph.nodes[x]['hopCountValue']))

            logFile.write("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

            if(len(Graph.nodes[x]['pathBundle']) < maxPaths and x != root):
                # Update the senders count because it has to transmit its path bundle to a neighbor without the max number of paths
                Graph.nodes[v]['updateCounter'] += 1

                # Append 'x' to each of v's paths in v's path bundle if not already in the path bundle
                newPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path and path + Graph.nodes[x]['ID'] not in Graph.nodes[x]['pathBundle']]
                logFile.write("\tNew path(s): {0}\n".format(newPaths))

                # Add these paths to x's path bundle
                Graph.nodes[x]['pathBundle'].extend(newPaths)
                logFile.write("\tUpdated path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

                # Remove extra paths (keep only 3)
                logFile.write("\tRemoved paths: {0}\n".format(Graph.nodes[x]['pathBundle'][maxPaths:]))
                del Graph.nodes[x]['pathBundle'][maxPaths:]
                
                logFile.write("\tUpdated path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

                # Add 'x' to the sending queue if not already in the queue (issue: it may never hit 3 paths, have to fix this)
                if x not in sendingQueue and newPaths:
                    sendingQueue.append(x)
                    logFile.write("\tNode appended to sending queue\n")

                logFile.write("\n")

            else:
                logFile.write("\t Max path limit hit (or root), no changes.\n\n")

        # Remove 'v' from the sending queue now that we are done with each neighbor
        sendingQueue.pop(topNode)

    logFile.write("-----------\nFINAL RESULTS: \n")
    for vertex in Graph:
        logFile.write("{0} ({1})\n\tpath bundle = {2}\n\thop count = {3}\n\tqueue count = {4}\n\tsending count = {5}\n\n"
            .format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], Graph.nodes[vertex]['hopCountValue'], nodeSendingCount[vertex], Graph.nodes[vertex]['updateCounter']))

    logFile.close()

    return nodeSendingCount


def getPathEdgeSet(path):
    edgeSet = []

    if path:
        if len(path) <= 2:
            edgeSet = [path]

        else:
            vertexSet = list(path)

            for currentEdge in range(1,len(vertexSet)): #vertexSet-1
                #edgeSet[currentEdge-1] =  edgeSet[currentEdge-1] + edgeSet[currentEdge]
                edgeSet.append(vertexSet[currentEdge-1] + vertexSet[currentEdge])

    return edgeSet


def mergePathBundles(pathBundle1, pathBundle2):
    greatBundle = []

    if not pathBundle1 and not pathBundle2:
       return greatBundle

    elif pathBundle1 and not pathBundle2:
       return greatBundle + pathBundle1

    elif not pathBundle1 and pathBundle2:
       return greatBundle + pathBundle2

    elif pathBundle1 and pathBundle2:
       if (len(pathBundle1[0]) < len(pathBundle2[0])) or (len(pathBundle1[0]) == len(pathBundle2[0]) and pathBundle1[0] < pathBundle2[0]):
          greatBundle.append(pathBundle1[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1[1:], pathBundle2)

       else:
          greatBundle.append(pathBundle2[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1, pathBundle2[1:])

    return greatBundle