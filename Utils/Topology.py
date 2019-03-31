import requests
import re

class ControllerSettings():
    def __init__(self, ip, user, password):
        self.settings = {'ip':ip, 'user':user, 'password':password}

class Node:
    def __init__(self, _id, tp):
        self.connections = []
        self.id = _id
        self.tp = tp

    def connect(self, elem, outport):
        self.connections.append((elem, outport))

class Leaf:
    def __init__(self, _id, tp, addr):
        self.connections = []
        self.id = _id
        self.tp = tp
        self.addr = addr

    def connect(self, elem, outport):
        self.connections.append((elem, outport))

class Topology:
    def getElemByRef(self, invReq, ref):
        matchDict = r'^\/([^:]*):([^\/\[]*)(.*)'
        machArray = r"^\[([^:]*):([^\/\[=]*)='([^']*)'\](.*)" 
        res = invReq        
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

    def __init__(self, cs):
        settings = cs.settings
        topoUrl = "http://%s:8181/restconf/operational/network-topology:network-topology/" % settings['ip']
        invUrl = "http://%s:8181/restconf/operational/opendaylight-inventory:nodes/" % settings['ip']
        user, password = settings['user'], settings['password']

        try:
            topoRequest = requests.get(topoUrl, auth=(user, password))
            invRequest = requests.get(invUrl, auth=(user, password))
        except:
            print('Error loading data.'); return      

        topoJson = topoRequest.json()
        invJson = invRequest.json()
        
        for topology in topoJson['network-topology']['topology']:
            noderefs = dict()
            for node in topology['node']:
                inv = node.get('opendaylight-topology-inventory:inventory-node-ref')
                tp = node['termination-point']
                _id = node['node-id']
                if (inv):
                    # switch
                    ofSwitch = Node(_id, tp)
                    noderefs[_id] = ofSwitch
                else:
                    # host
                    addresses = [(addr['mac'], addr['ip']) for addr in node['host-tracker-service:addresses']]
                    host = Leaf(_id, tp, addresses)
                    noderefs[_id] = host
            
            for link in topology['link']:
                source = (link['source']['source-node'], link['source']['source-tp'])
                destination = (link['destination']['dest-node'], link['destination']['dest-tp'])

                port = -1
                if (type(noderefs[source[0]]) == Node):
                    ref = [e['opendaylight-topology-inventory:inventory-node-connector-ref'] for e in noderefs[source[0]].tp if e['tp-id'] == source[1]][0]
                    port = self.getElemByRef(invJson, ref)['flow-node-inventory:port-number']
                noderefs[source[0]].connect(noderefs[destination[0]], port)
        
            self.elements = noderefs



#test
if __name__ == "__main__":
    used = set()
    def dfs(node, pre, portinfo):
        used.add(node.id)
        nc = node.connections
        print(pre + ('port:' + portinfo + '-> ' if len(portinfo) else '') + node.id)
        for i in range(len(nc)):
            next = nc[i][0]
            port = nc[i][1] 
            if not next.id in used: 
                dfs(next, pre + ('              ' if len(portinfo) else '     '), str(port))


    cs = ControllerSettings('localhost', 'admin', 'admin')
    t = Topology(cs)
    node = [e for e in t.elements.values() if type(e) == Node][0]
    dfs(node, '', '')
