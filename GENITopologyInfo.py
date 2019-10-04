#!/usr/bin/env python
from GENIutils import *

RSTPInfoList = []
interfaceList = []
cmdList = []
linkStatus = defaultdict(list)
addressing = []
outputAddressing = []

RSPEC = getConfigInfo("Local Utilities", "RSPEC")
endNodeNamingSyntax = getConfigInfo("MTP Utilities", "endNodeName")
GENIDict = buildDictonary(RSPEC)

getInterfaces = "ls /sys/class/net/"
RSTPInfo = "sudo ovs-vsctl list p {} | grep rstp_status"
addressingInfo = "ifconfig {} | grep -E 'inet|ether'"

f = open("Topology.txt", "w+")

for currentRemoteNode in GENIDict:
    if(endNodeNamingSyntax not in currentRemoteNode):
        RSTPInfoList[:] = []
        interfaceList[:] = []

        interfaceList = orchestrateRemoteCommands(currentRemoteNode, GENIDict, getInterfaces, getOutput=True).split("\n")
        interfaceList[:] = [interface for interface in interfaceList if "eth" in interface and "eth0" not in interface]

        for interface in interfaceList:
            updated_addressingInfo = addressingInfo.format(interface)
            RSTPOutput = orchestrateRemoteCommands(currentRemoteNode, GENIDict, updated_addressingInfo, getOutput=True)
            IPAddr = re.search(r'inet(.*?)netmask', RSTPOutput).group(1).strip()

            RSTPInfoList = re.split(",|}|{", RSTPOutput)
            del RSTPInfoList[0]

            linkStatus[IPAddr].append(currentRemoteNode)
            linkStatus[IPAddr].append(interface)
            addressing.append(IPAddr)

for address in linkStatus:
    localValue = ""
    remoteValue = ""

    for addr in addressing:
        if(address.split(".")[2] == addr.split(".")[2]):
            if(address == addr):
                localValue = address
            else:
                remoteValue = addr

    if(localValue and remoteValue):
        outputAddressing.append("{0}_{1}\n".format(linkStatus[localValue][0],linkStatus[remoteValue][0]))

outputAddressing.sort()
nodeHeader = outputAddressing[0].split("_")[0]

for entry in outputAddressing:
    currentNode = entry.split("_")[0]
    if(currentNode != nodeHeader):
        nodeHeader = currentNode
    f.write(entry)
f.close()
