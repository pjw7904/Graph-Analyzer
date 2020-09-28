#!/usr/bin/env python

def createMeshedTreeDatatStructures(G, root):
    IDCount = 0

    for node in G:
        G.nodes[node]['ID'] = chr(65 + IDCount)

        if(node == root):
            rootInfo = {
                'isRoot': True,
                'state': "F",
                'ACK(child)': [],
                'ACK(noChild)': [],
                'inBasket': [],
                'pathBundle': [G.nodes[node]['ID']]
            }

            G.nodes[node]['rootInfo'] = rootInfo
            print("- Root node is {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        else:
            nodeInfo = {
                'isRoot': False,
                'state': "I",
                'NEXT': False,
                'STOP': False,
                'inBasket': [],
                'pathBundle': []
            }

            G.nodes[node]['nodeInfo'] = nodeInfo
            print("- Non-Root node {0}, ID = {1}".format(node, G.nodes[node]['ID']))

        IDCount += 1

    print("---------\n")

    return


def rootActions(G, root):
    rootConf = G.nodes[root]['rootInfo']

    if(rootConf['state'] == 'F'):
        print("hi")

        #for nbr in G.neighbors(root):
            #G.nodes[nbr]['nodeInfo']['inBasket'].extend(G.nodes[root]['rootInfo']['pathBundle'])
            #print(G.nodes[nbr]['nodeInfo']['inBasket'])

    return


def nodeActions():

    return


def runMTASimulation(G, root):
    rootActions(G, root)

    return



'''
class MTA:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = MTA("John", 36)

print(p1.name)
print(p1.age)
'''
