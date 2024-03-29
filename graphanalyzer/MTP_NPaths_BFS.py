#!/usr/bin/env python
import copy
'''
===========================
MESHED TREE ALGORITHM - BFS N-PATHS
===========================
'''
import logging
import MTP_NPaths
from TreeAnalyzer import TreeValidator
from networkx import single_source_shortest_path_length, is_k_regular

#
# Constants
#
TOP_NODE = 0

def init(Graph, root, m=2, removal=None):
    # Create a validation object to make sure the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root) 

    # Give each vertex an empty path bundle structure to start
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = [] # The bundle structure is a list
            Graph.nodes[vertex]['visited'] = False
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))
        else:
            # The root will add itself as the only path it will receive
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            Graph.nodes[vertex]['visited'] = True
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

    # Determines if there are still nodes to send
    stillActive = True
    # Count the number of iterations needed to send all updates
    queueCounter = 0
    # The maximum number of paths is the number of remedy paths (m) + the one primary path
    maxPaths = m + 1
    # flip at each depth, start with True for the root
    reversed = True

    # Lists to hold the vertices
    currentDepthVertices = [root]
    nextDepthVertices = []

    while currentDepthVertices:
        for v in currentDepthVertices:
            queueCounter += 1
            logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, currentDepthVertices))
            logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n".format(v, Graph.nodes[v]['pathBundle']))
            
            for neighbor in Graph.neighbors(v):
                logging.warning("NEIGHBOR: {0} ({1})".format(neighbor, Graph.nodes[neighbor]['ID']))
                logging.warning("\tCurrent path bundle: {0}".format(Graph.nodes[neighbor]['pathBundle']))

                # Per BFS logic, mark the neighbor as visited if it has not already, add to queue
                if(not Graph.nodes[neighbor]['visited']):
                    Graph.nodes[neighbor]['visited'] = True
                    nextDepthVertices.append(neighbor)
                    logging.warning("\tVisited status: Marked as visited")
                else:
                    logging.warning("\tVisited status: Already visited")

                # Append the ID of x to each of v's paths in its sent bundle if the path is not already in x's path bundle
                validPaths = [
                                path + Graph.nodes[neighbor]['ID'] 
                                for path in Graph.nodes[v]['pathBundle'] 
                                if Graph.nodes[neighbor]['ID'] not in path 
                                and path + Graph.nodes[neighbor]['ID'] not in Graph.nodes[neighbor]['pathBundle']
                            ]

                # If there are paths left that survived the previous filter
                if(validPaths):
                    logging.warning("\tNew path(s): {0}".format(validPaths))
                    MTP_NPaths.addAdditionalPaths(Graph, neighbor, validPaths)
                    
                    # If the maximum number of paths has been exceeded, remove the extras
                    if(len(Graph.nodes[neighbor]['pathBundle']) > maxPaths):
                        logging.warning("\tRemoved paths: {0}".format(Graph.nodes[neighbor]['pathBundle'][maxPaths:]))
                        del Graph.nodes[neighbor]['pathBundle'][maxPaths:]
                        logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[neighbor]['pathBundle']))

                    # If the maximum number of paths is hit exactly, note that the bundle is full
                    elif(len(Graph.nodes[neighbor]['pathBundle']) == maxPaths):
                        logging.warning("\tUpdated path bundle: {0}".format(Graph.nodes[neighbor]['pathBundle']))

                    # If x is now a child of v, note that updated relationship
                    if(Graph.nodes[neighbor]['pathBundle'][0][-2] == Graph.nodes[v]['ID']):
                        # v is linked to neighbor as a parent, neighbor is linked to v as a child
                        treeValidator.addParent(v, neighbor)
                else:
                    logging.warning("\tNo new paths, no changes.")

        if(not reversed):
            currentDepthVertices.reverse()
            reversed = True
            logging.warning("\n++++++ REVERSE ++++++\n")

        else:
            currentDepthVertices = copy.deepcopy(nextDepthVertices)
            nextDepthVertices.clear()
            reversed = False

    # Log the results of the process
    logResults(Graph, treeValidator)

    return

def logResults(graph, treeValidator):
    # Log the resulting path bundles, tree, and statistics if necessary
    logging.warning("-----------\nFINAL RESULTS:\n")
    for vertex in sorted(graph.nodes):
        logging.warning("\t{0} ({1})\npath bundle = {2}\n{3}\n".format(vertex, graph.nodes[vertex]['ID'], graph.nodes[vertex]['pathBundle'], treeValidator.relationshipStatus(vertex)))

    # Confirm that what is created is a tree
    logging.warning("Results is a tree: {0}".format(treeValidator.isTree()))