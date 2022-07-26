## Standard modules
from os.path import join as getFile

import networkx as nx
import GraphGenerator
import Algorithms
from FigureGenerator import plotAlgorithmSteps

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