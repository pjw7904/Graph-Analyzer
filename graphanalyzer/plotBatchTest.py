import matplotlib.pyplot as plt
import numpy as np

def plotResults(algoName):
    with open('results/log_results/batch_test.log') as f:
        v = np.loadtxt(f, delimiter=",", dtype='int', comments="#", usecols=None)

    size = int((v.size / 3) + (v.size % 3))

    xAxis = [v[i][0] for i in range(0, size)]
    edgeAxis = [v[i][1] for i in range(0, size)]
    stepAxis = [v[i][2] for i in range(0, size)]

    plt.bar(edgeAxis, stepAxis)
    plt.title("Number of steps in {0}".format(algoName))
    plt.ylabel("Number of steps")
    plt.xlabel("Number of edges")
    plt.savefig('results/fig_results/{0}_steps_edges.png'.format(algoName))
    plt.close()

    plt.bar(xAxis, edgeAxis)
    plt.title("Number of edges in {0}".format(algoName))
    plt.ylabel("Number of edges")
    plt.xlabel("Number of nodes")
    plt.savefig('results/fig_results/{0}_edges_nodes.png'.format(algoName))
    plt.close()