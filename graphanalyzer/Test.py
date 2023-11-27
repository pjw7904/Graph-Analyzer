from DistributedAlgorithm import DistributedAlgorithm
from TreeAnalyzer import TreeValidator
from timeit import default_timer as timer
from os.path import join as getFile
import glob
import GraphGenerator
import Algorithms
import statistics
import os
import csv

TOP_NODE = 0 # For popping the next node to send

def runTest(graph, sendQueue, treeValidator, algo):
    startTime = timer()

    while sendQueue:
        sender = sendQueue.pop(TOP_NODE)
        senderAlgorithm = graph.nodes[sender]['algo']

        for receiver in graph.neighbors(sender):
            #print(f"{sender} --> {receiver}")
            receiverAlgorithm = graph.nodes[receiver]['algo']

            receiverMustSend = propagation(senderAlgorithm, receiverAlgorithm)

            if(receiverMustSend and receiver not in sendQueue):
                sendQueue.append(receiver)

        senderAlgorithm.sendingCleanup()

    endTime = timer()
    graph.graph[algo]["time"] = (endTime - startTime)
    print(f"Tree status: {treeValidator.isTree()}")

    return

    # Print the results
'''    for node in sorted(graph.nodes):
        print(graph.nodes[node]['algo'])

    print("\n==============================")

    if(algo == "rsta"):
        for edge in graph.edges:
            role1 = graph.nodes[edge[0]]['algo'].role[graph.nodes[edge[1]]['algo'].id]
            role2 = graph.nodes[edge[1]]['algo'].role[graph.nodes[edge[0]]['algo'].id]
            print(f"{graph.nodes[edge[0]]['algo'].id}, {graph.nodes[edge[1]]['algo'].id} ---> ({role1}, {role2})")
            if(role1 == role2 or (role1 != "D" and role2 != "D")):
                print("BAD")'''

def propagation(sender: DistributedAlgorithm, receiver: DistributedAlgorithm):
    return receiver.processMessage(sender.messageToSend())

# Names = the vertex name, ID = the ID given to the vertex.
def runFailureTest(graph, failedEdgeNames, treeValidator, algo, failedEdgeIDs=None):
    startingNodes = []
    for node in failedEdgeNames:
        failureInfo = failedEdgeIDs if failedEdgeIDs is not None else failedEdgeNames
        graph.nodes[node]['algo'].processFailure(failureInfo)
        startingNodes.append(node)

    runTest(graph, startingNodes, treeValidator, algo)

    return

def runBatchDirectoryTest(graphDirectory, logDirectory, args):
    # Create a log file for data collection
    testSet = os.path.basename(graphDirectory)
    csvFile = open(getFile(logDirectory, testSet + ".log"), 'w')
    csvwriter = csv.writer(csvFile)  

    # Cycle through each saved graph in a given file
    for graphmlFile in glob.glob(graphDirectory + '/*.graphml'):
        # Import the graph into a networkx graph
        currentGraph = GraphGenerator.fromGraphml(graphmlFile)

        # Run tests with each algorithm
        for currentAlgo in ("mta", "rsta", "da"):
            args.algorithm = currentAlgo
            currentGraph.graph[currentAlgo] = {} # Metrics dict

            # Set up topology with Algorithms
            Algorithms.runAlgorithmOnGraph(currentGraph, args)

            csvwriter.writerow([testSet, os.path.basename(graphmlFile), currentAlgo, currentGraph.graph[currentAlgo]["time"]])

    csvFile.close()
    
    return


#runBatchDirectoryTest("C:/Users/peter/Documents/research/mtp-analysis/graphs/graphml/test_node")