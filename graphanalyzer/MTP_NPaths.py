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
MAX_PATHS = 3
LOG_FILE = "results/log_results/MTA_NPath_Output.log"
LOG_FILE_BATCH = "C:/Users/peter/Desktop/Research/mtp-analysis/results/log_results/MTA_NPath_batch_test.csv"
LOG_FILE_ERROR = "C:/Users/peter/Desktop/Research/mtp-analysis/results/log_results/VmFailure_{}.graphml"

def createMeshedTreeDatatStructures(G, root):
    IDCount = 0
    G.graph['ID_to_vertex'] = {} # Define a graph-wide dictionary to translate IDs back to vertices

    for node in sorted(G.nodes):
        # Add a mapping in both directions, node --> ID (vertex-level) and ID --> node (graph-level)
        G.nodes[node]['ID'] = chr(65 + IDCount)
        G.graph['ID_to_vertex'][chr(65 + IDCount)] = node
    
        if(node == root):
            logging.warning("Root node is {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))
        else:
            logging.warning("Non-Root node {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        IDCount += 1

    logging.warning("---------\n\n")

    return

def init(Graph, root, loggingStatus, batch=False, removal=None):
    setLoggingLevel(loggingStatus, batch)
    createMeshedTreeDatatStructures(Graph, root) # Every vertex is given a single-character ID (starting with 'A')
    treeValidator = TreeValidator(Graph.nodes, root) # Create a validation object to make sure the result is a tree

    Graph.graph["step"] = 0

    # Counts the number of times a given node is added to the sending queue and sends updates, for complexity calculations
    nodeSendingCount = {}

    # Birds-eye-view sending queue to not send to additional nodes.

    for vertex in Graph:
        Graph.nodes[vertex]['sendCount'] = 0
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = []
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))
        else:
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            Graph.graph["step"] += 1
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

    sendingQueue = [root] # Queue being represented as list data structure

    # Count the number of iterations needed to send all updates
    queueCounter = 0

    # Define function sending(v)
    while sendingQueue:
        # Update meta-information about algorithm sending queue
        queueCounter += 1
        logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendingQueue))

        # v is the top node in the sending queue
        v = sendingQueue[TOP_NODE]
        logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n".format(v, Graph.nodes[v]['pathBundle']))
        Graph.nodes[v]['sendCount'] += 1

        # For each neighbor x of v
        for x in Graph.neighbors(v):
            logging.warning("NEIGHBOR: {0} ({1})".format(x, Graph.nodes[x]['ID']))
            logging.warning("\tCurrent path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

            if(len(Graph.nodes[x]['pathBundle']) < MAX_PATHS and x != root):
                # Append 'x' to each of v's paths in v's path bundle if not already in the path bundle
                validPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path and path + Graph.nodes[x]['ID'] not in Graph.nodes[x]['pathBundle']]
                if(validPaths):
                    logging.warning("\tNew path(s): {0}".format(validPaths))

                    # Add these paths to x's path bundle
                    Graph.nodes[x]['pathBundle'] = mergePathBundles(copy.deepcopy(Graph.nodes[x]['pathBundle']), validPaths, Graph)
                    logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

                    # Remove extra paths (keep only 3)
                    logging.warning("\tRemoved paths: {0}".format(Graph.nodes[x]['pathBundle'][MAX_PATHS:]))
                    del Graph.nodes[x]['pathBundle'][MAX_PATHS:]

                    logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[x]['pathBundle']))

                    # If this vertex (x) is now a child of the sender (v), update the tree validator with that information
                    if(Graph.nodes[x]['pathBundle'][0][-2] == Graph.nodes[v]['ID']):
                        treeValidator.addParent(v, x)

                    # Add 'x' to the sending queue if not already in the queue, but you need to see if something changes perhaps? Not just that you have new paths
                    if x not in sendingQueue:
                        sendingQueue.append(x)
                        logging.warning("\tNode appended to sending queue.")

                else:
                    logging.warning("\tNo new paths, no changes.")
            else:
                logging.warning("\tMax path limit hit (or root), no changes.")

        # Remove v from the sending queue now that we are done with each neighbor
        sendingQueue.pop(TOP_NODE)

    logging.warning("-----------\nFINAL RESULTS:\n")
    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    # Confirm that what is created is a tree
    logging.warning("Results is a tree: {0}".format(treeValidator.isTree()))
    
    # Network survival stats
    Vm, probOfSurvival = calculateNetworkSurvival(Graph, root)
    logging.warning("|Vm| = {0}".format(len(Vm)))
    logging.warning("Probability of network survival >= {:0.2f}%".format(probOfSurvival*100))

    # If an edge is to be removed and the resulting tree studied
    if(removal):
        removalResults = analyzeEdgeRemoval(Graph, root, removal[0], removal[1], Vm, batch)
        # For batch testing
        if(batch):
            logging.error("{0},{1},{2},{3},{4:.2f},{5},{6},{7},{8},{9:.2f},{10}"
            .format(treeValidator.isTree(), Graph.number_of_nodes(), Graph.number_of_edges(), len(Vm), (probOfSurvival*100), removal, removalResults[0], removalResults[1], removalResults[2], removalResults[3], removalResults[4]))

    elif(batch):
        logging.error("{0},{1},{2},{3},{4:.2f}"
        .format(treeValidator.isTree(), Graph.number_of_nodes(), Graph.number_of_edges(), len(Vm), (probOfSurvival*100)))

    return Vm


def analyzeEdgeRemoval(Graph, root, nodeWithRemovedEdge1, nodeWithRemovedEdge2, Vm, batch=False):
    removedEdge = Graph.nodes[nodeWithRemovedEdge1]['ID'] + Graph.nodes[nodeWithRemovedEdge2]['ID']
    removedEdgeFlipped = Graph.nodes[nodeWithRemovedEdge2]['ID'] + Graph.nodes[nodeWithRemovedEdge1]['ID']

    removedPathCount = 0
    totalNumberOfPaths = 0

    treeValidator = TreeValidator(Graph.nodes, root) # Create a validation object to make sure the result is a tree

    for vertex in Graph:
        if(vertex != root):
            totalNumberOfPaths += len(Graph.nodes[vertex]['pathBundle'])

            res = set(filter(lambda x: removedEdge in x or removedEdgeFlipped in x, Graph.nodes[vertex]['pathBundle']))
            removedPathCount += len(res)

            Graph.nodes[vertex]['pathBundle'] = [e for e in Graph.nodes[vertex]['pathBundle'] if e not in res]

            if(Graph.nodes[vertex]['pathBundle']):
                parentID = Graph.nodes[vertex]['pathBundle'][0][-2]
                treeValidator.addParent(Graph.graph['ID_to_vertex'][parentID], vertex)

    isStrandedVerticesInVm = False
    strandedVertices = treeValidator.getStrandedVertices()
    strandedVerticesInVm = set(strandedVertices).intersection(Vm.keys())

    if(strandedVerticesInVm):
        isStrandedVerticesInVm = True
        BadGraph = nx.Graph(incoming_graph_data=Graph.edges)
        stamp = uuid.uuid4().hex[:10]
        write_graphml(BadGraph, LOG_FILE_ERROR.format(stamp))

    logging.warning("-----------\nUPDATED RESULTS:\nremoved edge: {0}/{1}\n".format(removedEdge, removedEdgeFlipped))

    for vertex in sorted(Graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    logging.warning("total paths before removal: {0}\ntotal paths lost: {1}\npercent of paths lost: {2:.2f}%".format(totalNumberOfPaths, removedPathCount, (removedPathCount/totalNumberOfPaths)*100))
    logging.warning("Result is a tree: {0}".format(treeValidator.isTree()))
    logging.warning("Stranded vertices: {0}".format(strandedVertices))
    logging.warning("Stranded vertices in Vm: {0}".format(isStrandedVerticesInVm))

    if(batch):
        return [treeValidator.isTree(), totalNumberOfPaths, removedPathCount, (removedPathCount/totalNumberOfPaths)*100, isStrandedVerticesInVm]

    return


def mergePathBundles(pathBundle1, pathBundle2, Graph):
    greatBundle = []

    Graph.graph["step"] += 1
    if not pathBundle1 and not pathBundle2:
        return greatBundle

    elif pathBundle1 and not pathBundle2:
        #Graph.graph["step"] += 1
        return greatBundle + pathBundle1

    elif not pathBundle1 and pathBundle2:
        #Graph.graph["step"] += 1
        return greatBundle + pathBundle2

    elif pathBundle1 and pathBundle2:
       if (len(pathBundle1[0]) < len(pathBundle2[0])) or (len(pathBundle1[0]) == len(pathBundle2[0]) and pathBundle1[0] < pathBundle2[0]):
          greatBundle.append(pathBundle1[0])
          #Graph.graph["step"] += 1
          greatBundle = greatBundle +  mergePathBundles(pathBundle1[1:], pathBundle2, Graph)

       else:
          greatBundle.append(pathBundle2[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1, pathBundle2[1:], Graph)

    return greatBundle


def calculateNetworkSurvival(G, root):
    # Maximum number of remedy paths in a bundle, meaning it does not include the primary path
    m = MAX_PATHS - 1
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