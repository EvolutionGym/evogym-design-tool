from tkinter import * 
from tkinter.ttk import *

class GUI:
    def __init__(self, name):

        self.master = Tk()
        self.master.title(name)
        self.master.geometry('400x800')
        # Entry widget
        e1 = Entry(self.master)
        e1.pack(expand = 1, fill = BOTH)
        
        # Button widget which currently has the focus
        e2 = Button(self.master, text ="Button")
        
        # here focus_set() method is used to set the focus
        e2.focus_set()
        e2.pack(pady = 5)
        
        # Radiobuton widget
        e3 = Radiobutton(self.master, text ="Hello")
        e3.pack(pady = 5)

    def update(self):
        self.master.update_idletasks()
        self.master.update()