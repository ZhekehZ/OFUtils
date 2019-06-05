from tkinter import *
from changeVLAN import changeVLAN
import Utils
import os
import json

FONT_A = ("Verdana", 12)

class VLANChanger:
    def __init__(self, cs, topo, window, vlansloc):
        self.a = None
        self.topo = topo
        self.window = window
        self.cs = cs
        self.vlansloc = vlansloc
        self.vlans = dict()
        if os.path.exists(vlansloc):
            self.vlans = dict(json.load(open(vlansloc)))
    
    def saveData(self):
        with open(self.vlansloc, 'w') as outfile:
            json.dump(self.vlans, outfile)
    
    def change(self, vf, vt, ip):
        vlans = changeVLAN(self.cs, self.topo, ip, vf, vt, self.vlans)
        self.saveData()
        if self.a:
            self.a.destroy()
        
    def create(self, ip):
        self.a = Toplevel()
        self.a.title("chVLAN %s"%ip)
        x, y = self.window.winfo_x(), self.window.winfo_y()
        w, h = self.window.winfo_width(), self.window.winfo_height()   
        self.a.geometry("%dx%d+%d+%d" % (230, 70, x + w // 2, y + h // 2))
        #a.geometry('240x90')
        self.a.resizable(False, False)  
        lold = Label(self.a, text="ORIGIN VLAN", justify=LEFT)
        lold.grid(row=0)
        eold = Entry(self.a, width=20)
        eold.grid(row=0, column=1)
        lnew = Label(self.a, text="NEW VLAN", justify=LEFT)
        lnew.grid(row=1)
        enew = Entry(self.a, width=20)
        enew.grid(row=1, column=1)
        Button(self.a, text="submit", width=20, command=lambda:self.change(eold.get(), enew.get(), ip)).grid(row=2, column=0, columnspan=2)

class pathCreator:
    def __init__(self, cs, topo, window):
        self.mac1 = None
        self.mac2 = None
        self.ip1 = None
        self.ip2 = None
        self.topo = topo
        self.cs = cs
        self.a = None
        self.window = window
        
    def make(self):
        Utils.pushFlow(self.cs, self.topo, self.mac1, self.mac2)
        Utils.pushFlow(self.cs, self.topo, self.mac2, self.mac1)
        if self.a:
            self.a.destroy()
            self.mac1 = None
            self.mac2 = None
            self.ip1 = None
            self.ip2 = None    
        
    def create(self, ip, mac):
        if not self.mac1:
            self.mac1 = mac
            self.ip1 = ip
        else:
            self.mac2 = mac
            self.ip2 = ip
            
            self.a = Toplevel()
            self.a.title("make path")
            x, y = self.window.winfo_x(), self.window.winfo_y()
            w, h = self.window.winfo_width(), self.window.winfo_height()   
            self.a.geometry("%dx%d+%d+%d" % (230, 100, x + w // 2, y + h // 2))
            self.a.resizable(False, False)  
            lbel = Label(self.a, text="path %s <---> %s" % (self.ip1, self.ip2), justify=CENTER, font=FONT_A)
            lbel.grid(row=0)
            lold = Label(self.a, text="MAC_1: %s"%self.mac1, justify=CENTER, font=FONT_A)
            lold.grid(row=3)
            lnew = Label(self.a, text="MAC_2: %s"%self.mac2, justify=CENTER, font=FONT_A)
            lnew.grid(row=4)
            Button(self.a, text="submit", width=20, command=lambda:self.make()).grid(row=5)

class Popup(Menu):
    def __init__(self, parent, cs, topo, vlansloc):
        Menu.__init__(self, parent.master)
        self.ip = None
        self.mac = None
        self.vlanChanger = VLANChanger(cs, topo, parent, vlansloc)
        self.pathCreator = pathCreator(cs, topo, parent)
        self.add_command(label="Change VLAN", command=lambda:self.vlanChanger.create(self.ip))
        self.add_command(label="Make path", command=lambda:self.pathCreator.create(self.ip, self.mac))
        #self.menu.add_separator()

    def show(self, event, nip, mac):
        self.ip = nip
        self.mac = mac
        self.tk_popup(event.x_root, event.y_root) 
        
    def getVlans(self):
        return self.vlanChanger.vlans      
