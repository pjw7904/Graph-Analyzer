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
      This implementation is build for a simple graph which represents a network full of point-to-point LAN segments, 
      no shared media, and no redundant links between nodes. This elminiates vector components 4 and 5. A root is 
      pre-designated, thus vector component 1 is eliminated as well.

    - All edges at this point are considered unweighted, so root path cost will, as a result, be distance from the root.

    - The set of all spanning tree priority vectors is totally ordered, a less priority vector component is superior, and earlier components in the vector are superior.
==========================='''
from collections import namedtuple

def createGraphPriorityVectors(Graph, root):
    '''
    Origional Rapid STA priority vector                                                 Modified priority vector
    {RootBridgeID:RootPathCost:DesignatedBridgeID:DesignatedPortID:BridgePortID} -----> {RootPathCost:DesignatedBridgeID}

    RootPathCost       = Root Path Cost, to that Root Bridge from the transmitting Bridge
    DesignatedBridgeID = Bridge Identifier, of the transmitting Bridge.
    '''
    portPriorityVector = namedtuple("RSTA_Vector", "RootPathCost DesignatedBridgeID")

    # Define starting bridge ID information (A bridgeID is normally a MAC address of the bridge, but that doesn't matter here, so it's just an integer)
    rootBridgeID = 1 # The designated root is always given the lowest bridge ID, just by default.
    bridgeID = 2

    startingRootPathCost = 0

    for node in Graph:
        if(node != root):
            Graph.nodes[node]["BridgeID"] = bridgeID
            bridgeID += 1
        else:
            Graph.nodes[node]["BridgeID"] = rootBridgeID

        for neighboringNode in Graph.neighbors(node):
            portName = node + "_" + neighboringNode # Create a custom port/edge name to store a priority vector (format: currentNode_currentNeighbor)
            Graph.nodes[node][portName] = portPriorityVector(startingRootPathCost, Graph.nodes[node]["BridgeID"]) # Create a port priority vector for each edge on the node (17.6 - P1)


    for node in Graph:
        print(node)
        print(Graph.nodes[node])
        print("\n")

    # Example of using tuple elements inside of node data:
    #if(Graph.nodes["node-3"]["node-3_node-2"].DesignatedBridgeID < Graph.nodes["node-0"]["node-0_node-1"].DesignatedBridgeID):
    #    print("it is less!")

    return