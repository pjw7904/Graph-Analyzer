#!/usr/bin/env python
from heapq import merge 
import copy

def createMeshedTreeDatatStructures(G, root):
    logFile = open("algoOutput.txt", "w")

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
            print("- Root node is {0}, ID = {1}".format(node, G.nodes[node]['ID']))
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
            print("- Non-Root node {0}, ID = {1}".format(node, G.nodes[node]['ID']))
            logFile.write("Non-Root node {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        IDCount += 1

    print("---------\n")
    logFile.write("---------\n\n")
    logFile.close()

    return


def rootActions(G, root):
    rootConf = G.nodes[root]['rootInfo']

    if(rootConf['state'] == 'F'):
        print("hi")

        #for nbr in G.neighbors(root):
            #G.nodes[nbr]['nodeInfo']['inBasket'].extend(G.nodes[root]['rootInfo']['pathBundle'])
            #print(G.nodes[nbr]['nodeInfo']['inBasket'])

    return


def nodeActions():

    return


def runMTASimulation(G, root):
    rootActions(G, root)

    return


def tuesdayAlgo(Graph, source, NP):
    
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

        nodeSendingCount[vertex] = 0

    # Define max paths
    maxPaths = 3

    sendingQueue = [root] # Queue being represented as list data structure

    #sendingEvents = []
    #sendingEvents2 = []

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

        # For each neighbor x of (v)
        for x in Graph.neighbors(v):
            logFile.write("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))

            if(Graph.nodes[x]['hopCountValue'] == INFINITE):
                Graph.nodes[x]['hopCountValue'] = Graph.nodes[v]['hopCountValue'] + 1
                logFile.write("\tHop count value updated to {0}\n".format(Graph.nodes[x]['hopCountValue']))

            logFile.write("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

            if(len(Graph.nodes[x]['pathBundle']) < maxPaths):
                # Append 'x' to each of v's paths in v's path bundle if not already in the path bundle
                newPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path]
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
                logFile.write("\t Max path limit hit, no changes.\n\n")

        # Remove 'v' from the sending queue now that we are done with each neighbor
        sendingQueue.pop(topNode)
    
    logFile.close()

    return nodeSendingCount