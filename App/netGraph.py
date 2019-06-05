from Utils import *

from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import Circle

from matplotlib.figure import Figure, Text
import networkx as nx
import numpy as np

FONT_A = ("Verdana", 12)

class graphLogic:
    @staticmethod
    def __nodeNameOptimizer(name):
        m = re.fullmatch(r"openflow:(\d+)", name)
        if m:
            res = 'of:*' + m.group(1)[-3:]
            return res
        m = re.fullmatch(("host:"+"([a-fA-F0-9]{2}):"*6)[:-1], name)    
        if m:
            res = 'h:\n*' + m.group(5) + ':' + m.group(6)
            return res
        return name

    def __fillGraph(self, node, port):
        self.__used.add(node.nId)
        self.graphRAW.add_node(node.nId, connections=[])
        self.labels[node.nId] = self.__nodeNameOptimizer(node.nId)
        for (next, port) in node.nConnections:
            self.graphRAW.nodes[node.nId]['connections'].append([port, next.nId])
            self.graphRAW.add_edge(node.nId, next.nId)
            if not next.nId in self.__used: 
                self.__fillGraph(next, str(port))

    def __init__(self, cs, topo, du):
        self.cs = cs
        self.topo = topo
        self.du = du
        self.graphRAW = nx.Graph() 
        self.selected = None
        self.labels = dict()
        self.__used = set()
        
        self.topo.requestData(self.cs)
        self.hosts = [h.nId for h in self.topo.nodes.values() if type(h) == Leaf]
        self.switches = [s.nId for s in self.topo.nodes.values() if type(s) == Node]
        self.__fillGraph(self.topo.nodes[self.switches[0]], '')
        
    def update(self):
        self.topo.requestData(self.cs)
        self.__used = set()
        self.hosts = [h.nId for h in self.topo.nodes.values() if type(h) == Leaf]
        self.switches = [s.nId for s in self.topo.nodes.values() if type(s) == Node]
        self.__fillGraph(self.topo.nodes[self.switches[0]], '')
    
    def checkMouse(self, ex, ey, xl, yl, box, dpi, pos):
        dist = 100
        width, height = box.width, box.height
        width *= dpi
        height *= dpi
        nearest_node = None
        for n in pos.keys():
            x, y = pos[n]
            x = (x - xl[0]) / (xl[1] - xl[0])
            y = (y - yl[0]) / (yl[1] - yl[0])
            x = width * x
            y = height * ( 1 - y)
            d = np.sqrt(abs(ex - x) ** 2 + abs(ey - y) ** 2)
            if d < dist:
                dist = d
                nearest_node = n
        return nearest_node

    def getConnections(self, node):
        return self.graphRAW.nodes[node]['connections']


class graphCanvas():
    def __init__(self, figure, parent):
        self.canvas = FigureCanvasTkAgg(figure, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().config(cursor='hand2')
    
    def pack(self, **kwargs):
        self.canvas.get_tk_widget().pack(**kwargs)
        
    def draw(self):
        self.canvas.draw()
        
    def registerOnClick(self, proc):
        self.canvas.get_tk_widget().bind('<Button-1>', proc)   
         
    def registerOnClick2(self, proc):
        self.canvas.get_tk_widget().bind('<Button-3>', proc)  

class infoFrame(LabelFrame):
    def __init__(self, parent, vlans):
        LabelFrame.__init__(self, parent, text="INFORMATION", bg='white')
        self.infoLabel = Label(self, anchor='nw', padx=30, pady=30, width=50, bg='white', 
                                text="Select any node", justify=LEFT, font=FONT_A)
        self.infoLabel.pack(side=LEFT, fill=Y, expand=1)
        self.vlans = vlans
        
    @staticmethod    
    def __infoToStr(info, node, topo, vlans):
        res = 'Name: ' + node.upper() + '\n\n' 
        node = topo.nodes[node]
        res += 'Type: ' + ( 'host' if type(node) == Leaf else 'switch') + '\n\n'   
        if (type(node) == Leaf):
            res += 'MAC-addr: ' + node.nAddresses[0][0] + '\n'
            res += 'IP-addr: ' + node.nAddresses[0][1] + '\n'
            res += '\n'
            res += 'Connected to: ' + info[0][1].upper()
            mac = node.nAddresses[0][0] 
            if info[0][1]:
                if info[0][1] in vlans.keys():
                    vs = vlans[info[0][1]]
                    if mac in vs:
                        res += "\n\n\nVLAN:\n    Device: \t%s"%vs[mac]["vlan_real"] + \
                                          "\n    Network: \t%s"%vs[mac]["vlan_fake"]
            return res   
        
        res += 'Connected to:\n'
        for i in info:
            res += "    [port %s]"%str(i[0]) + "  ➜  " + str(i[1]).upper() + "\n"
        return res    
        
    def updateInfo(self, con, nn, topo):
        self.infoLabel['text'] = self.__infoToStr(con, nn, topo, self.vlans) if not nn is None else 'Select any node'

class NetGraphFrame(Frame):
    def __init__(self, parent, vlans):
        Frame.__init__(self, parent)
        parent.add(self, text='NetGraph')
        
        self.fig = Figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_axis_off()
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('equal')
        self.ax.plot()
        
        self.pos = None
        
        self.nGraph = graphCanvas(self.fig, self)
        self.nGraph.pack(side=LEFT, fill=BOTH, expand=1)
        self.info = infoFrame(self, vlans)
        self.info.pack(side=TOP, fill=BOTH, expand=1)
    
    def registerOnClick(self, proc):
        self.nGraph.registerOnClick(proc)
        
    def registerOnClick2(self, proc):
        self.nGraph.registerOnClick2(proc)
        
    def updateInfo(self, con, nn, topo):
        self.info.updateInfo(con, nn, topo)
        
    def drawNetGraph(self, rawNet):
        self.ax.cla()
        colors = ['b' if n in rawNet.switches else 'r' for n in rawNet.graphRAW]
        self.pos = nx.spring_layout(rawNet.graphRAW, scale=0.1, seed=239, iterations=200, k=1)
        nx.draw_networkx_nodes(rawNet.graphRAW, self.pos, node_color=colors, node_size=500, alpha=0.5, ax=self.ax)
        nx.draw_networkx_edges(rawNet.graphRAW, self.pos, width=1, alpha=0.5, edge_color='k', ax=self.ax)
        nx.draw_networkx_labels(rawNet.graphRAW, self.pos, labels=rawNet.labels, font_size=11, ax=self.ax)
        if not (rawNet.selected in rawNet.hosts or rawNet.selected in rawNet.switches):
            rawNet.selected = None
        if rawNet.selected:    
            x, y = self.pos[rawNet.selected]
            stype = rawNet.selected in rawNet.switches
            circle = Circle((x, y), 0.01, lw=2, fill=False, ec="red" if stype else 'blue', linestyle='--')
            self.ax.add_artist(circle)
        self.nGraph.draw()
        
