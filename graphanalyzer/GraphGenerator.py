import sys
import networkx as nx


'''
Graphml Graph (import)
sourceFile = the graphml file
'''
def fromGraphml(sourceFile):
    try:
        G = nx.read_graphml(path=sourceFile)
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
def generateErdosRenyiGraph(n, p, inputSeed=None):
    return nx.gnp_random_graph(n, p, seed=inputSeed, directed=False)

'''
Ring Graph
n = Number of vertices
'''
def generateRingGraph(n):
    return nx.cycle_graph(n)

'''
Harary Graph
k = Node-connectivity of graph
n = Number of verticies
'''
def generateHararyGraph(k, n):
    return nx.hkn_harary_graph(k, n)

'''
K-Regular Graph
d = Degree shared by each node
n = Number of verticies
'''
def generateRegularGraph(d, n, inputSeed=None):
    return nx.random_regular_graph(d,n, seed=inputSeed)

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
    numLeafNodes = 2*(k/2)**(l-1)
    numOfHosts = 2*(k/2)**l

    if(l < 2):
        print("tier value is less than 2")
        return
    elif(l == 2):
        numOfPods = 1
    elif(l > 2):
        numOfPods = 2*(k/2)**(l-2)
    
    print("num of top tier nodes: {0}\nnum of leaf nodes: {1}\nnum of hosts: {2}\nnum of pods: {3}"
        .format(numTopTierSpineNodes, numLeafNodes, numOfHosts, numOfPods))

    G = nx.Graph()
    generatePod(G, l, k, numNodesAbove=numTopTierSpineNodes, topTier=True)

    return G