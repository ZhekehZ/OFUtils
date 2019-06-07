import Utils
from tkinter import *
from tkinter import ttk

from App.netGraph import NetGraphFrame, graphLogic
from App.flowModifier import FlowModFrame
from App.groupModifier import GroupModFrame
from App.UtilsPopup import Popup

import warnings
warnings.filterwarnings("ignore")

FONT_A = ("Verdana", 12)


class MainWindow(Tk):
    def __init__(self, vlanLoc):
        Tk.__init__(self)
        self.title("UI")
        self.geometry('1050x600') 
        tab_control = ttk.Notebook(self)
        
        cs = Utils.Controller('localhost', 'admin', 'admin')
        topo = Utils.Topology()
        FM = Utils.flowManager()
        FM.requestData(cs)
        self.du = Utils.DU()
        self.du.start(cs)
        
        self.popup = Popup(self, cs, topo, vlanLoc)
        
        self.tab1Log = graphLogic(cs, topo, self.du)
         
        self.tab1 = NetGraphFrame(tab_control, self.popup.getVlans())
        self.tab2 = FlowModFrame(tab_control, cs, FM)  
        self.tab3 = GroupModFrame(tab_control, cs, FM)  
        self.tab1.drawNetGraph(self.tab1Log)
     
        tab_control.pack(expand=1, fill=BOTH) 
        
        
        
        def buttonClick(event):
            params = (
                self.tab1.ax.get_xlim(),
                self.tab1.ax.get_ylim(),
                self.tab1.ax.get_window_extent().transformed(self.tab1.fig.dpi_scale_trans.inverted()),
                self.tab1.fig.dpi,
                self.tab1.pos
            )
            nn = self.tab1Log.checkMouse(event.x, event.y, *params)
            self.tab1Log.selected = nn
            self.update(True)
            return nn
            
        def onGCkick(event):
            nn = buttonClick(event)
            self.tab1.updateInfo(self.tab1Log.getConnections(nn), nn, self.tab1Log.topo)
            if nn and type(self.tab1Log.topo.nodes[nn]) == Utils.Node:
                self.tab2.setSwitch(nn)
                self.tab3.setSwitch(nn)
                
        def onCallMenu(event):
            nn = buttonClick(event)
            if nn and type(self.tab1Log.topo.nodes[nn]) == Utils.Leaf:
                addresses = self.tab1Log.topo.nodes[nn].nAddresses[0]
                self.popup.show(event, addresses[1], addresses[0])
                
        self.tab1.registerOnClick(onGCkick)
        self.tab1.registerOnClick2(onCallMenu)
        
            
        
    def update(self, force=False):
        if force or self.du.getTopoChanged():
            self.tab1Log.update()
            self.tab1.drawNetGraph(self.tab1Log)
            
        if force or self.du.getInvChanged():
            self.tab2.update()
            self.tab3.update()
        
    def run(self):
        def autoupdater():
            self.update()
            self.after(2000, autoupdater)
        self.update(True)
        self.after(0, autoupdater)

        self.mainloop()
        


