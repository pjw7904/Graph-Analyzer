import logging
from TreeAnalyzer import TreeValidator
from networkx import single_source_shortest_path_length

#
# Constants
#
TOP_NODE = 0

def init(Graph, root, m=2, removal=None):
    # Create a validation object to make sure the result is a tree
    treeValidator = TreeValidator(Graph.nodes, root) 

    # Give each vertex an empty path bundle structure to start
    for vertex in Graph:
        if vertex != root:
            Graph.nodes[vertex]['pathBundle'] = [] # The bundle structure is a list
            Graph.nodes[vertex]['done'] = False # Fully populated bundle
            Graph.nodes[vertex]['visited'] = False
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))
        else:
            # The root will add itself as the only path it will receive
            Graph.nodes[root]['pathBundle'] = [Graph.nodes[root]['ID']]
            Graph.nodes[vertex]['done'] = True
            Graph.nodes[vertex]['visited'] = True
            logging.warning("{0} path bundle = {1}\n\n".format(vertex, Graph.nodes[vertex]['pathBundle']))

    # Queue to determine who should be sending their bundle at a given discrete event
    sendingQueue = [root]
    # Count the number of iterations needed to send all updates
    queueCounter = 0
    # The maximum number of paths is the number of remedy paths (m) + the one primary path
    maxPaths = m + 1
    # How to mark to go backwards back up towards the root
    needsReverse = True

    while sendingQueue:
        queueCounter += 1
        logging.warning("-----------\nQUEUE ITERATION: {0}\nCURRENT QUEUE {1}\n".format(queueCounter, sendingQueue))

        v = sendingQueue.pop(TOP_NODE)
        logging.warning("SENDING NODE: {0}\nPATH BUNDLE = {1}\n".format(v, Graph.nodes[v]['pathBundle']))

        for neighbor in Graph.neighbors(v):
            if(not Graph.nodes[neighbor]['visited']):
                Graph.nodes[neighbor]['visited'] = True
                sendingQueue.append(neighbor)

        # if the queue is empty and we haven't gone back in reverse yet
        if(not sendingQueue and needsReverse):
            # mark this as complete, we are going in reverse now
            needsReverse = False

            # reset each visited status for every node
            for vertex in Graph:
                Graph.nodes[vertex]['visited'] = False

            # append the final node of the BFS, this is the new starting point
            sendingQueue.append(v)
            Graph.nodes[v]['visited'] = True

            logging.warning("++++++ REVERSE REVERSE ++++++\n")

    return