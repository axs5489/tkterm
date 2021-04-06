# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 17:23:33 2021

@author: axs5489

A Tkinter-based serial console

This software is in the public domain and is provided without express or 
implied warranty. Permission to use, modify, or distribute the software
for any purpose is hereby granted."""

debugOn = True
debugSerial = False
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk
#from tk import filedialog as fd
from tkinter import scrolledtext
from tkinter import ttk
from tkcolors import COLORS
from SerialPort import SerialPort
from win import listSerialPorts
import serial
import threading
import time
import win32clipboard

REVISION = "$Revision: 1.0 $"
VERSION = REVISION.split()[1]

PORTS = ["COM1"]
SPEEDS = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400,
		   57600, 115200, 230400, 460800, 921600]

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
		self.b_ok = tk.Button(self, text = "Ok", command = self.master.destroy, width = 6)
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

	def onReturn(self):
		self.master.deiconify()
		self.master.wait_window()
		t = (self.port.get(), self.speed.get())
		if(debugOn) : print(t)
		return t

class LogConsole(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Log tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

class Setup(tkDialog):
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
		self.b_ok = tk.Button(self, text = "Ok", command = self.master.destroy, width = 6)
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

	def onReturn(self):
		self.master.deiconify()
		self.master.wait_window()
		t = tuple(i.get() for i in self.vars)
		if(debugOn) : print(t)
		return t

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
		self.copypaste = ""
		self.history = []
		self.historyindex = None
		self.current = ""
		self.prefixes = ["$ ", "# ", "... ", ">>> ", ">> ", "> "]

		# Menu bar
		menubar = tk.Menu(self.master)
		self.master.config(menu=menubar)

		fileMenu = tk.Menu(menubar, tearoff=False)
		fileMenu.add_command(label="New", command=self.newConsole, accelerator ="")
		fileMenu.add_command(label="Log", command=self.logConsole)
		fileMenu.add_separator()
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

		# Text Box
		self.cmdvar = tk.StringVar()
		self.textvar = tk.StringVar()
		self.text = scrolledtext.ScrolledText(self, insertontime=200, insertofftime=150, bg=bg)
		#self.text = tk.Entry(self, textvariable = self.textvar, state="readonly")
		self.text.insert("end", "Python Console\n")
		self.text.insert("end", ">>> ")
		self.text.bind("<Key>", lambda e: self.txtEvent(e))
		#self.text.bind("<Return>", self.cb_return)
		self.text.configure(state="disabled")
		self.cmdentry = tk.Entry(self, textvariable = self.cmdvar)
		self.cmdentry.bind("<Return>", self.send)
		self.cmdentry.bind("<Up>", self.cb_back)
		self.cmdentry.bind("<Down>", self.cb_forward)
		#self.cmdentry.bind("<Tab>", self.cb_complete)
		self.bind_all("<Button-3>", self.paste)

		# Scroll bar
# 		self.scroll = tk.Scrollbar(self, command=self.text.yview)
# 		self.text.config(yscrollcommand=self.scroll.set)
# 		self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.text.pack(fill=tk.BOTH, expand=1)
		self.cmdentry.pack(fill=tk.BOTH)
		self.cmdentry.focus()

		if(debugSerial):	#try:
			if(isinstance(comport, str)):
				self.serial = SerialPort(comport, comport, asyncr=True)
			elif(isinstance(comport, serial.Serial) or isinstance(comport, SerialPort)):
				self.serial = comport
			else:
				pass
		else:	#except Exception as e:
			self.serial = []
			#self.setupPort()
			#self.serial = SerialPort(comport, comport, asyncr=True)


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
		settings = NewConsole(self.new).onReturn()
		if(debugOn) : print("SETTINGS: ", settings)

	def reset(self, event=None):
		self.text.delete(1.0, "end")
		self.cmdentry.delete(0, len(self.cmdvar.get()))

	def recv(self, event=None):
		self.text.configure(state="normal")
		self.text.configure(bg = COLORS[self.index])
		self.index += 1
		self.text.configure(state="disabled")
		self.after(2000, self.recv)

	def send(self, event=None):
		if(debugOn) : print(self.cmdvar.get())
		self.cmdentry.delete(0, len(self.cmdvar.get()))

	def setupPort(self, event=None):
		self.new = tk.Toplevel(self.master)
		settings = Setup(self.new).onReturn()
		if(debugOn) : print("PORTSETTINGS: ", settings)

	def setupWindow(self, event=None):
		self.new = tk.Toplevel(self.master)
		settings = Terminal(self.new).onReturn()
		if(debugOn) : print("WINDOWSETTINGS: ", settings)

	def txtEvent(self, event):
		if(event.state==12 and event.keysym=='c' ):
			return
		else:
			return "break"

	# History mechanism.

	def copy(self, event):
		pass

	def paste(self, event):
		if(self.copypaste == "") :
			try:
				win32clipboard.OpenClipboard()
				self.copypaste = win32clipboard.GetClipboardData()
				win32clipboard.CloseClipboard()
			except Exception as e:
				print(e)
		if(debugOn) : print("PASTE EVENT: ", self.copypaste)
		self.cmdentry.insert("end", self.copypaste)

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
