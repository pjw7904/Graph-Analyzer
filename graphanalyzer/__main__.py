## Standard modules
import sys # Access to system-level functions
from os.path import join as getFile

# Graph creation and analysis
import GraphGenerator # Generate graphs via well-known algorithms
import FigureGenerator
import TestGenerator
import Algorithms
import Test

# Configuration
import parseConfig as config

'''
main, entry to program 

# NetworkX graph used:
# |Type       | Self-Loops | Parallel Edges|
# |Undirected | No         | No            |
'''
def main():
    # Read in command-line arguments
    args = config.parseArgs()

    # Read the JSON files to determine what the graph and setup looks like
    programConfig = config.parseSettingsConfig()
    graphConfig = config.parseGraphConfig()

    # Graph meta-information
    typeOfTest = graphConfig["type"]
    typeOfGraph = graphConfig["choice"]
    nameOfTest = graphConfig["name"]
    testSeed = graphConfig["seed"]

    if(typeOfTest == None or typeOfGraph == None):
        print("ERROR: type and/or choice JSON object has a null value")
        sys.exit()

    # Generate a single graph of the given type
    if(typeOfTest == "single"):
        graph = GraphGenerator.generateGraph(typeOfGraph, graphConfig["single"][typeOfGraph], seed=testSeed, graphDirectory=programConfig["graphs"], logDirectory=programConfig["results"]["log"])

        # Option if you want to see a picture of the graph (Graphviz-generated)
        if(args.picture):
            FigureGenerator.drawGraph(graph, getFile(programConfig["results"]["figure"], nameOfTest + ".png"))

        # Option if you want to save a graphml of the graph, which will be placed in the graph folder
        if(args.save):
            GraphGenerator.toGraphml(graph, getFile(programConfig["graphs"], nameOfTest + ".graphml"))

        if(args.algorithm != "none"):
            # Run one of the algorithms for initial SPT convergence and potential further tests
            Algorithms.runAlgorithmOnGraph(graph, args, programConfig["results"]["log"], nameOfTest)

    elif(typeOfTest == "batch"):
        TestGenerator.runBatchTest(typeOfGraph, graphConfig["batch"][typeOfGraph], args, programConfig["results"]["log"], programConfig["results"]["figure"], nameOfTest)

    elif(typeOfTest == "test"):
        graphDirectory = getFile(programConfig["graphs"], graphConfig["test"]["graphDirectory"]).replace("\\","/")
        Test.runBatchDirectoryTest(graphDirectory, programConfig["results"]["test"], args)

if __name__ == "__main__":
    main()