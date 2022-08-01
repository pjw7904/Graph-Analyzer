from random import seed
import sys
import networkx as nx
from os.path import join as getFile

'''
Generate a single graph to study
'''
def generateGraph(graphType, graphConfig, graphDirectory=None):
    maxAttempts = 25
    currentAttempt = 0

    if(graphType == "graphml"):
        return fromGraphml(getFile(graphDirectory, graphConfig["fileName"]))
    elif(graphType == "leg"):
        return generateLeg(graphConfig["legLength"])
    else:
        while(currentAttempt != maxAttempts):
            if(graphType == "binomial"):
                G = generateBinomialGraph(graphConfig["numberOfVertices"], graphConfig["edgeProbability"])
            elif(graphType == "smallWorld"):
                G = generateSmallWorldGraph(graphConfig["numberOfVertices"], graphConfig["connectedNearestNeighbors"], graphConfig["rewiringProbability"])
            elif(graphType == "harary"):
                G = generateHararyGraph(graphConfig["nodeConnectivity"], graphConfig["numberOfVertices"])
            elif(graphType == "kRegular"):
                G = generateRegularGraph(graphConfig["sharedDegree"], graphConfig["numberOfVertices"])
            elif(graphType == "torus"):
                G = generateTorusGraph(graphConfig["rowsOfVertices"], graphConfig["columnsOfVertices"])
            elif(graphType == "ring"):
                G = generateRingGraph(graphConfig["numberOfVertices"])
            elif(graphType == "internet"):
                G = generateInternetGraph(graphConfig["numberOfVertices"])
            elif(graphType == "foldedClos"):
                G = generateFoldedClosGraph(graphConfig["sharedDegree"], graphConfig["numberOfTiers"])
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
Folded-Clos/Fat-Tree Graph
k = Degree shared by each node
l = Number of tiers in the graph
'''
def generateFoldedClosGraph(k, l):
    def generatePod(G, tier, k, podPrefix="", numNodesAbove=0, topTier=False):
        if(topTier):
            for podNum in range(1, k+1):
                podPrefix = "P{}".format(podNum)
                generatePod(G, tier-1, k, numNodesAbove=int(numNodesAbove/int(k/2)), podPrefix=podPrefix) 
                
                # for each super spine node
                for spine in range(1, int(numNodesAbove/int(k/2))+1):
                    spineNode = podPrefix + "_S{spineNum}".format(spineNum=spine)
                    # for each edge to a super spine node, step every other (2)
                    for port in range(0,int((k/2))):
                        superSpineNode = "TS{spineNum}".format(spineNum=spine+(int(numNodesAbove/int(k/2)*port)))
                        G.add_edge(spineNode, superSpineNode)

        # At tier one (leaf nodes), half of your ports (k/2) go to servers, the other half go to spines
        elif(tier == 1):
            # for each leaf node
            for leaf in range(1, int((k/2)+1)):
                leafNode = podPrefix + "_L{leafNum}".format(leafNum=leaf)
                # for each edge to a spine node
                for port in range(1,int((k/2)+1)):
                    spineNode = podPrefix + "_S{spineNum}".format(spineNum=port)
                    G.add_edge(leafNode, spineNode)

        # At tier one (first spines), 
        elif(tier == 2):
            for podNum in range(1, int((k/2)+1)):
                generatePod(G, tier-1, k, podPrefix)

        else:   
            for podNum in range(1, int((k/2)+1)):
                prefix = podPrefix + "P" + str(podNum)
                generatePod(G, tier-1, k, podPrefix=prefix, numNodesAbove=int(numNodesAbove/int(k/2)))

                # for each super spine node
                for spine in range(1, int(numNodesAbove/int(k/2))+1):
                    spineNode = prefix + "_S{spineNum}".format(spineNum=spine)
                    # for each edge to a super spine node, step every other (2)
                    for port in range(0,int((k/2))):
                        superSpineNode = podPrefix + "_S{spineNum}".format(spineNum=spine+(int(numNodesAbove/int(k/2)*port)))
                        G.add_edge(spineNode, superSpineNode)
        return

    numTopTierSpineNodes = (k/2)**(l-1)

    if(l < 2):
        raise nx.NetworkXError("folded-Clos topologies cannot have the number of tiers < 2. The minimum is 2.")

    G = nx.Graph()
    generatePod(G, l, k, numNodesAbove=numTopTierSpineNodes, topTier=True)

    return G

def generateLeg(legLen, legNum=""):
    graph = nx.Graph()
    currentLen = 1

    graph.add_edge("L{}_LF".format(legNum), "L{}_LT1".format(legNum))
    graph.add_edge("L{}_LF".format(legNum), "L{}_LB1".format(legNum))
    
    graph.add_edge("L{}_RF".format(legNum), "L{}_RT1".format(legNum))
    graph.add_edge("L{}_RF".format(legNum), "L{}_RB1".format(legNum))
    

    while(currentLen != legLen+1):
        # connect top and bottom
        graph.add_edge("L{}_LT{}".format(legNum, currentLen), "L{}_LB{}".format(legNum, currentLen))
        graph.add_edge("L{}_RT{}".format(legNum, currentLen), "L{}_RB{}".format(legNum, currentLen))

        # connect left and right
        graph.add_edge("L{}_LT{}".format(legNum, currentLen), "L{}_RT{}".format(legNum, currentLen))
        graph.add_edge("L{}_LB{}".format(legNum, currentLen), "L{}_RB{}".format(legNum, currentLen))

        if(currentLen != 1):
            # connect to back
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


'''
Graph is checked to be valid based on our constraints
'''
def isValidGraph(G):
    if(nx.is_connected(G) and nx.node_connectivity(G) >= 2):
        return True 
    else:
        return False