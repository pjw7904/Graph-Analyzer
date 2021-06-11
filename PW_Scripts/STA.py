from collections import namedtuple

# Port Roles & States. Setup: [ NODE [port]]------link------[[port] NODE ]
DESIGNATED_ROLE = "Designated [FWD]" # Superior port on link, forwards traffic
ROOT_ROLE       = "Root [FWD]"       # Best port on node, forwards traffic
ALT_ROLE        = "Alternate [BLK]"  # Inferior port on link, blocks traffic
STARTING_ROLE   = "UNDEFINED"        # Starting role, role undefined at startup
SYNC_ROLE       = "SYNC"             # When a new root port is chosen, all other ports are put into sync

RSTAVector = namedtuple("RSTA_Vector", "RootPathCost DesignatedBridgeID")
portInfo   = namedtuple("Port_Information", "portVector state")

def createSTADataStructures(Graph, root):
    # Starting Bridge IDs (BID), depending on node type (root or non-root)
    rootBridgeID = 0
    bridgeID     = 1

    # Starting root path cost (RPC) values, depending on node type
    startingRPCNonRoot = 999999 # This is not present in the algorithm, it's my own addition
    startingRPCRoot    = 0

    # For each node in the graph, give them an appropriate BID
    for node in Graph:
        if(node != root):
            Graph.nodes[node]["BID"] = bridgeID
            bridgeID += 1
        else:
            Graph.nodes[node]["BID"] = rootBridgeID

        # For each port on each node, add starting port vector based on defined starting defaults
        for neighboringNode in Graph.neighbors(node):
            portName = node + "_" + neighboringNode

            if(node != root):
                startingPortVector = RSTAVector(startingRPCNonRoot, Graph.nodes[node]["BID"])
                Graph.nodes[node][portName] = portInfo(startingPortVector, STARTING_ROLE)
            else:
                startingPortVector = RSTAVector(startingRPCRoot, Graph.nodes[node]["BID"])
                Graph.nodes[node][portName] = portInfo(startingPortVector, DESIGNATED_ROLE)

        # Add starting message vector, which is the same as the starting port vectors
        Graph.nodes[node]["msgVector"] = startingPortVector

        # Add starting root vector, which is the same as the starting port vectors
        Graph.nodes[node]["rootVector"] = startingPortVector

    for node in Graph:
        print(node)
        print(Graph.nodes[node])
        print("\n")
    
    return


def RSTA_algo(Graph, root):
    # Define starting/default Bridge ID and port, message, and root vectors for each node
    createSTADataStructures(Graph, root)

    # Startup values
    topNode = 0
    sendingQueue = [root] # Queue is based on a list for this implementation

    # Begin simulation. For each iteration, the top node in the queue will "transmit" its message vector to its neighbors
    while sendingQueue:
        sender = sendingQueue[topNode] # sender is the top node in the sending queue
        logRSTAEvent("Current sender: {0} | Msg Vector: {1}".format(sender, Graph.nodes[sender]["msgVector"]), 1)

        sendingQueue.pop(topNode)


    return


def logRSTAEvent(eventMsg, depth):
    print(depth * "*" + eventMsg)