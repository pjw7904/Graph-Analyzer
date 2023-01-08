import networkx as nx

class TreeValidator:
    def __init__(self, vertices, root):
        # Create an empty, simple graph and add the inputted vertices
        self.graph = nx.Graph()
        self.graph.add_nodes_from(vertices)

        # Mark the root of the tree, as it will never have a parent
        self.root = root

        # Add inputted vertices into new graph
        for vertex in vertices:
            self.graph.nodes[vertex]['children'] = []   # mark children on the given node
            self.graph.nodes[vertex]['parent'] = None   # mark the parent of the given node (root will not have one)

    def addParent(self, parent, child):
        # Determine who the child's previous parent is (or if they don't have one)
        previousParent = self.graph.nodes[child]['parent']

        if(previousParent == parent):
            return

        if(previousParent != None):
            self.removeRelationship(previousParent, child)

        self.addRelationship(parent, child)
        return

    def removeParent(self, child):
        # Determine who the child's previous parent is (or if they don't have one)
        previousParent = self.graph.nodes[child]['parent']

        if(previousParent != None):
            self.removeRelationship(previousParent, child)
        return

    def removeRelationship(self, parent, child):
        self.graph.nodes[parent]['children'].remove(child)
        self.graph.nodes[child]['parent'] = None
        self.graph.remove_edge(parent, child)
        return

    def addRelationship(self, parent, child):
        self.graph.nodes[parent]['children'].append(child)
        self.graph.nodes[child]['parent'] = parent
        self.graph.add_edge(parent, child)
        return

    def isTree(self):
        return nx.is_tree(self.graph)

    def isParent(self, vertex, potentialParent):
        return self.graph.nodes[vertex]['parent'] == potentialParent

    def isChild(self, vertex, potentialChild):
        return potentialChild in self.graph.nodes[vertex]['children']

    def relationshipStatus(self, vertex):
        return "Parent: {parent_vertex}\nChildren: {children_vertices}".format(parent_vertex=self.graph.nodes[vertex]['parent'], children_vertices=self.graph.nodes[vertex]['children'])

    def getParent(self, vertex):
        return self.graph.nodes[vertex]['parent']

    def getChildren(self, vertex):
        return self.graph.nodes[vertex]['children']

    def getGraph(self):
        return self.graph

    def getStrandedVertices(self):
        return [vertex for vertex in self.graph.nodes if self.graph.nodes[vertex]['parent'] == None and vertex != self.root]