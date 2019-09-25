#!/usr/bin/env python

import numpy as np
import math
import copy
import networkx as nx
from spanningTreeUtilities import *

np.set_printoptions(precision=3, linewidth=120)

G = nx.Graph()
type(G)


# ##Edge Lists

# ###graph 0
edges=[]
edges.append("ab")
edges.append("bc")
edges.append("cd")
edges.append("de")
edges.append("ea")
edges.append("bd")
edges0 = edgesUpper(edges)
#print("Graph 0:\n{0}".format(edges0))

# ###graph 1
edges=[]
edges.append("ab")
edges.append("bc")
edges.append("ad")
edges.append("be")
edges.append("cf")
edges.append("ae")
edges.append("bf")
edges.append("de")
edges.append("ef")
edges.append("dg")
edges.append("eh")
edges.append("fi")
edges.append("dh")
edges.append("ei")
edges.append("gh")
edges.append("hi")
edges1 = edgesUpper(edges)
#print("\nGraph 1:\n{0}".format(edges1))

# ###graph 2
edges=[]
edges.append("da")
edges.append("ar")
edges.append("dh")
edges.append("de")
edges.append("ae")
edges.append("ab")
edges.append("rb")
edges.append("rc")
edges.append("he")
edges.append("eb")
edges.append("bc")
edges.append("hk")
edges.append("ei")
edges.append("bf")
edges.append("cf")
edges.append("cg")
edges.append("ki")
edges.append("if")
edges.append("fg")
edges.append("km")
edges.append("im")
edges.append("il")
edges.append("fj")
edges.append("gj")
edges.append("ml")
edges.append("lj")
edges2 = edgesUpper(edges)
#print("\nGraph 2:\n{0}".format(edges2))

# ###graph 3
edges=[]
edges.append("ab")
edges.append("ac")
edges.append("bd")
edges.append("ce")
edges.append("cf")
edges.append("gd")
edges.append("gh") # this is the edge to comment out
edges.append("he")
edges.append("ei")
edges.append("if")
edges.append("fj")
edges.append("ij")
edges3 = edgesUpper(edges)
print("\nGraph 3 (currently used in example below):\n{0}".format(edges3))

# ###Select the Edges and the Root Vertex
edges = copy.deepcopy(edges3)           # Select the List of Edges
root = 'A'                              # Declare the root vertex
print('\nThe edges in graph 3 are:\n{0}\n'.format(edges))
print('The root vertex is:\n{0}\n'.format(root))

# ###Extract the Vertices and the Neighbors
verts = edgesToVerts(edges)
nbrs = edgesToNbrs(edges)
print("The verticies in graph 3:\n{0}\n".format(verts))
print("Verticies and their neighbors in graph 3:\n{0}\n".format(nbrs))

# ###Find the Adjacency Matrix 0
adj0 = getAdjacencyMatrix(verts,nbrs)
print("Adjacency Matrix for graph 3:\n{0}\n".format(adj0))


# ###Find the Total Number of Spanning Trees
nTrees0 = getNumSpanningTrees(root,verts,adj0)
print("Total number of spanning trees in graph 3 is: {0}".format(nTrees0))


# ###Find the Hops List, and Compute the Hop Counts
hops = nbrsToHops(root,nbrs)
print("Maximum hop count in graph 3 is: {0}\n".format(len(hops)-1))
print("Forwarding/Hopping breakdown:\n{0}\n".format(hops))

hopCounts = hopsToHopCounts(hops)
print("Hop cycles:\n{0}\n".format(hopCounts))

# ###Find the Optimal Parents
optParents = getOptimalParents(root,verts,nbrs,hopCounts)
print("Optimal parents:\n{0}\n".format(optParents))

# ###Find the Adjacency Matrix 1
adj1 = getAdjacencyMatrix(verts,optParents)
print("Optimal parents matrix:\n{0}\n".format(adj1))

# ###Find the Number of Optimal Spanning Trees
nTrees1 = getNumSpanningTrees(root,verts,adj1)
print("Number of optimal spanning trees is: {0}\n".format(nTrees1))

# ###Find the Near-Optimal Parents
nearOptParents = getNearOptimalParents(root,verts,nbrs,hopCounts)
print("Near-optimal parents:\n{0}\n".format(nearOptParents))

# ###Find the Adjacency Matrix 2
adj2 = getAdjacencyMatrix(verts,nearOptParents)
print("Near-optimal parents adjacency matrix:\n{0}\n".format(adj2))

# ###Find the Number of Near-Optimal Spanning Trees
nTrees2 = getNumSpanningTrees(root,verts,adj2)
print("Number of near-optimal spanning trees is: {0}\n".format(nTrees2))

# ###Tree Summary
nTrees3 = len(verts)
print('Number of spanning trees required to repair any single link failure is: {0}\n'.format(nTrees3))
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

seed = 'C'
fixPath = getFixPath(seed,tree,costs)
print("fixed path:\n{0}\n".format(fixPath))
