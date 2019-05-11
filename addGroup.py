import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *

cs = Controller('localhost', 'admin', 'admin')
topo = Topology()
topo.requestData(cs)

gr = SimpleGroup().withId(17).withName('GROUP-17').withSwitch("openflow:1")
gr.addBucket([]).addAction(SimpleGroup.createActionOutputToPort(1), 0)
gr.addBucket([]).addAction(SimpleGroup.createActionOutputToPort(2), 1)
gr.addAction(SimpleGroup.createActionSetTTL(127), 0)
gr.addAction(SimpleGroup.createActionSetTTL(137), 1)
print(gr.push(cs))
