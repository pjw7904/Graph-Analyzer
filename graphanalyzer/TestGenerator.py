## Standard modules
from os.path import join as getFile

import networkx as nx
import GraphGenerator
import Algorithms
import ClosAddressing
from FigureGenerator import plotAlgorithmSteps, drawGraph
from GraphGenerator import fromGraphml

def run(graphConfig, programConfig, args):

    '''
        print("test")
    #threeTier = GraphGenerator.generateGraph("foldedClos", graphConfig["single"]["foldedClos"], logDirectory=programConfig["results"]["log"])
    #nx.write_gpickle(threeTier, "test.gpickle")

    threeTier = nx.read_gpickle("clos_k4_t3.gpickle")
    ClosAddressing.addVIDss(threeTier, 3, topTierRoot=False)
    '''

    print("TEST STARTING NOW")

    d = 6
    n = 7
    valNum = 7
    algos = {'mta':['remedy'], 'npaths':['npaths'], 'rsta':['rsta']}
    args.remove = [0,4] # break edge (0,4)

    for _ in range(6):
        print(f"d = {d} | n = {n}")
        G = nx.random_regular_graph(d, n, seed=37) # take the steps from here my dude
        #drawGraph(G, getFile(programConfig["results"]["figure"], f"d{d}n{n}.png"))

        for algo in algos.keys():
            args.algorithm = algo
            G = nx.random_regular_graph(d, n, seed=37) # take the steps from here my dude
            Algorithms.runAlgorithmOnGraph(G, args, programConfig["results"]["log"], f"recovery4_{valNum}")
            algos[algo].append(G.graph["step"])

        n += 1
        valNum += 1

    print(algos)

    '''
    d = 6
    n = 10
    algos = ['mta', 'npaths']

    print("muhhhhhhhhhh")

    for algo in algos:
        args.algorithm = algo
        G = nx.random_regular_graph(d, n, seed=37) # take the steps from here my dude
        Algorithms.runAlgorithmOnGraph(G, args, programConfig["results"]["log"], "treetest")
        drawGraph(G.graph["tree"], getFile(programConfig["results"]["figure"], f"d{d}n{n}_{algo}_tree.png"))
    '''

    return


def runBatchTest(testType, testConfig, algoConfig, logFilePath, figFilePath, nameOfTest):
    if(testType == "binomial_scale_vertices"):
        runBinomialScaleVerticesTest(testConfig, algoConfig, logFilePath, nameOfTest)
    elif(testType == "kRegular_scale_edges"):
        runKRegularScaleEdgesTest(testConfig, algoConfig, logFilePath, nameOfTest)
    else:
        raise nx.NetworkXError("Graph type is not valid")

    # If a figure is requested, create it based on the resulting data
    if(algoConfig.graph):
        plotAlgorithmSteps(algoConfig.algorithm, nameOfTest, getFile(logFilePath, nameOfTest + "_batch_test.csv"), figFilePath)

    return

def runBinomialScaleVerticesTest(testConfig, algoConfig, logFilePath, nameOfTest):
    typeOfGraph = "binomial"
    
    # Binomial graph generation options that will be changed each iteration
    testConfig["numberOfVertices"] = testConfig["startingNumberOfVertices"]

    notFinished = True
    while(notFinished):
        graph = GraphGenerator.generateGraph(typeOfGraph, testConfig)
        Algorithms.runAlgorithmOnGraph(graph, algoConfig, logFilePath, nameOfTest, batch=True)

        if(testConfig["numberOfVertices"] == testConfig["endingNumberOfVertices"]):
            notFinished = False

        testConfig["numberOfVertices"] += 1

    return

def runKRegularScaleEdgesTest(testConfig, algoConfig, logFilePath, nameOfTest):
    typeOfGraph = "kRegular"

    # K-regular graph generation options that will be changed each iteration
    testConfig["sharedDegree"] = testConfig["startingkRegular"]

    notFinished = True
    while(notFinished):
        graph = GraphGenerator.generateGraph(typeOfGraph, testConfig)
        Algorithms.runAlgorithmOnGraph(graph, algoConfig, logFilePath, nameOfTest, batch=True)

        if(testConfig["sharedDegree"] == testConfig["endingkRegular"]):
            notFinished = False

        testConfig["sharedDegree"] += 1

    return