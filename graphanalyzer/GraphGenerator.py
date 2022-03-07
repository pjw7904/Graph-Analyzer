import sys
import networkx as nx
import numpy as np

from networkx.generators.harary_graph import hnm_harary_graph
from networkx.generators.harary_graph import hkn_harary_graph

'''
Graphml Graph (import)
sourceFile = the graphml file
'''
def fromGraphml(sourceFile):
    try:
        G = nx.read_graphml(path=sourceFile)
    except FileNotFoundError:
        print("graphml graph file {0} does not exist in this location".format(sourceFile))
        sys.exit()

    return G

'''
Erdős-Rényi Graph
n = Number of verticies
p = Probability of edge creation between two nodes
seed = seed value for generation
'''
def generateErdosRenyiGraph(n, p, inputSeed=None):
    return nx.gnp_random_graph(n, p, seed=inputSeed, directed=False)

'''
Ring Graph
n = Number of verticies
'''
def generateRingGraph(n):
    return nx.cycle_graph(n)

'''
Harary Graph
k = Node-connectivity of graph
n = Number of verticies
'''
def generateHararyGraph(k, n):
    return nx.hkn_harary_graph(k, n)


'''
K-Regular Graph
d = Degree shared by each node
n = Number of verticies
'''
def generateRegularGraph(d, n, inputSeed=None):
    return nx.random_regular_graph(d,n, seed=inputSeed)