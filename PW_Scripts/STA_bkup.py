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

# Port Roles & States
DESIGNATED_ROLE = "Designated [FWD]"
ROOT_ROLE       = "Root [FWD]"
ALT_ROLE        = "Alternate [BLK]"
STARTING_ROLE   = "UNDEFINED"
SYNC_ROLE       = "SYNC"

'''
Origional Rapid STA priority vector                                                 Modified priority vector
{RootBridgeID:RootPathCost:DesignatedBridgeID:DesignatedPortID:BridgePortID} -----> {RootPathCost:DesignatedBridgeID}

RootPathCost       = Root Path Cost, to that Root Bridge from the transmitting Bridge
DesignatedBridgeID = Bridge Identifier, of the transmitting Bridge.
'''
portPriorityVector = namedtuple("RSTA_Vector", "RootPathCost DesignatedBridgeID")
portInfo = namedtuple("Port_Information", "portVector state")


def createSTADataStructures(Graph, root):
    # Define starting bridge ID information (A bridgeID is normally a MAC address of the bridge, but that doesn't matter here, so it's just an integer)
    rootBridgeID = 0 # The designated root is always given the lowest bridge ID, just by default.
    bridgeID = 1

    startingRPCNonRoot = 999999
    startingRPCRoot = 0

    for node in Graph:
        if(node != root):
            Graph.nodes[node]["BridgeID"] = bridgeID
            bridgeID += 1
        else:
            Graph.nodes[node]["BridgeID"] = rootBridgeID

        for neighboringNode in Graph.neighbors(node):
            portName = node + "_" + neighboringNode # Create a custom port/edge name to store a priority vector (format: currentNode_currentNeighbor)

            if(node != root):
                startingPortVector = portPriorityVector(startingRPCNonRoot, Graph.nodes[node]["BridgeID"]) # Create a port priority vector for each edge on the node (17.6 - P1)
                Graph.nodes[node][portName] = portInfo(startingPortVector, STARTING_ROLE)
            else:
                startingPortVector = portPriorityVector(startingRPCRoot, Graph.nodes[node]["BridgeID"]) # Create a port priority vector for each edge on the node (17.6 - P1)
                Graph.nodes[node][portName] = portInfo(startingPortVector, DESIGNATED_ROLE)
        
        Graph.nodes[node]["messagePriorityVector"] = startingPortVector

    for node in Graph:
        print(node)
        print(Graph.nodes[node])
        print("\n")

    return


def syncPortVectors(Graph, node, newRPC, rootUpstream):
    rootPortName = node + "_" + rootUpstream

    for neighbor in Graph.neighbors(node):
        portName = node + "_" + neighbor

        if(portName == rootPortName):
            updatedPortVector = portPriorityVector(newRPC+1, Graph.nodes[rootUpstream]["BridgeID"])
            Graph.nodes[node][portName] = portInfo(updatedPortVector, ROOT_ROLE)
        else:
            updatedPortVector = portPriorityVector(newRPC+2, Graph.nodes[node]["BridgeID"])
            Graph.nodes[node][portName] = portInfo(updatedPortVector, SYNC_ROLE)

    return


def RSTA_algo(Graph, root):
    # Startup tasks
    topNode = 0
    createSTADataStructures(Graph, root) # Every vertex is given their port information (creates the Rapid STA port priority vectors)
    sendingQueue = [root] # Queue is based on a list for this implementation test

    # Go through the sending process
    while sendingQueue:
        v = sendingQueue[topNode] # sender is the top node in the sending queue
        print("\n==Currently sending STA vector information: {0}==".format(v))

        # For each neighbor (x) of the node currently sending an update, send them the best STA vector
        for neighbor in Graph.neighbors(v):
            print("receiving vector info: {0}".format(neighbor))
            #sendingPort = v + "_" + neighbor
            receivingPort = neighbor + "_" + v

            sender = Graph.nodes[v]["messagePriorityVector"]
            receiver = Graph.nodes[neighbor][receivingPort]
            receiverMsgVector = Graph.nodes[neighbor]["messagePriorityVector"]

            receivedRootPathCost = sender.RootPathCost
            receivedBridgeID = sender.DesignatedBridgeID

            if(receivedRootPathCost+1 < receiver.portVector.RootPathCost or (receivedRootPathCost+1 == receiver.portVector.RootPathCost and receivedBridgeID < receiver.portVector.DesignatedBridgeID)):
                print("Vector {0} from {1} is SUPERIOR to current port vector {2}".format(sender, v, receiver.portVector))
                updatedRole = ALT_ROLE
                updatedPortVector = portPriorityVector(receivedRootPathCost+1, Graph.nodes[v]["BridgeID"])
                Graph.nodes[neighbor][receivingPort] = portInfo(updatedPortVector, updatedRole)
                print("current {0} message vector: {1}".format(neighbor, receiverMsgVector))

                if(receivedRootPathCost < receiverMsgVector.RootPathCost):
                    print("Vector {0} from {1} is the new message vector for {2}".format(sender, v, neighbor))
                    updatedPortVector = portPriorityVector(receivedRootPathCost+1, Graph.nodes[neighbor]["BridgeID"])
                    Graph.nodes[neighbor]["messagePriorityVector"] = updatedPortVector
                    syncPortVectors(Graph, neighbor, receivedRootPathCost, v)

                if(neighbor not in sendingQueue):
                    sendingQueue.append(neighbor)
                    print("{0} added to sending queue".format(neighbor))

            elif((receivedRootPathCost+1 > receiver.portVector.RootPathCost) or (receivedRootPathCost+1 == receiver.portVector.RootPathCost and receivedBridgeID > receiver.portVector.DesignatedBridgeID)):
                if(receiver.state != DESIGNATED_ROLE):
                    print("Vector {0} from {1} is INFERIOR to current port vector {2}".format(sender, v, receiver.portVector))
                    
                    updatedRole = DESIGNATED_ROLE
                    updatedPortVector = portPriorityVector(receiver.portVector.RootPathCost, Graph.nodes[neighbor]["BridgeID"])
                    Graph.nodes[neighbor][receivingPort] = portInfo(updatedPortVector, updatedRole)

                    if(neighbor not in sendingQueue):
                        sendingQueue.append(neighbor)
                        print("+++++++++++++++++++{0} added to sending queue".format(neighbor))

        sendingQueue.pop(topNode)

    print("==Finished==")
    for node in Graph:
        print(node)
        print(Graph.nodes[node])
        print("\n")

    return

