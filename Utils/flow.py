from controller import Controller

class SimpleFlow:
    def __init__(self):
        self.fSwitch = None
        self.fTbl = 0   
        self.fId = 0    
        self.fPri = 100   
        self.fMatches = []
        self.fActions = []
        
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
        self.fActions.append(data)
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
            _action = {"order": aOrder}
            aOrder += 1
            _action.update(action)
            _actions.append(_action)
        res["flow"][0]["instructions"] = {"instruction": [{"order": 0, 
                                          "apply-actions": {"action": _actions}}]}           
            
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
    def createActionOutputToPort(port, maxLength=65535):
       res = {"output-action": { "output-node-connector": port, "max-length": maxLength }}
       return res

       
