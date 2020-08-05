#!/usr/bin/env python
# coding: utf-8

# #MeshedPaths

# In[1]:
import sys

# In[2]:
import numpy as np
import math
import copy

from spanningTreeUtilities import * # from franklin.spanningTreeUtilities import *
from meshedPathUtilities import * # from franklin.meshedPathUtilities import *

np.set_printoptions(precision=3,linewidth=120)

# ##Edge Lists
# In[4]:
edgeChoice = getEdgeChoice()
#print('Edge choices are: ',sorted(list(edgeChoice.keys())))

# ###Select the Edges and the Root Vertex
# In[5]:
#choice = 'icosa'    #Select the list of edge choices above
#choice = 'dodec'    #Select the list of edge choices above
choice = 'peterson'    #Select the list of edge choices above
#choice = 'T16'    #Select the list of edge choices above
edges = copy.deepcopy(edgeChoice[choice])
print("\nGraph choice: {0}".format(choice))
print('\nEdges: ',edges)

# In[6]:
root = 'A'   #Declare the root vertex
print('\nThe root vertex is:',root)

# ###Extract the Vertices and the Neighbors
# In[7]:
graf = getGraph(edges)

# In[8]:
#print("\nGraph and its neighbors: {0}".format(graf))

# In[9]:
verts = graf.verts
print("\nVertices: {0}".format(verts))

# In[10]:
nbrs = graf.nbrs
print("\nNeighbors: {0}".format(nbrs))

# In[11]:
mPaths = getMeshedPaths(nbrs, root)
print("\nMeshed Paths:")

# In[12]:
# Used to actually print the paths, it's not printed in the above print statement
null = [print(mPaths.pathBundles[vert]) for vert in verts]

# In[13]:
bndlSizes = [len(mPaths.pathBundles[vert]) for vert in verts]
bndlSum = sum(bndlSizes)
print('\nbundle sizes = {0}'.format(bndlSizes))
print('total paths  = {0}'.format(bndlSum))

# In[14]:
parents = getParents(verts, mPaths.pathBundles)
print("Node parents: {0}".format(parents))

# In[15]:
valid = getParentsValidity(verts,parents,root)
print("Validation: {0}".format(valid))

# In[16]:
children = getChildren(verts,parents)
print("Node children: {0}".format(children))
