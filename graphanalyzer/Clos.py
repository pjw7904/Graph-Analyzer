import logging
import Algorithms
import random
import re
import networkx as nx
from copy import deepcopy
from collections import defaultdict

'''
In the context of vertices/interfaces/ports, there is an upper tier, "north", and a lower tier, "south"
======
north tier
======
|
|
======
south tier
======
'''

# Vertex prefixes to denote position in topology
TOF_NAME = "tof"
SPINE_NAME = "spine"
LEAF_NAME = "leaf"
COMPUTE_NAME = "compute"

# Specific tier values
LOWEST_SPINE_TIER = 2
LEAF_TIER = 1
COMPUTE_TIER = 0

'''
Starting function to build folded-Clos graphs
k = Degree shared by each node
t = Number of tiers in the graph
options = other configuration options
'''
def folded_clos_graph(k, t, options=None, logDirectory=None):
    # Make any modifications as needed prior to building the graph
    if(options):
        if(options["logging"] and logDirectory):
            name1 = "clos"
            name2 = "k{}_t{}".format(k,t)
            Algorithms.setLoggingLevel(logDirectory, False, name1, name2)

    # Build the graph
    graph = buildGraph(k, t)

    # Log resulting graph if necessary
    logGraphInfo(graph, k, t, t)

    # OTHER TESTS I'VE RUN
    #testBlocking(graph, t)
    #definePlanes(graph, t)

    return graph

def getNodeTitle(currentTier, topTier):
    if(currentTier == topTier):
        title = TOF_NAME    
    elif(currentTier > 1):
        title = SPINE_NAME
    elif(currentTier == 1):
        title = LEAF_NAME
    else:
        title = COMPUTE_NAME
    
    return title

def generateNodeName(prefix, nodeNum, currentTier, topTier):
    name = getNodeTitle(currentTier, topTier)

    if(currentTier == topTier):
        name += "-"
    else:
        name += prefix + "-"

    name += nodeNum

    return name

def generatePrefix(prefix, addition):
    return prefix + "-" + addition


def determinePrefixVisitedStatus(prefix, prefixList):
    if(prefix not in prefixList):
        prefixList.append(prefix)

    return

def isNotValidClosInput(k):
    if(k % 2 != 0):
        return True
    else:
        return False

def addConnectionToGraph(graph, northNode, southNode, northTier, southTier):
    if(northNode not in graph):
        graph.add_node(northNode, northbound=[], southbound=[], tier=northTier)
    if(southNode not in graph):
        graph.add_node(southNode, northbound=[], southbound=[], tier=southTier)

    graph.nodes[northNode]["southbound"].append(southNode)
    graph.nodes[southNode]["northbound"].append(northNode)

    graph.add_edge(northNode, southNode)

    return

def logGraphInfo(graph, k, t, topTier):
    numTofNodes = (k//2)**(t-1)
    numServers = 2*((k//2)**t)
    numSwitches = ((2*t)-1)*((k//2)**(t-1))
    numLeaves = 2*((k//2)**(t-1))
    numPods = 2*((k//2)**(t-2))

    logging.warning("=============\nFOLDED CLOS\nk = {k}, t = {t}\n{k}-port devices with {t} tiers.\n=============\n".format(k=k, t=t))

    logging.warning("Number of ToF Nodes: {}".format(numTofNodes))
    logging.warning("Number of physical servers: {}".format(numServers))
    logging.warning("Number of networking nodes: {}".format(numSwitches))
    logging.warning("Number of leaves: {}".format(numLeaves))
    logging.warning("Number of Pods: {}".format(numPods))

    for tier in reversed(range(topTier+1)):
        nodes = [v for v in graph if graph.nodes[v]["tier"] == tier]
        logging.warning("\n== TIER {} ==".format(tier))

        for node in sorted(nodes):
            logging.warning(node)
            logging.warning("\tnorthbound:")
            for n in graph.nodes[node]["northbound"]:
                logging.warning("\t\t{}".format(n))
            logging.warning("\tsouthbound:")
            for s in graph.nodes[node]["southbound"]:
                logging.warning("\t\t{}".format(s))


def testBlocking(graph, topTier):

    '''
    Check if you're in the same macro-pod:
        if yes:
            - Find the shared tier value via name.
            - Check all tier x nodes to destination.
        if no:
            - Go up and check all ToF nodes to destination.
            - the length of the path list will be numTiers+1 (includes the ToF node)

    result = re.findall(r'(?<=-)(\d+)', test2)[:-1]
    '''

    blockingGraph = deepcopy(graph)
    servers = [server for server in blockingGraph if COMPUTE_NAME in server]

    # https://www.anycodings.com/1questions/804952/random-pairs-without-repeats-in-python-numpy-or-itertools
    # https://stackabuse.com/how-to-randomly-select-elements-from-a-list-in-python/
    random.shuffle(servers)
    result = []
    for i in range(0, len(servers), 2):
        result.append(servers[i:i + 2])
    print(result)

    for pair in result:
        source = pair[0]
        destination = pair[1]
        print("\n{} --> {}".format(source, destination))

        tofNodes = [node for node in graph if "tof" in node]

        # grab the values (list) in between the node name (compute) and the node number
        sourcePod = re.findall(r'(?<=-)(\d+)', source)[:-1]
        destinationPod = re.findall(r'(?<=-)(\d+)', destination)[:-1]
        sharedPod = []
    
        # Find what tier the nodes meet, or if they don't at all
        for tier in range(0, len(sourcePod)):
            if(sourcePod[tier] == destinationPod[tier]):
                sharedPod.append(sourcePod[tier])
            else:
                break

        if(not sharedPod):
            print(tofNodes)

            for node in tofNodes:
                path = nx.shortest_path(G=blockingGraph, source=node, target=destination)
                print("{} --> {}".format(node, destination))
                print(path)
                print(len(path))
        else:
            pod = "spine-"
            pod += "-".join(sharedPod)
            print(pod)
            spineNodes = [
                            node for node in graph 
                            if pod in node 
                            and graph.nodes[node]["tier"] == topTier-len(sharedPod)
                        ]
            print(spineNodes)

            for node in spineNodes:
                path = nx.shortest_path(G=blockingGraph, source=node, target=destination)

    '''
    for pair in result:
        print("\n{} --> {}".format(pair[0], pair[1]))
        path = nx.shortest_path(blockingGraph, source=pair[0], target=pair[1])
        #pathList = [path[i:i+2] + [1000] for i in range(len(path)-1)]
        print(path)
        sourcePod = re.findall(r'^[^-]*-([^-]*).*', pair[0]) # compute-RESULT-....
        destinationPod = re.findall(r'^[^-]*-([^-]*).*', pair[1])
        if(sourcePod == destinationPod):
            print("YURRR")
        #print("EDGES")
        #print(blockingGraph.edges.data("weight"))
        #print([p for p in nx.all_shortest_paths(graph, source=pair[0], target=pair[1])])
    '''

    return

def definePlanes(graph, topTier):
    planes = defaultdict(list)

    for tier in range(topTier-1, 1, -1):
        nodes = [v for v in graph if graph.nodes[v]["tier"] == tier]

        for node in nodes:
            planes[tuple(graph.nodes[node]["northbound"])].append(node)

    for plane in planes:
        nodes = planes[plane]
        print(f"plane {plane}")
        print(f"\t{nodes}")

    return

'''
k = number of ports shared between all leaf and spine nodes (not compute)
t = number of tiers in the topology

Fat Tree is a TREE, thus we can traverse and build via a modified BFS
'''
def buildGraph(k, t):
    # Check to make sure the input is valid, return an error if not
    if(isNotValidClosInput(k)):
        raise nx.NetworkXError("Invalid Clos input (must be equal number of north and south links)")

    # Create base graph to add vertices and edges to
    graph = nx.Graph(topTier=t)

    currentTierPrefix = [""] # Queue for current prefix being connected to a southern prefix
    nextTierPrefix = [] # Queue for the prefixes of the tier directly south of the current tier

    currentPodNodes = (k//2)**(t-1) # Number of top-tier nodes
    topTier = t # The starting tier, and the highest tier in the topology
    currentTier = t # Tracking the tiers as it iterates down them

    southboundPorts = k # Start with top-tier having all southbound ports

    while currentTierPrefix:
        currentPrefix = currentTierPrefix.pop(0)
        nodeNum = 0 # The number associated with a given node, appended after the prefix (ex: 1-1-1, pod 1-1, node number 1)

        for node in range(1,currentPodNodes+1):
            northNode = generateNodeName(currentPrefix, str(node), currentTier, topTier)

            for intf in range(1, southboundPorts+1):
                # Per BFS logic, mark the neighbor as visited if it has not already, add to queue
                # All tiers > 2
                if(currentTier > LOWEST_SPINE_TIER):
                    southPrefix = generatePrefix(currentPrefix, str(intf))
                    determinePrefixVisitedStatus(southPrefix, nextTierPrefix)
                    southNodeNum = (nodeNum%(currentPodNodes // (k//2)))+1

                # The Leaf tier needs to have the same prefix of the spine tier (tier-2), as that is the smallest unit (pod)
                elif(currentTier == LOWEST_SPINE_TIER):
                    southPrefix = currentPrefix
                    determinePrefixVisitedStatus(southPrefix, nextTierPrefix)
                    southNodeNum = intf

                # Tier 1 connects to Tier 0, the compute nodes.
                elif(currentTier == LEAF_TIER):
                    southPrefix = northNode.strip(LEAF_NAME)
                    southNodeNum = intf

                southNode = generateNodeName(southPrefix, str(southNodeNum), currentTier-1, topTier)

                addConnectionToGraph(graph, northNode, southNode, currentTier, currentTier-1)

            nodeNum += 1

        if(not currentTierPrefix):
            currentTierPrefix = deepcopy(nextTierPrefix)
            nextTierPrefix.clear()

            # If the top tier was just connected with its soutbound neighbors
            if(currentTier == topTier):
                southboundPorts = k//2 # All tiers except the top have half of their ports southbound

                # Proper distribution of links for 2-tier topologies
                if(topTier == LOWEST_SPINE_TIER):
                    currentPodNodes = k

            # The number of connections in the next tier below will be cut down appropriately
            if(currentTier > LOWEST_SPINE_TIER):
                currentPodNodes = currentPodNodes // (k//2)

            currentTier -= 1 # Now that the current tier is complete, move down to the next one

    return graph

'''
Folded-Clos/Fat-Tree Graph
k = Degree shared by each node
l = Number of tiers in the graph

DFS
'''
def buildGraph_DFS(k, l):
    def generatePod(G, tier, k, podPrefix="", numNodesAbove=0, topTier=False):
        if(topTier):
            if(tier != 2):
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
            else:
                # for each leaf node
                for leaf in range(1, k+1):
                    leafNode = "P1_L{leafNum}".format(leafNum=leaf)
                    # for each edge to a spine node and compute node
                    for port in range(1,int((k/2)+1)):
                        spineNode = "TS{spineNum}".format(spineNum=port)
                        G.add_edge(leafNode, spineNode)
                        computeNode = ("P1L{leafNum}" + "_C{computeNum}").format(leafNum=leaf, computeNum=port)
                        G.add_edge(leafNode, computeNode)

        # At tier one (leaf nodes), half of your ports (k/2) go to servers, the other half go to spines
        elif(tier == 1):
            # for each leaf node
            for leaf in range(1, int((k/2)+1)):
                leafNode = podPrefix + "_L{leafNum}".format(leafNum=leaf)
                # for each edge to a spine node and compute node
                for port in range(1,int((k/2)+1)):
                    spineNode = podPrefix + "_S{spineNum}".format(spineNum=port)
                    G.add_edge(leafNode, spineNode)
                    computeNode = (podPrefix + "L{leafNum}" + "_C{computeNum}").format(leafNum=leaf, computeNum=port)
                    G.add_edge(leafNode, computeNode)

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