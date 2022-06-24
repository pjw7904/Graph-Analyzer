#!/usr/bin/env python
from collections import defaultdict
from operator    import itemgetter
import networkx as nx

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


def generatePossibleVIDs(network, MT_root, node, startingVID=None, numOfVIDs=None):
    allPossibleVIDs = defaultdict(list)
    finalPVID       = {}
    finalVIDTable   = [] # Tuple for holding N number of VIDs
    #VIDStats        =
    activeInterface = None

    rootVID = ""
    PVID    = ""

    totalPossibleVIDs = 0

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

            possibleVIDTableAddition = (finalHop, VID)
            finalVIDTable.append(possibleVIDTableAddition)

        finalVIDTable.sort(key=lambda tup: len(tup[1])) # Sorts first by length then by value (ex: 1.1 is before 1.2 because .1 is < .2)
        activeInterface = finalVIDTable[0][0]
        PVID = finalVIDTable[0][1]

        totalPossibleVIDs = len(finalVIDTable)

        if(numOfVIDs and len(finalVIDTable) > numOfVIDs):
            del finalVIDTable[len(finalVIDTable) - (len(finalVIDTable) - numOfVIDs):]

        for VIDEntry in finalVIDTable:
            allPossibleVIDs[VIDEntry[0]].append(VIDEntry[1])

        finalPVID[activeInterface] = PVID


    else:
        allPossibleVIDs["Self"] = rootVID
        finalPVID["Self"]       = rootVID

    VIDStats = (node, PVID, totalPossibleVIDs)

    return allPossibleVIDs, finalPVID
