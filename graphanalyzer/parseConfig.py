## Standard modules
import argparse # Parsing command-line arguments
import json # Parsing JSON-formatted configuration files

'''
Parse command-line arguments
'''
def parseArgs():
    # ArgumentParser object to read in command-line arguments
    argParser = argparse.ArgumentParser(description="Graph and shortest path tree algorithm analysis script. Please update JSON config files before running.")

    # Tree algorithms
    argParser.add_argument('algorithm', choices=["mta", "npaths", "rsta", "da", "none"], help="tree algorithm to run on graph (or none).")

    # Tree algorithm modifiers
    argParser.add_argument('--root', default=0, type=int, metavar="vertex", help="the root of the tree (leave blank for none)")
    argParser.add_argument("--remedy", default=False, action="store_true", help="(MTA N-paths) m number of remedy paths, not any paths") # MTA N-paths, remedy paths
    argParser.add_argument("-m", "--backups", default=2, type=int, metavar='numOfBackups', help="(MTA N-paths) number of backup paths, N = m+1") # MTA N-paths, number of additional paths
    argParser.add_argument("-r", "--remove", type=int, nargs=2, metavar=('vertex1', 'vertex2'), help="(all algorithms, only MTA N-paths confirmed to work) remove edge to test algorithm recovery") # Allow the user to remove an edge from the graph (result is algorithm-dependent)

    # Graph visualization
    argParser.add_argument("-p", "--picture", default=False, action="store_true", help="Save Graphviz-generated picture of graph") # Graphviz-based

    # Parse the arguments
    args = argParser.parse_args()

    return args

'''
Parse JSON settings configuration file
'''
def parseSettingsConfig():
    with open("config.json") as file:
        data = json.load(file)
    return data

'''
Parse JSON graph configuration file
'''
def parseGraphConfig():
    with open("graph.json") as file:
        data = json.load(file)
    return data