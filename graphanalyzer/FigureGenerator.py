## Standard modules
#from os.path import join as getFile

## External modules
from networkx import nx_pydot as nxpd
import matplotlib.pyplot as plt
import numpy as np


def drawGraph(graph, figurePath):
    P = nxpd.to_pydot(graph)
    P.write_png(figurePath)

    return

'''
#Graphviz figure - pygraphviz package

from networkx import nx_agraph as nxgraph

def drawGraphPyGraphviz(graph, figurePath):
    A = nxgraph.to_agraph(graph)
    A.layout(prog="dot")
    A.draw(figurePath)

    return
'''

'''
Histogram - Steps 
'''
def plotAlgorithmSteps(algoName, batchResultsPath):
    with open(batchResultsPath) as f:
        v = np.loadtxt(f, delimiter=",", usecols=None) # update usecols appropriately

    size = int((v.size / 3) + (v.size % 3))

    # Start of all batch tests rows are numVerts,numEdges,numSteps
    vertexAxis = [v[i][0] for i in range(0, size)]
    edgeAxis   = [v[i][1] for i in range(0, size)]
    stepAxis   = [v[i][2] for i in range(0, size)]

    plt.bar(edgeAxis, stepAxis)
    plt.title("Number of steps in {0}".format(algoName))
    plt.xlabel("Number of edges")
    plt.ylabel("Number of steps")
    plt.savefig('results/fig_results/{0}_steps_edges.png'.format(algoName))
    plt.close()

    plt.bar(vertexAxis, edgeAxis)
    plt.title("Number of edges in {0}".format(algoName))
    plt.ylabel("Number of edges")
    plt.xlabel("Number of nodes")
    plt.savefig('results/fig_results/{0}_edges_nodes.png'.format(algoName))
    plt.close()

    return