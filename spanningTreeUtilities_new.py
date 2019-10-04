import numpy as np
import math
import copy

from collections import namedtuple
Mesh = namedtuple('Mesh','root graph costs tree coords')
Graph = namedtuple('Graph','edges verts nbrs')
Costs = namedtuple('Cost','verts hops hopCounts')
Tree = namedtuple('Tree','verts parents children friends vids')

FIRST = 0
REST = 1
LAST = -1
REV = -1

def edgesToVerts(edges): # Updated
    allEdges = [element for item in edges for element in item.split('_')]
    verts = list(allEdges)
    verts.sort()

    return verts

def edgesToNbrs(edges):
    verts = edgesToVerts(edges)
    nbrs = {}
    for vert in verts:
        tmp1 = [edge[1] for edge in edges if edge[0] == vert]
        tmp2 = [edge[0] for edge in edges if edge[1] == vert]
        tmp = list(set(tmp1+tmp2))
        nbrs[vert] = tmp
    return nbrs

def nbrsToHops(root,nbrs):
    hops = []
    prev = []
    curr = [root]
    while curr:
        hops.append(curr)
        next = []
        for vert in curr:
            next.extend(nbrs[vert])
        prev.extend(curr)
        curr = list(set(next)-set(prev))
    return hops

def hopsToHopCounts(hops):
    hopCounts = {}
    for k in range(len(hops)):
        for vert in hops[k]:
            hopCounts[vert] = k
    return hopCounts

def getOptimalParents(root,verts,nbrs,hopCounts):
    optimalParents = {root:[]}
    nonRoot = list(set(verts) - set(root))
    for vert in nonRoot:
        tmp = [nbr for nbr in nbrs[vert] if hopCounts[nbr]<hopCounts[vert]]
        optimalParents[vert] = tmp
    return optimalParents

def getNearOptimalParents(root,verts,nbrs,hopCounts):
    nearOptimalParents = {root:[]}
    nonRoot = list(set(verts) - set(root))
    for vert in nonRoot:
        tmp = [nbr for nbr in nbrs[vert] if hopCounts[nbr]<=hopCounts[vert]]
        nearOptimalParents[vert] = tmp
    return nearOptimalParents

def getAdjacencyMatrix(verts,nbrs):
    n = len(verts)
    adj = np.zeros([n, n], dtype = int)
    for vert in verts:
        row = verts.index(vert)
        for nbr in nbrs[vert]:
            col = verts.index(nbr)
            adj[row,col] = 1
    return adj

def adjToNbrs(verts,adj):
    n = len(verts)
    nbrs = dict()
    for row in range(n):
        vert = verts[row]
        tmp = []
        for col in range(n):
            if adj[row,col] > 0:
                tmp.append(verts[col])
        nbrs.update({vert:tmp})
    return nbrs

def getNumSpanningTrees(root,verts,adj):
    n = len(verts)
    uVec = np.ones([n], dtype = int)
    degs = adj.dot(uVec)
    lap1 = np.diag(degs) - adj

    nRoot = verts.index(root)
    tmp = np.delete(lap1,nRoot,0)
    lap2 = np.delete(tmp,nRoot,1)
    return int(np.round(np.linalg.det(lap2)))

def getRandomOptimalSpanningTree(verts,optParents):
    parents = {}
    for vert in verts:
        tmp = optParents[vert]
        k = len(tmp)
        if 1 < k:
            kk = int(math.floor(np.random.rand()*k))
            tmp = [tmp[kk]]
        parents[vert] = tmp
    return parents

def getChildren(verts,parents):
    children = {}
    for vert in verts:
        children[vert] = [kid for kid in verts if vert in parents[kid]]
    return children

def getFriends(verts,nbrs,parents,children):
    friends = {}
    for vert in verts:
        tmp = nbrs[vert]
        tmp = set(tmp) - set(parents[vert])
        friends[vert] = list(tmp - set(children[vert]))
    return friends

def getVids(verts,parents):
    vids = {}
    for vert in verts:
        curr = vert
        vid = [curr]
        next = parents[curr]
        while next:
            curr = next[FIRST]
            vid.extend(curr)
            next = parents[curr]
        vids[vert] = vid
    return vids

def getNextNbrs(verts,nbrs):
    nextNbrs = {}
    for seed in verts:
        next = []
        curr = nbrs[seed]
        for vert in curr:
            next.extend(nbrs[vert])
        prev = curr+[seed]
        nextNbrs[seed] = list(set(next)-set(prev))
    return nextNbrs

def getGraph(edges):
    verts = edgesToVerts(edges)
    nbrs = edgesToNbrs(edges)
    return Graph(edges,verts,nbrs)

def getCosts(root,graf):
    hops = nbrsToHops(root,graf.nbrs)
    hopCounts = hopsToHopCounts(hops)
    return Costs(graf.verts,hops,hopCounts)

def getTree(graf,parents):
    children = getChildren(graf.verts,parents)
    friends = getFriends(graf.verts,graf.nbrs,parents,children)
    vids = getVids(graf.verts,parents)
    return Tree(graf.verts,parents,children,friends,vids)

def getFixPath(seed,tree,costs):
    maxDepth = len(tree.verts)
    fixPath, depth = findFixPath(seed,maxDepth,seed,tree.children,
                                    tree.friends,tree.vids,costs.hopCounts)
    if fixPath:
        print('FixPath found: ',fixPath)
    else:
        print('FixPath not found: Graph is disconnected')
    return fixPath

def findFixPath(vert,depth,seed,children,friends,vids,hopCounts):
    fixFriends = [friend for friend in friends[vert]
                                if seed not in vids[friend]]
    if fixFriends:
        pair = min([(hopCounts[v],v) for v in fixFriends])
        fixPath = list(pair)+[vert]
        down = 0
    else:
        fixPath = []
        down = depth-1
        if down > 0:
            kids = children[vert]
            for kid in kids:
                newPath, down = findFixPath(kid,down,seed,children,
                                            friends,vids,hopCounts)
                if newPath:
                    if not fixPath:
                        fixPath = newPath
                    elif newPath[FIRST] < fixPath[FIRST]:
                        fixPath = newPath
        if fixPath:
            fixPath.append(vert)
    up = down+1
    return fixPath, up
