import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *

def resetIPv4Flows(cs, topo):
    FM = flowManager()
    FM.requestData(cs)
    
    deleted, created, failed = 0, 0, 0
    _config = 0

    print("Deleting old flows... ", end='', flush=True)

    hosts = [node.nId for node in topo.nodes.values() if type(node) == Leaf]
    switches = [node.nId for node in topo.nodes.values() if type(node) != Leaf]
    for sw in FM.getSwitchList():
        for tbl in FM.getSwitchTableList(sw):
            for fl in FM.getSwitchTableFlowList(sw, tbl):
                if FM.flowIsIPv4(sw, tbl, fl['flow']['id']) or \
                   FM.flowIsInPortMatch(sw, tbl, fl['flow']['id']):
                    deleted += 1
                    _config += fl['isConfig']
                    FM.removeFlow(cs, sw, tbl, fl['flow']['id'])
    print("OK", flush=True)
    print("Adding new flows... ", end='', flush=True)            
    for srcMacId in range(len(hosts)):
        for dstMacId in range(srcMacId + 1, len(hosts)):
            srcMac = hosts[srcMacId][5:]
            dstMac = hosts[dstMacId][5:]
            #print('AddingFlow %s <-> %s' % (srcMac, dstMac))
            
            add1 = pushFlow(cs, topo, srcMac, dstMac)
            add2 = pushFlow(cs, topo, dstMac, srcMac)
            created += add1[0] + add2[0]
            failed += add1[1] + add2[1]
            
    flow = SimpleFlow()
    flow = flow.withPri(1) \
               .withTbl(0) \
               .addMatch(SimpleFlow.createMatchARP()) \
               .addAction(SimpleFlow.createActionNormal()) 
    for sw in switches:
        flow = flow.withId(sw + "_ARP").withSwitch(sw)
        if not flow.push(cs):
            failed += 1
        else:
            created += 1
    
    print('OK', flush=True)
    printi("""resetIPv4Flows.py:\n\tDeleted {rb}{deleted}{re} flows {wb}({con} config, {op} operational){we}\n\tCreated {rb}{created}{re} flows\n\tFailed  {rb}{failed}{re} flows""" \
        .format(con=_config, \
                op=deleted-_config, \
                deleted=deleted, \
                created=created, \
                failed=failed, \
                rb=("" + '\033[0m' + '\033[31m'), \
                re=("" +'\033[93m' + '\033[92m'), \
                wb='\033[0m', \
                we='\033[92m'))

if __name__ == '__main__':  
    cs = Controller('localhost', 'admin', 'admin')
    topo = Topology()
    topo.requestData(cs)      
    resetIPv4Flows(cs, topo)
