import sys
sys.path.append(sys.path[0]+'/../Utils')

from FlowMaker import *
from Topology import ControllerSettings

cs = ControllerSettings('localhost', 'admin', 'admin')
srcMAC = '5e:ac:8b:ce:ae:b7'
dstMAC = '6a:0c:5e:73:c0:5e'
makeFlow(cs, srcMAC, dstMAC)
