#!/usr/bin/env python
from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
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
LOG_FILE = "results/log_results/MTA_NPath_Output.log"
LOG_FILE_BATCH = "C:/Users/peter/Desktop/Research/mtp-analysis/results/log_results/MTA_NPath_batch_test.csv"
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
loggingStatus = If algorithm process and/or result should be logged to a file
m = The maximum number of backup paths a vertex can hold in its path bundle 
batch = If batch testing (multiple tests one after the other rapidly) is being performed
removal = If an edge is to be removed after the init convergence, to study how the graph looks as a result
'''
def init(Graph, root, loggingStatus, m=2, batch=False, removal=None):
    # Determine amount of information added to log file
    setLoggingLevel(loggingStatus, batch)

    # Every vertex is given a single-character ID (starting with 'A')
    createMeshedTreeDatatStructures(Graph, root) 

    # Create a validation object to make sure the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root) 

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
    sendingQueue = [root] # The queue structure is a list

    # Count the number of iterations needed to send all updates
    queueCounter = 0

    # The maximum number of paths is the number of remedy paths (m) + the one primary path
    maxPaths = m + 1

    # Define function sending(v)
    while sendingQueue:
        # Update meta-information about algorithm sending queue
        queueCounter += 1
        logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendingQueue))

        # v is the top node in the sending queue, thus it is its turn to send its bundle
        v = sendingQueue[TOP_NODE]
        logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n".format(v, Graph.nodes[v]['pathBundle']))

        # For each neighbor x of v
        for x in Graph.neighbors(v):
            logging.warning("NEIGHBOR: {0} ({1})".format(x, Graph.nodes[x]['ID']))
            logging.warning("\tCurrent path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

            # If neighbor x has room for one or more paths in its bundle and it is not the root, process the bundle sent by v 
            if(len(Graph.nodes[x]['pathBundle']) < maxPaths and x != root):
                # Append the ID of x to each of v's paths in its sent bundle if the path is not already in x's path bundle
                validPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path and path + Graph.nodes[x]['ID'] not in Graph.nodes[x]['pathBundle']]
                
                # If there are paths left that surived the previous filter
                if(validPaths):
                    logging.warning("\tNew path(s): {0}".format(validPaths))

                    # Add these paths to x's path bundle
                    Graph.nodes[x]['pathBundle'] = mergePathBundles(copy.deepcopy(Graph.nodes[x]['pathBundle']), validPaths, Graph)
                    logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

                    # Remove extra paths (keep only maxPaths)
                    logging.warning("\tRemoved paths: {0}".format(Graph.nodes[x]['pathBundle'][maxPaths:]))
                    del Graph.nodes[x]['pathBundle'][maxPaths:]
                    logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

                    # If x is now a child of v, note that updated relationship
                    if(Graph.nodes[x]['pathBundle'][0][-2] == Graph.nodes[v]['ID']):
                        treeValidator.addParent(v, x) # v is linked to x as a parent, x is linked to v as a child

                    # Add x to the sending queue if not already in the queue (watch this for algorithm errors)
                    if x not in sendingQueue:
                        sendingQueue.append(x)
                        logging.warning("\tNode appended to sending queue.")

                else:
                    logging.warning("\tNo new paths, no changes.")
            else:
                logging.warning("\tMax path limit hit (or root), no changes.")

        # Remove v from the sending queue now that we are done with each neighbor
        sendingQueue.pop(TOP_NODE)

    # Log the resulting path bundles, tree, and statistics if necessary
    logging.warning("-----------\nFINAL RESULTS:\n")
    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    # Confirm that what is created is a tree
    logging.warning("Results is a tree: {0}".format(treeValidator.isTree()))
    
    # Network survival statistics
    Vm, probOfSurvival = calculateNetworkSurvival(Graph, root, m)
    logging.warning("|Vm| = {0}".format(len(Vm)))
    logging.warning("Probability of network survival >= {:0.2f}%".format(probOfSurvival*100))

    # If an edge is to be removed and the resulting tree studied
    if(removal):
        removalResults = edgeRemoval(Graph, root, removal[0], removal[1], Vm, batch)
        
        # For batch testing removals
        if(batch):
            logging.error("{0},{1},{2},{3},{4:.2f},{5},{6},{7},{8},{9:.2f},{10}"
            .format(treeValidator.isTree(), Graph.number_of_nodes(), Graph.number_of_edges(), len(Vm), (probOfSurvival*100), removal, removalResults[0], removalResults[1], removalResults[2], removalResults[3], removalResults[4]))

    # if an edge is not being removed, but batch testing is occurring for the initial result
    elif(batch):
        logging.error("{0},{1},{2},{3},{4:.2f}"
        .format(treeValidator.isTree(), Graph.number_of_nodes(), Graph.number_of_edges(), len(Vm), (probOfSurvival*100)))

    # Return pertinent information, will change over time depending on the test 
    return Vm

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


def setLoggingLevel(requiresLogging, batch):
    if(requiresLogging):
        if(batch):
            logging.basicConfig(format='%(message)s', filename=LOG_FILE_BATCH, filemode='a', level=logging.ERROR) 
        else:
            logging.basicConfig(format='%(message)s', filename=LOG_FILE, filemode='w', level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    return