import logging

from collections import namedtuple, Counter
from queue import PriorityQueue
from operator import itemgetter
from copy import deepcopy
from timeit import default_timer as timer # Get elasped time of execution
from os.path import join as getFile
from TreeAnalyzer import TreeValidator
from networkx import NetworkXError

#
# Constants
#
TOP_NODE = 0
LOG_FILE = "{}RSTA_Output.log"
LOG_FILE_BATCH = "{}batch_test.csv"

# Vector that is exchanged between vertices to determine tree structure
RSTAVector = namedtuple("RSTA_Vector", "RPC VID")

DESIGNATED_ROLE = "D"
ROOT_ROLE = "R"
ALTERNATE_ROLE = "A"

# Sending Queue
Q = []

### OUTPUT / FORMATTING FUNCTIONS ###
def setVIDs(Graph, root):
    IDCount = 0
    Graph.graph['VID_to_vertex'] = {}

    for node in sorted(Graph.nodes):
        Graph.nodes[node]['VID'] = chr(65 + IDCount)
        Graph.graph['VID_to_vertex'][chr(65 + IDCount)] = node

        if(node == root):
            logging.warning("Root node is {0}, VID = {1}\n".format(node, Graph.nodes[node]['VID']))
        else:
            logging.warning("Non-Root node {0}, VID = {1}\n".format(node, Graph.nodes[node]['VID']))

        IDCount += 1

    logging.warning("---------\n\n")

    return

def prettyVectorOutput(G, v, vector):
    output = "{{{RPC}, {VID}}}"

    return output.format(RPC=G.nodes[v][vector].RPC, VID=G.nodes[v][vector].VID)

def prettyEdgeRolesOutput(G, v):
    output = ""

    for edge in list(G.edges(v)): 
        output += "\t{edge} = {role}\n".format(edge=edge, role=G.nodes[v][edge])

    return output

def verboseOutput(Graph):
    logging.warning("")
    logging.warning("---------")
    logging.warning("RESULTING ROLE TABLES:")

    for v in sorted(Graph.nodes):
        logging.warning("{nodeName} ({VID}) - RPC: {RPC}".format(nodeName=v, VID=Graph.nodes[v]['VID'], RPC=Graph.nodes[v]['VV'].RPC))

        for edge in Graph.edges([v]):
            RPC = Graph.nodes[v]["RT"][(edge)][0].RPC
            VID = Graph.nodes[v]["RT"][(edge)][0].VID
            role = Graph.nodes[v]["RT"][(edge)][1]
            logging.warning(f"{edge}: RPC: {RPC} | VID: {VID} | Role: {role}")

        logging.warning("")

    return

'''
Data:   RSTA Vector in the form {RPC, VID}, sending queue Q, 
        array of priority queues for each vertex alt, parent struture
        parent to link nodes with their upstream parent

Input:  Graph G, root node r

Output: Parent structure, which will create a shortest path tree
'''
def init(G, r, logFilePath, batch=False, testName=None, removal=None):
    #setLoggingLevel(logFilePath, batch, testName)
    setVIDs(G, r)
    G.graph["step"] = 0

    # Create a validation object to make sure the result is a tree
    treeValidator = TreeValidator(G.nodes, r) 


    Q.append(r)

    for v in G:
        if(v == r):
            G.nodes[r]['VV'] = RSTAVector(0, G.nodes[r]['VID'])
        else:
            G.nodes[v]['VV'] = RSTAVector(float('inf'), G.nodes[v]['VID'])
        
        G.nodes[v]["RT"] = {}
        G.nodes[v]["AVPQ"] = PriorityQueue() # PQ to keep track of AV order
        G.nodes[v]["Delete"] = Counter() # Counter to allow for lazy deletions from PQ
        G.nodes[v]['PV'] = None

        for localEdge in G.edges([v]):
            if(v == r):
                 G.nodes[r]["RT"][localEdge] = [RSTAVector(0, G.nodes[r]['VID']), "D"]
            else:
                G.nodes[v]["RT"][localEdge] = [RSTAVector(float('inf'), G.nodes[v]['VID']), "U"]

    s = Q.pop(TOP_NODE)
    send(G,r,s,treeValidator)

    verboseOutput(G)

    if(not treeValidator.isTree()):
        raise NetworkXError("RSTA graph did not converge.")

    logging.warning("steps: {}".format(G.graph["step"]))

    # For batch testing
    logging.error("{0},{1},{2}".format(G.number_of_nodes(), G.number_of_edges(), G.graph["step"]))

    # If an edge is to be removed, run the reconvergence process
    if(removal):
        print(removal[0])
        print(removal[1])
        reconverge(G, r, removal[0], removal[1])

    return

'''
Input: Graph G (populated with RSTA Vector info), brokenVertex, brokenEdge
'''
def reconverge(G, r, brokenVertex1, brokenVertex2):
    '''
    There are two possibilities in a break, considering edge (X,Y) broke:

    1. Y is inferior (R), X is superior (D) [X_D--------R_Y]
    2. Y is inferior (A), X is superior (D) [X_D--------A_Y]
    '''

    logging.warning("============RECONVERGE============\n")

    # Grab the information from the appropriate nodes based on the broken edge
    affectedVertices = {
                        brokenVertex1: G.nodes[brokenVertex1]["RT"][(brokenVertex1, brokenVertex2)],
                        brokenVertex2: G.nodes[brokenVertex2]["RT"][(brokenVertex2, brokenVertex1)]
                        }

    startingVertex = None

    for vertex in affectedVertices:
        # The root port is broken, move to an alternate port if possible
        if(affectedVertices[vertex][1] == ROOT_ROLE):
            startingVertex = vertex
            getNewRootPort(G, vertex)

        elif(affectedVertices[vertex][1] == ALTERNATE_ROLE):
            G.nodes[vertex]["Delete"][affectedVertices[vertex][0]] += 1

            logging.warning(f"{vertex} - Alternate port broken, no change.")

        else:
            logging.warning(f"{vertex} - Designated port broken, no change.")

        affectedVertices[vertex][1] = "B"

    logging.warning("")

    # Remove the edge from the graph
    if(G.has_edge(brokenVertex1, brokenVertex2)):
        G.remove_edge(brokenVertex1, brokenVertex2)
    else:
        G.remove_edge(brokenVertex2, brokenVertex1)

    # Start sending and reconverging, if necessary
    if(startingVertex):
        send(G, r, startingVertex)

    verboseOutput(G)

    return


def send(G, root, sender, treeValidator):
    logging.warning(f"\n-------------------{sender} sending [{G.nodes[sender]['VV']}]-------------------")

    for receiver in G.neighbors(sender):
        logging.warning(f"\n+++++++++++{receiver} receiving [{G.nodes[receiver]['VV']}]+++++++++++")
        G.graph["step"] += 1 # For each neighbor that has received an RSTA Vector

        # If the receiver is the root, skip, as the root won't have any changes
        if(receiver == root):
            logging.warning("I am root, ignore.")
            continue

        # Make a copy of the receivers current parent vector, note that it hasn't been updated yet (may not be updated)
        updated = False
        receiverOldPV = deepcopy(G.nodes[receiver]['PV']) # PV = Parent Vector
        receivedOldTV = deepcopy(G.nodes[receiver]['RT'][(receiver, sender)]) # TV = Table Vector

        # "Receive" the vector on the neighbor and update the weight +1 for the edge it traveled over
        receivedVector = RSTAVector(G.nodes[sender]['VV'].RPC + 1, G.nodes[sender]['VV'].VID)
        
        # Update table with what you've received [VV from sender is noted]
        G.nodes[receiver]["RT"][(receiver, sender)][0] = receivedVector

        # If the device has already seen this before, don't do anything
        if(receivedVector == receivedOldTV[0]):
            logging.warning("VV hasn't been updated, ignore.")
            continue
        
        # If there is a situation where there is no parent
        elif(receiverOldPV is None):
            logging.warning("No current root, sender is the new root by default.")
            treeValidator.addParent(sender, receiver)
            G.graph["step"] += 1 # For each neighbor that has received the updated information

            # Update parent and vertex vectors
            G.nodes[receiver]['PV'] = (receiver, sender)
            G.nodes[receiver]['VV'] = RSTAVector(receivedVector.RPC, G.nodes[receiver]['VID'])

            # If this was previously an alternate port, it needs to be removed from the priority queue lazily
            if(G.nodes[receiver]["RT"][(receiver, sender)][1] == ALTERNATE_ROLE):
                G.nodes[receiver]["Delete"][receivedOldTV[0]] += 1
                logging.warning("Interface was set to alternate prior, mark for removal.")

            # Update table vector
            G.nodes[receiver]["RT"][(receiver, sender)][1] = ROOT_ROLE

            logging.warning(f"PV ---> {G.nodes[receiver]['PV']}")
            logging.warning(f"VV ---> {G.nodes[receiver]['VV']}")
            logging.warning(f"{receiver, sender} Role ---> {ROOT_ROLE}")

        # If the received vector is the best vector heard from all neighbors
        elif(receivedVector < G.nodes[receiver]["RT"][receiverOldPV][0]):
            logging.warning("Sender beats current PV, new root.")
            treeValidator.addParent(sender, receiver)
            G.graph["step"] += 1 # For each neighbor that has received the updated information

            # Update parent and vertex vectors
            G.nodes[receiver]['PV'] = (receiver, sender)
            G.nodes[receiver]['VV'] = RSTAVector(receivedVector.RPC, G.nodes[receiver]['VID'])

            # If this was previously an alternate port, it needs to be removed from the priority queue lazily
            if(G.nodes[receiver]["RT"][(receiver, sender)][1] == ALTERNATE_ROLE):
                G.nodes[receiver]["Delete"][receivedOldTV[0]] += 1
                logging.warning("Interface was set to alternate prior, mark for removal.")

            # Update table vector
            G.nodes[receiver]["RT"][(receiver, sender)][1] = ROOT_ROLE

            logging.warning(f"PV ---> {G.nodes[receiver]['PV']}")
            logging.warning(f"VV ---> {G.nodes[receiver]['VV']}")
            logging.warning(f"{(receiver, sender)} Role ---> {ROOT_ROLE}")

            # The old root port needs to be updated to an alternate port, if applicable
            G.nodes[receiver]["RT"][receiverOldPV][1] = ALTERNATE_ROLE
            G.nodes[receiver]["AVPQ"].put(G.nodes[receiver]["RT"][receiverOldPV][0])

            logging.warning(f"{receiverOldPV} Role ---> {ALTERNATE_ROLE}")
            logging.warning(f"{receiverOldPV} put into AVPQ")
            G.graph["step"] += 1

        # If the receiver has the better vector on the link
        elif(G.nodes[receiver]['VV'] < G.nodes[sender]['VV']):
            logging.warning("Sender has an inferior VV.")
            G.graph["step"] += 1 # For each neighbor that has received the updated information

            # If this was previously an alternate port, it needs to be removed from the priority queue lazily
            if(G.nodes[receiver]["RT"][(receiver, sender)][1] == ALTERNATE_ROLE):
                G.nodes[receiver]["Delete"][receivedOldTV[0]] += 1
                logging.warning("Interface was set to alternate prior, mark for removal.")
            # If this was previously a root port, a new root port must be found or reset
            elif(G.nodes[receiver]["RT"][(receiver, sender)][1] == ROOT_ROLE):
                getNewRootPort(G, receiver)    

            # Update table vector
            G.nodes[receiver]["RT"][(receiver, sender)][1] = DESIGNATED_ROLE 

            logging.warning(f"{(receiver, sender)} Role ---> {DESIGNATED_ROLE}")               

        # If it is the alternate port on the link
        else:
            logging.warning("Sender has the superior VV.")
            G.graph["step"] += 1 # For each neighbor that has received the updated information

            # If the link was already alternate, but now has an updated value, remove the old entry from the PQ
            if((receivedOldTV[1] == ALTERNATE_ROLE) and (receivedOldTV[0] != G.nodes[receiver]["RT"][(receiver, sender)][0])):
                G.nodes[receiver]["Delete"][receivedOldTV[0]] += 1
                logging.warning("Interface was already set to alternate prior, mark old vector for removal.")
            else:
                G.nodes[receiver]["RT"][(receiver, sender)][1] = ALTERNATE_ROLE
                logging.warning(f"{(receiver, sender)} Role ---> {ALTERNATE_ROLE}")   
            
            G.nodes[receiver]["AVPQ"].put(receivedVector)
            logging.warning(f"{receiverOldPV} put into AVPQ")
            G.graph["step"] += 1

        # Note the change that needs to be propagated
        updated = True

        if(updated):
            Q.append(receiver)
            logging.warning("Added to the send queue.")

    if(Q):
        s = Q.pop(TOP_NODE)
        send(G, root, s, treeValidator)

    return


### RSTA ADDITIONAL FUNCTIONS ###
def resetTable(G, vertex):
    for localEdge in G.edges([vertex]):
        G.nodes[vertex]["RT"][localEdge] = [RSTAVector(float('inf'), G.nodes[vertex]['VID']), "U"]    

    return

def getNewRootPort(G, vertex):
    newRoot = getAlternatePort(G.nodes[vertex]["AVPQ"], G.nodes[vertex]["Delete"])

    if(not newRoot):
        G.nodes[vertex]['VV'] = RSTAVector(float('inf'), G.nodes[vertex]['VID'])
        G.nodes[vertex]['PV'] = None
        resetTable(G, vertex)
        
        logging.warning(f"{vertex} - Root port lost, no Alternate to fall back on.")

    else:
        rootPort = (vertex, G.graph['VID_to_vertex'][newRoot[1]])

        G.nodes[vertex]['PV'] = rootPort
        G.nodes[vertex]["RT"][rootPort][1] = ROOT_ROLE
        G.nodes[vertex]['VV'] = RSTAVector(G.nodes[vertex]["RT"][rootPort][0].RPC, G.nodes[vertex]['VID'])

        logging.warning(f"{vertex} - Root port lost, new root port is {rootPort}.")

    return

def getAlternatePort(PQ, deleteDict):
    # If there are no alternate ports, return as such
    if(PQ.empty()):
        return None
    
    # Find the best non-deleted alternate
    while not PQ.empty():
        alternate = PQ.get()

        if(deleteDict[alternate] > 0):
            deleteDict[alternate] -= 1
        else:
            return alternate

    # If all alternate ports were marked for deletion, there are none and return as such
    return None