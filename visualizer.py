import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *
import networkx as nx
import numpy as np

from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
import matplotlib.patches as patches
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['toolbar'] = 'None'
    

class App:
    def __init__(self):
        self.__used = set()
        self.G = nx.Graph()  
        self.topo = Topology()
        self.selected = []
        
    def __fillGraph(self, node, port):
        self.__used.add(node.nId)
        self.G.add_node(node.nId, connections=[])
        for (next, port) in node.nConnections:
            self.G.nodes[node.nId]['connections'].append([port, next.nId])
            self.G.add_edge(node.nId, next.nId)
            if not next.nId in self.__used: 
                self.__fillGraph(next, str(port))

    def requestData(self, cs):
        self.topo.requestData(cs)
        self.hosts = [h.nId for h in self.topo.nodes.values() if type(h) == Leaf]
        self.switches = [s.nId for s in self.topo.nodes.values() if type(s) == Node]
        self.__fillGraph(self.topo.nodes[self.switches[0]], '')
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Network graph')
        self.pos = nx.spring_layout(self.G)
        self.txt = plt.text(-10, -10, '', fontsize=8)
        self.cs = cs
 
        

    def addFlow(self):
        if len(self.selected) == 0:
            return
        a, b = self.selected
        if (not a in self.switches) or (not b in self.switches):
            pushFlow(self.cs, self.topo, a[5:], b[5:])
        
    def draw(self):
        plt.clf()
        colors = []
        
        def isSel(n, m):
            if len(self.selected) < m:
                return False
            else:
                return self.selected[m-1] == n
                
        for n in self.G:
            colors.append('b' if n in self.switches else 'g' if isSel(n, 1) else 'y' if isSel(n, 2) else 'r')
        nx.draw_networkx_nodes(self.G, self.pos, node_color=colors, node_size=500, alpha=0.5)
        nx.draw_networkx_edges(self.G, self.pos, width=1, alpha=0.5, edge_color='k')
        nx.draw_networkx_labels(self.G, self.pos, font_size=11)
        plt.axis('off')
        plt.axis(xmin=-2, ymin=-2, xmax=2, ymax=2)
        
        


    def show(self):
        def infoToStr(info):
            res = ""
            for i in info:
                if (i[0] == -1):
                    res += "➜  " + str(i[1]) + "\n"
                else:
                    res += "port " + str(i[0]) + ":\n     ➜  " + str(i[1]) + "\n"
            return res   
    
        def onPick(event):
            if (not event.xdata) or (not event.ydata):
                 return
                 
            if (event.xdata < -1) and (event.xdata > -2) and (event.ydata < -1) and (event.ydata > -2):
                self.addFlow()
                
        
        
            drawText, textX, textY, content = False, 0, 0, ''
            maxdist = 0.1
            dist = maxdist
            for n in self.pos.keys():
                x,y = self.pos[n]
                d = np.sqrt(abs(event.xdata - x) ** 2 + abs(event.ydata - y) ** 2)
                if d < dist:
                    dist, drawText = d, True
                    textX, textY = event.xdata, event.ydata
                    content = infoToStr(self.G.nodes[n]['connections'])
                    self.G.nodes[n]
                    if len(self.selected) < 2:
                        self.selected.append(n)
                    else:
                        self.selected = [n]
            if self.txt: 
                self.txt.remove()
                self.txt = None
            if drawText:    
                self.txt = plt.text(textX, textY, content, fontsize=14, verticalalignment='top', 
                                    bbox=dict(boxstyle='round', facecolor='gray'))
            else:
                self.selected = []
            self.draw()
            self.fig.canvas.draw()
        self.fig.canvas.callbacks.connect('button_press_event', onPick) 
        
        self.draw()       
        plt.show()
        
     
cs = Controller('localhost', 'admin', 'admin')
vis = App()   
vis.requestData(cs)      
vis.show() 




