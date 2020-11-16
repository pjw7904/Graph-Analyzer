#!/usr/bin/env python

# Standard modules
import statistics # Calculating mathematical statistics of numeric (Real-valued) data
import math # Access to the mathematical functions defined by the C standard.
import argparse # Parsing command-line arguments
import configparser # Parsing configuration file arguments
import sys

# External modules
from tabulate import tabulate # Printing formatted ASCII tables
import networkx as nx # Graph creation and analysis
import numpy as np # For all thinks linear algebra, matricies, etc and efficent memory usage compared to Py lists
import matplotlib.pyplot as plt # Drawing graphs

# Custom modules
from GENIutils import getConfigInfo # Custom library for GENI functions
import MT_VIDs_Utils # Creates VIDs from possible simple paths in the graph
import MTA # MTA simulation based on John's FSM
import ClassicalMetrics

'''
Start of program
'''
def main():
    # ArgumentParser object to read in command-line arguments
    argParser = argparse.ArgumentParser(description="Graph Theory Analysis Script")

    # The source of the graph
    argParser.add_argument("-s", "--source", nargs='*')

    # Calculating graph metrics
    argParser.add_argument("--CalcClassicalMetrics", action="store_true") # Compute classical metrics from algebraic and spectral graph theory
    argParser.add_argument("--CalcBC", action="store_true") # Compute betweenness centrality for each vertex
    argParser.add_argument("--CalcAvgNC", action="store_true")

    # Meshed Tree Algorithm (MTA) simulation options depending on how it is implemented
    argParser.add_argument("--GetVIDs") # VID-Based Meshed Tree rooted at the inputted vertex (classic MTA)
    argParser.add_argument("--numOfVIDs", type = int) # Used with GetVIDs to describe the maximum amount of VIDs to store
    argParser.add_argument("--tuesdayAlgo") # JH version of basic MTA
    argParser.add_argument("--PanAlgo") # YP version of basic MTA 

    # Get a visual of the generated graph
    argParser.add_argument("--ShowPic", action="store_true")

    # Parse the arguments
    args = argParser.parse_args()

    #######
    # NetworkX Graph In Use:
    # |Type       | Self-Loops | Parallel Edges|
    # |Undirected | No         | No            |
    #######
    G = generateGraph(args.source)

    # Structure to hold what metrics the user wants calcuated
    metricOptions = {
        "Classical": args.CalcClassicalMetrics,
        "BC": args.CalcBC,
        "AvgNC": args.CalcAvgNC
    }

    # Compute and print out the metric results
    computeMetrics(metricOptions, G)

    # MTA simulation (version with 3 paths, nothing disjoint):
    if(args.tuesdayAlgo):
        sendingEvents, sendingEvents2 = MTA.tuesdayAlgo(G, args.tuesdayAlgo, 3)

        for vertex in G:
            print("Path Bundle for {0} (ID = {1})\n===".format(vertex, G.nodes[vertex]['ID']))
            for path in G.nodes[vertex]['pathBundle']:
                print(path)
            print("===\n")

        print(sendingEvents)
        print("sending events 2: {0}".format(sendingEvents2))
        print(len(sendingEvents2))


    if(args.PanAlgo):
        nodeSendingCount = MTA.PanAlgo(G, args.PanAlgo)

        for vertex in G:
            print("Path Bundle for {0} (ID = {1})\n===".format(vertex, G.nodes[vertex]['ID']))
            for path in G.nodes[vertex]['pathBundle']:
                print(path)
            print("===\n")
        
        print("Sending count: {0}".format(nodeSendingCount))


    if(args.GetVIDs):
        G_MT = G.to_directed() # Graph Meshed Tree (G_MT)

        MT_root = args.GetVIDs # The root of the meshed tree
        numOfVIDs = None

        if(args.numOfVIDs):
            numOfVIDs = args.numOfVIDs

        possibleVIDs = {}
        PVID         = {}

        MT_VIDs_Utils.createMeshedTreeTable(G_MT)
        MT_VIDs_Utils.addInterfaceNums(G_MT)

        # Generating the possible VIDs from each non-root node
        for currentNode in G_MT:
            possibleVIDs, PVID = MT_VIDs_Utils.generatePossibleVIDs(G_MT, MT_root, currentNode, numOfVIDs=numOfVIDs)
            G_MT.nodes[currentNode]['VIDTable'].update(possibleVIDs)
            G_MT.nodes[currentNode]['PVID'].update(PVID)

        #PVIDColors = nx.get_node_attributes(G_MT, "PVID")
        #activeLinks = [list(PVIDColors[node].keys())[0] for node in G_MT.nodes if node != MT_root]
        #colorBroadcastTree = ['black' if e in activeLinks else 'white' for e in G_MT.edges]
        #nx.draw(G_MT, with_labels=True, edge_color=colorBroadcastTree, font_weight='bold', labels = PVIDColors)
        #plt.show()

    if(args.ShowPic):
        nx.draw(G, with_labls=True)
        plt.show()

    # End of script
    return


def generateGraph(sourceInput):
    graphFormat = sourceInput[0]

    if(graphFormat == "RSPEC"):
        G = getGENINetworkInfo()

    elif(graphFormat == "graphml" and len(sourceInput) == 2):
        G = nx.read_graphml(path=sourceInput[1])

    else:
        sys.exit("Error: invalid source, please try again using RSPEC or graphml")

    return G


def getGENINetworkInfo():
    # Read the necessary configuration information from creds.cnf
    switchNamingSyntax  = getConfigInfo("RSTP Utilities", "MTSName")
    endNodeNamingSyntax = getConfigInfo("RSTP Utilities", "endNodeName")
    networkInfo         = getConfigInfo("Local Utilities", "endnodeInfoLocation")

    # Create a Config Parser object so GENI topology information can be read
    config = configparser.ConfigParser()
    config.read(networkInfo) # Grabbing information from addrinfo.cnf

    # Creating a list of GENI topology verticies
    V = [node for node in config.sections() if(switchNamingSyntax in node and endNodeNamingSyntax not in node)]

    # Creating a list of GENI topology edges
    E = []
    for node in V:
        nodeNeighbors = [(key, value) for key, value in config.items(node) if("_neighbor" in key and endNodeNamingSyntax not in value)]
        for neighbor in nodeNeighbors:
            E.append((node, neighbor[1]))

    # Creating a NetworkX graph and adding in the GENI topology information
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)

    # Write this graph to a graphml file to be reused later on
    fileName = input("Graph name: ")
    nx.write_graphml(G=G, path=fileName + ".graphml", prettyprint=True)
    print("Note: graph {0} has been converted to a graphml file named {1}. It is saved in the current directory."
        .format(fileName, fileName + ".graphml"))

    return G


def computeMetrics(calcOptions, G):
    if(calcOptions["Classical"]):
        # Calculate metric results based on the appropriate graph theory algorithms included and display them with Tabulate
        results = ClassicalMetrics.calculateClassicalMetricsResults(G)
        print("{Header}\n{Results}\n".format(Header="____CLASSICAL METRICS____", Results=tabulate(results, headers=["Metric", "Results"], numalign="right", floatfmt=".4f")))

    if(calcOptions["BC"]):
        results = ClassicalMetrics.calculatePerNodeBetweennessCentrality(G)
        print("{Header}\n{Results}\n".format(Header="____BETWEENNESS CENTRALITY____", Results=tabulate(results, headers=["Node", "Results"], numalign="right", floatfmt=".4f")))

    if(calcOptions["AvgNC"]):
        results = ClassicalMetrics.calculatePerDegreeAvgNeighborConnectivity(G)
        print("{Header}\n{Results}\n".format(Header="____AVG NEIGHBOR CONNECTIVITY____", Results=tabulate(results, headers=["Degree", "Results"], numalign="right", floatfmt=".4f")))

    return

# Calling main function, start of script
if __name__ == "__main__":
    main()
