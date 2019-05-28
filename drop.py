from Utils import *

cs = Controller('localhost', 'admin', 'admin')
topo = Topology()
topo.requestData(cs)
srcMAC = '00:00:00:00:00:02'
dstMAC = '00:00:00:00:00:04'

print(
SimpleFlow().withPri(1000).resetMatches().addMatch(SimpleFlow.createMatchL2(srcMAC, dstMAC)).addAction(SimpleFlow.createActionDrop()).withSwitch('openflow:1').withTbl(0).withId('viktorKOKO').push(cs)
)
