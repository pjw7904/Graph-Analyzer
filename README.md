# MTP-Analysis

A collection of code and documentation for the purposes of defining and analyzing the properties of Meshed Trees.

## Dependencies / Requirements

- Python $\geq$ 3.8
- ConfigParser
- matplotlib
- networkx
- numpy
- pydot
- pygraphviz
- tabulate

## Running

usage: graphanalyzer [-h] [--root vertex] [--remedy] [-m numOfBackups] [-r vertex1 vertex2] [-p] {mta,npaths,rsta,da,none}

Graph and shortest path tree algorithm analysis script. Please update JSON config files before running.

positional arguments:
  {mta,npaths,rsta,da,none}
                        tree algorithm to run on graph (or none).

optional arguments:
  -h, --help            show this help message and exit
  --root vertex         the root of the tree (leave blank for none)
  --remedy              (MTA N-paths) m number of remedy paths, not any paths
  -m numOfBackups       (MTA N-paths) number of backup paths, N = m+1
  -r vertex1 vertex2    (MTA N-Paths) remove edge to test algorithm recovery
  -p, --picture         Save Graphviz-generated picture of graph