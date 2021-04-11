# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 15:56:24 2021

@author: axs5489
"""

debugOn = True
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk
from tkinter import ttk
from win import listSerialPorts


PORTS = ["COM1"]
SPEEDS = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400,
		   57600, 115200, 230400, 460800, 921600]

class tkDialog(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master)
		self.master = master
		self.pack(fill=tk.BOTH, expand=1)
		self.returnNone = True 		# Return nothing on close by default

	def onOK(self):
		self.returnNone = False 	# RETURN SOMETHING
		self.close()

	def close(self, event=None):
		self.master.destroy()

class NewSetup(tkDialog):
	YBUT = 100
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("New Console")
		self.master.geometry("230x150")
		self.master.resizable(False, False)

		self.l_speed = tk.Label(self, text = "Speed:")
		self.l_speed.place(x=30, y=20)
		self.speed = tk.StringVar()
		self.box = ttk.Combobox(self, width=10, state="readonly",
							values = SPEEDS, textvariable = self.speed)
		self.box.current(11)
		self.box.place(x=100, y=20)
		self.l_ports = tk.Label(self, text = "Port(s):")
		self.l_ports.place(x=30, y=50)
		self.port = tk.StringVar()
		self.portsel = ttk.Combobox(self, width=10, state="readonly",
							values = PORTS, textvariable = self.port)
		self.portsel.place(x=100, y=50)
		self.refresh()

		self.b_cancel = tk.Button(self, text = "Cancel", command = self.close, width = 6)
		self.b_cancel.place(x=30, y=self.YBUT)
		self.b_refresh = tk.Button(self, text = "Refresh", command = self.refresh, width = 6)
		self.b_refresh.place(x=90, y=self.YBUT)
		self.b_ok = tk.Button(self, text = "Ok", command = self.onOK, width = 6)
		self.b_ok.place(x=150, y=self.YBUT)

	def refresh(self):
		global PORTS
		PORTS = []
		p = listSerialPorts()
		if(p == []) :
			PORTS.append("COM1")
		else:
			PORTS.append(p)
		self.portsel['values'] = PORTS
		self.port.set(PORTS[0])

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = (self.port.get(), self.speed.get())
		if(debugOn) : print(t)
		return t

class LogSetup(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Log tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

class PortSetup(tkDialog):
	XLABEL = 30
	XOPT = 120
	YBUT = 210
	FONT= ('calibri', 12)
	DATA = ["7 bit", "8 bit"]
	PARITY = ["none", "odd", "even", "mark", "space"]
	STOP = ["1 bit", "2 bit"]
	FLOW = ["none", "Xon/Xoff", "RTS/CTS", "DSR/DTR"]
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Serial Setup")
		self.master.geometry("230x250")
		self.master.resizable(False, False)
		self.index = 0
		self.labels = [None, None, None, None, None, None]
		self.vars = [None, None, None, None, None, None]
		self.boxes = [None, None, None, None, None, None]

		self.addOption("Port:", PORTS, 20)
		self.addOption("Speed:", SPEEDS, 50, 11)
		self.addOption("Data:", self.DATA, 80, 1)
		self.addOption("Parity:", self.PARITY, 110)
		self.addOption("Stop bits:", self.STOP, 140)
		self.addOption("Flow control:", self.FLOW, 170)
		self.refresh()

		self.b_cancel = tk.Button(self, text = "Cancel", command = self.close, width = 6)
		self.b_cancel.place(x=30, y=self.YBUT)
		self.b_refresh = tk.Button(self, text = "Refresh", command = self.refresh, width = 6)
		self.b_refresh.place(x=90, y=self.YBUT)
		self.b_ok = tk.Button(self, text = "Ok", command = self.onOK, width = 6)
		self.b_ok.place(x=150, y=self.YBUT)

	def addOption(self, lbl, lst, y, dflt=0):
		self.labels[self.index] = tk.Label(self, text = lbl)
		self.labels[self.index].place(x=self.XLABEL, y=y)
		self.vars[self.index] = tk.StringVar()
		self.boxes[self.index] = ttk.Combobox(self, width=10, state="readonly",
							values = lst, textvariable = self.vars[self.index])
		self.boxes[self.index].current(dflt)
		self.boxes[self.index].place(x=self.XOPT, y=y)
		self.index += 1

	def refresh(self):
		global PORTS
		PORTS = []
		p = listSerialPorts()
		if(p == []) :
			PORTS.append("COM1")
		else:
			PORTS.append(p)
		self.boxes[0]['values'] = PORTS
		self.vars[0].set(PORTS[0])

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = tuple(i.get() for i in self.vars)
		if(debugOn) : print(t)
		return t

class TerminalSetup(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Terminal tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = tuple(i.get() for i in self.vars)
		if(debugOn) : print(t)
		return t
