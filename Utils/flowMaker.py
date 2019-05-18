from flow import *
from topology import *

def __dfs(topo, node, dst, used, path):
    used.add(node.nId)
    
    if type(node) == Leaf:
        if node == dst:
            return True
    
    for (next, port) in node.nConnections:
        if not next.nId in used:
            if __dfs(topo, next, dst, used, path):
                if type(node) == Node:
                    path.append((node, port))
                return True
    return False
    

def getPath(topo, src, dst):
    pSrc, pDst = None, None    
    for node in topo.nodes.values():
        if type(node) == Leaf:
            for addr in node.nAddresses:
                if addr[0] == src:
                    pSrc = node
                if addr[0] == dst:
                    pDst = node
    if pDst == pSrc:
        return []
        
    path = []
    __dfs(topo=topo, node=pSrc, dst=pDst, used=set(), path=path)
    return path


def pushFlow(cs, topo, src, dst, flow=None, suffix="-flow(FM)"):
    if not flow:
        flow = SimpleFlow()
    flow.resetMatches().addMatch(SimpleFlow.createMatchL2(src, dst))
    path = getPath(topo, src, dst)
    
    fail = 0 # stats
    for (node, port) in path:
        flowId = str(node.nId) + "-( " + src + " -> " + dst + ") " + suffix
        action = SimpleFlow.createActionOutputToPort(port)
        flow.resetActions().addAction(action).withSwitch(node.nId)
        flow.withId(flowId)
        if not flow.push(cs):
            fail += 1
    #print("FM> ADDING " + str(len(path)) + " NEW FLOWS:")
    #print("\tsuccess:  " + str(len(path) - fail))
    #print("\tfailure:  " + str(fail))         
    return (len(path) - fail, fail)  
        
        
        
 
