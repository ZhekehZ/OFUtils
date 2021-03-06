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
           


class FlowModFrame(Frame):
   
    def __selectItem(self):
        crs = self.flowL.listbox.curselection()
        if len(crs) == 0:
            return
        self.currFlow = self.flowL.listbox.get(crs[0])
        self.textF.textarea.delete('1.0',END)
        new_text = json.dumps({"flow":self.currSFlowList[self.currFlow]}, indent=4, ensure_ascii=False)
        self.textF.textarea.insert('1.0',"".join(new_text))
    
    def __init__(self, parent, cs, fm):
        Frame.__init__(self, parent, bg='white')
        parent.add(self, text='Flows')
        
        self.currFlow = None
        self.currSwitch = None
        self.FM = fm
        self.cs = cs
        
        self.currSFlowList = dict()
        self.currSFlowStats = dict()
        
        self.union = Frame(self)
        self.controls = controlFrame(self.union)
        self.controls.pack(side=BOTTOM, fill=X)
        self.flowL = flowList(self.union)
        self.flowL.pack(side=TOP, expand=1, fill=BOTH)
        self.union.pack(side=LEFT, expand=1, fill=BOTH)
        
        self.textF = textField(self)
        self.textF.pack(side=LEFT, expand=1, fill=BOTH)
        
        self.flowL.listbox.bind("<<ListboxSelect>>", lambda event: self.__selectItem()) 
        
        def sendflowProc():
            rawflow = json.loads(self.textF.textarea.get(1.0, END))["flow"]
            sflow = Utils.SimpleFlow.fromRAWFlow(self.currSwitch, rawflow)
            print(sflow.push(self.cs), self.currSwitch)
            #time.sleep(1)
            self.update()
            self.setSwitch(self.currSwitch)
        
        def addFlowProc():
            dumm = """{
    "flow": {
        "match": {
            <?>
        },
        "id": <?>,
        "priority": <?>,
        "instructions": {
            "instruction": [
                <?>
            ]
        },
        "table_id": <?>
    }
}"""
            self.textF.textarea.delete('1.0',END)
            self.textF.textarea.insert('1.0',"".join(dumm))
        
        def showStats():
            if not self.currFlow:
                return
            stats = self.currSFlowStats[self.currFlow]
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
        
        def deleteFlowProc():
            print("REMOVING FLOW")
            self.FM.removeFlow(self.cs, self.currSwitch, 0, self.currFlow)
            self.update()
        
        self.controls.addFlowBtn.bind('<Button-1>', lambda event: addFlowProc())
        self.controls.sendFlowBtn.bind('<Button-1>', lambda event: sendflowProc())
        self.controls.statFlowBtn.bind('<Button-1>', lambda event: showStats())
        self.controls.deleteFlowBtn.bind('<Button-1>', lambda event: deleteFlowProc())
    
    def update(self):
        self.FM.requestData(self.cs)
        if self.currSwitch:
            self.setSwitch(self.currSwitch)
        
    def setSwitch(self, switch):
        self.flowL.listbox.delete(0, END)
        self.currSwitch = switch
        #for table
        self.currSFlowList = dict() 
        flows = self.FM.getSwitchTableFlowList(switch, 0)
        for flow in flows: 
            if 'opendaylight-flow-statistics:flow-statistics' in flow['flow'].keys(): 
                self.currSFlowStats[flow['flow']["id"]] = flow['flow']['opendaylight-flow-statistics:flow-statistics']
            flow['flow'].pop('opendaylight-flow-statistics:flow-statistics', None)
            self.currSFlowList[flow['flow']["id"]] = flow['flow']
            self.flowL.listbox.insert(END, flow['flow']["id"])
        
        
        
