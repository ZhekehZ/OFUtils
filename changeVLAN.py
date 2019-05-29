from Utils import *

def changeVLAN(cs, topo, ip, vlanFrom, vlanTo, vlans = None):
    host = None
    if not vlans: 
        vlans = {}
    for node in topo.nodes.values():
        if type(node) == Leaf and node.nAddresses[0][1] == ip:
            host = node

    if not host:
        exit("WRONG IP: %s" % ip)

    switch = host.nConnections[0][0]

    mac, ip = host.nAddresses[0]
    print("Host:\r\n\tIP: %s\r\n\tMAC: %s" % (ip, mac))
    print("Switch:\r\n\tName: %s" % switch.nId)

    vs = {}
    #print(vlans)
    if not (switch.nId in vlans.keys()):
        vlans[switch.nId] = {} 
    vlans[switch.nId][mac] = {"vlan_real": vlanFrom, "vlan_fake": vlanTo}
    if switch.nId in vlans.keys():
        vs = vlans[switch.nId]

    FM = flowManager()
    FM.requestData(cs)
    
    for fl in FM.getSwitchTableFlowList(switch.nId, 0):
        if fl['flow']['id'].startswith(str(switch.nId) + "_" + ip + "_arp"):
            FM.removeFlow(cs, switch.nId, 0, fl['flow']['id'])

    count, succ = 0, 0
    
    arpflowin = SimpleFlow().withId(str(switch.nId) + "_" + ip + "_arp_vlan_in") \
                          .withPri(1000) \
                          .withTbl(0) \
                          .withSwitch(switch.nId) \
                          .addMatch(SimpleFlow.createMatchVLAN(vlanTo)) \
                          .addMatch(SimpleFlow.createMatchEthernetType(2054)) \
                          .addMatch(SimpleFlow.createMatchArpTargetTransportAddress(ip)) \
                          .addAction(SimpleFlow.createActionNormal()) \
                          .addAction(SimpleFlow.createActionSetVLAN(vlanFrom)) 
    arpflowout = SimpleFlow().withId(str(switch.nId) + "_" + ip + "_arp_vlan_out") \
                          .withPri(1000) \
                          .withTbl(0) \
                          .withSwitch(switch.nId) \
                          .addMatch(SimpleFlow.createMatchVLAN(vlanFrom)) \
                          .addMatch(SimpleFlow.createMatchEthernetType(2054)) \
                          .addMatch(SimpleFlow.createMatchArpSourceTransportAddress(ip)) \
                          .addAction(SimpleFlow.createActionNormal()) \
                          .addAction(SimpleFlow.createActionSetVLAN(vlanTo))
    succ += arpflowin.push(cs) + arpflowout.push(cs)
    count += 2      
       
                          
    for arpmac in vs.keys():
        if arpmac != mac:
            if vs[arpmac]["vlan_fake"] == vlanTo:
                arpip = topo.macToIp(arpmac)
                arpf1 = SimpleFlow().withId(str(switch.nId) + "_" + ip + "_arp_->_" + arpip) \
                          .withPri(1001) \
                          .withTbl(0) \
                          .withSwitch(switch.nId) \
                          .addMatch(SimpleFlow.createMatchVLAN(vlanFrom)) \
                          .addMatch(SimpleFlow.createMatchEthernetType(2054)) \
                          .addMatch(SimpleFlow.createMatchArpTargetTransportAddress(arpip)) \
                          .addMatch(SimpleFlow.createMatchArpSourceTransportAddress(ip)) \
                          .addAction(SimpleFlow.createActionNormal()) \
                          .addAction(SimpleFlow.createActionSetVLAN(vs[arpmac]["vlan_real"]))
                arpf2 = SimpleFlow().withId(str(switch.nId) + "_" + arpip + "_arp_->_" + ip) \
                          .withPri(1001) \
                          .withTbl(0) \
                          .withSwitch(switch.nId) \
                          .addMatch(SimpleFlow.createMatchVLAN(vs[arpmac]["vlan_real"])) \
                          .addMatch(SimpleFlow.createMatchEthernetType(2054)) \
                          .addMatch(SimpleFlow.createMatchArpTargetTransportAddress(ip)) \
                          .addMatch(SimpleFlow.createMatchArpSourceTransportAddress(arpip)) \
                          .addAction(SimpleFlow.createActionNormal()) \
                          .addAction(SimpleFlow.createActionSetVLAN(vlanFrom))
                succ += arpf1.push(cs) + arpf2.push(cs)
                count += 2  
                   
    
    for flow in FM.getSwitchTableFlowList(switch.nId, 0):
        if FM.flowSrcDstMacIs(switch.nId, 0, flow['flow']['id'], 'src', mac):
            dst = FM.getSrcDstMac(switch.nId, 0, flow['flow']['id'], 'dst')
            vfr = vlanFrom
            vto = vlanTo
            if dst in vs.keys():
                if vto == vs[dst]["vlan_fake"]:
                    vto = vs[dst]["vlan_real"]
                    #print(vto)
            sflow = SimpleFlow.fromRAWFlow(switch.nId, flow['flow'])
            sflow.fActions = list(filter(lambda x: not SimpleFlow.isActionSetVLAN(x), sflow.fActions))
            sflow.fMatches = list(filter(lambda x: not SimpleFlow.isMatchVLAN(x),     sflow.fMatches))
            sflow.addMatch(SimpleFlow.createMatchVLAN(vfr)) \
                 .addAction(SimpleFlow.createActionSetVLAN(vto))
            succ += sflow.push(cs)
            count+=1
    for flow in FM.getSwitchTableFlowList(switch.nId, 0):
        if FM.flowSrcDstMacIs(switch.nId, 0, flow['flow']['id'], 'dst', mac):
            src = FM.getSrcDstMac(switch.nId, 0, flow['flow']['id'], 'src')
            vfr = vlanFrom
            vto = vlanTo
            if src in vs.keys():
                if vto == vs[src]["vlan_fake"]:
                    vto = vs[src]["vlan_real"]
                    #print(vto)
            sflow = SimpleFlow.fromRAWFlow(switch.nId, flow['flow'])
            sflow.fActions = list(filter(lambda x: not SimpleFlow.isActionSetVLAN(x), sflow.fActions))
            sflow.fMatches = list(filter(lambda x: not SimpleFlow.isMatchVLAN(x),     sflow.fMatches))
            sflow.addMatch(SimpleFlow.createMatchVLAN(vto)) \
                 .addAction(SimpleFlow.createActionSetVLAN(vfr))
            succ += sflow.push(cs)
            count+=1
    print("RESULT: %d/%d"%(succ, count))
    return vlans

if __name__ == '__main__':
    cs = Controller('localhost', 'admin', 'admin')
    topo = Topology()
    topo.requestData(cs)
    ip = input("IP>  ") # 10.0.0.1
    vlanFrom = input("VLAN FROM> ") # 100
    vlanTo = input("VLAN TO> ") # 101
    changeVLAN(cs, topo, ip, vlanFrom, vlanTo)

#vlanFlow = SimpleFlow()
#vlanFlow = vlanFlow.withId("VLAN-BAN-%s" % host.nAddresses[0][0]) \
#                   .withPri(100) \
#                   .withTbl(0) \
#                   .withSwitch(switch.nId) \
#                   .addMatch(SimpleFlow.createMatchMacSrc(host.nAddresses[0][0])) \
#                   .addMatch(SimpleFlow.createMatchVLAN(44)) \
#                   .addAction(SimpleFlow.createActionSetVLAN(vlan))
#                   
#print(vlanFlow.push(cs))



