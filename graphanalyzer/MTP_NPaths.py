#!/usr/bin/env python
from heapq import merge # Merge function implemented for path bundle merging
from timeit import default_timer as timer # Get elasped time of execution
from TreeAnalyzer import TreeValidator
import copy
import logging

#
# Constants
#
TOP_NODE = 0
MAX_PATHS = 3
LOG_FILE = "results/log_results/MTA_NPath_Output.log"
LOG_FILE_BATCH = "results/log_results/batch_test.log"

def createMeshedTreeDatatStructures(G, root):
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)
    
        if(node == root):
            logging.warning("Root node is {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        else:
            logging.warning("Non-Root node {0}, ID = {1}\n".format(node, G.nodes[node]['ID']))

        IDCount += 1

    logging.warning("---------\n\n")

    return

def init(Graph, root, loggingStatus, batch=False):
    setLoggingLevel(loggingStatus, batch)
    createMeshedTreeDatatStructures(Graph, root) # Every vertex is given a single-character ID (starting with 'A')
    treeValidator = TreeValidator(Graph.nodes) # Create a validation object to make sure the result is a tree

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
        logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n\n".format(v, Graph.nodes[v]['pathBundle']))
        Graph.nodes[v]['sendCount'] += 1

        # For each neighbor x of v
        for x in Graph.neighbors(v):
            logging.warning("NEIGHBOR: {0} ({1})\n".format(x, Graph.nodes[x]['ID']))
            logging.warning("\tCurrent path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

            if(len(Graph.nodes[x]['pathBundle']) < MAX_PATHS and x != root):
                # Append 'x' to each of v's paths in v's path bundle if not already in the path bundle
                validPaths = [path + Graph.nodes[x]['ID'] for path in Graph.nodes[v]['pathBundle'] if Graph.nodes[x]['ID'] not in path and path + Graph.nodes[x]['ID'] not in Graph.nodes[x]['pathBundle']]
                if(validPaths):
                    logging.warning("\tNew path(s): {0}\n".format(validPaths))

                    # Add these paths to x's path bundle
                    Graph.nodes[x]['pathBundle'] = mergePathBundles(copy.deepcopy(Graph.nodes[x]['pathBundle']), validPaths, Graph)
                    logging.warning("\tUpdated path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

                    # Remove extra paths (keep only 3)
                    logging.warning("\tRemoved paths: {0}\n".format(Graph.nodes[x]['pathBundle'][MAX_PATHS:]))
                    del Graph.nodes[x]['pathBundle'][MAX_PATHS:]
                
                    logging.warning("\tUpdated path bundle: {0}\n".format(Graph.nodes[x]['pathBundle']))

                    # If this vertex is now a child of the sender, update the tree validator with that information
                    if(Graph.nodes[x]['pathBundle'][0][:-1] == Graph.nodes[v]['pathBundle'][0]):
                        treeValidator.addParent(v, x)

                    # Add 'x' to the sending queue if not already in the queue (issue: it may never hit 3 paths, have to fix this)
                    if x not in sendingQueue:
                        sendingQueue.append(x)
                        logging.warning("\tNode appended to sending queue\n")

                else:
                    logging.warning("\t No new paths, no changes.\n\n")

            else:
                logging.warning("\t Max path limit hit (or root), no changes.\n\n")

        # Remove 'v' from the sending queue now that we are done with each neighbor
        sendingQueue.pop(TOP_NODE)

    logging.warning("-----------\nFINAL RESULTS: \n")
    for vertex in Graph:
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    # Confirm that what is created is a tree
    logging.warning("Results in a tree: {0}".format(treeValidator.isTree()))

    # For batch testing
    logging.error("{0},{1},{2}".format(Graph.number_of_nodes(), Graph.number_of_edges(), Graph.graph["step"]))

    return nodeSendingCount


def analyzeEdgeRemoval(Graph, nodeWithRemovedEdge1, nodeWithRemovedEdge2):
    removedEdge = Graph.nodes[nodeWithRemovedEdge1]['ID'] + Graph.nodes[nodeWithRemovedEdge2]['ID']
    removedEdge2 = Graph.nodes[nodeWithRemovedEdge2]['ID'] + Graph.nodes[nodeWithRemovedEdge1]['ID']
    removedPathCount = 0
    totalNumberOfPaths = 0
    usedPaths = set()
    newUsedPaths = set()

    for vertex in Graph:
        newBundle = []
        
        # old way
        #res = set(filter(lambda x: removedEdge in x, Graph.nodes[vertex]['pathBundle']))
        #removedPathCount += len(res)

        totalNumberOfPaths += len(Graph.nodes[vertex]['pathBundle'])

        for path in Graph.nodes[vertex]['pathBundle']:
            usedPaths.update(getPathEdgeSet(path))

            if(removedEdge not in path and removedEdge2 not in path):
                newBundle.append(path)
            else:
                removedPathCount += 1

        Graph.nodes[vertex]['pathBundle'] = newBundle

        for path in Graph.nodes[vertex]['pathBundle']:
            newUsedPaths.update(getPathEdgeSet(path))

        # old way
        #Graph.nodes[vertex]['pathBundle'] = [e for e in Graph.nodes[vertex]['pathBundle'] if e not in res]

    logging.warning("-----------\nUPDATED RESULTS:\nremoved edge: {0}\n".format(removedEdge))

    for vertex in Graph:
        logging.warning("{0} ({1})\n\tpath bundle = {2}".format(vertex, Graph.nodes[vertex]['ID'], Graph.nodes[vertex]['pathBundle']))

    logging.warning("\ntotal paths before removal: {0}\ntotal paths lost: {1}\npercent of paths lost: {2:.2f}%".format(totalNumberOfPaths, removedPathCount, (removedPathCount/totalNumberOfPaths)*100))
   # logging.warning("\ntotal number of edges: {0}\nnumber edges used before removal: {1}\npercent of edges used before removal: {2:2f}\nnumber of edges used after removal: {3}\npercent of edges used after removal: {4:2f}"
    #                .format(Graph.number_of_edges(), str(usedPaths), (len(usedPaths)/Graph.number_of_edges())*100, len(newUsedPaths), (len(newUsedPaths)/Graph.number_of_edges())*100))
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


def setLoggingLevel(requiresLogging, batch):
    if(requiresLogging):
        if(batch):
            logging.basicConfig(format='%(message)s', filename=LOG_FILE_BATCH, filemode='a', level=logging.ERROR) 
        else:
            logging.basicConfig(format='%(message)s', filename=LOG_FILE, filemode='w', level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    return