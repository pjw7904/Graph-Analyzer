import numpy as np
import math
import copy

from spanningTreeUtilities import *

from collections import namedtuple
#Mesh = namedtuple('Mesh','root graph costs tree coords')
MeshedTree = namedtuple('MeshedTree','verts pathBundles parents children')
MeshedPaths = namedtuple('MeshedPaths','verts nbrs root pathBundles sendingEvents')

FIRST = 0
REST = 1
LAST = -1
REV = -1

def getEdgeChoice():
    edgeChoice = {}   #Dictionary of all edge choices
###graph 0   K4   Tetrahedron   3-regular   v4, e6
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("ca")
    edges.append("ad")
    edges.append("bd")
    edges.append("cd")

    edgeChoice['K4'] = edgesUpper(edges)

###graph 1   K5   Star in Box   4-regular   v5, e10
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ea")

    edges.append("ac")
    edges.append("ce")
    edges.append("eb")
    edges.append("bd")
    edges.append("da")

    edgeChoice['K5'] = edgesUpper(edges)

###graph 2   Peterson   3-regular   v10, e15
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ea")

    edges.append("af")
    edges.append("bg")
    edges.append("ch")
    edges.append("di")
    edges.append("ej")

    edges.append("fh")
    edges.append("hj")
    edges.append("jg")
    edges.append("gi")
    edges.append("if")

    edgeChoice['peterson'] = edgesUpper(edges)

###graph 3   K6   5-regular   v6, e15
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ef")
    edges.append("fa")

    edges.append("ac")
    edges.append("ce")
    edges.append("ea")

    edges.append("bd")
    edges.append("df")
    edges.append("fb")

    edges.append("ad")
    edges.append("be")
    edges.append("cf")

    edgeChoice['K6'] = edgesUpper(edges)

###graph 4   Octahedron    4-regular   v6, e12
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ef")
    edges.append("fa")

    edges.append("ac")
    edges.append("ce")
    edges.append("ea")

    edges.append("bd")
    edges.append("df")
    edges.append("fb")

    edgeChoice['octa'] = edgesUpper(edges)

###graph 5   Cube    3-regular   v8, e12
    edges = []
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("da")

    edges.append("ae")
    edges.append("bf")
    edges.append("cg")
    edges.append("dh")

    edges.append("ef")
    edges.append("fg")
    edges.append("gh")
    edges.append("hf")

    edgeChoice['cube'] = edgesUpper(edges)

###graph 6   Dodecahedron    3-regular   v20, e30
    edges=[]
    edges.append("ab")
    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ea")

    edges.append("af")
    edges.append("bh")
    edges.append("cj")
    edges.append("dl")
    edges.append("en")

    edges.append("fg")
    edges.append("gh")
    edges.append("hi")
    edges.append("ij")
    edges.append("jk")
    edges.append("kl")
    edges.append("lm")
    edges.append("mn")
    edges.append("np")
    edges.append("pf")

    edges.append("gq")
    edges.append("ir")
    edges.append("ks")
    edges.append("mt")
    edges.append("pu")

    edges.append("qr")
    edges.append("rs")
    edges.append("st")
    edges.append("tu")
    edges.append("uq")

    edgeChoice['dodec'] = edgesUpper(edges)

###graph 7   Icosahedron     5-regular   v12, e30
    edges=[]
    edges.append("ab")
    edges.append("ac")
    edges.append("ad")
    edges.append("ae")
    edges.append("af")

    edges.append("bc")
    edges.append("cd")
    edges.append("de")
    edges.append("ef")
    edges.append("fb")

    edges.append("lg")
    edges.append("lh")
    edges.append("li")
    edges.append("lj")
    edges.append("lk")

    edges.append("gh")
    edges.append("hi")
    edges.append("ij")
    edges.append("jk")
    edges.append("kg")

    edges.append("bg")
    edges.append("bh")
    edges.append("ch")
    edges.append("ci")
    edges.append("di")
    edges.append("dj")
    edges.append("ej")
    edges.append("ek")
    edges.append("fk")
    edges.append("fg")

    edgeChoice['icosa'] = edgesUpper(edges)

###graph 8   Cayley S4     4-regular   v24, e48
    edges=[]
    edges.append("ab")
    edges.append("ac")
    edges.append("ad")
    edges.append("ae")

    edges.append("bc")
    edges.append("bf")
    edges.append("bg")
    edges.append("ch")
    edges.append("ci")
    edges.append("di")
    edges.append("dj")
    edges.append("dk")
    edges.append("ek")
    edges.append("el")
    edges.append("ef")

    edges.append("fl")
    edges.append("fn")
    edges.append("gh")
    edges.append("gn")
    edges.append("gp")
    edges.append("hp")
    edges.append("hq")
    edges.append("ij")
    edges.append("iq")
    edges.append("jr")
    edges.append("js")
    edges.append("ks")
    edges.append("kt")
    edges.append("lt")
    edges.append("lm")

    edges.append("mn")
    edges.append("mu")
    edges.append("mv")
    edges.append("nv")
    edges.append("pv")
    edges.append("pw")
    edges.append("qr")
    edges.append("qw")
    edges.append("rw")
    edges.append("rx")
    edges.append("st")
    edges.append("sx")
    edges.append("tu")

    edges.append("ux")
    edges.append("uy")
    edges.append("vy")
    edges.append("wy")
    edges.append("xy")

    edgeChoice['S4'] = edgesUpper(edges)

###graph 9   TestBed T16    2-connected     v16, e33
    edges=[]
    edges.append("ab")
    edges.append("ac")
    edges.append("bc")
    edges.append("bd")
    edges.append("be")

    edges.append("ce")
    edges.append("cf")
    edges.append("de")
    edges.append("dg")
    edges.append("dh")

    edges.append("eh")
#    edges.append("ei")  #2
#    edges.append("ef")  #3
    edges.append("fi")
    edges.append("fj")

    edges.append("gh")
    edges.append("gk")
#    edges.append("hi")  #1
    edges.append("hk")
#    edges.append("hl")  #2

    edges.append("ij")
    edges.append("il")
    edges.append("im")
    edges.append("jm")
#    edges.append("kl")  #3

    edges.append("kn")
    edges.append("lm")
    edges.append("ln")
    edges.append("lp")
    edges.append("mp")

    edges.append("np")
    edges.append("nq")
    edges.append("pq")

    edgeChoice['T16'] = edgesUpper(edges)

    return edgeChoice

def getParents(verts,pathBundles):
    parents = {}
    for vert in verts:
        bndl = pathBundles[vert]
        if len(bndl) == 0:
            parents = {}
            print('Empty path bundle for vert ',vert)
            break
        topPath = bndl[FIRST]
        if len(topPath) > 1:
            parents[vert] = topPath[-2]
        else:
            parents[vert] = ''
    return parents


# The core function of computing path bundles for a given network
def getMeshedPaths(nbrs,root):
    verts = sorted(list(nbrs.keys())) # Lexigraphically sorted list of nodes/vertices because each neighbor-dictionary key is a node/vertex.

    # Dictonaries for the path bundles and incoming neighbor bundles
    pathBundles = {}
    inBaskets = {}

    for vert in verts:         # for each node in the network...
        pathBundles[vert] = [] # Create an empty path bundle.
        inBaskets[vert] = []   # Create an empty neighbor bundle input queue.

    pathBundles[root] = [root] # The root node will only ever have a path bundle of size 1 (itself/its own label).
    sending = [root]           # The root node is the first node to send path bundle information to neighbors. Sending represents nodes which need to update its neighbors
    sendingEvents = []         # The number of nodes that need to update their neighbors in a given step/event (don't focus on this for convergence).

    while sending: # While there are node's that need to send path bundle updates / while every node has not converged with its final path bundle...
        sendingEvents.append(len(sending)) # Append the number of entries in the sending list to sendingEvents (don't focus on this for convergence).
        nextSending = []                   # Clear the list that decides which node sends a path bundle update next.
        receiving = []                     # Clear the list of nodes that receive a path bundle update based on the current sender.

        for vert in sending: # For each node that needs to send a path bundle update...
            for nbr in nbrs[vert]:                       # For each neighbor the current node has, send the current node's path bundle...
                inBaskets[nbr].append(pathBundles[vert]) # The neighbor receives the neighbor bundle sent by the current node and puts it in its input queue.
                receiving.extend(nbr)                    # Note that the neighbor has received the neighbor bundle.

        receiving = list(set(receiving)) # Remove all duplicate neighbors from the received list due to multiple senders that could share a neighbor.

        for vert in receiving: # For each node that received a neighbor bundle update from a sender...
            acyclics = []      # Create a list that will contain paths (not a cycle/network loop).
            for bndl in inBaskets[vert]: # For each neighbor bundle the receiving node obtained...
                for path in bndl:         # For each path in the current neighbor bundle being analyzed...
                    if vert not in path:  # If the node which received the neighbor bundle is not in the current path (its label is not present in the path):
                        acyclics.append(path + vert) # Take the path and append the receiving node, which completes the path from the root to the receiver.
            bndl = copy.deepcopy(pathBundles[vert])  # Get a copy of the receiving node's current path bundle
            bndl = list(set(bndl).union(acyclics))   # Add the valid paths from the neighbor bundle to the path bundle to create a grand bundle
            bndl.sort()
            bndl.sort(key=len) # Sort the grand bundle by the length of the path, meaning the shortest path is the first index of the list.

            if len(bndl) < 3: # If the number of paths in the updated path bundle is less than three...
                newBndl = bndl
            else:
                newBndl = trimBundle(bndl) # Trim the updated path bundle down to three entries.

            chng = list(set(newBndl).difference(set(pathBundles[vert]))) # Find the new paths (if any) that the receiving node added to its path bundle.
            if chng:                        # If there was a new path added to the receiving node's path bundle...
                pathBundles[vert] = newBndl # Designate the updated path bundle as the new official path bundle of that node
                nextSending.append(vert)    # Add node to the list of nodes which needs to send a path bundle update (because it has new paths).
            inBaskets[vert] = [] # Received neighbor bundle(s) have been processed, so they can be cleared from the node's input queue.

        sending = nextSending # The node(s) which needs to send path bundle updates are marked as such.

    return MeshedPaths(verts,nbrs,root,pathBundles,sendingEvents)


def getPathEdges(path):
    p0 = path[:LAST]
    p1 = path[REST:]
    edges = [''.join(sorted([v0,v1])) for v0, v1 in zip(p0,p1)]

    return set(edges)

def trimBundle(bndl):
    pPath = bndl[FIRST]
    if len(pPath) < 3:
        newBndl = bndl[FIRST:2]
    else:
        newBndl = [pPath]
        ppEdge = getPathEdges(pPath)
        ppVert = set(pPath[REST:LAST])
        for nPath in bndl[REST:]:
            npEdge = getPathEdges(nPath)
            npVert = set(nPath)
            nbEdge = ppEdge - npEdge
            nbVert = ppVert - npVert
            if nbEdge or nbVert:
                newBndl.append(nPath)
                ppEdge = ppEdge - nbEdge
                ppVert = ppVert - nbVert
            if not(ppEdge or ppVert):
                break

    return newBndl

def getParentsValidity(verts,parents,root):
    valid = True
    msg = 'Parents build a spanning tree.'
    if root not in parents:
        valid = False
        msg = 'Root must be in "parents.keys"'
    elif parents[root] != '':
        valid = False
        msg = 'Root parent must be the null string.'
    else:
        inputs = set(parents.keys())
        if inputs != set(verts):
            valid = False
            msg = 'Parents.keys must equal verts.'
        else:
            twin = copy.deepcopy(parents)
            twin.pop(root)
            outputs = list(twin.values())
            if not set(outputs).issubset(set(verts)):
                valid = False
                msg = 'Parents of root progeny must be a subset of verts.'
            else:
                approved = [root]
                pending = []
                untested = list(twin.keys())
                vert = ''
                bail = 0
                while untested:
                    if vert == '':
                        vert = untested.pop(0)
                        pending.append(vert)
                    vert = twin[vert]
                    if vert in approved:
                        approved.extend(pending)
                        pending = []
                        vert = ''
                    elif vert in pending:
                        valid = False
                        msg = 'Parent loop detected.'
                        break
                    else:
                        pending.append(vert)
                        untested.remove(vert)
                    bail += 1
                    if bail > 100:
                        msg = 'Bailout limit exceeded.'
                        break
    return valid, msg

def disableVert(pathBundles,badVert):
    if badVert not in pathBundles:
        newBundles = {}
        msg = 'Label ' + badVert + ' is unknown.'
    elif pathBundles[badVert] == [badVert]:
        newBundles = {}
        msg = 'The root has failed and the pathBundle is dead.'
    else:
        newBundles = copy.deepcopy(pathBundles)
        for vert, bndl in pathBundles.items():
            if vert == badVert:
                newBundles.pop(vert)
            else:
                bag = []
                for path in bndl:
                    if badVert in path:
                        bag.append(path)
                newBundles[vert] = sorted(list(set(bndl) - set(bag)),key=len)
        msg = 'Disabled vert removed.'
    return newBundles, msg

def disableVertList(pathBundles,badVertList):
    newBundles = copy.deepcopy(pathBundles)
    msgDict = {}
    for badVert in badVertList:
        newBundles, msg = disableVert(newBundles,badVert)
        msgDict[badVert] = msg
    return newBundles, msgDict

def disableEdge(pathBundles,badEdge):
    revEdge = badEdge[LAST] + badEdge[FIRST]
    if len(badEdge) != 2:
        newBundles = {}
        msg = 'Edge ' + badEdge + ' must have two characters.'
    elif (badEdge[FIRST] not in pathBundles) or (badEdge[LAST] not in pathBundles):
        newBundles = {}
        msg = 'Edge ' + badEdge + ' has unknown vert.'
    else:
        newBundles = copy.deepcopy(pathBundles)
        for vert, bndl in pathBundles.items():
            bag = []
            for path in bndl:
                if (badEdge in path) or (revEdge in path):
                    bag.append(path)
            newBundles[vert] = sorted(list(set(bndl) - set(bag)),key=len)
        msg = 'Disabled edge removed.'
    return newBundles, msg
