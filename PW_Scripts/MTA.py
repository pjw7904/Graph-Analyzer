#!/usr/bin/env python

def createMeshedTreeDatatStructures(G, root):
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)
    
        if(node == root):
            '''
            rootInfo = {
                'isRoot': True,
                'state': "F",
                'ACK(child)': [],
                'ACK(noChild)': [],
                'inBasket': [],
                'pathBundle': [G.nodes[node]['ID']]
            }

            G.nodes[node]['rootInfo'] = rootInfo
            '''
            print("- Root node is {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        else:
            '''
            nodeInfo = {
                'isRoot': False,
                'state': "I",
                'NEXT': False,
                'STOP': False,
                'inBasket': [],
                'pathBundle': []
            }

            G.nodes[node]['nodeInfo'] = nodeInfo
            '''
            print("- Non-Root node {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        IDCount += 1

    print("---------\n")

    return


def rootActions(G, root):
    rootConf = G.nodes[root]['rootInfo']

    if(rootConf['state'] == 'F'):
        print("hi")

        #for nbr in G.neighbors(root):
            #G.nodes[nbr]['nodeInfo']['inBasket'].extend(G.nodes[root]['rootInfo']['pathBundle'])
            #print(G.nodes[nbr]['nodeInfo']['inBasket'])

    return


def nodeActions():

    return


def runMTASimulation(G, root):
    rootActions(G, root)

    return


def tuesdayAlgo(Graph, source, NP):

    createMeshedTreeDatatStructures(Graph, source) # Every vertex is given a single-character ID 

    for vertex in Graph:
        Graph.nodes[vertex]['pathBundle'] = [] # A data structure (list for Python) to hold paths to the vertex from the root
        Graph.nodes[vertex]['inBasket']   = [] # A data structure (list for Python) to hold path bundles send from nbrs to vertex

    Graph.nodes[source]['pathBundle'].append(Graph.nodes[source]['ID']) # source's PB contains only the trivial path RID (Root ID)
    
    sending = set([source]) # Sending is the set containing any vertex ready to send its PB.

    nextSending = [] # Verticies that need to send a pb update to nbrs during the next cycle
    receiving   = set() # Verticies that have received a path bundle update from a nbr

    while sending: # Convergence happens when sending goes empty
        nextSending.clear()
        receiving.clear()

        for u in sending: # For each vertex u in the sending list
            u_pathBundle = Graph.nodes[u]['pathBundle']
            for v in Graph.neighbors(u):
                v_inBasket = Graph.nodes[v]['inBasket']

                v_inBasket.extend(u_pathBundle)
                receiving.add(v)

        for v in list(receiving):
            Graph.nodes[v]['inBasket'] = [path + Graph.nodes[v]['ID'] for path in Graph.nodes[v]['inBasket'] if Graph.nodes[v]['ID'] not in path] # Delete any path that already contains vertex v
            
            v_grandBundle = list(set(Graph.nodes[v]['pathBundle']).union(Graph.nodes[v]['inBasket']))
            v_grandBundle.sort(key=len)

            del v_grandBundle[NP:]

            pbChanges = list(set(v_grandBundle).difference(set(Graph.nodes[v]['pathBundle'])))

            if(pbChanges):
                Graph.nodes[v]['pathBundle'] = v_grandBundle
                nextSending.append(v)

            Graph.nodes[v]['inBasket'].clear()
    
        sending = nextSending.copy()


    return