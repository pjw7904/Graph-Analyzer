import heapq
from collections import namedtuple

MTAVector = namedtuple("MTA_Vector", "cost path")

# The empty path bundle
pathBundle = []

# Add the paths to maintain the heap invariant
heapq.heappush(pathBundle, MTAVector(0, "A")) # 1
heapq.heappush(pathBundle, MTAVector(1, "AC")) # 2
heapq.heappush(pathBundle, MTAVector(2, "ABC")) # 3
heapq.heappush(pathBundle, MTAVector(2, "ACD")) # 5
heapq.heappush(pathBundle, MTAVector(2, "ABD")) # 4

while(pathBundle):
    print(heapq.heappop(pathBundle))
