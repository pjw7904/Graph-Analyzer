#!/usr/bin/env python

import numpy as np
import math
import copy
import networkx as nx
import matplotlib.pyplot as plt # Used for drawing the graph
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
print("\nedges:\n{0}".format(edges))
root = "node-0"

# ###Extract the Vertices and the Neighbors
verts = edgesToVerts(edges)
nbrs = edgesToNbrs(edges)
print("\nedgesToVerts:\n{0}".format(verts))
print("\nedgesToNbrs:\n{0}".format(nbrs))


# ###Find the Adjacency Matrix 0
adj0 = getAdjacencyMatrix(verts,nbrs)
print("\ngetAdjacencyMatrix:\n{0}".format(adj0))

# ###Find the Total Number of Spanning Trees
nTrees0 = getNumSpanningTrees(root,verts,adj0)
print("\ngetNumSpanningTrees:\n{0}".format(nTrees0))

# ###Find the Hops List, and Compute the Hop Counts
hops = nbrsToHops(root,nbrs)
hopCounts = hopsToHopCounts(hops)
print("\nnbrsToHops:\n{0}".format(len(hops)-1))
print("\nnbrsToHops breakdown:\n{0}".format(hops))
print("\nhopsToHopCounts:\n{0}".format(hopCounts))

# ###Find the Optimal Parents
optParents = getOptimalParents(root,verts,nbrs,hopCounts)
print("\ngetOptimalParents:\n{0}".format(optParents))

# ###Find the Adjacency Matrix 1
adj1 = getAdjacencyMatrix(verts,optParents)
print("\ngetAdjacencyMatrix (optimal):\n{0}".format(adj1))

# ###Find the Number of Optimal Spanning Trees
nTrees1 = getNumSpanningTrees(root,verts,adj1)
print("\ngetNumSpanningTrees (optimal):\n{0}".format(nTrees1))

# ###Find the Near-Optimal Parents
nearOptParents = getNearOptimalParents(root,verts,nbrs,hopCounts)
print("\nnearOptParents (near optimal):\n{0}".format(nearOptParents))

# ###Find the Adjacency Matrix 2
adj2 = getAdjacencyMatrix(verts,nearOptParents)
print("\nadj2 (near optimal):\n{0}".format(adj2))

# ###Find the Number of Near-Optimal Spanning Trees
nTrees2 = getNumSpanningTrees(root,verts,adj2)
print("\nnTrees2 (near optimal):\n{0}".format(nTrees2))

# ###Tree Summary
nTrees3 = len(verts)
print('\nNumber of spanning trees required to repair any single link failure is:\n{0}\n'.format(nTrees3))
print('=== Summary of spanning tree counts: ===\n+ Total Trees: {0}\n+ Total Optimal Trees: {1}\n+ Total Near-Optimal Trees: {2}\n+ Number of Verticies: {3}\n'
      .format(nTrees0,nTrees1,nTrees2,nTrees3))

print("---------------------------------\n")

parents = getRandomOptimalSpanningTree(verts,optParents)
print("A random optimal tree from the inputted graph:\n{0}\n".format(parents))

children = {}
for vert in verts:
    children[vert] = [kid for kid in verts if vert in parents[kid]]
print("Children of the vertices:\n{0}\n".format(children))

friends = getFriends(verts,nbrs,parents,children)
print("Friends of the vertices:\n{0}\n".format(friends))

graf = getGraph(edges)
print("The graph:\n{0}\n".format(graf))

costs = getCosts(root,graf)
print("Cost of the graph:\n{0}\n".format(costs))

tree = getTree(graf,parents)
print("The Tree of the graph:\n{0}\n".format(tree))

print("VIDS:\n{0}\n".format(tree.vids))

seed = 'node-3'
fixPath = getFixPath(seed,tree,costs)
print("fixed path:\n{0}\n".format(fixPath))

###### DRAWING THE GRAPH STUFF
for edge in edges:
    test = edge.split("_")
    G.add_edge(*test)

nx.draw(G, with_labels=True)
plt.show() # display
