from tkinter import *
from subprocess import call
import subprocess
from tkinter.ttk import *
from tkinter import ttk


class Network:
    def __init__(self, master):
        self.master = master
        self.nb = ttk.Notebook(self.master, height=200, width=350)

        # install frame
        self.network = ttk.Frame(self.nb)
        self.label = Label(self.network, text="Install samba from here!")
        self.label.grid(row=0, column=0, pady=1, padx=1)

        self.install_btn = Button(self.network, text="INSTALL", command=self.set)
        self.install_btn.grid(row=1, column=0, padx=2, pady=2)


        self.nb.add(self.network, text='Install')
        self.nb.grid(row=0, column=0)

        self.w = 550  # width for the Tk root
        self.h = 250  # height for the Tk root

        self.ws = self.master.winfo_screenwidth()  # width of the screen
        self.hs = self.master.winfo_screenheight()  # height of the screen

        self.x = (self.ws / 2) - (self.w / 2)
        self.y = (self.hs / 2) - (self.h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))

    def close_window(self):
        self.master.destroy()