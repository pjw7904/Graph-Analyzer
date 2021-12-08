import logging

from collections import namedtuple
from tabulate import tabulate
from timeit import default_timer as timer # Get elasped time of execution

# Location/name of the log file
LOG_FILE = "results/log_results/RSTA_Output.log"

# Constant for popping in send queue
TOP_NODE = 0

# Vector that is exchanged between vertices to determine tree structure
RSTAVector = namedtuple("RSTA_Vector", "RPC BID")

# Sending Queue
Q = []

def setBIDs(G, root):
    IDCount = 0

    for node in G:
        G.nodes[node]['BID'] = chr(65 + IDCount)
    
        if(node == root):
            logging.debug("Root node is {0}, BID = {1}\n".format(node, G.nodes[node]['BID']))

        else:
            logging.debug("Non-Root node {0}, BID = {1}\n".format(node, G.nodes[node]['BID']))

        IDCount += 1

    logging.debug("---------\n\n")

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
def init(G, r, loggingStatus):
    setLoggingLevel(loggingStatus)

    setBIDs(G, r)

    Q.append(r)

    for v in G:
        G.nodes[v]['VV'] = RSTAVector(float('inf'), G.nodes[v]['BID'])
        G.nodes[v]['PV'] = RSTAVector(float('inf'), G.nodes[v]['BID'])
        G.nodes[v]['AV'] = RSTAVector(float('inf'), G.nodes[v]['BID'])

    G.nodes[r]['VV'] = RSTAVector(0, G.nodes[r]['BID'])
    G.nodes[r]['PV'] = RSTAVector(0, G.nodes[r]['BID'])
    G.nodes[r]['AV'] = RSTAVector(0, G.nodes[r]['BID'])

    s = Q.pop(TOP_NODE)
    sendVertexVector(G, r, s)

    for v in G:
        formattedOutput = "{nodeName}\n\tVV({BID}) = {VV}\n\tPV({BID}) = {PV}\n\tAV({BID}) = {AV}\n"
        logging.debug(formattedOutput.format(nodeName=v, BID=G.nodes[v]['BID'], VV=prettyVectorOutput(G,v,"VV"), PV=prettyVectorOutput(G,v,"PV"), AV=prettyVectorOutput(G,v, "AV")))

    return

'''
Input: vertex s, the vertex sending its vector to neighbors
'''
def sendVertexVector(G, r, s):
    for x in G.neighbors(s):
        updatedVector = False

        VV_s_prime = RSTAVector(G.nodes[s]['VV'].RPC + 1, G.nodes[s]['BID'])
        VV_x_prime = RSTAVector(G.nodes[x]['VV'].RPC + 1, G.nodes[x]['BID'])

        if(senderVectorIsSuperior(VV_s_prime, VV_x_prime)):
            if(senderVectorIsSuperior(G.nodes[s]['VV'], G.nodes[x]['PV'])):
                updatedVector = True

                G.nodes[x]['AV'] = G.nodes[x]['PV']          
                G.nodes[x]['PV'] = G.nodes[s]['VV']
                G.nodes[x]['VV'] = RSTAVector(VV_s_prime.RPC, G.nodes[x]['BID'])

            # VV_s_prime.BID != G.nodes[x]['PV'].BID and
            elif(senderVectorIsSuperior(G.nodes[s]['VV'], G.nodes[x]['AV'])):
                G.nodes[x]['AV'] = G.nodes[s]['VV'] 

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

def setLoggingLevel(requiresLogging):
    if(requiresLogging):
        logging.basicConfig(format='%(message)s', filename=LOG_FILE, filemode='w', level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    return