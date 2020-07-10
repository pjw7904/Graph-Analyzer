'''
Just a little test script to help understand what is going on with algebraic connectivity.
Example topologies and their expected results will be from wiki, links will be posted before the code segment to check
This version is to be stuffed into a Jupyter notebook so that it can be shared and such
'''
import networkx as nx # External Python library (Anaconda provided) for graph creation and analysis
import numpy as np # External Python library (Anaconda provided) for all thinks linear algebra, arrays, matricies, etc and efficent memory usage compared to Py lists
import matplotlib.pyplot as plt # # External Python library (Anaconda provided) for drawing graphs

### Graph example from: https://en.wikipedia.org/wiki/Laplacian_matrix (Example section with resulting matricies I need the results here to match)
## Setting up the example graph
G = nx.Graph() # Create empty graph

# Adding the six verticies of the Wiki example graph
V = [1, 2, 3, 4, 5, 6]
G.add_nodes_from(V)

# Adding the seven edges from the Wiki example graph
E = [(1,2), (1,5), (2,3), (2,5), (3,4), (4,5), (6,4)]
G.add_edges_from(E)

# Print current graph info
numOfVerticies = G.number_of_nodes()
numOfEdges = G.number_of_edges()
print("Number of verticies: {verts}".format(verts=numOfVerticies))
print("Number of verticies: {edges}\n".format(edges=numOfEdges))

#nx.draw(G, with_labels=True, font_weight='bold')
#plt.savefig("graph.png",format="PNG")


## Creating the degree matrix for the graph (https://en.wikipedia.org/wiki/Degree_matrix)
D = []
for i in G:
    for j in G:
        if(i == j):
            D.append(G.degree(i))
        else:
            D.append(0)

D = np.array(D)
D = D.reshape(numOfVerticies, numOfVerticies)
print(D)

## Creating the adjacency matrix for the graph (https://en.wikipedia.org/wiki/Adjacency_matrix)
A = []
for i in G:
    for j in G:
        if(G.has_edge(i,j)):
            A.append(1)
        else:
            A.append(0)

A = np.array(A)
A = A.reshape(numOfVerticies, numOfVerticies)
print(A)

## Creating the laplacian matrix for the graph (https://en.wikipedia.org/wiki/Laplacian_matrix)
L = D - A

print(L)


## Determine algebraic connectivity for the graph (https://en.wikipedia.org/wiki/Algebraic_connectivity)
eigVals = np.linalg.eigvals(L)
eigVals = set(eigVals)

fiedlerValue = sorted(eigVals)[1] # index 1, which is where the second-smallest eigenvalue is located in the set

print(fiedlerValue)
