#!/usr/bin/env python
from GENIutils import * # Custom library for GENI functions
from tabulate import tabulate # External Python library (Anaconda provided) for printing formatted ASCII tables
import networkx as nx # External Python library (Anaconda provided) for graph creation and analysis
import numpy as np # External Python library (Anaconda provided) for all thinks linear algebra, arrays, matricies, etc and efficent memory usage compared to Py lists
import matplotlib.pyplot as plt # # External Python library (Anaconda provided) for drawing graphs
import statistics
import math

def main():
    userInput = input("GENI Addr Info (1) | Random Graph (2) | Custom Selections (3): ") # Get user input

    # Create an empty graph so vertex and edge sets can be added by the user selection
    G = nx.Graph()

    # If user picks 1, read and analyze a graph created in GENI
    if(userInput == "1"):
        G = getGENINetworkInfo()

    # If user picks 2, analyze a selection of graphs that I or someone else think is interesting
    elif(userInput == "2"):
        G = interestingGraphs()

    # Calculate the results based on the graph(s) chosen
    results, betweennessCentrality, avgNeighborConnectivity = calculateMetricsResults(G)

    # Print the results
    print(tabulate(results, headers=["Metric", "Results"], numalign="right", floatfmt=".4f"))
    print(tabulate(betweennessCentrality, headers=["Node", "Results"], numalign="right", floatfmt=".4f"))
    print(tabulate(avgNeighborConnectivity, headers=["Degree", "Results"], numalign="right", floatfmt=".4f"))

    # Output the curent graph in a pyplot window
    #nx.draw(G, with_labels=True, font_weight='bold')
    #plt.show()


def calculateMetricsResults(G):
    # Collect results for output
    results     = []
    BC_results  = []
    ANC_results = []

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

    averageClusteringCoeff   = nx.average_clustering(G) # The average clustering coeffient of the graph
    results.append(["Clustering Coefficent (Graph Average)", averageClusteringCoeff])

    betweennessCentrality = nx.betweenness_centrality(G)
    for key, value in betweennessCentrality.items():
        BC_results.append([key,value])

    avgNeighborConnectivity = nx.average_degree_connectivity(G)
    for key, value in avgNeighborConnectivity.items():
        ANC_results.append([key,value])

    return results, BC_results, ANC_results


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


def interestingGraphs():

    return

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
    numOfVerticies = G.number_of_nodes()
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
