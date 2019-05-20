#!/usr/bin/python3 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure, Text
from matplotlib.pyplot import Circle

import warnings
warnings.filterwarnings("ignore")

from tkinter import *
from tkinter import ttk
import networkx as nx
import numpy as np

from changeVLAN import *

import sys
sys.path.append(sys.path[0]+'/Utils')
from Utils.imports import *


class App:
    def __init__(self):
        self.__used = set()
        self.G = nx.Graph()  
        self.topo = Topology()
        self.selected = None
        
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
        self.fig.tight_layout()
        #self.ax = self.fig.add_subplot(111)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis('equal')
        #self.ax.set_title('Network graph')
        
        self.ax.set_axis_off()
        self.pos = nx.spectral_layout(self.G, scale=0.1)
        self.cs = cs
        
    def draw(self):
        self.ax.cla()
        self.ax.set_axis_off()
        colors = ['b' if n in self.switches else 'r' for n in self.G]
        nx.draw_networkx_nodes(self.G, self.pos, node_color=colors, node_size=500, alpha=0.5, ax=self.ax)
        nx.draw_networkx_edges(self.G, self.pos, width=1, alpha=0.5, edge_color='k', ax=self.ax)
        nx.draw_networkx_labels(self.G, self.pos, font_size=11, ax=self.ax)
        if self.selected:    
            x, y = self.pos[self.selected]
            stype = self.selected in self.switches
            circle = Circle((x, y), 0.01, lw=2, fill=False, ec="red" if stype else 'blue', linestyle='--')
            self.ax.add_artist(circle)
 
 



FONT= ("Verdana", 12)

window = Tk()
window.title("UI")
window.geometry('1200x600')  

cs = Controller('localhost', 'admin', 'admin')
vis = App()   
vis.requestData(cs) 

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

tab_control.pack(expand=1, fill='both') 

def update():
    vis.draw()
    canvas.draw()

update()

def infoToStr(info):
    res = ""
    for i in info:
        if (i[0] == -1):
            res += "➜  " + str(i[1]) + "\n"
        else:
            res += "port " + str(i[0]) + ":\n➜  " + str(i[1]) + "\n"
    return res
       
def checkMouse(ex, ey):
    dist = 100
    xl = vis.ax.get_xlim()
    yl = vis.ax.get_ylim()
    box = vis.ax.get_window_extent().transformed(vis.fig.dpi_scale_trans.inverted())
    width, height = box.width, box.height
    width *= vis.fig.dpi
    height *= vis.fig.dpi
    
    if ex > width:
        return
    
    nearest_node = None
    for n in vis.pos.keys():
        x,y = vis.pos[n]
        x = (x - xl[0]) / (xl[1] - xl[0])
        y = (y - yl[0]) / (yl[1] - yl[0])
        x = width*x
        y = height*(1-y)
        
        d = np.sqrt(abs(ex - x) ** 2 + abs(ey - y) ** 2)
        if d < dist:
            dist = d
            nearest_node = n
            #content = str(n).upper() + "\n\n"+ infoToStr(vis.G.nodes[n]['connections'])
   
    return nearest_node

def changeVlan(ip):
    def change(vf, vt, win):
        #print(vf, vt, ip)
        changeVLAN(cs, vis.topo, ip, vf, vt)
        a.destroy()
    a = Toplevel()
    x, y = window.winfo_x(), window.winfo_y()
    w, h = window.winfo_width(), window.winfo_height()   
    a.geometry("%dx%d+%d+%d" % (230, 70, x + w // 2, y + h // 2))
    #a.geometry('240x90')
    a.resizable(False, False)  
    lold = Label(a, text="OLD VLAN", justify=LEFT)
    lold.grid(row=0)
    eold = Entry(a, width=20)
    eold.grid(row=0, column=1)
    lnew = Label(a, text="NEW VLAN", justify=LEFT)
    lnew.grid(row=1)
    enew = Entry(a, width=20)
    enew.grid(row=1, column=1)
    Button(a, text="submit", width=20, command=lambda:change(eold.get(), enew.get(), a)).grid(row=2, column=0, columnspan=2)

class Popup:
    def __init__(self):
        self.menu = Menu(window.master)
        self.ip = None
        self.menu.add_command(label="Изменить VLAN", command=lambda:changeVlan(self.ip))
        #self.menu.add_separator()

    def show_menu_(self, event, nip):
        self.ip = nip
        self.menu.tk_popup(event.x_root, event.y_root)
pop = Popup()          
        
def b1(event):
    nn = checkMouse(event.x, event.y)
    vis.selected = nn
    content = str(nn).upper() + "\n\n"+ infoToStr(vis.G.nodes[nn]['connections']) if not nn is None else ''
    lblt['text'] = content   
    update()    
            
def b3(event):
    nn = checkMouse(event.x, event.y)
    vis.selected = nn
    if nn in vis.hosts:
        pop.show_menu_(event, vis.topo.nodes[nn].nAddresses[0][1])
    update()

def move(event):
    update()
    x = event.x
    y = event.y
    s = "Движение мышью {}x{}".format(x, y)
    window.title(s)

window.bind('<Button-1>', b1)
window.bind('<Button-3>', b3)
#window.bind('<Motion>', move)



window.mainloop()
