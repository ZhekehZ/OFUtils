from . controller import *

class SimpleFlow:
    def __init__(self):
        self.fSwitch = None
        self.fTbl = 0   
        self.fId = 0    
        self.fPri = 100   
        self.fMatches = []
        self.fActions = []
        self.fOther = {}
        
    def withSwitch(self, s):
        self.fSwitch = s
        return self
        
    def withTbl(self, tid):
        self.fTbl = tid
        return self
        
    def withId(self, fid):
        self.fId = fid
        return self
        
    def withPri(self, p):
        self.fPri = p
        return self
        
    def addMatch(self, data):
        self.fMatches.append(data)
        return self
        
    def addAction(self, data):
        self.fActions = [data] + self.fActions
        #self.fActions.append(data)
        return self
        
    def resetActions(self):
        self.fActions = []
        return self
    
    def resetMatches(self):
        self.fMatches = []
        return self    
        
    def toJson(self):
        res = {"flow": [{}]}
        res["flow"][0]["table_id"] = self.fTbl
        res["flow"][0]["id"] = self.fId
        res["flow"][0]["priority"] = self.fPri
        
        res["flow"][0]["match"] = {}
        for m in self.fMatches:
            res["flow"][0]["match"].update(m)
            
        _actions = []
        aOrder = 0
        for action in self.fActions:
            _action = action.copy()
            _action["order"] = aOrder
            aOrder += 1
            _actions.append(_action)
        res["flow"][0]["instructions"] = {"instruction": [{"order": 0, 
                                          "apply-actions": {"action": _actions}}]}           
        res["flow"][0].update(self.fOther)    
        return res
        
        
        
    def push(self, cs):
        url = "opendaylight-inventory:nodes/node/%s/table/%d/flow/%s" % (self.fSwitch, self.fTbl, self.fId)
        return cs.put(url, self.toJson())    
        
        
        
    @staticmethod
    def createMatchL2(src, dst):
        res = { "ethernet-match": {
                    "ethernet-type": { "type": "2048" },
                    "ethernet-destination": { "address": dst },
                    "ethernet-source": { "address": src }
              } }
        return res
        
    @staticmethod
    def createMatchARP():
        res = { "ethernet-match": { "ethernet-type": { "type": "2054" } } }
        return res
        
    @staticmethod
    def createMatchVLAN(vlanId):
        res = {"vlan-match": { "vlan-id": { "vlan-id": vlanId, "vlan-id-present": "true"}}}
        return res

    @staticmethod
    def createActionDrop():
        res = { "drop-action": {} }
        return res                        
        
    @staticmethod
    def createMatchMacSrc(src):
        res = { "ethernet-match": {
                    "ethernet-type": { "type": "2048" },
                    "ethernet-source": { "address": src }
              } }
        return res
        
    @staticmethod
    def createActionOutputToPort(port, maxLength=65535):
       res = {"output-action": { "output-node-connector": port, "max-length": maxLength }}
       return res
       
    @staticmethod
    def createActionNormal(maxLength=65535):
        return SimpleFlow.createActionOutputToPort("NORMAL", maxLength)
       
    @staticmethod
    def createActionSetVLAN(vlanId):
        res = {"set-field": { "vlan-match": { "vlan-id": { "vlan-id": str(vlanId), "vlan-id-present": "true" }}}}
        return res
        
    @staticmethod 
    def fromRAWFlow(switch, rFlow):
        rawFlow = rFlow.copy()
        sflow = SimpleFlow()
        sflow.fSwitch = switch
        sflow.fTbl = rawFlow['table_id']  
        sflow.fId = rawFlow['id']      
        sflow.fPri = rawFlow['priority']
        sflow.fMatches = []
        for match in rawFlow['match'].keys():
            sflow.fMatches.append({match : rawFlow['match'][match]})
           
        sflow.fActions = []
        if len(rawFlow['instructions']['instruction']):
            error("ERROR PARSE FLOW: NO MULTI-INSTRUCTION SUPPORT")
        for action in rawFlow['instructions']['instruction'][0]['apply-actions']['action']:
            action.pop('order', None)
            sflow.fActions.append(action)
       
        others = rawFlow.copy()
        others.pop("table_id", None)
        others.pop("id", None)
        others.pop("priority", None)
        others.pop("match", None)
        others.pop("instructions", None)

        sflow.fOther = others
        return sflow
       
