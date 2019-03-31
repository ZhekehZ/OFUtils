import sys
sys.path.append(sys.path[0]+'/../Utils')

from Topology import *
import networkx as nx
import numpy as np

from matplotlib.widgets import TextBox
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['toolbar'] = 'None'

# nodes to draw
switches, hosts = [], []

# DFS/
used = set()
def dfs(node, pre, portinfo):
    used.add(node.id)
    G.add_node(node.id, connections=[])
    nc = node.connections
    if type(node) == Leaf:
        hosts.append(node.id)
    else:
        switches.append(node.id)

    for i in range(len(nc)):
        next = nc[i][0]
        port = nc[i][1] 
        G.nodes[node.id]['connections'].append([port, next.id])
        G.add_edge(node.id, next.id)
        if not next.id in used: 
            dfs(next, pre + ('              ' if len(portinfo) else '     '), str(port))
# /DFS


cs = ControllerSettings('localhost', 'admin', 'admin')
t = Topology(cs)
G = nx.Graph()
node = [e for e in t.elements.values() if type(e) == Node][0]
dfs(node, '', '')

# Graph/
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('Network graph')
pos=nx.spring_layout(G)
nx.draw_networkx_nodes(G,pos,
                       node_color='b',
                       node_size=500,
                       nodelist=switches, alpha=0.5)
nx.draw_networkx_nodes(G,pos,
                       node_color='r',
                       node_size=500,
                       nodelist=hosts, alpha=0.5,picker=True)
nx.draw_networkx_edges(G,pos,
                       width=1,alpha=0.5,edge_color='b')
nx.draw_networkx_labels(G,pos,font_size=11)

plt.axis('off')
plt.axis(xmin=-1.5, ymin=-1.5, xmax=1.5, ymax=1.5)
# /Graph

# onPick/
txt = plt.text(-10, -10, 'fgffg', fontsize=8)

def infoTostr(info):
    res = ""
    for i in info:
        if (i[0] == -1):
            res += "➜  " + str(i[1]) + "\n"
        else:
            res += "port " + str(i[0]) + ":\n     ➜  " + str(i[1]) + "\n"
    return res

def onPick(event):
    global txt
    if txt: 
        txt.remove()
        txt = False
        fig.canvas.draw()
    for n in pos.keys():
        x,y = pos[n]
        if np.sqrt(abs(event.xdata - x)**2 + abs(event.ydata - y)**2) < 0.1:
            #txt = plt.text(event.xdata, event.ydata, G.nodes[n]['connections'], fontsize=8)
            props = dict(boxstyle='round', facecolor='gray')

            txt = plt.text(event.xdata, event.ydata, infoTostr(G.nodes[n]['connections']), fontsize=14, verticalalignment='top', bbox=props)
            fig.canvas.draw()

fig.canvas.callbacks.connect('button_press_event', onPick)
# /onPick

# draw
plt.show()
