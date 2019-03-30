import requests
import json

class simpleL2Flow():
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def withOPA(self, port):
        # output port action
        self.port = port
        return self

    def withP(self, p):
        # priority
        self.p = p
        return self

    def withTID(self, table):
        # table id
        self.table = table
        return self

    def withFID(self, flow):
        # flow id
        self.flow = flow
        return self


    def toJson(self):
        res =   {
                    "flow": [
                        {
                            "table_id": self.table,
                            "id": self.flow,
                            "priority": self.p,
                            "match": {
                    			"ethernet-match": {
			                        "ethernet-type": {
				                        "type": "2048"
			                        },
			                        "ethernet-destination": {
				                        "address": self.dst
			                        },
			                        "ethernet-source": {
				                        "address": self.src
			                        }
		                        }
                            },
                            "instructions": {
	                            "instruction": [
                                    {
		                                "order": "0",
		                                "apply-actions": {
			                                "action": [
                                                {
				                                    "order": "0",
				                                    "output-action": {
					                                    "output-node-connector": self.port,
					                                    "max-length": "65535"
				                                    }
                                                }
			                                ]
		                                }
                                    }
	                            ]
                            }
                        }
                    ]
                }
        return res      

def pushFlow(cs, node, flow):
    settings = cs.settings
    user, password = settings['user'], settings['password']
    flowUrl = "http://%s:8181/restconf/config/opendaylight-inventory:nodes/node/%s/table/%d/flow/%s" % (settings['ip'], node, flow.table, flow.flow)

    try:
        topoRequest = requests.put(flowUrl, auth=(user, password), json=flow.toJson())
    except:
        return False
    return True     
