#!/usr/bin/env python
from collections import defaultdict
import networkx          as nx
import numpy             as np
import matplotlib.pyplot as plt
import statistics
import math

def createMeshedTreeTable(G):
    for node in G:
        G.nodes[node]['VIDTable'] = {}
        G.nodes[node]['PVID'] = {}

    return


def addInterfaceNums(G):
    for node in G:
        nodeEdges = G.out_edges(node)
        intNum = 1

        for edges in nodeEdges:
            G[edges[0]][edges[1]]['intNum'] = str(intNum)
            intNum += 1

    return


def generatePossibleVIDs(network, MT_root, node, startingVID=None):
    allPossibleVIDs = defaultdict(list)
    finalPVID       = {}
    ActiveInt       = None

    rootVID = ""
    PVID    = ""

    if(startingVID):
        rootVID = startingVID
    else:
        rootVID = "1"

    if(node != MT_root):
        paths = nx.all_simple_paths(network, source=MT_root, target=node)

        for path in map(nx.utils.pairwise, paths):
            switchedPath = list(path)
            finalHop = switchedPath[-1]

            # Taking the root VID, adding the first deminiting period (ex: 1 + "." = 1.), and then adding the egress value of each hop in the path deliminted (list comprehension)
            VID = rootVID + "." + ".".join(["{egressPort}".format(egressPort=network[hop[0]][hop[1]]['intNum']) for hop in switchedPath])

            allPossibleVIDs[finalHop].append(VID)

            if(len(VID) < len(PVID) or (len(VID) == len(PVID) and VID < PVID) or PVID == ""):
                PVID      = VID
                ActiveInt = finalHop

        finalPVID[ActiveInt] = PVID

    else:
        allPossibleVIDs["Self"] = rootVID
        finalPVID["Self"]       = rootVID

    return allPossibleVIDs, finalPVID
