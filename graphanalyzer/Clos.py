import networkx as nx
from copy import deepcopy

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

# values for the north and south tiers at any given adjacent tiers
NORTH = 1
SOUTH = 2

'''
Smallest unit in the DCN, tier 1 leaf and tier 2 spine full mesh and compute nodes
k = number of ports on each node
podPrefix = prefix for the pod
'''
def buildPod(k, podPrefix):
    # (k+1)+1 = k/2 for the range function
    for leafNum in range(1, (k/2)+1):
        leafName = getNodeName(LEAF_NAME, podPrefix, leafNum)
        computeConnections = [(leafName, getNodeName(COMPUTE_NAME, podPrefix, computeNum)) 
                            for computeNum in range(0,(k/2))]
        spineConnections = [(leafName, getNodeName(SPINE_NAME, podPrefix, spineNum)) 
                            for spineNum in range(0,(k/2))]
        
    return

def getNodeName(type, num, prefix=""):
    if(type != TOF_NAME):
        name = "{type}-{prefix}-{num}".format(type,prefix,num)
    else:
        name = "{type}-{num}".format(type,num)
    
    return name

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
    #print("maybe ", prefix)

    #if((currentPrefix + "-" + str(intf)) not in nextTierPrefix):
    if(prefix not in prefixList):
        #print("appended")
        #nextTierPrefix.append((currentPrefix + "-" + str(intf)))
        prefixList.append(prefix)

    return

def isNotValidClosInput(k):
    if(k % 2 != 0):
        return True
    else:
        return False

'''
k = number of ports shared between all leaf and spine nodes (not compute)
t = number of tiers in the 

Fat Tree is a TREE, thus we can traverse and build via a modified BFS
'''
def buildClos(k, t):
    if(isNotValidClosInput(k)):
        raise nx.NetworkXError("Invalid Clos input (must be equal number of north and south links)")

    prefix = [""] # Queue for current prefix being connected to a southern prefix
    nextTierPrefix = []


    currentPodNodes = (k//2)**(t-1) # Number of top-tier nodes
    topTier = t
    currentTier = t # Tracking the tiers as it iterates down them

    southboundPorts = k # Start with top-tier having all southbound ports

    while prefix:
        currentPrefix = prefix.pop(0)
        nodeNum = 0
        print("\ncurrent prefix: ", currentPrefix.lstrip("-"))
        print("current tier: ", currentTier)

        for node in range(1,currentPodNodes+1):
            #print("current node: ", nodeTitle + currentPrefix + "-" + str(node))
            currentNode = generateNodeName(currentPrefix, str(node), currentTier, topTier)
            print("current node: ", currentNode)

            for intf in range(1, southboundPorts+1):
                # Per BFS logic, mark the neighbor as visited if it has not already, add to queue
                if(currentTier > LOWEST_SPINE_TIER):
                    southPrefix = generatePrefix(currentPrefix, str(intf))
                    determinePrefixVisitedStatus(southPrefix, nextTierPrefix)
                    southNodeNum = (nodeNum%southboundPorts)+1

                # The Leaf tier needs to have the same prefix of the north spine tier, as that is the smallest unit (pod)
                elif(currentTier == LOWEST_SPINE_TIER):
                    southPrefix = currentPrefix
                    nextTierPrefix.append(southPrefix)
                    southNodeNum = intf

                elif(currentTier == LEAF_TIER):
                    southPrefix = currentNode.strip(LEAF_NAME)
                    southNodeNum = intf

                print("\tconnect to: ", generateNodeName(southPrefix, str(southNodeNum), currentTier-1, topTier))

            nodeNum += 1

        if(not prefix):
            prefix = deepcopy(nextTierPrefix)
            nextTierPrefix.clear()

            if(currentTier == topTier):
                southboundPorts = k//2

            if(currentTier > LOWEST_SPINE_TIER):
                currentPodNodes = currentPodNodes // (k//2)

            currentTier -= 1

    return


'''
    notDone = True
    while notDone:
        prefix = currentPrefix.pop(0)
        print(prefix)
        for node in range(1,currentPodNodes+1):
            if(currentTier == topTier):
                spineConnections = [(getNodeName(TOF_NAME, prefix, spineNum), getNodeName(SPINE_NAME, podPrefix, spineNum)) 
                                    for spineNum in range(0,(k/2))]

            elif(currentTier == LOWEST_SPINE_TIER):
                continue
            
            else:
                continue
'''
buildClos(4, 4)