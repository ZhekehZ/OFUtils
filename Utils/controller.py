import re
import requests

def error(s):
    return Exception('\033[91m' + s + '\033[0m')
    
def printe(s):
    print('\033[93m' + s + '\033[0m')

class Controller():
    def __init__(self, ip, user, password):
        ipMatch = re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip)
        
        if ipMatch: 
            raise error("WRONG IP ADDRESS")
        
        self.ip = ip
        self.user = user
        self.password = password
        
        
    def request(self, loc, operational=True):
        mode = "operational" if operational else "config"
        url = "http://%s:8181/restconf/%s/%s" % (self.ip, mode, loc)
        
        try:
            result = requests.get(url, auth=(self.user, self.password))
            return result.json()
        except:
            printe( "ERROR LOADING DATA" )
            return None
        
        
    def put(self, loc, data, operational=False):
        mode = "operational" if operational else "config"
        url = "http://%s:8181/restconf/%s/%s" % (self.ip, mode, loc)
        
        try:
            requests.put(url, auth=(self.user, self.password), json=data)
            return True
        except:
            printe( "ERROR LOADING DATA" )
            return False
            
        
        
