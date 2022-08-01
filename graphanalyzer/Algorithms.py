## Custom modules
import MTA_RP # MTA Remedy Path algorithm
import MTP_NPaths # MTA N-Path algorithm
import MTP_NPaths_BFS # MTA N-Path BFS algorithm
import RSTA # Rapid Spanning Tree algorithm
import DA # Dijkstra's algorithm
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

    ## Run the specified algorithm
    # Rapid Spanning Tree Algorithm
    if(args.algorithm == "rsta"):
        RSTA.init(G=graph, r=root, logFilePath=logFilePath, batch=batch, testName=nameOfTest)

    # Meshed Tree Algorithm - N-Paths
    elif(args.algorithm == "npaths"):
        # If a valid edge is to be removed, it will be included in the analysis
        MTP_NPaths.init(Graph=graph, root=root, logFilePath=logFilePath, remedyPaths=args.remedy, m=args.backups, batch=batch, removal=removedEdge(graph, args.remove), testName=nameOfTest)

    # Meshed Tree Algorithm - N-Paths - BFS
    elif(args.algorithm == "bfs"):
        setLoggingLevel(logFilePath, batch, nameOfTest, args.algorithm)
        setVertexLabels(graph, root)
        MTP_NPaths_BFS.init(Graph=graph, root=root, m=args.backups)

    # Meshed Tree Algorithm - Remedy Paths 
    elif(args.algorithm == "mta"):
        MTA_RP.init(Graph=graph, root=root, logFilePath=logFilePath, batch=batch, testName=nameOfTest)

    # Dijkstra's Algorithm
    elif(args.algorithm == "da"):
        DA.init(Graph=graph, root=root, logFilePath=logFilePath, batch=batch, testName=nameOfTest)

    else:
        raise nx.NetworkXError("Graph type is not valid")

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
        logging.basicConfig(format='%(message)s', filename=getFile(logFilePath, LOG_FILE.format(testName, algoName)), filemode='w', level=logging.WARNING)

    return

'''
Create graph and node-wide structures for algorithm analysis

Graph = The graph the algorithm is run on
root = The root of the tree
'''
def setVertexLabels(Graph, root):
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