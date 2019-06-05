import threading
from websocket import create_connection
import base64
from . controller import *

invChanged = False
topoChanged = False
invLock = threading.Lock()
topoLock = threading.Lock()

def dataNotificationPicker(auth, url, inv):
    global invChanged
    global topoChanged
    global invLock
    global topoLock
    
    headers = {
        'Authorization': auth,
        'Content-Type': 'application/json',
    }
    while threading.main_thread().is_alive():
        ws = create_connection(url, headers=headers, timeout=1)
        try:
            result = ws.recv()
        except:
            continue
        if inv:
            with invLock:
                invChanged = True
        else:
            with topoLock:
                topoChanged = True

class DU:
    def __init__(self):
        pass
            
    def getInvChanged(self):
        global invChanged
        global invLock
        res = False
        with invLock:
            res = invChanged
            invChanged = False
        return res
            
    def getTopoChanged(self):
        global topoChanged
        global topoLock
        res = False
        with topoLock:
            res = topoChanged
            topoChanged = False
        return res
            
    def start(self, cs):
        odlInvSubscribe = """<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote">
                      <path xmlns:a="urn:opendaylight:inventory">/a:nodes</path>
                      <datastore xmlns="urn:sal:restconf:event:subscription">CONFIGURATION</datastore>
                      <scope xmlns="urn:sal:restconf:event:subscription">BASE</scope>  
                    </input>
                  """
        urlOdlInvWSName = cs.subscribeEvent('sal-remote:create-data-change-event-subscription', odlInvSubscribe)["output"]["stream-name"]
        urlOdlInvWS = cs.getStream(urlOdlInvWSName)["location"]
        
        odlTopoSubscribe = """<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote">
                      <path xmlns:a="urn:TBD:params:xml:ns:yang:network-topology">/a:network-topology</path>
                      <datastore xmlns="urn:sal:restconf:event:subscription">OPERATIONAL</datastore>
                      <scope xmlns="urn:sal:restconf:event:subscription">BASE</scope>  
                    </input>
                  """
        odlTopoWSName = cs.subscribeEvent('sal-remote:create-data-change-event-subscription', odlTopoSubscribe)["output"]["stream-name"]
        odlTopoWS = cs.getStream(odlTopoWSName)["location"]
        
        auth = base64.b64encode(bytes("Basic %s:%s"%(cs.user, cs.password), 'utf-8'))
        
        threadOdlInv = threading.Thread(target=dataNotificationPicker, args=(auth, urlOdlInvWS, True))
        threadTopo = threading.Thread(target=dataNotificationPicker, args=(auth, odlTopoWS, False))
        thread1 = threadOdlInv.start()
        thread2 = threadTopo.start()
   
   
    
#test
if __name__=='__main__':
    import time
    cs = Controller('localhost', 'admin', 'admin')
    du = DU()
    du.start(cs)
    print("ready")
    while(1):
        time.sleep(1)
        if du.getInvChanged():
            print('invChanged')
            
        if du.getTopoChanged():
            print('topoChanged')
