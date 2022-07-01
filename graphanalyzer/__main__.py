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
from plotBatchTest import plotResults # Plotting for batch testing
import GraphGenerator as generator # Generate graphs via well-known algorithms

# Configuration
import parseConfig as config

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

    # Determine how many graphs are to be created
    typeOfTest = graphConfig["type"]
    typeOfGraph = graphConfig["choice"]

    if(typeOfTest == None or typeOfGraph == None):
        print("ERROR: type and/or choice JSON object has a null value")
        sys.exit()

    # Generate a single graph of the given type
    if(typeOfTest == "single"):
        G = generator.generateGraph(typeOfGraph, graphConfig["single"][typeOfGraph], programConfig["graphs"])

        # If you want to see a picture of the graph
        if(args.picture):
            A = nx.nx_agraph.to_agraph(G)
            A.layout(prog="dot")
            A.draw(getFile(programConfig["results"]["figure"], args.picture + ".png"))

        ## Run one of the algorithms for initial SPT convergence
        # Rapid Spanning Tree Algorithm
        if(args.algorithm == "rsta"):
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
        elif(args.algorithm == "npaths"):
            # If a valid edge is to be removed, it will be included in the analysis
            MTP_NPaths.init(Graph=G, root=int(args.root), logFilePath=programConfig["results"]["log"], remedyPaths=args.remedy, m=args.backups, removal=removedEdge(G, args.remove))

        # Meshed Tree Algorithm - Remedy Paths 
        elif(args.algorithm == "remedy"):
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
        elif(args.algorithm == "da"):
            DA.init(Graph=G, source=int(args.DA))


if __name__ == "__main__":
    main()