from DistributedAlgorithm import DistributedAlgorithm
from TreeAnalyzer import TreeValidator

TOP_NODE = 0 # For popping the next node to send

def runTest(graph, sendQueue, treeValidator, algo):
    while sendQueue:
        sender = sendQueue.pop(TOP_NODE)
        senderAlgorithm = graph.nodes[sender]['algo']

        for receiver in graph.neighbors(sender):
            print(f"{sender} --> {receiver}")
            receiverAlgorithm = graph.nodes[receiver]['algo']

            receiverMustSend = propagation(senderAlgorithm, receiverAlgorithm)

            if(receiverMustSend and receiver not in sendQueue):
                sendQueue.append(receiver)

        senderAlgorithm.sendingCleanup()

    # Print the results
    for node in sorted(graph.nodes):
        print(graph.nodes[node]['algo'])

    print(f"Tree status: {treeValidator.isTree()}")

    print("\n==============================")

    if(algo == "rsta"):
        for edge in graph.edges:
            role1 = graph.nodes[edge[0]]['algo'].role[graph.nodes[edge[1]]['algo'].id]
            role2 = graph.nodes[edge[1]]['algo'].role[graph.nodes[edge[0]]['algo'].id]
            print(f"{graph.nodes[edge[0]]['algo'].id}, {graph.nodes[edge[1]]['algo'].id} ---> ({role1}, {role2})")
            if(role1 == role2):
                print("BAD")
    return

# Names = the vertex name, ID = the ID given to the vertex.
def runFailureTest(graph, failedEdgeNames, treeValidator, algo, failedEdgeIDs=None):
    startingNodes = []
    for node in failedEdgeNames:
        failureInfo = failedEdgeIDs if failedEdgeIDs is not None else failedEdgeNames
        graph.nodes[node]['algo'].processFailure(failureInfo)
        startingNodes.append(node)

    runTest(graph, startingNodes, treeValidator, algo)

    return

def propagation(sender: DistributedAlgorithm, receiver: DistributedAlgorithm):
    return receiver.processMessage(sender.messageToSend())