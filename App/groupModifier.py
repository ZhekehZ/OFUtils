import Utils
from tkinter import *
import json
import time

FONT_A = ("Verdana", 12)

class controlFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg="white")
        self.sendFlowBtn = Button(self, text="Send", font=FONT_A, bg="white")
        self.deleteFlowBtn = Button(self, text="Delete", font=FONT_A, bg="white")
        self.statFlowBtn = Button(self, text="Stats", font=FONT_A, bg="white")
        self.addFlowBtn = Button(self, text="Add", font=FONT_A, bg="white")
        self.addFlowBtn.pack(side=LEFT)
        self.sendFlowBtn.pack(side=RIGHT)
        self.deleteFlowBtn.pack(side=RIGHT)
        self.statFlowBtn.pack(side=RIGHT)
   

class flowList(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.scroll = Scrollbar(self, bg='white')
        self.listbox = Listbox(self, width=50, bd=0, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.listbox.yview)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.scroll.pack(side=LEFT, fill=Y)
            
            
class textField(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.scroll = Scrollbar(self, bg='white')
        self.textarea = Text(self, wrap=NONE, yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.textarea.yview)
        self.textarea.pack(side=LEFT, fill=BOTH, expand=1)
        self.scroll.pack(side=LEFT, fill=Y)
           


class GroupModFrame(Frame):
   
    def __selectItem(self):
        crs = self.groupL.listbox.curselection()
        if len(crs) == 0:
            return
        self.currGroup = self.groupL.listbox.get(crs[0])
        self.textF.textarea.delete('1.0',END)
        new_text = json.dumps({"group":self.currSGroupList[self.currGroup]}, indent=4, ensure_ascii=False)
        self.textF.textarea.insert('1.0',"".join(new_text))
    
    def __init__(self, parent, cs, fm):
        Frame.__init__(self, parent, bg='white')
        parent.add(self, text='Groups')
        
        self.currGroup = None
        self.currSwitch = None
        self.FM = fm
        self.cs = cs
        
        self.currSGroupList = dict()
        self.currSGroupStats = dict()
        
        self.union = Frame(self)
        self.controls = controlFrame(self.union)
        self.controls.pack(side=BOTTOM, fill=X)
        self.groupL = flowList(self.union)
        self.groupL.pack(side=TOP, expand=1, fill=BOTH)
        self.union.pack(side=LEFT, expand=1, fill=BOTH)
        
        self.textF = textField(self)
        self.textF.pack(side=LEFT, expand=1, fill=BOTH)
        
        self.groupL.listbox.bind("<<ListboxSelect>>", lambda event: self.__selectItem()) 
        
        def sendGroupProc():
            rawgroup = json.loads(self.textF.textarea.get(1.0, END))["group"]
            sgroup = Utils.SimpleGroup.fromRAWGroup(self.currSwitch, rawgroup)
            print(sgroup.push(self.cs), self.currSwitch)
            #time.sleep(1)
            self.update()
        
        def addGroupProc():
            dumm = """{
    "flow-node-inventory:group": [
        {
            "group-id": <?>,
            "group-type": <?>,
            "buckets": {
                "bucket": [
                    <?>
                ]
            }
        }
    ]
}"""
            self.textF.textarea.delete('1.0',END)
            self.textF.textarea.insert('1.0',"".join(dumm))
        
        def showStats():
            if not self.currGroup:
                return
            stats = self.currSGroupStats[self.currGroup]
            
            statstext = 'Bytes: '
            if stats and 'byte-count' in stats.keys():
                statstext += str(stats['byte-count']) + '\n'
            else:
                statstext += '0\n'
            statstext += 'Packets: '
            if stats and 'packet-count' in stats.keys():
                statstext += str(stats['packet-count']) + '\n'
            else:
                statstext += '0\n'
            messagebox.showinfo("Flow stats", statstext)
        
        def deleteGroupProc():
            print("REMOVING GROUP")
            self.FM.removeGroup(self.cs, self.currSwitch, self.currGroup)
            self.update()
            
        self.controls.addFlowBtn.bind('<Button-1>', lambda event: addGroupProc())
        self.controls.sendFlowBtn.bind('<Button-1>', lambda event: sendGroupProc())
        self.controls.statFlowBtn.bind('<Button-1>', lambda event: showStats())
        self.controls.deleteFlowBtn.bind('<Button-1>', lambda event: deleteGroupProc())
        
    def update(self):
        self.FM.requestData(self.cs)
        if self.currSwitch:
            self.setSwitch(self.currSwitch)
        
    def setSwitch(self, switch):
        self.groupL.listbox.delete(0, END)
        self.currSwitch = switch
        self.currSGroupList = dict() 
        groups = self.FM.getSwitchGroupList(switch)
        for group in groups:
            group = group[0]     
            _gr = 'flow-node-inventory:group'
            _st = 'opendaylight-group-statistics:group-statistics'
            if _st in group[_gr].keys():
                self.currSGroupStats[group[_gr]["group-id"]] = group[_gr][_st]
            else:
                self.currSGroupStats[group[_gr]["group-id"]] = None
            group[_gr].pop(_st, None)
            
            self.currSGroupList[group['flow-node-inventory:group']["group-id"]] = group['flow-node-inventory:group']
            self.groupL.listbox.insert(END, group['flow-node-inventory:group']["group-id"])
        
        
        
