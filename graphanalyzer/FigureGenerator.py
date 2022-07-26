## Standard modules
from os.path import join as getFile

## External modules
from networkx import nx_pydot as nxpd
import matplotlib.pyplot as plt
import numpy as np


def drawGraph(graph, figurePath):
    P = nxpd.to_pydot(graph)
    P.write_png(figurePath)

    return

'''
Histogram - Steps 
'''
def plotAlgorithmSteps(algoName, testName, batchResultsPath, figurePath):
    with open(batchResultsPath) as f:
        data = np.loadtxt(f, delimiter=",", usecols=(0,1,2))

    # Start of all batch tests rows are numVerts,numEdges,numSteps
    vertexAxis = data[:,0].tolist()
    edgeAxis   = data[:,1].tolist()
    stepAxis   = data[:,2].tolist()

    plt.bar(edgeAxis, stepAxis)
    plt.title("{0} - {1} - steps".format(testName, algoName))
    plt.xlabel("Number of edges")
    plt.ylabel("Number of steps")
    plt.savefig(getFile(figurePath, testName + "_steps_edges.png"))
    plt.close()

    plt.bar(vertexAxis, edgeAxis)
    plt.title(" {0} - {1} - edges".format(testName, algoName))
    plt.ylabel("Number of edges")
    plt.xlabel("Number of nodes")
    plt.savefig(getFile(figurePath, testName + "_edges_nodes.png"))
    plt.close()

    return