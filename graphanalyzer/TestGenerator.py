## Standard modules
from pathlib import Path

from networkx import NetworkXError, write_graphml
from networkx.utils import graphs_equal
import GraphGenerator

def generateRegularGraphs(numOfGraphs, numNodes, sharedDegree):
    graphsToSave = [] # Turn these into graphml files
    graphLocation = f"C:/Users/peter/Documents/research/mtp-analysis/graphs/graphml/{sharedDegree}_regular_{numNodes}_node"

    Path(graphLocation).mkdir(parents=False, exist_ok=False)

    graphLocation += "/{}"

    for graphNum in range(numOfGraphs):
        maxAttempts = 25
        currentAttempt = 0

        print(f"Generating graph #{graphNum+1}")

        while(currentAttempt != maxAttempts):
            candidateGraph = GraphGenerator.generateRegularGraph(sharedDegree, numNodes, inputSeed=None)

            if(GraphGenerator.isValidGraph(candidateGraph)):
                for savedGraph in graphsToSave:
                    if(graphs_equal(candidateGraph, savedGraph)):
                        currentAttempt += 1
                        break
                else:
                    print(f"Saving graph #{graphNum+1}")
                    graphsToSave.append(candidateGraph)
                    write_graphml(candidateGraph, graphLocation.format(f"regular_{numNodes}_{sharedDegree}_{graphNum+1}.graphml"))
                    break
            else:
                currentAttempt += 1

        if(currentAttempt == maxAttempts):
            raise NetworkXError("Cannot get valid graph")

    return

#generateRegularGraphs(25, 500, 10)