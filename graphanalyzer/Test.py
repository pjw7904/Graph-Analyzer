from DistributedAlgorithm import DistributedAlgorithm
from TreeAnalyzer import TreeValidator
from timeit import default_timer as timer
from os.path import join as getFile
import glob
import GraphGenerator
import Algorithms
import pandas as pd 
import os
import csv

TOP_NODE = 0 # For popping the next node to send

def runTest(graph, sendQueue, treeValidator, algo):
    # Initalize metrics
    receiveCounter = 0  # Record the number of nodes which needed to process a message
    hasUpdate = 0       # Record the number of nodes which which updated their state as a result of a message received.
    startTime = timer() # Record elapsed time to converge or reconverge

    # While there is still a node that needs to send an update to neighbors
    while sendQueue:
        sender = sendQueue.pop(TOP_NODE)
        senderAlgorithm = graph.nodes[sender]['algo']

        for receiver in graph.neighbors(sender):
            receiveCounter += 1

            receiverAlgorithm = graph.nodes[receiver]['algo']

            receiverMustSend = propagation(senderAlgorithm, receiverAlgorithm)

            if(receiverMustSend):
                hasUpdate += 1

                # RSTA in recovery mode requires the repeated sending for redefining roles
                if(receiver not in sendQueue or algo == "rsta_recovery"):
                    sendQueue.append(receiver)

        senderAlgorithm.sendingCleanup()

    endTime = timer() # End timer once there is no more sending and processing from nodes

    # Collect metrics
    graph.graph[algo]["receives"] = receiveCounter
    graph.graph[algo]["updates"] = hasUpdate
    graph.graph[algo]["time"] = (endTime - startTime)
    graph.graph[algo]["tree"] = treeValidator.isTree()

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

    csvInitFile = open(getFile(logDirectory, testSet + ".log"), 'w', newline='')
    csvRecoverFile = open(getFile(logDirectory, testSet + "_recovery.log"), 'w', newline='')

    csvInitwriter = csv.writer(csvInitFile)
    csvRecoverwriter = csv.writer(csvRecoverFile)

    # Write header
    csvInitwriter.writerow(("testSetName","graphName","algo","time","receives","updates","tree"))
    csvRecoverwriter.writerow(("testSetName","graphName","algo","time","receives","updates","tree"))

    # Cycle through each saved graph in a given file
    for graphmlFile in glob.glob(graphDirectory + '/*.graphml'):
        # Import the graph into a networkx graph
        currentGraph = GraphGenerator.fromGraphml(graphmlFile)

        # Find an edge to remove, 0 = the default root
        args.remove = (0, list(currentGraph.neighbors(0))[0])

        print(f"Testing on: {graphmlFile}, break {args.remove}")

        # Run tests with each algorithm
        for currentAlgo in ("mta", "rsta", "da"):
            args.algorithm = currentAlgo

            print(f"\tStarting test for: {currentAlgo}")

            # Set up topology with Algorithms
            Algorithms.runAlgorithmOnGraph(currentGraph, args)

            # Write results in csv form - testSetName,graphName,algo,time,receives,updates,tree
            row = (testSet, os.path.basename(graphmlFile), 
                   currentAlgo, currentGraph.graph[currentAlgo]["time"],
                   currentGraph.graph[currentAlgo]["receives"], 
                   currentGraph.graph[currentAlgo]["updates"],
                   currentGraph.graph[currentAlgo]["tree"])
            csvInitwriter.writerow(row)

            recoveryName = f"{args.algorithm}_recovery"

            row = (testSet, os.path.basename(graphmlFile), 
                   currentAlgo, currentGraph.graph[recoveryName]["time"],
                   currentGraph.graph[recoveryName]["receives"], 
                   currentGraph.graph[recoveryName]["updates"],
                   currentGraph.graph[recoveryName]["tree"])
            csvRecoverwriter.writerow(row)

            # Add the edge back before the next algorithm starts its test
            currentGraph.add_edge(*args.remove)

            print(f"\tEnding test for: {currentAlgo}\n")

    # Close the file
    csvInitFile.close()
    csvRecoverFile.close()
    
    return