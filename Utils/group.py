from . controller import *
from enum import Enum

class SimpleGroup:
    class GType(Enum):
        ALL = "group-all"
        SELECT = "group-select"

    def __init__(self):
        self.gSwitch = None  
        self.gId = 0   
        self.gName = "GROUP-0" 
        self.gType = self.GType.ALL
        self.gBuckets = []
        
    def withSwitch(self, s):
        self.gSwitch = s
        return self        
        
    def withId(self, gid):
        self.gId = gid
        return self
        
    def withName(self, name):
        self.gName = name
        return self
        
    def withType(self, t):
        self.gType = t
        return self
        
    def addBucket(self, bucket):
        self.gBuckets.append(bucket)
        return self
        
    def addAction(self, action, nBucket):
        if nBucket >= len(self.gBuckets):
            raise error("WRONG BUCKET NUM.")
        self.gBuckets[nBucket].append(action)
        return self    
        
    def toJson(self):
        groupStr = "flow-node-inventory:group"
        res = {groupStr: [{}]}
        res[groupStr][0]["group-id"] = self.gId
        res[groupStr][0]["group-name"] = self.gName
        res[groupStr][0]["group-type"] = self.gType.value
        res[groupStr][0]["barrier"] = False
        
        res[groupStr][0]["buckets"] = {"bucket":[]}
        _buckets = []
        bOrder = 0
        for bucket in self.gBuckets:
            _bucket = {"bucket-id": bOrder, "action": []}
            bOrder += 1
            aOrder = 0
            for action in bucket:
                _action = {"order": aOrder}
                aOrder += 1
                _action.update(action)
                _bucket["action"].append(_action)
            _buckets.append(_bucket)
        res[groupStr][0]["buckets"]["bucket"] = _buckets
   
        return res
        
    def push(self, cs):
        url = "opendaylight-inventory:nodes/node/%s/group/%d/" % (self.gSwitch, self.gId)
        return cs.put(url, self.toJson())    
        
    @staticmethod
    def createActionSetTTL(ttl):
        res = {"set-nw-ttl-action": { "nw-ttl": ttl }}
        return res
        
    @staticmethod
    def createActionOutputToPort(port, maxLength=65535):
       res = {"output-action": { "output-node-connector": port, "max-length": maxLength }}
       return res







       
