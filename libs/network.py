import tkinter as tk
from subprocess import call
import subprocess
from tkinter.ttk import *
from tkinter import ttk

class Network:
    def __init__(self, master, network):
        self.master = master
        self.w = 220  # width for the Tk root
        self.h = 100  # height for the Tk root
        self.ws = self.master.winfo_screenwidth()  # width of the screen
        self.hs = self.master.winfo_screenheight()  # height of the screen

        self.x = (self.ws / 2) - (self.w / 2)
        self.y = (self.hs / 2) - (self.h / 2)
        self.master.geometry('%dx%d+%d+%d' % (self.w, self.h, self.x, self.y))
        self.label = Label(self.master, text="Network segment")
        self.combo = ttk.Combobox(self.master,
                                    values=[
                                        "192.168.1.0/24",
                                        "192.168.61.0/24",
                                        "192.168.62.0/24",
                                        "192.168.63.0/24"])
        self.combo.current(0)
        self.close_button = Button(self.master, text="Save", command=self.save)
        self.label.pack(side='top', pady=5)
        self.combo.pack(side='top', pady=5)
        self.close_button.pack(side='bottom', pady=5)

    def save(self):
        print(self.combo.current(), self.combo.get())
        # self.network_segment = self.combo.get()
        # self.master.destroy()