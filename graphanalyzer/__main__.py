## Standard modules
import argparse # Parsing command-line arguments
import sys # Access to system-level functions

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
from plotBatchTest import plotResults # Plotting for batch testing

def parseArgs():
    # ArgumentParser object to read in command-line arguments
    argParser = argparse.ArgumentParser(description="Graph Theory Analysis Script")

    # The source of the graph
    argParser.add_argument("-s", "--source", nargs='*')

    # If logging should be performed in a text file
    argParser.add_argument("--log", action="store_true")

    # If a formal experiement with a large number of graphs is needed
    # 0 = # vertex or edge (k-regular), 1 = min value, 2 = max value
    argParser.add_argument("-t", "--test", nargs='*')

    # Calculating graph metrics
    argParser.add_argument("--CalcClassicalMetrics", action="store_true") # Compute classical metrics from algebraic and spectral graph theory
    argParser.add_argument("--CalcBC", action="store_true") # Compute betweenness centrality for each vertex
    argParser.add_argument("--CalcAvgNC", action="store_true")

    # Meshed Tree Algorithm (MTA) simulation options depending on how it is implemented
    argParser.add_argument("--MTA") # MTA - Remedy Path (no bundle limit)
    argParser.add_argument("--NPaths") # MTA - Backup or Remedy Path (N paths in bundle limit)

    # IEEE Rapid Spanning Tree Algorithm (Rapid STA) simulation options
    argParser.add_argument("--RSTA") # Root pre-designated by adding it as argument

    # Dijkstra's Algorithm
    argParser.add_argument("--DA") # Argument of the root of the SPT

    # Get a visual of the batch test results
    argParser.add_argument("--plot", action="store_true")

    # Get figures/plots of data collected
    argParser.add_argument("--stats") # Argument of the name of the topology

    # Allow the user to remove an edge from the graph. 
    # The algorithm being run will determine what happens based on that removed edge input
    argParser.add_argument("-r", "--remove", type=int, nargs=2)

    # Parse the arguments
    args = argParser.parse_args()

    return args

def generateGraph(sourceInput):
    graphFormat = sourceInput[0]

    if(graphFormat == "graphml" and len(sourceInput) == 2):
        try:
            G = nx.read_graphml(path=sourceInput[1], node_type=int) # Reads in names as ints for simplicity, may change back to str in the future
        except FileNotFoundError:
            print("graphml graph file {0} does not exist in this location".format(sourceInput[1]))
            sys.exit()

    elif(graphFormat == "ring" and len(sourceInput) == 2):
        G = nx.cycle_graph(int(sourceInput[1]))

    elif(graphFormat == "random" and len(sourceInput) == 2):
        hardCodedNumOfNodes = 25
        probabilityForEdgeCreation = float(sourceInput[1])
        G = GraphGenerator.generateErdosRenyiGraph(hardCodedNumOfNodes, probabilityForEdgeCreation)

    else:
        sys.exit("Error: invalid source, please try again using RSPEC, graphml, random, or simulation")

    return G

def computeMetrics(calcOptions, G):
    if(calcOptions["Classical"]):
        results = ClassicalMetrics.calculateClassicalMetricsResults(G)
        print("{Header}\n{Results}\n".format(Header="____CLASSICAL METRICS____", Results=tabulate(results, headers=["Metric", "Results"], numalign="right", floatfmt=".4f")))

    if(calcOptions["BC"]):
        results = ClassicalMetrics.calculatePerNodeBetweennessCentrality(G)
        print("{Header}\n{Results}\n".format(Header="____BETWEENNESS CENTRALITY____", Results=tabulate(results, headers=["Node", "Results"], numalign="right", floatfmt=".4f")))

    if(calcOptions["AvgNC"]):
        results = ClassicalMetrics.calculatePerDegreeAvgNeighborConnectivity(G)
        print("{Header}\n{Results}\n".format(Header="____AVG NEIGHBOR CONNECTIVITY____", Results=tabulate(results, headers=["Degree", "Results"], numalign="right", floatfmt=".4f")))

    return

def removedEdge(Graph, edge):
    if(edge and len(edge) == 2 and Graph.has_edge(int(edge[0]), int(edge[1]))):
        return edge
    else:
        return None

'''
#######
main 
#######

# NetworkX graph used:
# |Type       | Self-Loops | Parallel Edges|
# |Undirected | No         | No            |
'''
def main():
    # Read in command-line arguments
    args = parseArgs()

    # Create a structure to hold graphs for batch testing (if needed)
    graphList = [] # A place to hold ya graphs

    if(args.test):
        if(len(args.test) < 3):
            print("error: Missing test arguments")
            sys.exit(0)

        testType = args.test[0]
        minValue = args.test[1]
        maxValue = int(args.test[2])

        notFinished = True

        # Scale the number of vertices
        if(testType == "vertex"):
            numberOfVerticies = int(minValue)

            if(args.test[3]):
                edgeProb = float(args.test[3])
            else:
                edgeProb = .5

            if(args.test[4] != "None"):
                seed = int(args.test[4])
            else:
                seed = None

            while(notFinished):
                G = GraphGenerator.generateErdosRenyiGraph(numberOfVerticies, edgeProb, inputSeed=seed)

                if(nx.is_connected(G) and nx.node_connectivity(G) >= 2):
                    graphList.append(G)
                    numberOfVerticies += 1

                    if(numberOfVerticies == maxValue+1):
                        notFinished = False

        # Scale the number of edges
        elif(testType == "edge"):
            numberOfEdges = int(minValue)

            if(args.test[3]):
                numberOfVerticies = int(args.test[3])
            else:
                print("error: must include # of verticies for k-regular test")
                sys.exit()

            if(numberOfVerticies % 2 != 0):
                print("error: k-regular tests must have an even number of vertices")
                sys.exit()

            if(args.test[4] != "None"):
                seed = int(args.test[4])
            else:
                seed = None

            while(notFinished):
                G = GraphGenerator.generateRegularGraph(numberOfEdges, numberOfVerticies, inputSeed=seed)

                if(nx.is_connected(G) and nx.node_connectivity(G) >= 2):
                    graphList.append(G)
                    numberOfEdges += 1

                    if(numberOfEdges == maxValue+1):
                        notFinished = False

    else:
        G = generateGraph(args.source) # Generate a graph to use for calculations

    ## Run one of the algorithms for initial SPT convergence
    # Rapid Spanning Tree Algorithm
    if(args.RSTA):
        if(args.test):
            for graph in graphList:
                RSTA.init(G=graph, r=0, loggingStatus=True, batch=True)
            plotName = "RSTA"
        else:
            RSTA.init(G, int(args.RSTA), args.log) # 5/20/22 --> UPDATE FOR INT-NAMED VERTICIES

            if(args.remove):            
                if (len(args.remove) == 2):
                    try:
                        G.remove_edge(int(args.remove[0]), int(args.remove[1]))
                    except NetworkXError:
                        print("ARGS ERROR (-r/--remove): edge to be removed does not exist")
                        sys.exit(0)

                    RSTA.reconverge(G, args.RSTA, int(args.remove[0]), int(args.remove[1]))

                else:
                    print("ARGS ERROR (-r/--remove): two arguments are needed to remove an edge")
                    sys.exit(0)

    # Meshed Tree Algorithm - N-Paths
    elif(args.NPaths):
        if(args.test):
            for graph in graphList:
                MTP_NPaths.init(Graph=graph, root=0, loggingStatus=True, batch=True)
            plotName = "MTA N-Paths"
        else:
            # If a valid edge is to be removed, it will be included in the analysis
            MTP_NPaths.init(Graph=G, root=int(args.NPaths), loggingStatus=args.log, remedyPaths=True, removal=removedEdge(G, args.remove))

    # Meshed Tree Algorithm - Remedy Paths 
    elif(args.MTA):
        if(args.test):
            for graph in graphList:
                MTA_RP.init(Graph=graph, root=0, loggingStatus=True, batch=True)
            plotName = "MTA Remedy"
        else:
            MTA_RP.init(G, int(args.MTA), args.log)

            if(args.remove):            
                if (len(args.remove) == 2):
                    try:
                        G.remove_edge(args.remove[0], args.remove[1])
                    except NetworkXError:
                        print("ARGS ERROR (-r/--remove): edge to be removed does not exist")
                        sys.exit(0)

                    MTA_RP.MTA_reconverge(G, int(args.remove[0]), int(args.remove[1]))

                else:
                    print("ARGS ERROR (-r/--remove): two arguments are needed to remove an edge")
                    sys.exit(0)

    # Dijkstra's Algorithm
    elif(args.DA):
        if(args.test):
            for graph in graphList:
                DA.init(Graph=graph, source=0, loggingStatus=True, batch=True)
            plotName = "Dijkstra's Algo"
        else:
            DA.init(Graph=G, source=int(args.DA))

    # We just want to look at the graph, no algorithm to study for additional info

    if(args.plot):
        plotResults(plotName)

if __name__ == "__main__":
    main()