from Utils import *

cs = Controller('localhost', 'admin', 'admin')
topo = Topology()
topo.requestData(cs)

srcMAC = '00:00:00:00:00:01'
dstMAC = '00:00:00:00:00:05'

pushFlow(cs, topo, srcMAC, dstMAC)
