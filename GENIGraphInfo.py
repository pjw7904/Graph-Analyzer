#!/usr/bin/env python

import numpy as np
import math
import copy
import networkx as nx
from spanningTreeUtilities_new import *
#from GENIutils import * - We need Scapy and don't have it right now

# I'm not sure if this is even needed right now, but porting it over just in case
np.set_printoptions(precision=3, linewidth=120)
G = nx.Graph()
type(G)
###############

graphFile = open("Topology.txt", "r")

edges_org = []
for edge in graphFile:
    edges_org.append(edge.strip())

# ###Select the Edges and the Root Vertex
edges = copy.deepcopy(edges_org) # Select the List of Edges
print(edges)
