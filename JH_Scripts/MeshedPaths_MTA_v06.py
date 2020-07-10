#!/usr/bin/env python
# coding: utf-8

# #MeshedPaths

# In[1]:


import sys
#sys.path.append("../")
#sys.path.append('C:/Users/John/Documents/Python/MachineLearning')
#get_ipython().run_line_magic('load_ext', 'autoreload')
#get_ipython().run_line_magic('autoreload', '2')


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
print('Edge choices are: ',sorted(list(edgeChoice.keys())))


# ###Select the Edges and the Root Vertex

# In[5]:


#choice = 'icosa'    #Select the list of edge choices above
#choice = 'dodec'    #Select the list of edge choices above
choice = 'S4'    #Select the list of edge choices above
#choice = 'T16'    #Select the list of edge choices above
edges = copy.deepcopy(edgeChoice[choice])
print('Edges: ',edges)


# In[6]:


root = 'A'   #Declare the root vertex
print('The root vertex is:',root)


# ###Extract the Vertices and the Neighbors

# In[7]:


graf = getGraph(edges)


# In[8]:


graf


# In[9]:


verts = graf.verts
print(verts)


# In[10]:


nbrs = graf.nbrs
print(nbrs)


# In[11]:


mPaths = getMeshedPaths(nbrs,root)
mPaths


# In[12]:


null = [print(mPaths.pathBundles[vert]) for vert in verts]


# In[13]:


bndlSizes = [len(mPaths.pathBundles[vert]) for vert in verts]
bndlSum = sum(bndlSizes)
print('bundle sizes = ',bndlSizes)
print('total paths  = ',bndlSum)


# In[14]:


parents = getParents(verts,mPaths.pathBundles)
parents


# In[15]:


valid = getParentsValidity(verts,parents,root)
valid


# In[16]:


children = getChildren(verts,parents)
children
