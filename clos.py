import networkx as nx # Graph creation and analysis
import matplotlib.pyplot as plt

'''
    prefix = "P{0}"
    for i in range(0, k):
        prefix += "P{}"

number of top-tier pods = k, because the top tier of nodes will have k connections, 1 to each pod

number of pods within that top-tier pod = k/2, because you have half of your connections 
to the top tier and half 
'''
def generatePod(G, tier, k, podPrefix="", numNodesAbove=0, topTier=False):

    if(topTier):
        for podNum in range(1, 2): #k+1
            podPrefix = "P{}".format(podNum)
            generatePod(G, tier-1, k, numNodesAbove=int(numNodesAbove/int(k/2)), podPrefix=podPrefix) 

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
            print("pod prefix: {}\nprefix: {}".format(podPrefix, prefix))

            # for each super spine node
            for spine in range(1, int(numNodesAbove/int(k/2))+1):
                spineNode = prefix + "_S{spineNum}".format(spineNum=spine)

                # for each edge to a super spine node, step every other (2)
                for port in range(0,int((k/2))):
                    superSpineNode = podPrefix + "_S{spineNum}".format(spineNum=spine+(int(numNodesAbove/int(k/2)*port)))
                    G.add_edge(spineNode, superSpineNode)

    return


'''
Folded-Clos/Fat-Tree Graph
k = Degree shared by each node
l = Number of tiers in the graph
'''
def generateFoldedClosGraph(k, l):
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
    print(list(G))
    nx.draw(G,with_labels=True)
    plt.show()

    return G

G = generateFoldedClosGraph(6, 4)
nx.write_graphml(G=G, path="test.graphml", prettyprint=True)


# Naming prefix in the form P{tier-(l-1) pod #}P{tier-(l-2) pod #} and so on as needed
#prefix = ("P{}" * (l-2)) + "_"