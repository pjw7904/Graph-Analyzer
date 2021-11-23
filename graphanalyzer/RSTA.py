from collections import namedtuple
from tabulate import tabulate
from timeit import default_timer as timer # Get elasped time of execution

# Location/name of the log file
LOG_FILE = "RSTA_Output.txt"

# Constant for popping in send queue
TOP_NODE = 0

# Port Role [state]. Setup: [ VERTEX [role]]------edge------[[role] VERTEX ]
DESIGNATED_ROLE = "Designated [FWD]" # Superior vertex on edge, forwards traffic, always one on each link
ROOT_ROLE       = "Root [FWD]"       # Best edge on node, forwards traffic
ALT_ROLE        = "Alternate [BLK]"  # Inferior vertex on edge, blocks traffic
STARTING_ROLE   = "Undefined [N/A]"  # Starting role, role undefined at startup

# Vector that is exchanged between vertices to determine tree structure
RSTAVector = namedtuple("RSTA_Vector", "RPC BID")

# Sending Queue
Q = []

def setBIDs(G, root):
    logFile = open(LOG_FILE, "w")
    IDCount = 0

    for node in G:
        G.nodes[node]['BID'] = chr(65 + IDCount)
    
        if(node == root):
            logFile.write("Root node is {0}, BID = {1}\n".format(node, G.nodes[node]['BID']))

        else:
            logFile.write("Non-Root node {0}, BID = {1}\n".format(node, G.nodes[node]['BID']))

        IDCount += 1

    logFile.write("---------\n\n")
    logFile.close()

    return

def prettyVectorOutput(G, v, vector):
    output = "{{{RPC}, {BID}}}"

    return output.format(RPC=G.nodes[v][vector].RPC, BID=G.nodes[v][vector].BID)

def prettyEdgeRolesOutput(G, v):
    output = ""

    for edge in list(G.edges(v)): 
        output += "\t{edge} = {role}\n".format(edge=edge, role=G.nodes[v][edge])

    return output

'''
Data:   RSTA Vector in the form {RPC, BID}, sending queue Q, 
        array of priority queues for each vertex alt, parent struture
        parent to link nodes with their upstream parent

Input:  Graph G, root node r

Output: Parent structure, which will create a shortest path tree
'''
def init(G, r):
    setBIDs(G, r)

    Q.append(r)

    for v in G:
        G.nodes[v]['VV'] = RSTAVector(float('inf'), G.nodes[v]['BID'])
        G.nodes[v]['PV'] = RSTAVector(float('inf'), G.nodes[v]['BID'])
        G.nodes[v]['AV'] = None

        for edge in list(G.edges(v)): 
            G.nodes[v][edge] = STARTING_ROLE

    G.nodes[r]['VV'] = RSTAVector(0, G.nodes[r]['BID'])
    G.nodes[r]['PV'] = RSTAVector(0, G.nodes[r]['BID'])
    G.nodes[r]['AV'] = None # This will stay null, as r is the root

    s = Q.pop(TOP_NODE)
    sendVertexVector(G, r, s)

    for v in G:
        formattedOutput = "{nodeName}\n\tVV({BID}) = {VV}\n\tPV({BID}) = {PV}\n{roles}\n"
        print(formattedOutput.format(nodeName=v, BID=G.nodes[v]['BID'], VV=prettyVectorOutput(G,v,"VV"), PV=prettyVectorOutput(G,v,"PV"), roles=prettyEdgeRolesOutput(G,v)))

    return

'''
Input: vertex s, the vertex sending its vector to neighbors
'''
def sendVertexVector(G, r, s):
    for x in G.neighbors(s):
        updatedVector = False

        VV_s_prime = RSTAVector(G.nodes[s]['VV'].RPC + 1, G.nodes[s]['BID'])
        VV_x_prime = RSTAVector(G.nodes[x]['VV'].RPC + 1, G.nodes[x]['BID'])

        s_x_edge = (s, x)
        x_s_edge = (x, s)

        if(senderVectorIsSuperior(VV_s_prime, VV_x_prime)):
            G.nodes[s][s_x_edge] = DESIGNATED_ROLE

            if(senderVectorIsSuperior(G.nodes[s]['VV'], G.nodes[x]['PV'])):
                G.nodes[x][x_s_edge] = ROOT_ROLE
                updatedVector = True
              
                for edge in list(G.edges(x)):
                    if(edge != (x, s)):
                        G.nodes[x][edge] = ALT_ROLE
               
                G.nodes[x]['PV'] = G.nodes[s]['VV']
                G.nodes[x]['VV'] = RSTAVector(VV_s_prime.RPC, G.nodes[x]['BID'])

        else:
            if(G.nodes[x][x_s_edge] != DESIGNATED_ROLE):
                G.nodes[x][x_s_edge] = DESIGNATED_ROLE
                updatedVector = True

        if(updatedVector):
            Q.append(x)

    if(Q):
        s = Q.pop(TOP_NODE)
        sendVertexVector(G, r, s)

    return

# Check the inputted vectors to see if the first is superior to the second
def senderVectorIsSuperior(senderVector, receiverVector):
    isSuperior = False

    if(
        (senderVector.RPC < receiverVector.RPC) or
        (senderVector.RPC == receiverVector.RPC and senderVector.BID < receiverVector.BID)
    ):
        isSuperior = True

    return isSuperior