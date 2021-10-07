import os
import configparser # Parsing configuration file arguments
import networkx as nx # Graph creation and analysis

'''
start of main
'''
switchNamingSyntax = input("MTP Switch node naming prefix (ex: node-): ")
endNodeNamingSyntax = input("Client node naming prefix (ex: endnode-): ")
cnfFileName = input("addrInfo file path: ")
fileName = input("Graph name: ")

# Create a Config Parser object so GENI topology information can be read
config = configparser.ConfigParser()
config.read(cnfFileName) # Grabbing information from addrinfo.cnf

# Creating a list of GENI topology verticies
V = [node for node in config.sections() if(switchNamingSyntax in node and endNodeNamingSyntax not in node)]

# Creating a list of GENI topology edges
E = []
for node in V:
    nodeNeighbors = [(key, value) for key, value in config.items(node) if("_neighbor" in key and endNodeNamingSyntax not in value)]
    for neighbor in nodeNeighbors:
        E.append((node, neighbor[1]))

# Create a NetworkX graph and add in the GENI topology information
G = nx.Graph()
G.add_nodes_from(V)
G.add_edges_from(E)

# Write this graph to a graphml file to be reused later on
nx.write_graphml(G=G, path=fileName + ".graphml", prettyprint=True)
print("Note: graph {0} has been converted to a graphml file named {1}. It is saved in the current directory."
    .format(fileName, fileName + ".graphml"))