from DistributedAlgorithm import DistributedAlgorithm
from TreeAnalyzer import TreeValidator

TOP_NODE = 0 # For popping the next node to send

def runTest(graph, root, treeValidator):
    # Determines who is to send at any given tick
    sendQueue = [root] # send queue could turn into a 2-tuple of (sender, receivers) if not always all neighbor

    while sendQueue:
        sender = sendQueue.pop(TOP_NODE)

        for receiver in graph.neighbors(sender):
            senderAlgorithm = graph.nodes[sender]['algo']
            receiverAlgorithm = graph.nodes[receiver]['algo']

            receiverMustSend = propagation(senderAlgorithm, receiverAlgorithm)

            if(receiverMustSend):
                sendQueue.append(receiver)

    # Print the results
    for node in sorted(graph.nodes):
        print(graph.nodes[node]['algo'])

    print(f"Tree status: {treeValidator.isTree()}")

    return

def propagation(sender: DistributedAlgorithm, receiver: DistributedAlgorithm):
    return receiver.processMessage(sender.messageToSend())