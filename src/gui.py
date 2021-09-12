from tkinter import * 
from tkinter.ttk import *

class GUI:
    def __init__(self, name, window_data):

        self.master = Tk()
        self.master.title(name)

        mx, my, fy = window_data
        self.width = mx//4
        self.height = my


        self.master.geometry(f'{self.width}x{self.height}+{0}+{0}')
        self.update()

        dx, dy = self.master.winfo_rootx(), self.master.winfo_rooty()
        self.master.geometry(f'{self.width}x{self.height}+{mx-self.width-dx}+{-dy+fy-my}')

        
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

        self.master.focus_displayof()