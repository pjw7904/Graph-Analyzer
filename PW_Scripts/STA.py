'''===========================
IEEE RAPID SPANNING TREE ALGORITHM (RAPID STA)

Overview:
    - A python-based, non-distributed (centralized) implementation of the IEEE Rapid STA. This is not a full RSTP implementation, just certain parts of the algorithm that the protocol builds from.

Outline:
    - Rapid STA defines a spanning tree priority vector, which is information sent between nodes of the graph to determine the state and role of edges.
    
    - The spanning tree priority vector includes the following data, which is followed by whether or not this implementation uses that information in its vector:
        1. Root Bridge Identifier, the Bridge Identifier of the Bridge believed to be the Root by the transmitter [NOT INCLUDED]
        2. Root Path Cost, to that Root Bridge from the transmitting Bridge [INCLUDED]
        3. Bridge Identifier, of the transmitting Bridge [INCLUDED]
        4. Port Identifier, of the Port through which the message was transmitted [NOT INCLUDED]
        5. Port Identifier, of the Port through which the message was received (where relevant) [NOT INCLUDED]

    - The only vector components utilized here are the Root Path Cost (RPC) and transmitting Bridge Identifer (BID). 
      This implementation is built for a simple graph which represents a network full of point-to-point LAN segments, 
      no shared media, and no redundant links between nodes. This elminiates vector components 4 and 5. A root is 
      pre-designated, thus vector component 1 is eliminated as well.

    - All edges at this point are considered unweighted, so root path cost will, as a result, be distance from the root.

    - The set of all spanning tree priority vectors is totally ordered, a lower-valued priority vector component is superior, and earlier components in the vector are superior.
==========================='''
from collections import namedtuple

# Port Role [state]. Setup: [ NODE [port]]------link------[[port] NODE ]
DESIGNATED_ROLE = "Designated [FWD]" # Superior port on link, forwards traffic, always one on each link
ROOT_ROLE       = "Root [FWD]"       # Best port on node, forwards traffic
ALT_ROLE        = "Alternate [BLK]"  # Inferior port on link, blocks traffic
STARTING_ROLE   = "Undefined [N/A]"  # Starting role, role undefined at startup
SYNC_ROLE       = "Sync [N/A]"       # When a new root port is chosen, all other ports are put into sync

'''
Origional Rapid STA priority vector                                                 Modified priority vector
{RootBridgeID:RootPathCost:DesignatedBridgeID:DesignatedPortID:BridgePortID} -----> {RootPathCost:DesignatedBridgeID}

RootPathCost       = Root Path Cost, to that Root Bridge from the transmitting Bridge
DesignatedBridgeID = Bridge Identifier, of the transmitting Bridge.
'''
RSTAVector = namedtuple("RSTA_Vector", "RootPathCost DesignatedBridgeID")

'''
Each port on each RSTA node is give a structure with its given RSTA port vector
and the state of that port as a result of exchanging vectors with that link's neighbor. 
The set of all states on all ports of all nodes in the graph will result in a shortest path tree.
'''
portInfo   = namedtuple("Port_Information", "portVector state")

# Gives each node the required data structures, including a vector and state for each port
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
            portName = node + "_" + neighboringNode # port name format: localNode_NeighborNode

            if(node != root):
                startingPortVector = RSTAVector(startingRPCNonRoot, Graph.nodes[node]["BID"])
                Graph.nodes[node][portName] = portInfo(startingPortVector, STARTING_ROLE)
            else:
                # RSTA root node has the best vector in the graph and all ports are designated
                startingPortVector = RSTAVector(startingRPCRoot, Graph.nodes[node]["BID"])
                Graph.nodes[node][portName] = portInfo(startingPortVector, DESIGNATED_ROLE)

        # Add starting message vector (vector sent to neighbors), which is the same as the starting port vectors
        Graph.nodes[node]["msgVector"] = startingPortVector

        # Add starting root vector (vector of upstream node), which is the same as the starting port vectors
        Graph.nodes[node]["rootVector"] = startingPortVector
    
    return

# The logic and simulation of the Rapid Spanning Tree Algorithm
def RSTA_algo(Graph, root):
    # Define starting/default Bridge ID and port, message, and root vectors for each node
    createSTADataStructures(Graph, root)

    # Startup values
    topNode = 0
    sendingQueue = [root] # The top node in the queue will "transmit" its message vector to its neighbors

    # Begin transmission/simulaiton
    while sendingQueue:
        # Get sender/transmitter information
        sender = sendingQueue[topNode] # sender is the top node in the sending queue
        sender_MsgVector = Graph.nodes[sender]["msgVector"]

        logRSTAEvent("Current sender: {0} | Msg vector: {1}".format(sender, sender_MsgVector), 1)

        # For each neighbor of the sender
        for receiver in Graph.neighbors(sender):
            # Get receiver information
            recvPort = receiver + "_" + sender # port received on
            receiver_PortInfo = Graph.nodes[receiver][recvPort]
            receiver_PortVector = Graph.nodes[receiver][recvPort].portVector
            receiver_RootVector = Graph.nodes[receiver]["rootVector"]
            receiver_MsgVector = Graph.nodes[receiver]["msgVector"]

            logRSTAEvent("Receiving msg vector: {0} | Port vector: {1} | Root vector: {2}"
                         .format(receiver, receiver_PortVector, receiver_RootVector), 2)

            # If the sent message vector is SUPERIOR to the receiver port vector
            if(senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)):
                logRSTAEvent("sender vector is superior to receiver port vector", 2)

                # If the sent message vector is also superior to the receiver root vector
                if(senderVectorIsSuperior(sender_MsgVector, receiver_RootVector)):
                    # Make the receiving port a root + fwding port, change all other ports to sync
                    syncVectors(Graph, sender_MsgVector, receiver, recvPort)
                    logRSTAEvent("sender vector is superior to receiver root vector", 3)
                    addToSendingQueue(sendingQueue, receiver)
                
                # If the root vector on the receiver is still superior
                else:
                    # Make the receiving port an alternate + blocking port
                    updatedPortVector = RSTAVector(sender_MsgVector.RootPathCost+1, 
                                        sender_MsgVector.DesignatedBridgeID) # RPC + 1 for received link cost
                    Graph.nodes[receiver][recvPort] = portInfo(updatedPortVector, ALT_ROLE)
                    logRSTAEvent("sender vector is inferior to receiver root vector", 3)
                    addToSendingQueue(sendingQueue, receiver)

            # If the sent message vector is IDENTICAL to the receiver port vector, ignore it
            elif(senderVectorIsIdentical(sender_MsgVector, receiver_PortVector)):
                logRSTAEvent("vectors are identical", 2)
            
            # If the sent message vector is INFERIOR to the receiver port vector
            elif(not senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)):
                logRSTAEvent("sender vector is inferior to receiver port vector", 2)

                # If the receiver port role is already designated, ignore it
                if(receiver_PortInfo.state == DESIGNATED_ROLE):
                    logRSTAEvent("receiving port is already in designated state", 2)

                # Otherwise, move the port to the designated + fwding role
                else:
                    logRSTAEvent("receiving port moved to designated state", 2)
                    Graph.nodes[receiver][recvPort] = portInfo(receiver_PortVector, DESIGNATED_ROLE)
                    addToSendingQueue(sendingQueue, receiver)

            # Catch-all for vector comparision issues
            else:
                logRSTAEvent("vector parsing error", 2)

        # Sender is finished, pop it off the sending queue
        sendingQueue.pop(topNode)

    # Simulation finished
    logRSTAEvent("SIMULATION COMPLETE", 1)
    printAltPorts(Graph, DESIGNATED_ROLE)

    return

# Add a given node to the sending queue if it isn't there already
def addToSendingQueue(sendingQueue, node):
    if(node not in sendingQueue):
        sendingQueue.append(node)
        logRSTAEvent("{0} added to sending queue".format(node), 2)

    return


# Check the inputted vectors to see if the first is superior to the second
def senderVectorIsSuperior(senderVector, receiverVector):
    isSuperior = False

    # If sender RPC + 1 > receiver RPC, or RPCs are equal (after + 1) and sender BID > receiver BID
    if(
        (senderVector.RootPathCost+1 < receiverVector.RootPathCost) or
        (senderVector.RootPathCost+1 == receiverVector.RootPathCost and 
        senderVector.DesignatedBridgeID < receiverVector.DesignatedBridgeID)
    ):
        isSuperior = True

    return isSuperior


# Check the inputted vectors to see if they are identical
def senderVectorIsIdentical(senderVector, receiverVector):
    isIdentical = False

    if(senderVector.RootPathCost+1 == receiverVector.RootPathCost and 
       senderVector.DesignatedBridgeID == receiverVector.DesignatedBridgeID):
       isIdentical = True

    return isIdentical


# Set new root port as such, block all other ports with sync role
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

    # Set the new message vector to the root vector (RPC + 1)
    Graph.nodes[node]["msgVector"] = RSTAVector(superiorVector.RootPathCost+1, Graph.nodes[node]["BID"])

    return

# Log a given RSTA event
def logRSTAEvent(eventMsg, depth):
    print(depth * "*" + eventMsg)


# Print out RSTA graph information
def printAltPorts(Graph, portType):
    for node in Graph:
        print("\n", node)
        for neighbor in Graph.neighbors(node):
            port = node + "_" + neighbor

            if(Graph.nodes[node][port].state == portType):
                print(port)

    return