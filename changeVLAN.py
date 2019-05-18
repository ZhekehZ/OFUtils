import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *

cs = Controller('localhost', 'admin', 'admin')
topo = Topology()
topo.requestData(cs)
FM = flowManager

ip = input("IP>  ") # 10.0.0.1
vlanFrom = input("VLAN FROM> ") # 100
vlanTo = input("VLAN TO> ") # 101

host = None
for node in topo.nodes.values():
    if type(node) == Leaf and node.nAddresses[0][1] == ip:
        host = node

if not host:
    exit("WRONG IP: %s" % ip)

switch = host.nConnections[0][0]

mac, ip = host.nAddresses[0]
print("Host:\r\n\tIP: %s\r\n\tMAC: %s" % (ip, mac))
print("Switch:\r\n\tName: %s" % switch.nId)

FM = flowManager()
FM.requestData(cs)

for flow in FM.getSwitchTableFlowList(switch.nId, 0):
    if FM.flowSrcDstMacIs(switch.nId, 0, flow['flow']['id'], 'src', mac):
        sflow = SimpleFlow.fromRAWFlow(switch.nId, flow['flow'])
        sflow.addMatch(SimpleFlow.createMatchVLAN(vlanFrom)) \
             .addAction(SimpleFlow.createActionSetVLAN(vlanTo))
        print(sflow.push(cs))
for flow in FM.getSwitchTableFlowList(switch.nId, 0):
    if FM.flowSrcDstMacIs(switch.nId, 0, flow['flow']['id'], 'dst', mac):
        sflow = SimpleFlow.fromRAWFlow(switch.nId, flow['flow'])
        sflow.addMatch(SimpleFlow.createMatchVLAN(vlanTo)) \
             .addAction(SimpleFlow.createActionSetVLAN(vlanFrom))
        print(sflow.push(cs))

#vlanFlow = SimpleFlow()
#vlanFlow = vlanFlow.withId("VLAN-BAN-%s" % host.nAddresses[0][0]) \
#                   .withPri(100) \
#                   .withTbl(0) \
#                   .withSwitch(switch.nId) \
#                   .addMatch(SimpleFlow.createMatchMacSrc(host.nAddresses[0][0])) \
#                   .addMatch(SimpleFlow.createMatchVLAN(44)) \
#                   .addAction(SimpleFlow.createActionSetVLAN(vlan))
#                   
#print(vlanFlow.push(cs))



