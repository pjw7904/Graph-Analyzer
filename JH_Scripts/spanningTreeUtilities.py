import numpy as np
import math
import copy

from collections import namedtuple
Mesh = namedtuple('Mesh','root graph costs tree coords')
Graph = namedtuple('Graph','edges verts nbrs')
Costs = namedtuple('Cost','verts hops hopCounts')
Tree = namedtuple('Tree','verts parents children friends vids')
MeshedTree = namedtuple('MeshedTree','verts pathBundles parents children')
MeshedPaths = namedtuple('MeshedPaths','verts nbrs root pathBundles sendingEvents')

FIRST = 0
REST = 1
LAST = -1
REV = -1

def edgesUpper(edges):
    return [edge.upper() for edge in edges]

def edgesToVerts(edges):
    verts = list(set(''.join(edges)))
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

def getParents(verts,pathBundles):
    parents = {}
    for vert in verts:
        topPath = pathBundles[vert][FIRST]
        if len(topPath) > 1:
            parents[vert] = topPath[-2]
        else:
            parents[vert] = ''
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

def getMeshedTree(graf,root,maxClip):
    maxClip = 6
    pathBundles = {}
    inBaskets = {}
    parents = {}
    children = {}
    for vert in graf.verts:
        pathBundles[vert] = []
        inBaskets[vert] = []
        parents[vert] = ''
        children[vert] = []
    pathBundles[root] = [root]
    sending = [root]
    
    epoch = 0
    print('Epoch: ',epoch,'   sending: ', len(sending))
    
    while sending:
        nextSending = []
        receiving = []

        for vert in sending:
            for nbr in graf.nbrs[vert]:
                inBaskets[nbr].append(pathBundles[vert])
                receiving.extend(nbr)

        receiving = list(set(receiving))
        print('receiving: ',receiving)
        print('inBaskets: ',inBaskets)

        for vert in receiving:
            print('vert: ',vert)
            print('inBaskets[vert]: ',inBaskets[vert])
            acyclics = []
            for bndl in inBaskets[vert]:
                topPath = bndl[FIRST]
                if len(topPath) > 1:
                    kids = copy.deepcopy(children[vert])
                    if topPath[-2] == vert:
                        kids = list(set(kids).union(set(topPath[LAST])))
                    else:
                        kids = list(set(kids).difference(set(topPath[LAST])))
                    children[vert] = kids
                for path in bndl:
                    if vert not in path:
                        acyclics.append(path + vert)
            bndl = copy.deepcopy(pathBundles[vert])
            bndl = list(set(bndl).union(acyclics))
            bndl.sort(key=len)
            clip = min(len(bndl),maxClip)
            newBndl = bndl[:clip]
            chng = list(set(newBndl).difference(set(pathBundles[vert])))
            if chng:
                pathBundles[vert] = newBndl
                nextSending.extend(vert)
            inBaskets[vert] = []
            bndl = pathBundles[vert]
            print('bndl ',bndl)
            topPath = bndl[FIRST]
            if len(topPath) > 1:
                parents[vert] = topPath[-2]
            else:
                parents[vert] = ''

        sending = nextSending
        print('pathBundles: ',pathBundles)
    
        epoch += 1
        print('Epoch: ',epoch,'   sending: ', len(sending))

    return MeshedTree(graf.verts,pathBundles,parents,children)

def getMeshedPaths(verts,nbrs,root,maxClip):
    pathBundles = {}
    inBaskets = {}
    for vert in verts:
        pathBundles[vert] = []
        inBaskets[vert] = []
    pathBundles[root] = [root]
    sending = [root]
    sendingEvents = []
    
    while sending:
        sendingEvents.append(len(sending))
        nextSending = []
        receiving = []

        for vert in sending:
            for nbr in nbrs[vert]:
                inBaskets[nbr].append(pathBundles[vert])
                receiving.extend(nbr)

        receiving = list(set(receiving))

        for vert in receiving:
            acyclics = []
            for bndl in inBaskets[vert]:
                for path in bndl:
                    if vert not in path:
                        acyclics.append(path + vert)
            bndl = copy.deepcopy(pathBundles[vert])
            bndl = list(set(bndl).union(acyclics))
            bndl.sort(key=len)
            clip = min(len(bndl),maxClip)
            newBndl = bndl[:clip]
            chng = list(set(newBndl).difference(set(pathBundles[vert])))
            if chng:
                pathBundles[vert] = newBndl
                nextSending.append(vert)
            inBaskets[vert] = []

        sending = nextSending

    return MeshedPaths(verts,nbrs,root,pathBundles,sendingEvents)

def getParentsValidity(verts,parents,root):
    valid = True
    msg = 'Parents build a spanning tree.'
    if root not in parents:
        valid = False
        msg = 'Root must be in parents.keys.'
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