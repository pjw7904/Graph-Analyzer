#!/usr/bin/env python
# coding: utf-8
import sys
import numpy as np
import math
import copy

# Libraries of functions to perform graph-related calcuations and formatting
from spanningTreeUtilities import *
from meshedPathUtilities import *

# Numpy stuff, not 100% sure what this does yet, most likely how it formats printed tuples
np.set_printoptions(precision=3,linewidth=120)

# Populate structure with graphs (different graph options that are hard-coded)
edgeChoice = getEdgeChoice()

# Select the graph and root to use for the simulation (from getEdgeChoice())
choice = 'peterson'
root = 'A'
edges = copy.deepcopy(edgeChoice[choice])

# Printing information about the graph chosen
print("\nGraph choice: {0}".format(choice))
print('\nEdges: ',edges)
print('\nThe root vertex is:',root)

# Extract the Vertices and the Neighbors of those vertices
graf = getGraph(edges)

# Print the verticies and the neighbors of those verticies
verts = graf.verts
nbrs = graf.nbrs
print("\nVertices: {0}".format(verts))
print("\nNeighbors: {0}".format(nbrs))

# Running a simulated Meshed Tree Algorithm (MTA), which utilizies path bundles
mPaths = getMeshedPaths(nbrs, root)
print("\nMeshed Paths:")

# Print the paths
[print(mPaths.pathBundles[vert]) for vert in verts]

# Stats about the bundles from the verticies
bndlSizes = [len(mPaths.pathBundles[vert]) for vert in verts]
bndlSum = sum(bndlSizes)
parents = getParents(verts, mPaths.pathBundles)
valid = getParentsValidity(verts,parents,root)
children = getChildren(verts,parents)

print('\nbundle sizes = {0}'.format(bndlSizes))
print('total paths  = {0}'.format(bndlSum))
print("Node parents: {0}".format(parents))
print("Validation: {0}".format(valid))
print("Node children: {0}".format(children))
