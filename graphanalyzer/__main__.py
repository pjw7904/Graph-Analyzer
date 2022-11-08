## Standard modules
import sys # Access to system-level functions
from os.path import join as getFile

## External modules
import networkx as nx # Graph creation and analysis
import matplotlib.pyplot as plt # Drawing graphs
from tabulate import tabulate # Printing formatted ASCII tables
from networkx import NetworkXError # Handling graph-specific errors

## Custom modules
# Shortest Path Tree (SPT) algorithms
import MTA_RP # MTA Remedy Path algorithm
import MTP_NPaths # MTA N-Path algorithm
import RSTA # Rapid Spanning Tree algorithm
import DA # Dijkstra's algorithm

# Graph creation and analysis
import ClassicalMetrics # Classic Graphy Theory metrics
import GraphGenerator # Generate graphs via well-known algorithms
import FigureGenerator
import TestGenerator
import Algorithms

# Configuration
import parseConfig as config


'''
main, entry to program 

# NetworkX graph used:
# |Type       | Self-Loops | Parallel Edges|
# |Undirected | No         | No            |
'''
def main():
    # Read in command-line arguments
    args = config.parseArgs()

    # Read the JSON files to determine what the graph and setup looks like
    programConfig = config.parseSettingsConfig()
    graphConfig = config.parseGraphConfig()

    # Graph meta-information
    typeOfTest = graphConfig["type"]
    typeOfGraph = graphConfig["choice"]
    nameOfTest = graphConfig["name"]
    testSeed = graphConfig["seed"]

    if(typeOfTest == None or typeOfGraph == None):
        print("ERROR: type and/or choice JSON object has a null value")
        sys.exit()

    # Generate a single graph of the given type
    if(typeOfTest == "single"):
        graph = GraphGenerator.generateGraph(typeOfGraph, graphConfig["single"][typeOfGraph], seed=testSeed, graphDirectory=programConfig["graphs"], logDirectory=programConfig["results"]["log"])

        # Option if you want to see a picture of the graph (Graphviz-generated)
        if(args.picture):
            FigureGenerator.drawGraph(graph, getFile(programConfig["results"]["figure"], nameOfTest + ".png"))

        # Option if you want to save a graphml of the graph, which will be placed in the graph folder
        if(args.save):
            GraphGenerator.toGraphml(graph, getFile(programConfig["graphs"], nameOfTest + ".graphml"))

        if(args.algorithm != "none"):
            # Run one of the algorithms for initial SPT convergence and potential further tests
            Algorithms.runAlgorithmOnGraph(graph, args, programConfig["results"]["log"], nameOfTest)

    elif(typeOfTest == "batch"):
        TestGenerator.runBatchTest(typeOfGraph, graphConfig["batch"][typeOfGraph], args, programConfig["results"]["log"], programConfig["results"]["figure"], nameOfTest)

    elif(typeOfTest == "test"):
        TestGenerator.run(graphConfig , programConfig, args)

if __name__ == "__main__":
    main()