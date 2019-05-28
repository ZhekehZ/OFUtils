#!/usr/bin/python3 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure, Text
from matplotlib.pyplot import Circle

import json
import time

import warnings
warnings.filterwarnings("ignore")

from tkinter import *
from tkinter import ttk
import networkx as nx
import numpy as np

from changeVLAN import changeVLAN
from Utils import *


class App:
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

    def __init__(self):
        self.__used = set()
        self.G = nx.Graph()  
        self.topo = Topology()
        self.selected = None
        self.labels = dict()
        
    def __fillGraph(self, node, port):
        self.__used.add(node.nId)
        self.G.add_node(node.nId, connections=[])
        self.labels[node.nId] = App.__nodeNameOptimizer(node.nId)
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
        self.pos = nx.spring_layout(self.G, scale=0.1)
        self.cs = cs
        
    def draw(self):
        self.ax.cla()
        self.ax.set_axis_off()
        colors = ['b' if n in self.switches else 'r' for n in self.G]
        nx.draw_networkx_nodes(self.G, self.pos, node_color=colors, node_size=500, alpha=0.5, ax=self.ax)
        nx.draw_networkx_edges(self.G, self.pos, width=1, alpha=0.5, edge_color='k', ax=self.ax)
        nx.draw_networkx_labels(self.G, self.pos, labels=self.labels, font_size=11, ax=self.ax)
        if self.selected:    
            x, y = self.pos[self.selected]
            stype = self.selected in self.switches
            circle = Circle((x, y), 0.01, lw=2, fill=False, ec="red" if stype else 'blue', linestyle='--')
            self.ax.add_artist(circle)



FONT= ("Verdana", 12)

window = Tk()
window.title("UI")
window.geometry('1050x600')  

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
canvas.get_tk_widget().config(cursor='hand2')
canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)
#toolbar = NavigationToolbar2Tk(canvas, tab1)
#toolbar.update()
#canvas._tkcanvas.pack(side=LEFT, fill=BOTH, expand=True)

infoFrame = LabelFrame(tab1, text="Информация")
infoFrame.pack(side=TOP, fill=BOTH, expand=1)
tab1infoLabel = Label(infoFrame, anchor='nw', padx=30, pady=30, width=50, text="Выберите вершину", justify=LEFT, font=FONT)
tab1infoLabel.pack(side=LEFT, fill=Y, expand=1)
#lblt2 = Label(tab1,  width=50, height=20, text="-"*250)
#lblt2.pack(side=TOP, fill=X, expand=True)
"""
    TAB 2
"""
tab2 = ttk.Frame(tab_control)  
tab_control.add(tab2, text='Потоки')  


flowList, currFlow, currSwitch = dict(), None, None
scrollbar = Scrollbar(tab2)
scrollbarText = Scrollbar(tab2)
listbox = Listbox(tab2, width=50, bd=0, yscrollcommand=scrollbar.set)
listbox.pack(side=LEFT, fill=Y)
scrollbar.pack(side=LEFT, fill=Y)
#for i in range(100):
#    listbox.insert(END, i)
scrollbar.config(command=listbox.yview)
textarea = Text(tab2, wrap=NONE, yscrollcommand=scrollbarText.set, height=70)
def sendflowProc():
    rawflow = json.loads(textarea.get(1.0, END))["flow"]
    sflow = SimpleFlow.fromRAWFlow(currSwitch, rawflow)
    print(sflow.push(cs))
    time.sleep(1)
    loadFlowList(cs, currSwitch)

groupBtns = LabelFrame(tab2)

sendFlowBtn = Button(groupBtns, text="Отправить", command=sendflowProc, font=FONT)
updateFlowBtn = Button(groupBtns, text="Обновить", command=lambda: loadFlowList(cs, currSwitch), font=FONT)

groupBtns.pack(side=BOTTOM, fill=X, expand=1, anchor=S)
textarea.pack(side=LEFT, expand=1, fill=BOTH)
updateFlowBtn.pack(side=LEFT,anchor=SW)
sendFlowBtn.pack(side=RIGHT, anchor=SE)

scrollbarText.pack(side=LEFT, fill=Y)
scrollbarText.config(command=textarea.yview)


tab_control.pack(expand=1, fill='both') 


def update():
    vis.draw()
    canvas.draw()

update()


def loadFlowList(cs, switch):
    global currSwitch
    global currFlow
    FM = flowManager() 
    FM.requestData(cs)
    textarea.delete('1.0',END)
    listbox.delete(0, END)
    currFlow = None
    currSwitch = switch
    flows = FM.getSwitchTableFlowList(switch, 0)
    for flow in flows: 
        flowList[flow['flow']["id"]] = flow['flow']
        listbox.insert(END, flow['flow']["id"])
    
def selectItem():
    cs = listbox.curselection()
    if len(cs) == 0:
        return
    currFlow = listbox.get(cs[0])
    textarea.delete('1.0',END)
    new_text = json.dumps({"flow":flowList[currFlow]}, indent=4, ensure_ascii=False)
    textarea.insert('1.0',"".join(new_text))
    
listbox.bind("<<ListboxSelect>>", lambda x: selectItem())    

def infoToStr(info, node, topo):
    res = 'Имя: ' + node.upper() + '\n\n' 
    node = topo.nodes[node]
    res += 'Тип: ' + ( 'Хост' if type(node) == Leaf else 'Коммутатор') + '\n\n'   
    if (type(node) == Leaf):
        res += 'MAC-адрес: ' + node.nAddresses[0][0] + '\n'
        res += 'IP-адрес: ' + node.nAddresses[0][1] + '\n'
        res += '\n'
        res += 'Подключен к ' + info[0][1].upper()
        return res   
    
    res += 'Подключен к:\n'
    for i in info:
        res += "    [порт %s]"%str(i[0]) + "  ➜  " + str(i[1]).upper() + "\n"
    return res
       
def checkMouse(ex, ey):
    dist = 100
    xl = vis.ax.get_xlim()
    yl = vis.ax.get_ylim()
    box = vis.ax.get_window_extent().transformed(vis.fig.dpi_scale_trans.inverted())
    width, height = box.width, box.height
    width *= vis.fig.dpi
    height *= vis.fig.dpi
    
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
    a.title("chVLAN %s"%ip)
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


def makePath(mac1, mac2, ip1, ip2):
    def make(mac1, mac2):
        pushFlow(cs, vis.topo, mac1, mac2)
        pushFlow(cs, vis.topo, mac2, mac1)
        amp.destroy()
    amp = Toplevel()
    amp.title("make path")
    x, y = window.winfo_x(), window.winfo_y()
    w, h = window.winfo_width(), window.winfo_height()   
    amp.geometry("%dx%d+%d+%d" % (230, 100, x + w // 2, y + h // 2))
    amp.resizable(False, False)  
    lbel = Label(amp, text="path %s <---> %s" % (ip1, ip2), justify=CENTER, font=FONT)
    lbel.grid(row=0)
    lold = Label(amp, text="MAC_1: %s"%mac1, justify=CENTER, font=FONT)
    lold.grid(row=3)
    lnew = Label(amp, text="MAC_2: %s"%mac2, justify=CENTER, font=FONT)
    lnew.grid(row=4)
    Button(amp, text="submit", width=20, command=lambda:make(mac1, mac2)).grid(row=5)


class flowCreator():
    def __init__(self):
        self.aip = None
        self.bip = None
        self.amac = None
        self.bmac = None
    def call_fm(self):
        if self.aip and self.bip:
            makePath(self.amac, self.bmac, self.aip, self.bip)
    def path_from(self, aip, amac):
        self.aip = aip
        self.amac = amac
        self.call_fm()
    def path_to(self, bip, bmac):
        self.bip = bip
        self.bmac = bmac
        self.call_fm()
fc = flowCreator()        

class Popup:
    def __init__(self):
        self.menu = Menu(window.master)
        self.ip = None
        self.mac = None
        self.menu.add_command(label="Изменить VLAN", command=lambda:changeVlan(self.ip))
        self.menu.add_command(label="Путь отсюда", command=lambda:fc.path_from(self.ip, self.mac))
        self.menu.add_command(label="Путь сюда", command=lambda:fc.path_to(self.ip, self.mac))
        #self.menu.add_separator()

    def show_menu_(self, event, nip, mac):
        self.ip = nip
        self.mac = mac
        self.menu.tk_popup(event.x_root, event.y_root)
pop = Popup()          
        
def b1(event):
    nn = checkMouse(event.x, event.y)
    vis.selected = nn
    content = infoToStr(vis.G.nodes[nn]['connections'], nn, vis.topo) if not nn is None else ''
    if nn and type(vis.topo.nodes[nn]) == Node:
        loadFlowList(cs, nn)
    tab1infoLabel['text'] = content   
    update()    
            
def b3(event):
    nn = checkMouse(event.x, event.y)
    vis.selected = nn
    if nn in vis.hosts:
        pop.show_menu_(event, vis.topo.nodes[nn].nAddresses[0][1], vis.topo.nodes[nn].nAddresses[0][0])
    update()

def move(event):
    update()
    x = event.x
    y = event.y
    s = "Движение мышью {}x{}".format(x, y)
    window.title(s)

canvas.get_tk_widget().bind('<Button-1>', b1)
#window.bind('<Button-1>', b1)
canvas.get_tk_widget().bind('<Button-3>', b3)
#window.bind('<Motion>', move)



window.mainloop()
