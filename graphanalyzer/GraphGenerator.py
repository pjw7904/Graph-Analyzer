from random import seed
import sys
import Clos
import networkx as nx
from os.path import join as getFile


'''
Generate a single graph to study
'''
def generateGraph(graphType, graphConfig, seed=None, graphDirectory=None, logDirectory=None):
    maxAttempts = 25
    currentAttempt = 0

    if(graphType == "graphml"):
        return fromGraphml(getFile(graphDirectory, graphConfig["fileName"]))
    elif(graphType == "leg"):
        return generateRingLegs()
    elif(graphType == "foldedClos"):
        return generateFoldedClosGraph(graphConfig["sharedDegree"], graphConfig["numberOfTiers"], graphConfig, logDirectory)
    else:
        while(currentAttempt != maxAttempts):
            if(graphType == "binomial"):
                G = generateBinomialGraph(graphConfig["numberOfVertices"], graphConfig["edgeProbability"], inputSeed=seed)
            elif(graphType == "smallWorld"):
                G = generateSmallWorldGraph(graphConfig["numberOfVertices"], graphConfig["connectedNearestNeighbors"], graphConfig["rewiringProbability"], inputSeed=seed)
            elif(graphType == "harary"):
                G = generateHararyGraph(graphConfig["nodeConnectivity"], graphConfig["numberOfVertices"], inputSeed=seed)
            elif(graphType == "kRegular"):
                G = generateRegularGraph(graphConfig["sharedDegree"], graphConfig["numberOfVertices"], inputSeed=seed)
            elif(graphType == "torus"):
                G = generateTorusGraph(graphConfig["rowsOfVertices"], graphConfig["columnsOfVertices"])
            elif(graphType == "ring"):
                G = generateRingGraph(graphConfig["numberOfVertices"])
            elif(graphType == "internet"):
                G = generateInternetGraph(graphConfig["numberOfVertices"], inputSeed=seed)
            else:
                raise nx.NetworkXError("Graph type is not valid")
            
            if(isValidGraph(G)):
                return G
            else:
                currentAttempt += 1

    # If a graph cannot be generated, don't return anything
    raise nx.NetworkXError("Maximum number of tries exceeded to generate graph with valid constraints. Please modify configuration")

'''
Graphml Graph (import)
sourceFile = the graphml file
'''
def fromGraphml(sourceFile):
    try:
        G = nx.read_graphml(path=sourceFile, node_type=int)
    except FileNotFoundError:
        print("graphml graph file {0} does not exist in this location".format(sourceFile))
        sys.exit()

    return G

'''
Graphml Graph (export)
graph = the graph to export to graphml
filePath = the path and name of the graphml file
'''
def toGraphml(graph, filePath):
    nx.write_graphml(graph, filePath, prettyprint=True)
    return

'''
Erdős-Rényi Graph
n = Number of vertices
p = Probability of edge creation between two vertices
seed = seed value for generation
'''
def generateBinomialGraph(n, p, inputSeed=None):
    return nx.gnp_random_graph(n, p, seed=inputSeed, directed=False)

'''
n = Number of vertices
k = Each vertex is joined with its k nearest neighbors in a ring topology
p = The probability of rewiring each edge
tries = Number of attempts to generate a connected graph
'''
def generateSmallWorldGraph(n, k, p, tries=5, inputSeed=None):
    return nx.connected_watts_strogatz_graph(n, k, p, tries=tries, seed=inputSeed)

'''
Harary Graph
k = Node-connectivity of graph
n = Number of verticies
'''
def generateHararyGraph(k, n, inputSeed=None):
    return nx.hkn_harary_graph(k, n, seed=inputSeed)

'''
K-Regular Graph
d = Degree shared by each node
n = Number of verticies
'''
def generateRegularGraph(d, n, inputSeed=None):
    return nx.random_regular_graph(d, n, seed=inputSeed)

'''
Torus Graph
m = rows of vertices
n = columns of vertices
'''
def generateTorusGraph(m, n):
    return nx.grid_2d_graph(m,n,periodic=True)

'''
Ring Graph
n = Number of vertices
'''
def generateRingGraph(n):
    return nx.cycle_graph(n)

'''
Internet (AS-level) Graph
n = number of graph vertcies, must be in the range 1000-10000
'''
def generateInternetGraph(n, inputSeed=None):
    return nx.random_internet_as_graph(n, seed=inputSeed)

'''
Folded-Clos/Fat-Tree Graph (built via BFS)
k = Degree shared by each node
l = Number of tiers in the graph
'''
def generateFoldedClosGraph(k, t, options, logDirectory):
    return Clos.folded_clos_graph(k, t, options, logDirectory)

'''
John test graph
extra = the additional ring of nodes
'''
def generateRingLegs(extra=True):
    STANDARD_RING_LENGTH = 8
    graph = nx.Graph()

    def generateLeg(legLen, legNum=""):
        graph = nx.Graph()
        currentLen = 1

        graph.add_edge("L{}_LF".format(legNum), "L{}_LT1".format(legNum))
        graph.add_edge("L{}_LF".format(legNum), "L{}_LB1".format(legNum))
        
        graph.add_edge("L{}_RF".format(legNum), "L{}_RT1".format(legNum))
        graph.add_edge("L{}_RF".format(legNum), "L{}_RB1".format(legNum))
        
        while(currentLen != legLen+1):
            graph.add_edge("L{}_LT{}".format(legNum, currentLen), "L{}_LB{}".format(legNum, currentLen))
            graph.add_edge("L{}_RT{}".format(legNum, currentLen), "L{}_RB{}".format(legNum, currentLen))

            graph.add_edge("L{}_LT{}".format(legNum, currentLen), "L{}_RT{}".format(legNum, currentLen))
            graph.add_edge("L{}_LB{}".format(legNum, currentLen), "L{}_RB{}".format(legNum, currentLen))

            if(currentLen != 1):
                graph.add_edge("L{}_LT{}".format(legNum, currentLen), "L{}_LT{}".format(legNum, currentLen-1))
                graph.add_edge("L{}_RT{}".format(legNum, currentLen), "L{}_RT{}".format(legNum, currentLen-1))
                graph.add_edge("L{}_LB{}".format(legNum, currentLen), "L{}_LB{}".format(legNum, currentLen-1))
                graph.add_edge("L{}_RB{}".format(legNum, currentLen), "L{}_RB{}".format(legNum, currentLen-1))

            currentLen += 1

        graph.add_edge("L{}_E".format(legNum), "L{}_LT{}".format(legNum, legLen))
        graph.add_edge("L{}_E".format(legNum), "L{}_RT{}".format(legNum, legLen))
        graph.add_edge("L{}_E".format(legNum), "L{}_LB{}".format(legNum, legLen))
        graph.add_edge("L{}_E".format(legNum), "L{}_RB{}".format(legNum, legLen))

        return graph

    # generate 4 legs with a given leg length
    for legNum in range(1,5):
        graph.add_edges_from(generateLeg(2, str(legNum)).edges)
    #graph.add_edges_from(ring.edges)

    if(extra):
        ringNum = 1
        for legNum in range(1,5):
            graph.add_edge("L{}_LF".format(legNum), "R{}".format(ringNum))
            graph.add_edge("L{}_RF".format(legNum), "R{}".format(ringNum))

            if(legNum != 1):
                graph.add_edge("L{}_LF".format(legNum), "R{}".format(ringNum-1))
                graph.add_edge("L{}_RF".format(legNum), "R{}".format(ringNum+1))
            else:
                graph.add_edge("L{}_LF".format(legNum), "R{}".format(8))
                graph.add_edge("L{}_RF".format(legNum), "R{}".format(ringNum+1))
        
            ringNum += 2

        # inner rings
        for i in range (1,9):
            graph.add_edge("MT{}".format(i), "MB{}".format(i))

            graph.add_edge("MT{}".format(i), "R{}".format(i))
            graph.add_edge("MB{}".format(i), "R{}".format(i))

            if(i != 8):
                graph.add_edge("MT{}".format(i), "MT{}".format(i+1))
                graph.add_edge("MB{}".format(i), "MB{}".format(i+1))
            else:
                graph.add_edge("MT{}".format(i), "MT{}".format(1))
                graph.add_edge("MB{}".format(i), "MB{}".format(1))

    else:
        # attached the legs to the ring
        for legNum in range(1,5):
            graph.add_edge("L{}_LF".format(legNum), "L{}_RF".format(legNum))
            
            if(legNum != 4):
                graph.add_edge("L{}_RF".format(legNum), "L{}_LF".format(legNum+1))
            else:
                graph.add_edge("L{}_RF".format(legNum), "L{}_LF".format(1))

    return graph

'''
Graph is checked to be valid based on our constraints
'''
def isValidGraph(G):
    if(nx.is_connected(G) and nx.node_connectivity(G) >= 2):
        return True 
    else:
        return False