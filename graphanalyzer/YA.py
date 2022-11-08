#!/usr/bin/env python
'''
===========================
YENS'S ALGORITHM
===========================
'''
from networkx import shortest_path, Graph as newGraph

def init(baseGraph, source, sink, K=2):
    # Determine the shortest path from the source to sink via an existing shortest path algorithm
    A1 = shortest_path(baseGraph, source=source, target=sink, weight="weight", method="dijkstra")
    
    # Set up the structures to hold permenant and candidate paths
    A = [A1]
    B = []

    # Set up a second, empty graph. This will be used to handle the edge and node removals
    derivedGraph = newGraph()

    # For each additional path needed
    for k in range(1, K+1):
        # The spur node ranges from the first node to the next to last node in the previous k-shortest path.
        for i in range(0, len(A[k-1])-1):
            # Reset the derived graph to the original base graph
            derivedGraph.add_edges_from(baseGraph.edges(data=True))

            # Spur node is retrieved from the previous k-shortest path, k − 1.
            spurNode = A[k-1][i]

            # The sequence of nodes from the source to the spur node of the previous k-shortest path.
            rootPath = A[k-1][:(i+1)]

            for path in A:
                if(rootPath == path[:(i+1)]):
                    derivedGraph.remove_edge(path[i], path[i+1])

            for rootPathNode in rootPath:
                if(rootPathNode != spurNode):
                    derivedGraph.remove_node(rootPathNode)

            # Calculate the spur path from the spur node to the sink.
            spurPath = shortest_path(derivedGraph, source=spurNode, target=sink, weight="weight", method="dijkstra")

            # Entire path is made up of the root path and spur path.
            totalPath = rootPath + spurPath

            # Add the potential k-shortest path to the heap.
            if(totalPath not in B):
                    B.append(totalPath)

        # This handles the case of there being no spur paths, or no spur paths left
        if(not B):
            break
        
        # Sort the potential k-shortest paths by cost.
        B.sort(key = lambda i: (len(i), i))

        # Add the lowest cost path becomes the k-shortest path.
        A[k] = B.pop(0)

    print(A)

    return A