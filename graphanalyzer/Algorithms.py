## Custom modules
import MTA_RP # MTA Remedy Path algorithm
import MTP_NPaths # MTA N-Path algorithm
import RSTA # Rapid Spanning Tree algorithm
import DA # Dijkstra's algorithm

'''
Run the specified SPT algorithm with any included additional options
'''
def runAlgorithmOnGraph(graph, args, logFilePath, nameOfTest):
    # Rapid Spanning Tree Algorithm
    if(args.algorithm == "rsta"):
        RSTA.init(G=graph, r=args.root, logFilePath=logFilePath, testName=nameOfTest)

    # Meshed Tree Algorithm - N-Paths
    elif(args.algorithm == "npaths"):
        # If a valid edge is to be removed, it will be included in the analysis
        MTP_NPaths.init(Graph=graph, root=args.root, logFilePath=logFilePath, remedyPaths=args.remedy, m=args.backups, removal=removedEdge(graph, args.remove), testName=nameOfTest)

    # Meshed Tree Algorithm - Remedy Paths 
    elif(args.algorithm == "mta"):
        MTA_RP.init(Graph=graph, root=args.root, logFilePath=logFilePath, testName=nameOfTest)

    # Dijkstra's Algorithm
    elif(args.algorithm == "da"):
        DA.init(Graph=graph, root=args.root, logFilePath=logFilePath, testName=nameOfTest)

    return

'''
Determine if an edge exists to remove
'''
def removedEdge(graph, edge):
    if(edge and len(edge) == 2 and graph.has_edge(int(edge[0]), int(edge[1]))):
        return edge
    else:
        return None