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
from tabulate import tabulate
from timeit import default_timer as timer # Get elasped time of execution

# Location/name of the log file
LOG_FILE = "RSTA_Output.txt"

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
    logOutput = [] # Structure to hold output

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
        
        # Log name-BID info for log file
        logNodeInfo = [node,  Graph.nodes[node]["BID"]]
        logOutput.append(logNodeInfo)

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
    
    return logOutput

# The logic and simulation of the Rapid Spanning Tree Algorithm
def RSTA(Graph, root):
    Graph.graph["RSTA"] = 0 # count number of iterations needed
    Graph.graph["RSTA_recv"] = 0 # count number of times a node receives important information

    logFile = open(LOG_FILE, "w")

    # Define starting/default Bridge ID and port, message, and root vectors for each node
    nodeBIDInfo = createSTADataStructures(Graph, root)
    logRSTAEvent("{Header}\n{Results}\n\n".format(Header="Node Bridge IDs", Results=tabulate(nodeBIDInfo, headers=["Node", "BID"], numalign="right", floatfmt=".4f")), logFile)

    # Startup values
    topNode = 0
    sendingQueue = [root] # The top node in the queue will "transmit" its message vector to its neighbors

    # START TIMER
    startTime = timer()

    # Begin transmission/simulaiton
    while sendingQueue:
        Graph.graph["RSTA"] += 1

        # Get sender/transmitter information
        sender = sendingQueue[topNode] # sender is the top node in the sending queue
        sender_MsgVector = Graph.nodes[sender]["msgVector"]

        logRSTAEvent("---------\n({0}) Current sender: {1} | Msg vector: {2}\n".format(Graph.graph["RSTA"], sender, sender_MsgVector), logFile)

        # For each neighbor of the sender
        for receiver in Graph.neighbors(sender):
            # Get receiver information
            recvPort = receiver + "_" + sender # port received on
            receiver_PortInfo = Graph.nodes[receiver][recvPort]
            receiver_PortVector = Graph.nodes[receiver][recvPort].portVector
            receiver_RootVector = Graph.nodes[receiver]["rootVector"]
            receiver_MsgVector = Graph.nodes[receiver]["msgVector"]

            receiverInfo = "{0} - {1}: ".format(receiver, recvPort)

            # If the sent message vector is SUPERIOR to the receiver port vector
            if(senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)):
                Graph.graph["RSTA_recv"] += 1

                # If the sent message vector is also superior to the receiver root vector
                if(senderVectorIsSuperior(sender_MsgVector, receiver_RootVector)):
                    receiverInfo += "({0}){1} ----> {2}\n".format(Graph.graph["RSTA_recv"], receiver_PortInfo.state, ROOT_ROLE)
                    # Make the receiving port a root + fwding port, change all other ports to sync
                    syncVectors(Graph, sender_MsgVector, receiver, recvPort)
                    addToSendingQueue(sendingQueue, receiver)
                
                # If the root vector on the receiver is still superior
                else:
                    receiverInfo += "({0}){1} ----> {2}\n".format(Graph.graph["RSTA_recv"], receiver_PortInfo.state, ALT_ROLE)
                    # Make the receiving port an alternate + blocking port
                    updatedPortVector = RSTAVector(sender_MsgVector.RootPathCost+1, 
                                        sender_MsgVector.DesignatedBridgeID) # RPC + 1 for received link cost
                    Graph.nodes[receiver][recvPort] = portInfo(updatedPortVector, ALT_ROLE)
                    addToSendingQueue(sendingQueue, receiver)

            # If the sent message vector is IDENTICAL to the receiver port vector, ignore it
            elif(senderVectorIsIdentical(sender_MsgVector, receiver_PortVector)):
                receiverInfo += "No change, identical vectors\n"
            
            # If the sent message vector is INFERIOR to the receiver port vector
            elif(not senderVectorIsSuperior(sender_MsgVector, receiver_PortVector)):

                # If the receiver port role is already designated, ignore it
                if(receiver_PortInfo.state == DESIGNATED_ROLE):
                    receiverInfo += "No change, already designated\n"

                # Otherwise, move the port to the designated + fwding role
                else:
                    Graph.graph["RSTA_recv"] += 1
                    receiverInfo += "({0}){1} ----> {2}\n".format(Graph.graph["RSTA_recv"], receiver_PortInfo.state, DESIGNATED_ROLE)
                    Graph.nodes[receiver][recvPort] = portInfo(receiver_PortVector, DESIGNATED_ROLE)
                    addToSendingQueue(sendingQueue, receiver)

            # Catch-all for vector comparision issues
            else:
                receiverInfo += "Vector parsing error\n"

            logRSTAEvent(receiverInfo, logFile)

        # Sender is finished, pop it off the sending queue
        sendingQueue.pop(topNode)

    # STOP TIMER
    endTime = timer()

    # Simulation results and cleanup
    finalPortRoles = getPortInfo(Graph)
    finalCountingStats = "\nSender count: {0}\nNeeded Updated Count: {1}".format(Graph.graph["RSTA"], Graph.graph["RSTA_recv"])
    logRSTAEvent("\n=====RESULT=====\n" + finalPortRoles, logFile)
    logRSTAEvent(finalCountingStats, logFile)
    logRSTAEvent("\nTime to execute: {0}".format(endTime - startTime), logFile)

    logFile.close()

    return


# Add a given node to the sending queue if it isn't there already
def addToSendingQueue(sendingQueue, node):
    if(node not in sendingQueue):
        sendingQueue.append(node)

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
def logRSTAEvent(eventMsg, logFile):
    logFile.write(eventMsg)

    return


# Print out RSTA graph information
def getPortInfo(Graph):
    output = ""

    for node in Graph:
        output += "\n{0}\n".format(node)
        for neighbor in Graph.neighbors(node):
            port = node + "_" + neighbor
            output += "\t{0} - {1}\n".format(port, Graph.nodes[node][port].state)

    return output