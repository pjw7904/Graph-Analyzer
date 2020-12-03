# Standard modules
import math
import statistics

# External modules
import networkx as nx # Graph creation and analysis
import numpy as np # For all thinks linear algebra, matricies, etc and efficent memory usage compared to Py lists


def calculateClassicalMetricsResults(G):
    # Collect results for output
    results = []

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
    averageClusteringCoeff = nx.average_clustering(G)
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

    # Get the number of verticies and edges in the graph
    numOfVerticies = G.number_of_nodes()
    numOfEdges = G.number_of_edges()

    # Calculate the number of edges that are needed to the graph complete
    numOfEdgesInCompleteGraph = (numOfVerticies * (numOfVerticies - 1)) / 2

    if(numOfEdges == numOfEdgesInCompleteGraph):
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