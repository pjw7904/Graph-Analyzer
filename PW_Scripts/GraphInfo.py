#!/usr/bin/env python
from GENIutils import * # Custom library for GENI functions
import networkx as nx # External Python library (Anaconda provided) for graph creation and analysis
import numpy as np # External Python library (Anaconda provided) for all thinks linear algebra, arrays, matricies, etc and efficent memory usage compared to Py lists
import matplotlib.pyplot as plt # # External Python library (Anaconda provided) for drawing graphs
import statistics
import math

def main():
    userInput = input("GENI Addr Info (1) | Random Graph (2): ") # Get user input

    # If user picks 1, read and analyze a graph created in GENI
    if(userInput == "1"):
        getGENINetworkInfo()

    # If user picks 2, read and analyze 

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

    # Get other graph-related information
    numOfVerticies           = G.number_of_nodes()
    numOfEdges               = G.number_of_edges()
    connectionStatus         = nx.is_connected(G)
    nodeConnectivity         = nx.node_connectivity(G)
    linkConnectivity         = nx.edge_connectivity(G)
    algebraicConnectivity    = nx.algebraic_connectivity(G)
    graphDiameter            = nx.diameter(G)
    betweennessCentrality    = nx.betweenness_centrality(G)
    avgShortestPathLength    = nx.average_shortest_path_length(G)
    assortativityCoefficient = nx.degree_pearson_correlation_coefficient(G)
    completeStatus           = graphIsComplete(G)
    numOfSpanningTrees       = SpanningTreeCount(G)
    averageNodeDegree        = graphDegreeAverage(G)
    heterogeneity            = graphHeterogeneity(G)
    spectralRadius           = graphSpectralRadius(G)
    symmetryRatio            = graphSymmetryRatio(G)
    averageClusteringCoeff   = nx.average_clustering(G) # The average clustering coeffient of the graph
    avgNeighborConnectivity  = nx.average_degree_connectivity(G)

    # Print current graph info
    print("Is the graph connected (parsial mesh/A2TR)?: {conn}".format(conn=connectionStatus))
    print("Is the graph complete (full mesh)?: {comp}".format(comp=completeStatus))
    print("Number of verticies: {verts}".format(verts=numOfVerticies))
    print("Number of edges: {edges}".format(edges=numOfEdges))
    print("Average Nodal Degree: {avgDegree}".format(avgDegree=averageNodeDegree))
    print("Node Connectivity: {NC}".format(NC=nodeConnectivity))
    print("Link Connectivity: {LC}".format(LC=linkConnectivity))
    print("Heterogeneity: {hgny:.4f}".format(hgny=heterogeneity))
    print("Symmetry Ratio: {SYMR:.4f}".format(SYMR=symmetryRatio))
    print("Diameter: {DMR}".format(DMR=graphDiameter))
    print("Average Shortest Path Length: {ASPL:.4f}".format(ASPL=avgShortestPathLength))
    print("Assortativity Coefficient: {AC:.4f}".format(AC=assortativityCoefficient))
    print("Algebraic Connectivity: {AC:0.4f}".format(AC=algebraicConnectivity))
    print("Number of Possible Spanning Trees: {STs:.2f}".format(STs=numOfSpanningTrees))
    print("Spectral Radius (largest eigenvalue): {SR:.4f}".format(SR=spectralRadius))
    print("Clustering Coefficent (Graph Average): {COFF:.4f}".format(COFF=averageClusteringCoeff))
    print("\nBetweenness Centrality:")
    for key, value in betweennessCentrality.items():
        print("{key}: {value:.4f}".format(key=key,value=value))
    print("\nAverage Neighbor Connectivity:")
    for key, value in avgNeighborConnectivity.items():
        print("Degree {key}: {value:.4f}".format(key=key,value=value))


    # Output the curent graph in a pyplot window
    #nx.draw(G, with_labels=True, font_weight='bold')
    #plt.show()

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
