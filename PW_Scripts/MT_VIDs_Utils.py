#!/usr/bin/env python
import networkx          as nx
import numpy             as np
import matplotlib.pyplot as plt
import statistics
import math

def createMeshedTreeTable(G):
    nx.set_node_attributes(G, [], 'VIDTable')

    return


def addInterfaceNums(G):
    for node in G:
        nodeEdges = G.out_edges(node)
        intNum = 1

        for edges in nodeEdges:
            G[edges[0]][edges[1]]['intNum'] = str(intNum)
            intNum += 1

    return


def generatePossibleVIDs(network, MT_root, node):
    allPossibleVIDs = []
    rootVID = "1" # Eventually, this can become a parameter that can be changed with multiple roots

    paths = nx.all_simple_paths(network, source=MT_root, target=node)

    for path in map(nx.utils.pairwise, paths):
        VID = rootVID
        switchedPath = list(path)

        for hop in switchedPath:
            egressNode  = hop[0]
            ingressNode = hop[1]
            VID += "." + network[egressNode][ingressNode]['intNum']

        allPossibleVIDs.append(VID)

    return allPossibleVIDs
