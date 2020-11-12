#!/usr/bin/env python

# Standard modules
import statistics # Calculating mathematical statistics of numeric (Real-valued) data
import math # Access to the mathematical functions defined by the C standard.
import argparse # Parsing command-line arguments
import configparser # Parsing configuration file arguments

# External modules
from tabulate import tabulate # Printing formatted ASCII tables
import networkx as nx # Graph creation and analysis
import numpy as np # For all thinks linear algebra, matricies, etc and efficent memory usage compared to Py lists
import matplotlib.pyplot as plt # Drawing graphs

# Custom modules
from GENIutils import getConfigInfo # Custom library for GENI functions
import MT_VIDs_Utils # Creates VIDs from possible simple paths in the graph
import MTA # MTA simulation based on John's FSM

'''
Start of program
'''
def main():
    # ArgumentParser object to read in command-line arguments
    argParser = argparse.ArgumentParser(description="Graph Theory Analysis Script")

    argParser.add_argument("-s", "--source", nargs='*')   # The source of the graph
    argParser.add_argument("--CalcClassicalMetrics", action="store_true") # Compute classical metrics from algebraic and spectral graph theory
    argParser.add_argument("--CalcBC", action="store_true")
    argParser.add_argument("--CalcAvgNC", action="store_true")
    argParser.add_argument("--GetVIDs") # VID-Based Meshed Tree rooted at the inputted vertex
    argParser.add_argument("--ShowPic", action="store_true")
    argParser.add_argument("--numOfVIDs", type = int)

    # Algorithm for 3 paths (not worrying about specifc backups or disjoint paths)
    argParser.add_argument("--tuesdayAlgo")
    argParser.add_argument("--PanAlgo")

    # Algorithm based on the FSM and root-syncing idea
    argParser.add_argument("--runMTA")

    # Parse the arguments
    args = argParser.parse_args()

    #######
    # NetworkX Graph:
    # |Type       | Self-Loops | Parallel Edges|
    # |Undirected | No         | No            |
    #######
    G = nx.Graph()

    # If the user wants to import a graph from a GENI RSPEC
    if(args.source[0] == "RSPEC"):
        G = getGENINetworkInfo()

    elif(args.source[0] == "graphml"):
        G = nx.read_graphml(path=args.source[1])

        for v in G:
            print(v)

    if(args.CalcClassicalMetrics):
        # Calculate metric results based on the appropriate graph theory algorithms included and display them with Tabulate
        results = calculateClassicalMetricsResults(G)
        print("{Header}\n{Results}\n".format(Header="____CLASSICAL METRICS____", Results=tabulate(results, headers=["Metric", "Results"], numalign="right", floatfmt=".4f")))

    if(args.CalcBC):
        results = calculatePerNodeBetweennessCentrality(G)
        print("{Header}\n{Results}\n".format(Header="____BETWEENNESS CENTRALITY____", Results=tabulate(results, headers=["Node", "Results"], numalign="right", floatfmt=".4f")))

    if(args.CalcAvgNC):
        results = calculatePerDegreeAvgNeighborConnectivity(G)
        print("{Header}\n{Results}\n".format(Header="____AVG NEIGHBOR CONNECTIVITY____", Results=tabulate(results, headers=["Degree", "Results"], numalign="right", floatfmt=".4f")))

    # MTA simulation (FSM with root syncing version)
    if(args.runMTA):
        print("\n=== MTA SIMULATION ===")
        MTA.createMeshedTreeDatatStructures(G, args.runMTA)
        MTA.runMTASimulation(G, args.runMTA)

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



def calculateClassicalMetricsResults(G):
    # Collect results for output
    results     = []

    # Get other graph-related information
    numOfVerticies = G.number_of_nodes()
    results.append(["Number of verticies", numOfVerticies])

    numOfEdges = G.number_of_edges()
    results.append(["Number of edges", numOfEdges])

    connectionStatus = nx.is_connected(G)
    results.append(["Is the graph connected (parsial mesh/A2TR)", connectionStatus])

    nodeConnectivity = nx.node_connectivity(G)
    results.append(["Node Connectivity", nodeConnectivity])

    linkConnectivity = nx.edge_connectivity(G)
    results.append(["Link Connectivity", linkConnectivity])

    algebraicConnectivity = nx.algebraic_connectivity(G)
    results.append(["Algebraic Connectivity", algebraicConnectivity])

    graphDiameter = nx.diameter(G)
    results.append(["Diameter", graphDiameter])

    avgShortestPathLength = nx.average_shortest_path_length(G)
    results.append(["Average Shortest Path Length", avgShortestPathLength])

    assortativityCoefficient = nx.degree_pearson_correlation_coefficient(G)
    results.append(["Assortativity Coefficient", assortativityCoefficient])

    completeStatus = graphIsComplete(G)
    results.append(["Is the graph complete (full mesh)", completeStatus])

    numOfSpanningTrees = SpanningTreeCount(G)
    results.append(["Number of Possible Spanning Trees", numOfSpanningTrees])

    averageNodeDegree = graphDegreeAverage(G)
    results.append(["Average Nodal Degree", averageNodeDegree])

    heterogeneity = graphHeterogeneity(G)
    results.append(["Heterogeneity", heterogeneity])

    spectralRadius = graphSpectralRadius(G)
    results.append(["Spectral Radius (largest eigenvalue)", spectralRadius])

    symmetryRatio = graphSymmetryRatio(G)
    results.append(["Symmetry Ratio", symmetryRatio])

    #TODO: Based on the paper, this needs to switch to being the transitivity function, not average_clustering
    averageClusteringCoeff   = nx.average_clustering(G)
    results.append(["Clustering Coefficent (Graph Average)", averageClusteringCoeff])

    return results


def calculatePerNodeBetweennessCentrality(G):
    BC_results  = []

    betweennessCentrality = nx.betweenness_centrality(G)
    for key, value in betweennessCentrality.items():
        BC_results.append([key,value])

    return BC_results


def calculatePerDegreeAvgNeighborConnectivity(G):
    ANC_results = []

    avgNeighborConnectivity = nx.average_degree_connectivity(G)
    for key, value in avgNeighborConnectivity.items():
        ANC_results.append([key,value])

    return ANC_results


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

    return G


# Kirchhoff's matrix tree theorem is implemented to count the number of spanning trees
def SpanningTreeCount(G):
    treeCount = 0

    laplacianMatrix = nx.laplacian_matrix(G).toarray()
    laplacianSubMatrix = np.delete(laplacianMatrix, 0, 0)
    laplacianSubMatrix = np.delete(laplacianSubMatrix, 0, 1)

    treeCount = np.linalg.det(laplacianSubMatrix)

    return treeCount

# Checking if the graph is complete / fully meshed
def graphIsComplete(G):
    isCompleteGraph = False

    numOfVerticies = G.number_of_nodes()
    numOfEdges = G.number_of_edges()

    if(numOfEdges == numOfVerticies-1):
        isCompleteGraph = True

    return isCompleteGraph


# Written with possible directed graphs in mind, otherwise avg = 2m/n for undirected graphs
def graphDegreeAverage(G):
    average = 0
    edgeSum = 0

    numOfVerticies = G.number_of_nodes()

    for V in G:
        edgeSum += G.degree(V)

    average = edgeSum / numOfVerticies

    return average

def graphHeterogeneity(G):
    heterogeneity = 0
    nodeDegrees = []
    #numOfVerticies = G.number_of_nodes() not used, not sure why right now
    averageNodeDegree = graphDegreeAverage(G)

    for V in G:
        nodeDegrees.append(G.degree(V))
    standardDev = math.sqrt(statistics.variance(nodeDegrees))

    heterogeneity = standardDev/averageNodeDegree

    return heterogeneity


def graphSpectralRadius(G):
    adjacencyMatrix = nx.to_numpy_matrix(G,dtype=int)

    eigVals = np.linalg.eigvals(adjacencyMatrix)
    eigVals = set(eigVals)

    spectralRadius = sorted(eigVals)[-1]

    return spectralRadius


def graphSymmetryRatio(G):
    symmetryRatio = 0

    adjacencyMatrix = nx.to_numpy_matrix(G,dtype=int)
    graphDiameter = nx.diameter(G) + 1

    eigVals = np.linalg.eigvals(adjacencyMatrix)
    numOfEigVals = len(set(eigVals)) # We only consider distinct eigenvalues

    symmetryRatio = numOfEigVals/graphDiameter

    return symmetryRatio


# Not used right now while I figure out what is going on in the paper it's presented in (normalized version).
def graphAverageNeighborConnectivity(G):
    '''
    For ADC of degree 2, consider the 10 node GENI thesis topology. There are
    2 nodes with a degree of 2: node-0 and node-9 (at the ends of the topology).
    Take a look at the degree of those four neighbors (node-1 and node-2 for node-0, node-7 and node-8 for node-9)
    and then add those degrees together (3 + 4, 4 + 3 = 14). Divide that value (14) by the total number of neighbors (degree * 2 == 2 * 2 = 4).
    This gives an ADC of 3.5 for degree 2. For our metric from the paper, you divide this value by the numOfNodes - 1.
    '''
    numOfVerticies = G.number_of_nodes()
    ADC = nx.average_degree_connectivity(G) # For each degree present in network: avgNeighborDegree / numOfNeighbors
    ADC.update((x,y/(numOfVerticies - 1)) for x,y in ADC.items())

    return ADC

# Calling main function, start of script
if __name__ == "__main__":
    main()
