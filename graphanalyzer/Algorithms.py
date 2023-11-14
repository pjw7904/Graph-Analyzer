## Custom modules
from MTA import MTA
from LSA import LSA
from RSTA import RSTA
from TreeAnalyzer import TreeValidator
import Test as Test

import logging
import networkx as nx
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

    # Holds node-specific data not related to its ID
    data = {}

    # Additional graph validator for SPT algorithms
    treeValidator = TreeValidator(root)
    treeNodes = []

    # Initalize a distributed algorithm for each vertex in the graph
    for vertex in sorted(graph.nodes):
        id = chr(65 + IDCount)
        data["neighbors"] = list(graph.neighbors(vertex))
        data["tree"] = treeValidator

        if(vertex == root):
            logging.warning(f"{vertex} (root) ID = {id}\n")
            data["isRoot"] = True
        else:
            logging.warning(f"{vertex} ID = {id}\n")
            data["isRoot"] = False

        # Meshed Tree Algorithm - Remedy Paths 
        if(args.algorithm == "mta"):
            treeValidator.addNode(id)
            graph.nodes[vertex]['algo'] = MTA(vertex, id, data)
        elif(args.algorithm == "da"):
            treeValidator.addNode(vertex)
            graph.nodes[vertex]['algo'] = LSA(vertex, id, data)
        elif(args.algorithm == "rsta"):
            treeValidator.addNode(id)
            graph.nodes[vertex]['algo'] = RSTA(vertex, id, data)
        else:
            raise nx.NetworkXError("Algorithm type is not valid")

        if(IDCount == 25): # jump to lowercase Latin alphabet
            IDCount += 7
        elif(IDCount == 57): # jump to additional letters beyond standard Latin alphabet 
            IDCount = 192
        else:
            IDCount += 1

    # Execute the test
    Test.runTest(graph, root, treeValidator)

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