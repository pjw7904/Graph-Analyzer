## Custom modules
from MTA import MTA
import MTA_RP # MTA Remedy Path algorithm
import MTP_NPaths # MTA N-Path algorithm
import MTP_NPaths_BFS # MTA N-Path BFS algorithm
import RSTA # Rapid Spanning Tree algorithm
import DA # Dijkstra's algorithm
import YA # Yen's Algorithm
import logging
import networkx as nx
import Propagation
from os.path import join as getFile

LOG_FILE = "{}{}_Output.log"
LOG_FILE_BATCH = "{}batch_test.csv"

'''
Run the specified SPT algorithm with any included additional options
'''
def runAlgorithmOnGraph(graph, args, logFilePath, nameOfTest, batch=False):
    # set logging for the simulation
    setLoggingLevel(logFilePath, batch, nameOfTest, args.algorithm)

    # Make sure the root is the right type
    root = sanatizeRootType(args.root)

    # Start IDs at 'A'
    IDCount = 0

    # Initalize a distributed algorithm for each vertex in the graph
    for vertex in sorted(graph.nodes):
        id = chr(65 + IDCount)

        if(vertex == root):
            logging.warning(f"{vertex} (root) ID = {id}\n")
            isRoot = True
        else:
            logging.warning(f"{vertex} ID = {id}\n")
            isRoot = False

        # Meshed Tree Algorithm - Remedy Paths 
        if(args.algorithm == "mta"):
            graph.nodes[vertex]['algo'] = MTA(vertex, id, isRoot)

        else:
            raise nx.NetworkXError("Algorithm type is not valid")

        if(IDCount == 25): # jump to lowercase Latin alphabet
            IDCount += 7
        elif(IDCount == 57): # jump to additional letters beyond standard Latin alphabet 
            IDCount = 192
        else:
            IDCount += 1

    # Execute the test
    Propagation.runTest(graph, root)

    return

'''
Determine if the root identifier type is an int or string
'''
def sanatizeRootType(root):
    if(isinstance(root, int)):
        return root
    if(root.isdigit()):
        return int(root)
    else:
        return root

'''
Determine if an edge exists to remove
'''
def removedEdge(graph, edge):
    if(edge and len(edge) == 2 and graph.has_edge(int(edge[0]), int(edge[1]))):
        return edge
    else:
        return None

'''
Determine how much logging is required for a given simulation
'''
def setLoggingLevel(logFilePath, batch, testName, algoName):
    if(testName):
        testName = testName + "_"
    else:
        testName = ""

    if(batch):
        logging.basicConfig(format='%(message)s', filename=getFile(logFilePath, LOG_FILE_BATCH.format(testName)), filemode='a', level=logging.ERROR) 
    else:
        #logging.basicConfig(format='%(message)s', filename=getFile(logFilePath, LOG_FILE.format(testName, algoName)), filemode='w', level=logging.WARNING)
        logging.basicConfig(handlers=[logging.FileHandler(filename=getFile(logFilePath, LOG_FILE.format(testName, algoName)), 
                                                          encoding='utf-8', mode='w')],
                                                          format='%(message)s',
                                                          level=logging.WARNING)
    return