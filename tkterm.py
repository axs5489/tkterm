# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 17:23:33 2021

@author: axs5489

A Tkinter-based serial console

This software is in the public domain and is provided without express or 
implied warranty. Permission to use, modify, or distribute the software
for any purpose is hereby granted."""

debugSerial = False
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk
from tkcolors import COLORS
from SerialPort import SerialPort
from win import listSerialPorts
import threading
import time

REVISION = "$Revision: 1.0 $"
VERSION = REVISION.split()[1]

class OutputPipe:
	"""A substitute file object for redirecting output to a function."""

	def __init__(self, writer):
		self.writer = writer
		self.closed = 0

	def __repr__(self):
		return "<OutputPipe to %s>" % repr(self.writer)

	def flush(self):
		pass

	def read(self, length):
		return ""

	def write(self, data):
		if not self.closed: self.writer(data)

	def close(self):
		self.closed = 1

class tkDialog(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master)
		self.master = master
		self.pack(fill=tk.BOTH, expand=1)

	def close(self, event=None):
		self.master.destroy()

class NewConsole(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("New tkTerm Console")
		self.master.geometry("300x250")
		self.master.resizable(False, False)

		self.ports = tk.StringVar()
		self.ports.set(("COM1", "COM3", "COM4"))
		#self.refresh()
		self.portsel = tk.Listbox(self, listvariable = self.ports)
		self.portsel.pack()

		self.b_cancel = tk.Button(self, text = "Cancel", command = self.close)
		self.b_cancel.place(x=70, y=200)
		self.b_refresh = tk.Button(self, text = "Refresh", command = self.refresh)
		self.b_refresh.place(x=120, y=200)
		self.b_ok = tk.Button(self, text = "   Ok   ", command = self.newConsole)
		self.b_ok.place(x=170, y=200)

	def refresh(self):
		p = listSerialPorts()
		print(p)
		self.ports.set(p)

	def newConsole(self):
		print(self.portsel.get(self.portsel.curselection()))

class LogConsole(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Log tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

class SetupOptionMenu(tk.OptionMenu):
	FONT= ('calibri', 12)
	def __init__(self, master, status, *options):
		self.var = tk.StringVar(master)
		self.var.set(status)
		tk.OptionMenu.__init__(self, master, self.var, *options)
		self.config(width=10, bg = "white", font=self.FONT)
		self['menu'].config(width=10, bg = "white", font=self.FONT)

	def update(self, newlist):
		self["menu"].delete(0, "end")
		for opt in newlist:
			self["menu"].add_command(label=opt, command=lambda value=opt: self.var.set(value))
		self.var.set(newlist[0])

class Setup(tkDialog):
	XLABEL = 30
	XOPT = 120
	FONT= ('calibri', 12)
	PORTS = ["COM1", "COM3"]
	SPEEDS = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400,
		   57600, 115200, 230400, 460800, 921600]
	DATA = ["7 bit", "8 bit"]
	PARITY = ["none", "odd", "even", "mark", "space"]
	STOP = ["1 bit", "2 bit"]
	FLOW = ["none", "Xon/Xoff", "RTS/CTS", "DSR/DTR"]
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Serial Setup")
		self.master.geometry("280x330")
		self.master.resizable(False, False)

		self.l_port = tk.Label(self, text = "Port:")
		self.v_port = tk.StringVar()
		#self.refresh()
		self.v_port.set(self.PORTS[0])
		self.o_ports = tk.OptionMenu(self, self.v_port, *self.PORTS)
		self.o_ports.config(width=10, bg = "white", font=self.FONT)
		self.o_ports['menu'].config(bg = "white", font=self.FONT)
		self.l_port.place(x=self.XLABEL, y=25)
		self.o_ports.place(x=self.XOPT, y=20)

		self.l_speed = tk.Label(self, text = "Speed:")
		self.v_speed = tk.StringVar()
		self.v_speed.set(self.SPEEDS[11])
		self.o_speed = tk.OptionMenu(self, self.v_speed, *self.SPEEDS)
		self.o_speed.config(width=10, bg = "white", font=self.FONT)
		self.l_speed.place(x=self.XLABEL, y=66)
		self.o_speed.place(x=self.XOPT, y=60)

		self.l_data = tk.Label(self, text = "Data:")
		self.v_data = tk.StringVar()
		self.v_data.set(self.DATA[0])
		self.o_data = tk.OptionMenu(self, self.v_data, *self.DATA)
		self.o_data.config(width=10, bg = "white", font=self.FONT)
		self.l_data.place(x=self.XLABEL, y=106)
		self.o_data.place(x=self.XOPT, y=100)

		self.l_parity = tk.Label(self, text = "Parity:")
		self.v_parity = tk.StringVar()
		self.v_parity.set(self.PARITY[0])
		self.o_parity = tk.OptionMenu(self, self.v_parity, *self.PARITY)
		self.o_parity.config(width=10, bg = "white", font=self.FONT)
		self.l_parity.place(x=self.XLABEL, y=146)
		self.o_parity.place(x=self.XOPT, y=140)

		self.l_stop = tk.Label(self, text = "Stop bits:")
		self.v_stop = tk.StringVar()
		self.v_stop.set(self.STOP[0])
		self.o_stop = tk.OptionMenu(self, self.v_stop, *self.STOP)
		self.o_stop.config(width=10, bg = "white", font=self.FONT)
		self.l_stop.place(x=self.XLABEL, y=186)
		self.o_stop.place(x=self.XOPT, y=180)

		self.l_flow = tk.Label(self, text = "Flow control:")
		self.v_flow = tk.StringVar()
		self.v_flow.set(self.FLOW[0])
		self.o_flow = tk.OptionMenu(self, self.v_flow, *self.FLOW)
		self.o_flow.config(width=10, bg = "white", font=self.FONT)
		self.l_flow.place(x=self.XLABEL, y=226)
		self.o_flow.place(x=self.XOPT, y=220)

		self.b_cancel = tk.Button(self, text = "Cancel", command = self.close)
		self.b_cancel.place(x=50, y=280)
		self.b_refresh = tk.Button(self, text = "Refresh", command = self.refresh)
		self.b_refresh.place(x=120, y=280)
		self.b_ok = tk.Button(self, text = "   Ok   ", command = self.onReturn)
		self.b_ok.place(x=190, y=280)

	def refresh(self):
		p = listSerialPorts()
		self.PORTS = ["COM1"]
		print(p, self.PORTS)
		if(p != []) :
			self.PORTS.append(p)
		self.o_ports.update()
		self.o_ports["menu"].delete(0, "end")
		for string in self.PORTS:
			self.o_ports["menu"].add_command(label=string, command=lambda value=string: self.v_port.set(value))
		self.v_port.set(self.PORTS[0])

	def onReturn(self):
		print(self.portsel.get(self.portsel.curselection()))

class Terminal(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Terminal tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

class SerialConsole(tkDialog):
	def __init__(self, master=None, comport = "COM1", bg="blue", **kwargs):
		tkDialog.__init__(self, master)
		self.master.geometry("513x714")
		self.master.resizable(False, False)
		self.pad = 3
		self.MAX_WIDTH = master.winfo_screenwidth() - self.pad
		self.MAX_HEIGHT = master.winfo_screenheight() - self.pad
		self.index = 0

		# Command history
		self.cmdvar = tk.StringVar()
		self.history = []
		self.historyindex = None
		self.current = ""
		self.prefixes = ["... ", ">>> ", ">> ", "> "]

		# Text Box
		self.text = tk.Text(self, insertontime=200, insertofftime=150, bg=bg)
		self.text.insert("end", "Python Console\n")
		self.text.insert("end", ">>> ")
		#self.text.bind("<Return>", self.cb_return)
		self.text.bind("<Up>", self.cb_back)
		self.text.bind("<Down>", self.cb_forward)
		#self.text.bind("<Tab>", self.cb_complete)
		self.cmdentry = tk.Entry(self, textvariable = self.cmdvar)
		self.cmdentry.bind("<Return>", self.send)

		# Scroll bar
		self.scroll = tk.Scrollbar(self, command=self.text.yview)
		self.text.config(yscrollcommand=self.scroll.set)
		self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.text.pack(fill=tk.BOTH, expand=1)
		self.text.focus()
		self.cmdentry.pack(fill=tk.BOTH)

		# Menu bar
		menubar = tk.Menu(self.master)
		self.master.config(menu=menubar)

		fileMenu = tk.Menu(menubar, tearoff=False)
		fileMenu.add_command(label="New", command=self.newConsole)
		fileMenu.add_command(label="Log", command=self.logConsole)
		fileMenu.add_command(label="Exit", command=self.close)
		menubar.add_cascade(label="File", underline=0, menu=fileMenu)
		self.bind_all("<Control-n>", self.newConsole)
		self.bind_all("<Control-l>", self.logConsole)
		self.bind_all("<Control-q>", self.close)

		editMenu = tk.Menu(menubar, tearoff=False)
		editMenu.add_command(label="Reset", command=self.reset)
		editMenu.add_command(label="Setup", command=self.setupPort)
		editMenu.add_command(label="Terminal", command=self.setupWindow)
		menubar.add_cascade(label="Edit", underline=0, menu=editMenu)
		self.bind_all("<Control-r>", self.reset)
		self.bind_all("<Control-o>", self.setupPort)
		self.bind_all("<Control-t>", self.setupWindow)

		if(debugSerial):
			if(isinstance(comport, str)):
				self.serial = SerialPort(comport, comport, asyncr=True)
			elif(isinstance(comport, SerialPort)):
				self.serial = comport
			else:
				pass
		else:
			self.serial = []


		# Configurable options.
		self.options = {"stdoutcolour": "#7020c0",	#purple, print statements
						"stderrcolour": "#c03020",	#red/orange, errors
						"morecolour": "#a0d0f0",	#light blue
						"badcolour": "#e0b0b0",		#pastel red
						"runcolour": "#90d090"}		#pastel green, last python
		self.config(**self.options)
		self.config(**kwargs)

	def __getitem__(self, key):
		return self.options[key]

	def __setitem__(self, key, value):
		if not key in self.options:
			raise KeyError('no such configuration option "%s"' % key)
		self.options[key] = value
		if key == "stdoutcolour":
			self.text.tag_configure("stdout", foreground=value)
		if key == "stderrcolour":
			self.text.tag_configure("stderr", foreground=value)

	def config(self, *args, **kwargs):
		"""Get or set configuration options in a Tkinter-like style."""
		if args == () and kwargs == {}:
			return self.options
		if len(args) == 1:
			return self.options[args[0]]
		for key, value in kwargs.items():
			self[key] = value

	def logConsole(self, event=None):
		self.new = tk.Toplevel(self.master)
		LogConsole(self.new)

	def newConsole(self, event=None):
		self.new = tk.Toplevel(self.master)
		NewConsole(self.new)

	def reset(self, event=None):
		self.text.delete(0, len(self.text.get()))
		self.cmdentry.delete(0, len(self.cmdvar.get()))

	def recv(self, event=None):
		#print("Hello")
		self.text.configure(bg = COLORS[self.index])
		self.index += 1
		self.after(2000, self.recv)

	def send(self, event=None):
		print(self.cmdvar.get())
		self.cmdentry.delete(0, len(self.cmdvar.get()))

	def setupPort(self, event=None):
		self.new = tk.Toplevel(self.master)
		Setup(self.new)

	def setupWindow(self, event=None):
		self.new = tk.Toplevel(self.master)
		Terminal(self.new)

	# History mechanism.

	def cb_back(self, event):
		"""Step back in the history."""
		if self.history:
			if self.historyindex == None:
				self.current = self.getline(trim=1)
				self.historyindex = len(self.history) - 1
			elif self.historyindex > 0:
				self.historyindex = self.historyindex - 1
			self.recall()
			
		return "break"

	def cb_forward(self, event):
		"""Step forward in the history."""
		if self.history and self.historyindex is not None:
			self.historyindex = self.historyindex + 1
			if self.historyindex < len(self.history):
				self.recall()
			else:
				self.historyindex = None
				self.recall(self.current)

		return "break"

	def recall(self, command=None):
		"""Show a command from the history on the current line."""
		if command is None:
			command = self.history[self.historyindex]
		line, pos = self.cursor()
		current = self.getline(line)
		trimmed, trimmedline = self.trim(current)
		cutpos = "%d.%d" % (line, trimmed)
		self.text.delete(cutpos, "%d.end" % line)
		self.text.insert(cutpos, command)
		self.text.mark_set("insert", "%d.end" % line)



# Main program.
class SerialApp(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()
	def callback(self):
	   self.root.quit()
	def run(self):
		self.root=tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)
		self.strvar = tk.StringVar()
		self.strvar.set('Foo')
		l = tk.Label(self.root,textvariable=self.strvar)
		l.pack()
		c = SerialConsole(dict={})
		c.dict["console"] = c
		c.pack(fill=tk.BOTH, expand=1)
		c.master.title("tkTerm Console v%s" % VERSION)
		self.root.mainloop()

def start_new_console():
	root = tk.Tk()
	app = NewConsole(root)
	#app.dict["console"] = app
	app.pack(fill=tk.BOTH, expand=1)
	app.master.title("tkTerm v%s" % VERSION)
	tk.mainloop()

def start_console():
	root = tk.Tk()
	app = SerialConsole(root)
	#app.dict["console"] = app
	app.pack(fill=tk.BOTH, expand=1)
	#app.master.title("tkTerm v%s" % VERSION)
	root.after(1000, app.recv)
	tk.mainloop()

		
if __name__ == "__main__":
	start_console()
