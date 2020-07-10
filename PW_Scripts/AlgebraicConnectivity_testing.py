'''
Just a little test script to help understand what is going on with algebraic connectivity.
Example topologies and their expected results will be from wiki, links will be posted before the code segment to check
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


## Creating the degree matrix for the graph (https://en.wikipedia.org/wiki/Degree_matrix)
print("Degree matrix:")

vertDegrees = []
for V in G:
    vertDegrees.append(G.degree(V))

degreeMatrix = np.diag(vertDegrees)
print(degreeMatrix)


## Creating the adjacency matrix for the graph (https://en.wikipedia.org/wiki/Adjacency_matrix)
print("\nAdjacency matrix:")

adjacencyMatrix = nx.to_numpy_matrix(G,dtype=int) # This is the adjacency matrix for some reason, weird name. Also used is
print(adjacencyMatrix)


## Creating the laplacian matrix for the graph (https://en.wikipedia.org/wiki/Laplacian_matrix)
print("\nLaplacian matrix:")
laplacianMatrix = degreeMatrix - adjacencyMatrix
print(laplacianMatrix)


## Determine algebraic connectivity for the graph (https://en.wikipedia.org/wiki/Algebraic_connectivity)

FV = nx.fiedler_vector(G)
print(FV)

AC = nx.laplacian_spectrum(G)
print(AC)

'''
same thing in one statement:
L = nx.laplacian_matrix(G)
print(L.toarray())
'''

'''
# Draw current graph info with pyplot. Two different options shown just to show it's very customizable
options = {
    'node_color': 'black',
    'node_size': 100,
    'width': 3,
}

plt.subplot(211)
nx.draw(G, with_labels=True, font_weight='bold')
plt.subplot(212)
nx.draw(G, **options)
plt.show()
'''
