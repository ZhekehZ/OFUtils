from Topology import *
from FlowUtils import *

class DFS:
    def findSrc(self, node, srcMAC):
        self.used.add(node.id)
        nc = node.connections

        if (type(node) == Leaf):
            if node.addr[0][0] == srcMAC:
                return node

        for i in range(len(nc)):
            next = nc[i][0]
            port = nc[i][1] 
            if not next.id in self.used:
                tmp = self.findSrc(next, srcMAC)
                if (tmp):
                    return tmp

    def makePath(self, node, dstMAC):
        self.used.add(node.id)  
        nc = node.connections

        if (type(node) == Leaf):
            if node.addr[0][0] == dstMAC:
                return True

        for i in range(len(nc)):
            next = nc[i][0]
            port = nc[i][1] 
            if not next.id in self.used:
                if self.makePath(next, dstMAC):
                    if (type(node) == Node):
                        self.path.append([node, port])
                    return True
        return False

    def __init__(self, topo, srcMAC, dstMAC):
        node = [e for e in topo.elements.values() if type(e) == Node][0]
        self.used, self.path = set(), []
        node = self.findSrc(node, srcMAC)
        self.used = set()
        self.res = self.makePath(node, dstMAC)

def makeFlow(cs, src, dst, priority=500, suffix="-flow(FM)"):
    t = Topology(cs)
    d = DFS(t, src, dst)
    
    succ, fail = 0, 0
    fl = simpleL2Flow(src, dst)
    for node_port in d.path:    
        flow = fl.withOPA(node_port[1]).withP(priority).withFID(str(node_port[0].id) + suffix).withTID(0)
        if pushFlow(cs, node_port[0].id, flow):
            succ += 1
        else:
            fail +=1

    print("FM> ADDING " + str(succ + fail) + " NEW FLOWS:")
    print("\tsuccess:  " + str(succ))
    print("\tfailure:  " + str(fail))
