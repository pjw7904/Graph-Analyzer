'''
Clos traversal generator built with low space complexity in mind.
'''
def closTraversal(clos, topTier, topTierRoot=True):
    LEAF_TIER = 1

    # Define which way traversal should occur: from leaves to spines, or spines to leaves
    if(topTierRoot):
        propogationDirection = "southbound"
        currentTier = sorted([node for node in clos if clos.nodes[node]["tier"] == topTier])
    else:
        propogationDirection = "northbound"
        currentTier = sorted([node for node in clos if clos.nodes[node]["tier"] == LEAF_TIER])

    # Makes traversal easy in regards to space complexity
    nextTier = set()

    while(currentTier):
        for node in currentTier:
            for neighbor in clos.nodes[node][propogationDirection]:
                if((topTierRoot and clos.nodes[neighbor]["tier"] > 1) or (not topTierRoot and clos.nodes[neighbor]["tier"] < topTier)):
                    nextTier.add(neighbor)

                yield (node, neighbor, clos.nodes[node]["tier"], clos.nodes[neighbor]["tier"])

        currentTier = sorted(list(nextTier))
        nextTier.clear()

def addVIDss(clos, topTier, startTier, topTierRoot=True):
    # Arbitrary starting point for root VIDs
    currentRootVID = "10"
    visited = []

    for edge in closTraversal(clos, topTier, topTierRoot=topTierRoot):
        currentNode = edge[0]
        currentNeighbor = edge[1]
        currentNodeTier = edge[2]
        neighborTier = edge[3]

        if(currentNode not in visited):
            if(currentNodeTier == startTier):
                clos.nodes[currentNode]["VIDs"] = [currentRootVID]
                currentRootVID = str(int(currentRootVID) + 1)
            
            visited.append(currentNode)
            outboundValue = 1
        else:
            outboundValue += 1

        newVIDs = [vid + f".{outboundValue}" for vid in clos.nodes[currentNode]["VIDs"]]

        if("VIDs" not in clos.nodes[currentNeighbor]):
            clos.nodes[currentNeighbor]["VIDs"] = newVIDs
        else:
            clos.nodes[currentNeighbor]["VIDs"].extend(newVIDs)

    for tier in reversed(range(topTier+1)):
        if(tier == 0):
            break
        nodes = [v for v in clos if clos.nodes[v]["tier"] == tier]
        print("\n== TIER {} ==".format(tier))

        for node in sorted(nodes):
            print(node)
            vids = clos.nodes[node]["VIDs"]
            print(f"\t{vids}")

    return

def addVIDs(clos, topTier, startingTierNodes, topTierRoot=True):
    # Define who the root is in this addressing scheme: the top-tier spines, or the leaves
    if(topTierRoot):
        propogationDirection = "southbound"
    else:
        propogationDirection = "northbound"

    currentTier = startingTierNodes

    # Arbitrary starting point for root VIDs
    currentRootVID = "10"
    atRootTier = True
    nextTier = set()
    visited = []

    while(currentTier):
        for node in currentTier:
            outboundValue = 1

            if(atRootTier):
                clos.nodes[node]["VIDs"] = [currentRootVID]
                currentRootVID = str(int(currentRootVID) + 1)

            for neighbor in clos.nodes[node][propogationDirection]:
                newVIDs = [vid + f".{outboundValue}" for vid in clos.nodes[node]["VIDs"]]

                if(neighbor in visited):
                    clos.nodes[neighbor]["VIDs"].extend(newVIDs)
                else:
                    clos.nodes[neighbor]["VIDs"] = newVIDs
                    visited.append(neighbor)

                if((topTierRoot and clos.nodes[neighbor]["tier"] > 1) or (not topTierRoot and clos.nodes[neighbor]["tier"] < topTier)):
                    nextTier.add(neighbor)

                outboundValue += 1

        if(atRootTier):
            atRootTier = False

        currentTier = list(nextTier)
        nextTier.clear()


    for tier in reversed(range(3+1)):
        if(tier == 0):
            break
        nodes = [v for v in clos if clos.nodes[v]["tier"] == tier]
        print("\n== TIER {} ==".format(tier))

        for node in sorted(nodes):
            print(node)
            vids = clos.nodes[node]["VIDs"]
            print(f"\t{vids}")