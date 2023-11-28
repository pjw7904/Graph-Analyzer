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

            # Set up topology with Algorithms
            Algorithms.runAlgorithmOnGraph(currentGraph, args)

            # Write results in csv form
            csvwriter.writerow([testSet, os.path.basename(graphmlFile), currentAlgo, currentGraph.graph[currentAlgo]["time"]])

    # Close the file
    csvFile.close()
    
    return