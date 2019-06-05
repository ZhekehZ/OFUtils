from . controller import *
import re

class Node:
    def __init__(self, nId, nTp):
        self.nConnections = []
        self.nId = nId
        self.nTp = nTp

    def addConnection(self, pNode, port):
        self.nConnections.append((pNode, port))

class Leaf(Node):
    def __init__(self, nId, nTp, nAddresses):
        super().__init__(nId, nTp)
        self.nAddresses = nAddresses

class Topology:
    def __init__(self):
        self.nodes = dict()
        self.topoJson = None
        self.invJson = None
        self.dataReady = False

    def getElemByRef(self, ref):
        if not self.dataReady:
            raise error("REQUEST DATA FIRST")
            
        matchDict = r'^\/([^:]*):([^\/\[]*)(.*)'
        machArray = r"^\[([^:]*):([^\/\[=]*)='([^']*)'\](.*)" 
        res = self.invJson        
        while len(ref) > 0:
            mt = re.match(matchDict, ref)        
            if (mt):
                res = res[mt.group(2)]  
                ref = mt.group(3)  
            mt = re.match(machArray, ref)       
            if (mt):
                res = [i for i in res if i[mt.group(2)] == mt.group(3)][0]
                ref = mt.group(4)  
        return res
        
    def macToIp(self, mac):
        for n in self.nodes.values():
            if type(n) == Leaf:
                if n.nAddresses[0][0] == mac:
                    return n.nAddresses[0][1]
        return "0.0.0.0"     

    def requestData(self, cs):
        self.nodes = dict()
        self.topoJson = cs.request("network-topology:network-topology/")
        self.invJson = cs.request("opendaylight-inventory:nodes/")
        self.dataReady = True
        
        if not self.topoJson:
            raise error("Error connecting to OpenDayLight.")
        
        for topo in self.topoJson['network-topology']['topology']:
            for node in topo['node']:
                inv = node.get('opendaylight-topology-inventory:inventory-node-ref')
                nTp = node['termination-point']
                nId = node['node-id']
                if inv:
                    self.nodes[nId] = Node(nId, nTp)
                else:
                    nAddresses = [(a['mac'], a['ip']) for a in node['host-tracker-service:addresses']]
                    self.nodes[nId] = Leaf(nId, nTp, nAddresses)
            for link in topo['link']:
                src = (link['source']['source-node'], link['source']['source-tp'])
                dst = (link['destination']['dest-node'], link['destination']['dest-tp'])
                port = -1
                if (type(self.nodes[src[0]]) == Node):
                    loc = "opendaylight-topology-inventory:inventory-node-connector-ref"
                    ref = [e[loc] for e in self.nodes[src[0]].nTp if e['tp-id'] == src[1]][0]
                    port = self.getElemByRef(ref)['flow-node-inventory:port-number']
                self.nodes[src[0]].addConnection(self.nodes[dst[0]], port)



#test
if __name__ == "__main__":
    used = set()
    def dfs(node, pre, portinfo):
        used.add(node.nId)
        nc = node.nConnections
        print(pre + ('port:' + portinfo + '-> ' if len(portinfo) else '') + node.nId)
        for i in range(len(nc)):
            next = nc[i][0]
            port = nc[i][1] 
            if not next.nId in used: 
                dfs(next, pre + ('              ' if len(portinfo) else '     '), str(port))


    cs = Controller('localhost', 'admin', 'admin')
    t = Topology()
    t.requestData(cs)
    node = [e for e in t.nodes.values() if type(e) == Node][0]
    dfs(node, '', '')
