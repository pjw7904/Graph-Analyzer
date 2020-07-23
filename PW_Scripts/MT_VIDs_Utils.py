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
            G[edges[0]][edges[1]]['intNum'] = intNum
            intNum += 1

    return
