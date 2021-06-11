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
        sender_MsgVector = Graph.nodes[sender]["msgVector"]

        logRSTAEvent("Current sender: {0} | Msg vector: {1}".format(sender, sender_MsgVector), 1)

        for receiver in Graph.neighbors(sender):
            recvPort = receiver + "_" + sender
            receiver_PortInfo = Graph.nodes[receiver][recvPort]
            receiver_PortVector = Graph.nodes[receiver][recvPort].portVector
            receiver_RootVector = Graph.nodes[receiver]["rootVector"]
            receiver_MsgVector = Graph.nodes[receiver]["msgVector"]

            logRSTAEvent("Receiving msg vector: {0} | Port vector: {1} | Root vector: {2}"
                         .format(receiver, receiver_PortVector, receiver_RootVector), 2)

            # If the sent message vector is superior to the receiver port vector
            if(senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)): # send_msg vs recv_port
                logRSTAEvent("sender vector is superior to receiver port vector", 2)

                if(senderVectorIsSuperior(sender_MsgVector, receiver_RootVector)): # send_msg vs recv_root
                    # Make the receiving port a root port, change all other ports to sync
                    syncVectors(Graph, sender_MsgVector, receiver, recvPort)
                    logRSTAEvent("sender vector is superior to receiver root vector", 3)
                    addToSendingQueue(sendingQueue, receiver)
                else:
                    # Make the receiving port an alternate port
                    updatedPortVector = RSTAVector(sender_MsgVector.RootPathCost+1, 
                                        sender_MsgVector.DesignatedBridgeID)
                    Graph.nodes[receiver][recvPort] = portInfo(updatedPortVector, ALT_ROLE)
                    logRSTAEvent("sender vector is inferior to receiver root vector", 3)
                    addToSendingQueue(sendingQueue, receiver)

            # If the sent message vector is identical to the receiver port vector
            elif(senderVectorIsIdentical(sender_MsgVector, receiver_PortVector)):
                logRSTAEvent("vectors are identical", 2)
            
            # If the sent message vector is inferior to the receiver port vector
            elif(not senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)):
                logRSTAEvent("sender vector is inferior to receiver port vector", 2)

                if(receiver_PortInfo.state == DESIGNATED_ROLE):
                    logRSTAEvent("receiving port is already in designated state", 2)
                else:
                    logRSTAEvent("receiving port moved to designated state", 2)
                    Graph.nodes[receiver][recvPort] = portInfo(receiver_PortVector, DESIGNATED_ROLE)
                    addToSendingQueue(sendingQueue, receiver)

            # Catch-all for vector comparision issues
            else:
                logRSTAEvent("vector parsing error", 2)

        sendingQueue.pop(topNode)

    logRSTAEvent("SIMULATION COMPLETE", 1)
    printAltPorts(Graph, DESIGNATED_ROLE)

    return


def addToSendingQueue(sendingQueue, node):
    if(node not in sendingQueue):
        sendingQueue.append(node)
        logRSTAEvent("{0} added to sending queue".format(node), 2)

    return


def senderVectorIsSuperior(senderVector, receiverVector):
    isSuperior = False

    if(
        (senderVector.RootPathCost+1 < receiverVector.RootPathCost) or
        (senderVector.RootPathCost+1 == receiverVector.RootPathCost and 
        senderVector.DesignatedBridgeID < receiverVector.DesignatedBridgeID)
    ):
        isSuperior = True

    return isSuperior


def senderVectorIsIdentical(senderVector, receiverVector):
    isIdentical = False

    if(senderVector.RootPathCost+1 == receiverVector.RootPathCost and 
       senderVector.DesignatedBridgeID == receiverVector.DesignatedBridgeID):
       isIdentical = True

    return isIdentical


def syncVectors(Graph, superiorVector, node, newRootPort):
    for port in Graph.neighbors(node):
        portName = node + "_" + port

        if(portName == newRootPort):
            updatedPortVector = RSTAVector(superiorVector.RootPathCost+1, superiorVector.DesignatedBridgeID)
            Graph.nodes[node][portName] = portInfo(updatedPortVector, ROOT_ROLE)
            Graph.nodes[node]["rootVector"] = updatedPortVector
        else:
            updatedPortVector = RSTAVector(superiorVector.RootPathCost+2, Graph.nodes[node]["BID"])
            Graph.nodes[node][portName] = portInfo(updatedPortVector, SYNC_ROLE)

    Graph.nodes[node]["msgVector"] = RSTAVector(superiorVector.RootPathCost+1, Graph.nodes[node]["BID"])

    return


def logRSTAEvent(eventMsg, depth):
    print(depth * "*" + eventMsg)


def printAltPorts(Graph, portType):
    for node in Graph:
        print("\n", node)
        for neighbor in Graph.neighbors(node):
            port = node + "_" + neighbor

            if(Graph.nodes[node][port].state == portType):
                print(port)

    return