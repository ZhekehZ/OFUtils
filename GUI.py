#!/usr/bin/python3 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure, Text

from tkinter import *
from tkinter import ttk
import networkx as nx
import numpy as np

import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *


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
        self.fig = Figure()
        #self.ax = self.fig.add_subplot(111)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        #self.ax.set_title('Network graph')
        self.fig.tight_layout()
        self.ax.set_axis_off()
        self.pos = nx.spectral_layout(self.G, scale=0.1)
        self.cs = cs
        
    def draw(self):
        colors = []
        
        def isSel(n, m):
            if len(self.selected) < m:
                return False
            else:
                return self.selected[m-1] == n
                
        for n in self.G:
            colors.append('b' if n in self.switches else 'g' if isSel(n, 1) else 'y' if isSel(n, 2) else 'r')
        nx.draw_networkx_nodes(self.G, self.pos, node_color=colors, node_size=500, alpha=0.5, ax=self.ax)
        nx.draw_networkx_edges(self.G, self.pos, width=1, alpha=0.5, edge_color='k', ax=self.ax)
        nx.draw_networkx_labels(self.G, self.pos, font_size=11, ax=self.ax)

 
 



FONT= ("Verdana", 12)

window = Tk()
window.title("UI")
window.geometry('1200x600')  

cs = Controller('localhost', 'admin', 'admin')
vis = App()   
vis.requestData(cs) 
vis.draw()

tab_control = ttk.Notebook(window)  
"""
    TAB 1
"""
tab1 = ttk.Frame(tab_control)  
tab_control.add(tab1, text='График') 

canvas = FigureCanvasTkAgg(vis.fig, tab1)
canvas.draw()
canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
#toolbar = NavigationToolbar2Tk(canvas, tab1)
#toolbar.update()
canvas._tkcanvas.pack(side=LEFT, fill=BOTH, expand=True)

lblt = Label(tab1,  width=50, height=15, text="", justify=LEFT, font=FONT)
lblt.pack(side=TOP, fill=X, expand=True)
lblt2 = Label(tab1,  width=50, height=20, text="-"*250)
lblt2.pack(side=TOP, fill=X, expand=True)


"""
    TAB 2
"""
tab2 = ttk.Frame(tab_control)  
tab_control.add(tab2, text='Информация')  

lbl2 = Label(tab2, text='Информация какая-то')
lbl2.pack(pady=10,padx=10)


def infoToStr(info):
    res = ""
    for i in info:
        if (i[0] == -1):
            res += "➜  " + str(i[1]) + "\n"
        else:
            res += "port " + str(i[0]) + ":\n➜  " + str(i[1]) + "\n"
    return res
       
        
def b1(event):
    dist = 100
    xl = vis.ax.get_xlim()
    yl = vis.ax.get_ylim()
    box = vis.ax.get_window_extent().transformed(vis.fig.dpi_scale_trans.inverted())
    width, height = box.width, box.height
    width *= vis.fig.dpi
    height *= vis.fig.dpi
    
    if event.x > width:
        return
    
    content = ""
    for n in vis.pos.keys():
        x,y = vis.pos[n]
        x = (x - xl[0]) / (xl[1] - xl[0])
        y = (y - yl[0]) / (yl[1] - yl[0])
        x = width*x
        y = height*(1-y)
        
        d = np.sqrt(abs(event.x - x) ** 2 + abs(event.y - y) ** 2)
        if d < dist:
            dist = d
            content = str(n).upper() + "\n\n"+ infoToStr(vis.G.nodes[n]['connections'])
    lblt['text'] = content        
            
#def b3(event):
#    window.title("Правая кнопка мыши")
#def move(event):
#    x = event.x
#    y = event.y
#    s = "Движение мышью {}x{}".format(x, y)
#    window.title(s)

window.bind('<Button-1>', b1)
#window.bind('<Button-3>', b3)
#window.bind('<Motion>', move)

tab_control.pack(expand=1, fill='both') 
window.mainloop()
