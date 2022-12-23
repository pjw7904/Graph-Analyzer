#!/usr/bin/env python
'''
===========================
MESHED TREE ALGORITHM - N PATHS
===========================
'''
from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
from os.path import join as getFile
from TreeAnalyzer import TreeValidator
from networkx import single_source_shortest_path_length
from networkx import write_graphml
import copy
import logging
import networkx as nx
import uuid; # for output testing

#
# Constants
#
TOP_NODE = 0
LOG_FILE = "{}MTA_NPath_Output.log"
LOG_FILE_BATCH = "{}batch_test.csv"
LOG_FILE_ERROR = "C:/Users/peter/Desktop/Research/mtp-analysis/results/log_results/VmFailure_{}.graphml"

'''
Create graph and node-wide structures for algorithm analysis

Graph = The graph the algorithm is run on
root = The root of the tree
'''
def createMeshedTreeDatatStructures(Graph, root):
    IDCount = 0
    Graph.graph['ID_to_vertex'] = {} # Define a graph-wide dictionary to translate IDs back to vertices

    for node in sorted(Graph.nodes):
        # Add a mapping in both directions, node --> ID (vertex-level) and ID --> node (graph-level)
        Graph.nodes[node]['ID'] = chr(65 + IDCount)
        Graph.graph['ID_to_vertex'][chr(65 + IDCount)] = node
    
        if(node == root):
            logging.warning("Root node is {0}, ID = {1}\n".format(node, Graph.nodes[node]['ID']))
        else:
            logging.warning("Non-Root node {0}, ID = {1}\n".format(node, Graph.nodes[node]['ID']))

        IDCount += 1

    logging.warning("---------\n\n")

    return

'''
Meshed Tree Algorithm, N-Paths (MTA N-Paths)

Graph = The graph the algorithm is run on
root = The root of the tree
logFile = File to log results to
m = The maximum number of backup paths a vertex can hold in its path bundle 
batch = If batch testing (multiple tests one after the other rapidly) is being performed
removal = If an edge is to be removed after the init convergence, to study how the graph looks as a result
'''
def init(Graph, root, logFilePath, remedyPaths=False, m=2, batch=False, removal=None, testName=None):
    # Determine amount of information added to log file
    #setLoggingLevel(logFilePath, batch, testName)

    # Every vertex is given a single-character ID (starting with 'A')
    createMeshedTreeDatatStructures(Graph, root) 

    # Create a validation object to make sure the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root) 

    # step counter
    Graph.graph["step"] = 0

    # Give each vertex an empty path bundle structure to start
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = [] # The bundle structure is a list
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))
        else:
            # The root will add itself as the only path it will receive
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

    # Queue to determine who should be sending their bundle at a given discrete event
    sendingQueue = [] # The queue structure is a list

    # The maximum number of paths is the number of remedy paths (m) + the one primary path
    maxPaths = m + 1

    send(Graph, root, root, sendingQueue, remedyPaths, maxPaths, treeValidator)

    # Log the resulting path bundles, tree, and statistics if necessary
    logging.warning("-----------\nINIT RESULTS:\n")
    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    # Confirm that what is created is a tree
    logging.warning("Results is a tree: {0}".format(treeValidator.isTree()))
    
    # Network survival statistics
    Vm, probOfSurvival = calculateNetworkSurvival(Graph, root, m)
    logging.warning("|Vm| = {0}".format(len(Vm)))
    logging.warning("Probability of network survival >= {:0.2f}%".format(probOfSurvival*100))

    # Step stuff
    logging.warning("steps: {}".format(Graph.graph["step"]))

    # If an edge is to be removed and the resulting tree studied
    if(removal):
        recoveryTreeValidator = failureRecovery(Graph, root, removal[0], removal[1])

        # Log the resulting path bundles, tree, and statistics if necessary
        logging.warning("-----------\nRECOVERY RESULTS:\n")
        for vertex in sorted(Graph.nodes):
            logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], recoveryTreeValidator.relationshipStatus(vertex)))
    
        # Confirm that what is created is a tree
        logging.warning("Results is a tree: {0}".format(recoveryTreeValidator.isTree()))

        failureReconvergence(Graph, root, recoveryTreeValidator, remedyPaths, maxPaths)

    # if an edge is not being removed, but batch testing is occurring for the initial result
    elif(batch):
        logging.error("{},{},{},{},{},{:.2f}"
        .format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"], treeValidator.isTree(), len(Vm), (probOfSurvival*100)))

    # Return pertinent information, will change over time depending on the test 
    return Vm

def send(Graph, v, root, sendingQueue, remedyPaths, maxPaths, treeValidator: TreeValidator):
    logging.warning("-----------\nCURRENT QUEUE {0}".format(sendingQueue))
    logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n".format(v, Graph.nodes[v]['pathBundle']))

    # For each neighbor x of v
    for x in Graph.neighbors(v):
        logging.warning("NEIGHBOR: {0} ({1})".format(x, Graph.nodes[x]['ID']))
        logging.warning("\tCurrent path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

        # Append the ID of x to each of v's paths in its sent bundle if the path is not already in x's path bundle
        validPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path and path + Graph.nodes[x]['ID'] not in Graph.nodes[x]['pathBundle']]
        Graph.graph["step"] += 1

        # If there are paths left that survived the previous filter
        if(validPaths):
            logging.warning("\tNew path(s): {0}".format(validPaths))

            Graph.nodes[x]['oldPathBundle'] = copy.deepcopy(Graph.nodes[x]['pathBundle'])

            # Determine the algorithm to use to add paths to the path bundle
            if(remedyPaths):
                addRemedyPaths(Graph, x, validPaths)
            else:
                addAdditionalPaths(Graph, x, validPaths)

            # If the maximum number of paths has been exceeded, remove the extras
            if(len(Graph.nodes[x]['pathBundle']) > maxPaths):
                # Remove extra paths (keep only up to maxPaths)
                logging.warning("\tRemoved paths: {0}".format(Graph.nodes[x]['pathBundle'][maxPaths:]))
                del Graph.nodes[x]['pathBundle'][maxPaths:]
                Graph.graph["step"] += 1
                logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))
            
            # If the maximum number of paths is hit exactly, just note the resulting bundle
            elif(len(Graph.nodes[x]['pathBundle']) == maxPaths):
                logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

            # If x is now a child of v, note that updated relationship
            if(Graph.nodes[x]['pathBundle'][0][-2] == Graph.nodes[v]['ID']):
                treeValidator.addParent(v, x) # v is linked to x as a parent, x is linked to v as a child
            
            if Graph.nodes[x]['oldPathBundle'] != Graph.nodes[x]['pathBundle']:
                # Add x to the sending queue if not already in the queue (watch this for algorithm errors)
                if x not in sendingQueue:
                    sendingQueue.append(x)
                    logging.warning("\tNode appended to sending queue.")

        else:
            logging.warning("\tNo new paths, no changes.")

    # Remove v from the sending queue now that we are done with each neighbor
    s = sendingQueue.pop(TOP_NODE)
    if sendingQueue:
        send(Graph, s, root, sendingQueue, remedyPaths, maxPaths, treeValidator)

    return

'''
========================
EDGE FAILURE FUNCTIONS
========================
'''
def failureRecovery(Graph, root, brokenVertex1, brokenVertex2):
    # Determine the failed path ID (and its reverse, you won't know if the user put in the correct order)
    failedIDs = Graph.nodes[brokenVertex1]['ID'] + Graph.nodes[brokenVertex2]['ID']
    failedEdge = (failedIDs, failedIDs[::-1])
    print(failedEdge)

    # Set up recovery steps by clearing the init step count
    Graph.graph["step"] = 0

    # Remove the edge from the graph
    if(Graph.has_edge(brokenVertex1, brokenVertex2)):
        Graph.remove_edge(brokenVertex1, brokenVertex2)
    else:
        Graph.remove_edge(brokenVertex2, brokenVertex1)

    # Create a validation object to determine if the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root)

    # Propogate the failure of the edge
    Q = [brokenVertex1, brokenVertex2]
    while Q:
        v = Q.pop(0)
        for x in Graph.neighbors(v):
            # Add step for propogation
            Graph.graph["step"] += 1

            # Check if a path needs to be removed and do so
            bundleSize = len(Graph.nodes[x]['pathBundle'])
            Graph.graph["step"] += bundleSize
            Graph.nodes[x]['pathBundle'] = removePaths(Graph, x, failedEdge)

            # A path was removed
            if(bundleSize > len(Graph.nodes[x]['pathBundle'])):
                Q.append(x)

            # If the vertex still has paths in its bundle, determine its new parent and mark that relationship
            if(Graph.nodes[x]['pathBundle'] and x != root):
                parentID = Graph.nodes[x]['pathBundle'][0][-2]
                treeValidator.addParent(Graph.graph['ID_to_vertex'][parentID], x)

    return treeValidator

def failureReconvergence(Graph, root, treeValidator: TreeValidator, remedyPaths, maxPaths):
    # The ol' send queue, it needs to be the neighbors of the fallen brothers
    sendingQueue = []

    for vertex in treeValidator.getStrandedVertices():
        for neighbor in Graph.neighbors(vertex):
            sendingQueue.append(neighbor)

    if(not sendingQueue):
        logging.warning("-----------\nRECONVERGENCE RESULTS:\n")
        logging.warning("No stranded vertices, no change to bundles.")
        
        return

    else:
        s = sendingQueue.pop(0)
        send(Graph, s, root, sendingQueue, remedyPaths, maxPaths, treeValidator)

    logging.warning("-----------\nRECONVERGENCE RESULTS:\n")
    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    logging.warning("Results is a tree: {0}".format(treeValidator.isTree()))

    return

'''
Analyzing how the resulting MTA N-Path bundles hold up to an edge being removed

Graph = The graph the algorithm is run on
root = The root of the tree
vertexWithRemovedEdge1 = Vertex that lost an edge
vertexWithRemovedEdge2 = The other vertex that lost that same edge
Vm = Subset of vertex set V which should withstand an edge removal
batch = If batch testing (multiple tests one after the other rapidly) is being performed
'''
def edgeRemoval(Graph, root, vertexWithRemovedEdge1, vertexWithRemovedEdge2, Vm, batch=False):
    removedEdge = Graph.nodes[vertexWithRemovedEdge1]['ID'] + Graph.nodes[vertexWithRemovedEdge2]['ID']
    removedEdgeFlipped = Graph.nodes[vertexWithRemovedEdge2]['ID'] + Graph.nodes[vertexWithRemovedEdge1]['ID']

    # Counters to quantify the amount of loss to bundles
    removedPathCount = 0
    totalNumberOfPaths = 0

    # Create a validation object to determine if the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root)

    # Parse each vertices path bundle and remove the paths that utilize the now-removed edge
    for vertex in Graph:
        # Ignore the root, it cannot lose any paths
        if(vertex != root):
            totalNumberOfPaths += len(Graph.nodes[vertex]['pathBundle']) # Grab number of paths before any removals

            # Determine the set of paths in a path bundle that utilize the removed edge 
            res = set(filter(lambda x: removedEdge in x or removedEdgeFlipped in x, Graph.nodes[vertex]['pathBundle']))
            removedPathCount += len(res) # The size of the set is added to total lost path count

            # The path bundle of that vertex is updated to remove the now-obsolete path(s)
            Graph.nodes[vertex]['pathBundle'] = [e for e in Graph.nodes[vertex]['pathBundle'] if e not in res]

            # If the vertex still has paths in its bundle, determine its new parent and mark that relationship
            if(Graph.nodes[vertex]['pathBundle']):
                parentID = Graph.nodes[vertex]['pathBundle'][0][-2]
                treeValidator.addParent(Graph.graph['ID_to_vertex'][parentID], vertex)

    # Statistics for pathless vertices (stranded vertex) and if they were in subset Vm
    isStrandedVerticesInVm = False
    strandedVertices = treeValidator.getStrandedVertices()
    strandedVerticesInVm = set(strandedVertices).intersection(Vm.keys())

    # If a vertex was in Vm and is now stranded, save the graph for future analysis
    if(strandedVerticesInVm):
        isStrandedVerticesInVm = True
        BadGraph = nx.Graph(incoming_graph_data=Graph.edges)
        stamp = uuid.uuid4().hex[:10]
        write_graphml(BadGraph, LOG_FILE_ERROR.format(stamp))

    # Log results of the removal
    logging.warning("-----------\nUPDATED RESULTS:\nremoved edge: {0}/{1}\n".format(removedEdge, removedEdgeFlipped))
    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    logging.warning("total paths before removal: {0}\ntotal paths lost: {1}\npercent of paths lost: {2:.2f}%".format(totalNumberOfPaths, removedPathCount, (removedPathCount/totalNumberOfPaths)*100))
    logging.warning("Result is a tree: {0}".format(treeValidator.isTree()))
    logging.warning("Stranded vertices: {0}".format(strandedVertices))
    logging.warning("Stranded vertices in Vm: {0}".format(isStrandedVerticesInVm))

    # If batch testing is being used, return the derived stats for the batch log output with init results
    if(batch):
        return [treeValidator.isTree(), totalNumberOfPaths, removedPathCount, (removedPathCount/totalNumberOfPaths)*100, isStrandedVerticesInVm]

    return

'''
Backup path algorithm

Graph = The graph the algorithm is run on
vertex = The vertex whose path bundle is being modified
validPaths = Paths which are a canidate to be added to the vertex path bundle
'''
def addAdditionalPaths(Graph, vertex, validPaths):
    # Add these paths to x's path bundle
    Graph.nodes[vertex]['pathBundle'] = mergePathBundles(copy.deepcopy(Graph.nodes[vertex]['pathBundle']), validPaths, Graph)
    logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[vertex]['pathBundle']))
    Graph.graph["step"] += 1

    return

'''
Remedy path algorithm

Graph = The graph the algorithm is run on
vertex = The vertex whose path bundle is being modified
validPaths = Paths which are a canidate to be added to the vertex path bundle
'''
def addRemedyPaths(Graph, vertex, validPaths):
    # Form a great bundle B(v) by merging the path bundle with the paths from the calling vertex
    # Watch out with the doubling up of x in the lambda, did this change anything?
    greatBundle = list(merge(Graph.nodes[vertex]['pathBundle'], validPaths, key=lambda x: (len(x), x)))
    logging.warning("\tGreat bundle post-merge: {0}\n".format(greatBundle))

    # Remove the preferred path and create a new path bundle with it.
    P = copy.deepcopy(greatBundle[0])
    del greatBundle[0]
    Graph.nodes[vertex]['newPathBundle'] = [P] # the new path bundle with the preferred path

    logging.warning("\tNew path bundle created: {0}\n".format(Graph.nodes[vertex]['newPathBundle']))
    
    # NOTE: WATCH OUT FOR SHALLOW COPYING HERE AND BELOW
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
        logging.warning("\tRemedy Set ( T = s - E(Q) ): {0}\n".format(T))

        if(T):
            Graph.nodes[vertex]['newPathBundle'].append(Q)

            logging.warning("\tAdding new path: {0}\n".format(Q))

            # S now contains the remaining edges still in need of a remedy
            S = [edge for edge in S if edge not in T]
            logging.warning("\tUpdated S for remaining edges in need of a remedy: {0}\n".format(S))

    # If the new path bundle is different from the previous one, then the vertex must announce the new path bundle to neighbors
    if Graph.nodes[vertex]['newPathBundle'] != Graph.nodes[vertex]['pathBundle']:
        Graph.nodes[vertex]['pathBundle'] = Graph.nodes[vertex]['newPathBundle'] # WATCH FOR SHALLOW COPIES

        logging.warning("\tOfficial new path bundle for node: {0}\n".format(Graph.nodes[vertex]['pathBundle']))
        
        # Make sure the send queue is updated approp
        '''if(x not in sendQueue):
            sendQueue.append(x)'''

    return

def removePaths(Graph, vertex, failedEdge):
    return [path for path in Graph.nodes[vertex]['pathBundle'] if not any(map(path.__contains__, failedEdge))]


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

def mergePathBundles(pathBundle1, pathBundle2, Graph):
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
          greatBundle = greatBundle +  mergePathBundles(pathBundle1[1:], pathBundle2, Graph)

       else:
          greatBundle.append(pathBundle2[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1, pathBundle2[1:], Graph)

    return greatBundle


def calculateNetworkSurvival(G, root, m):
    # Maximum number of remedy paths in a bundle, meaning it does not include the primary path
    Vm = single_source_shortest_path_length(G, root, cutoff=m)

    # 1 - (|V|-|Vm|)/|E|
    probNetworkSurival = 1 - ((G.number_of_nodes() - len(Vm))/G.number_of_edges())

    return Vm, probNetworkSurival


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