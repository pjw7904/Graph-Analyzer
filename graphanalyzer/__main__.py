# Standard modules
import argparse # Parsing command-line arguments
import sys

# External modules
import networkx as nx # Graph creation and analysis
import matplotlib.pyplot as plt # Drawing graphs
from tabulate import tabulate # Printing formatted ASCII tables

# Custom modules
import MT_VIDs_Utils # Creates VIDs from possible simple paths in the graph
import MTA # MTA simulation based on John's FSM
import STA # STA simulation based on IEEE 802.1D-2004, Section 17
import DA # Dijkstra's algorithm simulation
import ClassicalMetrics

def parseArgs():
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
    argParser.add_argument("--numOfVIDs", type=int) # Used with GetVIDs to describe the maximum amount of VIDs to store
    argParser.add_argument("--hamiltonAlgo") # JH version of basic MTA
    argParser.add_argument("--PanAlgo") # YP version of basic MTA
    argParser.add_argument("--MTA") # JH version of MTA with remedy paths (01/2021)

    # IEEE Rapid Spanning Tree Algorithm (Rapid STA) simulation options
    argParser.add_argument("--STA") # Root pre-designated by adding it as argument

    # Dijkstra's Algorithm
    argParser.add_argument("--DA") # Argument of the root of the SPT

    # Get a visual of the generated graph
    argParser.add_argument("--ShowPic", action="store_true")

    # Get figures/plots of data collected
    argParser.add_argument("--stats") # Argument of the name of the topology

    # Parse the arguments
    args = argParser.parse_args()

    return args

def generateGraph(sourceInput):
    graphFormat = sourceInput[0]

    if(graphFormat == "graphml" and len(sourceInput) == 2):
        G = nx.read_graphml(path=sourceInput[1])

    elif(graphFormat == "random" and len(sourceInput) == 2):
        hardCodedNumOfNodes = 25
        probabilityForEdgeCreation = float(sourceInput[1])
        G = nx.fast_gnp_random_graph(n=hardCodedNumOfNodes, p=probabilityForEdgeCreation)

    else:
        sys.exit("Error: invalid source, please try again using RSPEC, graphml, random, or simulation")

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

'''
main
'''
# Read in command-line arguments
args = parseArgs()

# Structure to hold what metrics the user wants calcuated
metricOptions = {
    "Classical": args.CalcClassicalMetrics,
    "BC": args.CalcBC,
    "AvgNC": args.CalcAvgNC
}

#######
# NetworkX Graph In Use:
# |Type       | Self-Loops | Parallel Edges|
# |Undirected | No         | No            |
#######
G = generateGraph(args.source) # Generate a graph to use for calculations

# Define structures to collect X and Y axis info for statistics
xAxisLabels = []
yAxisValues = []
recvValues = [] # For receiving important info, not number of times sent
stepValues = [] # For any step that required some sort of computation, whether it resulted in a modified state or not

# Running the algorithms in their most up-to-date form:
if(args.STA):
    STA.RSTA(G, args.STA)
    xAxisLabels.append("RSTA")
    yAxisValues.append(G.graph["RSTA"])
    recvValues.append(G.graph["RSTA_recv"])
    stepValues.append(G.graph["RSTA_step"])

if(args.MTA):
    MTA.MTA(G, args.MTA)
    xAxisLabels.append("MTA")
    yAxisValues.append(G.graph["MTA"])
    recvValues.append(G.graph["MTA_recv"])
    stepValues.append(G.graph["MTA_step"])

if(args.DA):
    DA.DA(G, args.DA)
    xAxisLabels.append("DA")
    yAxisValues.append(G.graph["DA"])
    recvValues.append(G.graph["DA_recv"])
    stepValues.append(G.graph["DA_step"])

if(args.stats):
    plt.figure()
    plt.bar(xAxisLabels, yAxisValues)

    plt.title("Sender Iterations to Output SPT - {0}".format(args.stats))
    plt.ylabel("Iteration count")
    plt.xlabel("SPT Algorithm")

    for index, value in enumerate(yAxisValues):
        plt.text(value, index, str(value), color='black')
        print(str(value))

    plt.figure()
    plt.bar(xAxisLabels, recvValues)
    plt.title("Node State Modifications - {0}".format(args.stats))
    plt.ylabel("Modifications")
    plt.xlabel("SPT Algorithm")

    plt.figure()
    plt.bar(xAxisLabels, stepValues)
    plt.title("Distributed Computational Steps - {0}".format(args.stats))
    plt.ylabel("steps")
    plt.xlabel("SPT Algorithm")

    plt.show()

# JH MTA simulation (version with 3 paths, nothing disjoint)
if(args.hamiltonAlgo):
    sendingEvents, sendingEvents2 = MTA.hamiltonAlgo(G, args.hamiltonAlgo, 3)

    for vertex in G:
        print("Path Bundle for {0} (ID = {1})\n===".format(vertex, G.nodes[vertex]['ID']))
        for path in G.nodes[vertex]['pathBundle']:
            print(path)
        print("===\n")

    print(sendingEvents)
    print("sending events 2: {0}".format(sendingEvents2))
    print(len(sendingEvents2))

# YP MTA simulation (version with 3 paths, nothing disjoint)
if(args.PanAlgo):
    nodeSendingCount = MTA.PanAlgo(G, args.PanAlgo)

    print("Sending count: {0}".format(nodeSendingCount))
    print("other:\n{0}".format(nx.get_node_attributes(G, 'updateCounter')))

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