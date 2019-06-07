from . controller import *
from json2xml import json2xml

class flowManager:
    def __init__(self):
        self.raw_flow_tables = dict()
        self.raw_group_tables = dict()
        
    @staticmethod
    def __findById(jsData, switch, table, flowId):
        for s in jsData:
            if s['id'] == switch:
                for t in s['flow-node-inventory:table']:
                    if t['id'] == table and 'flow' in t.keys():
                        for f in t['flow']:
                            if f['id'] == flowId:
                                return True
        return False
    
    def flowIsIPv4(self, switch, table, flowId):
        if flowId in self.getSwitchTableFlowList(switch, table):
            return False
        flows = self.raw_flow_tables[switch][table]
        flow = [f['flow'] for f in flows if f['flow']['id'] == flowId][0]
        if not 'match' in flow.keys():
            return False    
        if not 'ethernet-match' in flow['match'].keys():
            return False         
        if not 'ethernet-type' in flow['match']['ethernet-match'].keys():
            if 'ethernet-source' in flow['match']['ethernet-match'].keys() and \
               'ethernet-destination' in flow['match']['ethernet-match'].keys():
                return True
        return str(flow['match']['ethernet-match']['ethernet-type']['type']) == "2048"  
        
        
    def flowIsInPortMatch(self, switch, table, flowId):
        if flowId in self.getSwitchTableFlowList(switch, table):
            return False
        flows = self.raw_flow_tables[switch][table]
        flow = [f['flow'] for f in flows if f['flow']['id'] == flowId][0]
        if not 'match' in flow.keys():
            return False
        return 'in-port' in flow['match'].keys()
        
    def flowSrcDstMacIs(self, switch, table, flowId, kind, addr):
        kind = 'ethernet-source' if kind == 'src' else 'ethernet-destination'
        if not self.flowIsIPv4(switch, table, flowId):
            return False
        flows = self.raw_flow_tables[switch][table]
        flow = [f['flow'] for f in flows if f['flow']['id'] == flowId][0]
        ethMatch = flow['match']['ethernet-match']
        if not kind in flow['match']['ethernet-match'].keys():
            return False
        else:
            return str(flow['match']['ethernet-match'][kind]['address']) == addr
   
    def getSrcDstMac(self, switch, table, flowId, kind):
        kind = 'ethernet-source' if kind == 'src' else 'ethernet-destination'
        if not self.flowIsIPv4(switch, table, flowId):
            return -1
        flows = self.raw_flow_tables[switch][table]
        flow = [f['flow'] for f in flows if f['flow']['id'] == flowId][0]
        ethMatch = flow['match']['ethernet-match']
        if not kind in flow['match']['ethernet-match'].keys():
            return -1
        else:
            return str(flow['match']['ethernet-match'][kind]['address'])   
        
    def requestData(self, cs):
        dataJson = cs.request("opendaylight-inventory:nodes", True)['nodes']['node'] #operational datastore
        configJson = cs.request("opendaylight-inventory:nodes", False)['nodes']['node'] #config datastore
        
        for switchData in dataJson:
            tables = switchData['flow-node-inventory:table']
            parsed_tables = {}
            for table in tables:
                if 'flow' in table.keys():
                    parsed_tables[table['id']] = \
                        [ {'flow'    :f, \
                           'isConfig':flowManager.__findById(configJson, switchData['id'], table['id'], f['id'])} \
                        for f in table['flow']]
            self.raw_flow_tables[switchData['id']] = parsed_tables
            
            parsed_groups = {}
            if 'flow-node-inventory:group' in switchData.keys():
                groups = switchData['flow-node-inventory:group']
                for group in groups:
                    parsed_groups[group['group-id']] = \
                        [ {'flow-node-inventory:group':group}]
            self.raw_group_tables[switchData['id']] = parsed_groups 
        
        
    def getSwitchList(self):
        if not self.raw_flow_tables:
            printe("FM: REQUEST DATA FIRST")
            return []
        return list(self.raw_flow_tables.keys())
        
    def getSwitchTableList(self, switch):
        if not switch in self.getSwitchList():
            return []
        return list(self.raw_flow_tables[switch].keys())
        
    def getSwitchTableFlowList(self, switch, table):
        if not table in self.getSwitchTableList(switch):
            return []
        return list(self.raw_flow_tables[switch][table])
        
    def getSwitchGroupList(self, switch):
        if not switch in self.getSwitchList():
            return []
        #print(*[(a, len(self.raw_group_tables[a])) for a in self.raw_group_tables.keys()])
        return list(self.raw_group_tables[switch].values())
        
    def removeFlow(self, cs, switch, table, flow):
        flowData = [f for f in self.getSwitchTableFlowList(switch, table) if f['flow']['id'] == flow]
        if len(flowData) == 0:
            return None
        flowData = flowData[0]
        if flowData['isConfig']:
            cs.deleteConfig("opendaylight-inventory:nodes/node/%s/table/%s/flow/%s" % (str(switch), str(table), str(flow)))
        else:
            match = json2xml.Json2xml(flowData['flow']['match'], wrapper="match").to_xml()
            cs.deleteOperational(switch, table, flowData['flow']['priority'], match)
    
    def removeGroup(self, cs, switch, group):
        groupData = []
        for g in self.getSwitchGroupList(switch):
            g = g[0]
            if g['flow-node-inventory:group']['group-id'] == group:
                groupData.append(g)
        if len(groupData) == 0:
            return None
        groupData = groupData[0]
        cs.deleteConfig("opendaylight-inventory:nodes/node/%s/group/%s" % (str(switch), str(group)))
    
#test
if __name__ == "__main__":
    cs = Controller('localhost', 'admin', 'admin')
    FM = flowManager()
    FM.requestData(cs)
    FM.removeFlow(cs, 'openflow:7', 0, 'L2switch-31')
    
    
    FM.requestData(cs)
    switches = FM.getSwitchList()
    for switch in switches:
        print("< %s >    table 0:" % switch)
        for f in FM.getSwitchTableFlowList(switch, 0):
            print("\t%s:\t%s" % ('     Config' if f['isConfig'] else 'Operational', f['flow']['id']))
            
    #flow = [f['flow'] for f in FM.getSwitchTableFlowList('openflow:5', 0) if f['flow']['id'] == "#UF$TABLE*0-226"][0]
    #print(flow)
