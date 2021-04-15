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
from tkinter import TclError
from tkinter.scrolledtext import ScrolledText
from tkcolors import COLORS
from tkSetup import tkDialog, LogSetup, NewSetup, PortSetup, TerminalSetup
from SerialPort import SerialPort
from idlelib.redirector import WidgetRedirector
import serial
import threading
import time
import win32clipboard

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

class ReadOnlyScrolledText(ScrolledText):
	def __init__(self, master=None, **kwargs):
		ScrolledText.__init__(self, master, **kwargs)
		self.redirector = WidgetRedirector(self)
		self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
		self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

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
		fileMenu.add_command(label="New", command=self.newConsole)#, accelerator ="")
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
		#self.textvar = tk.StringVar()
		#self.text = ScrolledText(self, insertontime=200, insertofftime=150, bg=bg)
		self.text = ReadOnlyScrolledText(self)#, textvariable = self.textvar)#, state="readonly")
		self.text.configure(state="readonly")
		self.text.insert("end", "Python Console\n")
		self.text.insert("end", ">>> ")
		self.text.bind("<ButtonRelease-1>", self.copy)
		#self.text.bind("<Key>", lambda e: self.txtEvent(e))
		#self.text.bind("<Return>", self.cb_return)
		self.text.configure(state="readonly")

		# Scroll bar
#		self.scroll = tk.Scrollbar(self, command=self.text.yview)
#		self.text.config(yscrollcommand=self.scroll.set)
#		self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.text.pack(fill=tk.BOTH, expand=1)

		# Command Entry Box
		self.cmdentry = tk.Entry(self, textvariable = self.cmdvar)
		self.cmdentry.bind("<Return>", self.send)
		self.cmdentry.bind("<Up>", self.cb_back)
		self.cmdentry.bind("<Down>", self.cb_forward)
		#self.cmdentry.bind("<Tab>", self.cb_complete)
		self.bind_all("<Control-c>", self.copy)
		self.bind_all("<Control-v>", self.paste)
		self.bind_all("<Button-3>", self.paste)
		self.cmdentry.pack(fill=tk.BOTH)
		self.cmdentry.focus()

		self.logfile = None
		self.settings = ('COM1', '115200', '8 bit', 'none', '1 bit', 'none')
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
		#self.config(**self.options)
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
		if(self.logfile == None) :
			self.new = tk.Toplevel(self.master)
			LogSetup(self.new)
		else:
			pass

	def newConsole(self, event=None):
		self.new = tk.Toplevel(self.master)
		st = NewSetup(self.new).settings()
		if(debugOn) : print("SETTINGS: ", st)
		if(self.logfile != None) : self.logConsole()
		#self.setupSerial(*st)

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

	def setupSerial(self, comport="COM1", baud=115200, data=8,
				 parity="N", stop=1, xonxoff=None, rtscts=None):
		if(self.serial.handle.isOpen()) : self.serial.close()
		#self.setupSerial(*st)

	def setupPort(self, event=None):
		self.new = tk.Toplevel(self.master)
		st = PortSetup(self.new).settings()
		if(debugOn) : print("PORTSETTINGS: ", st)
		#self.setupSerial(*st)

	def setupWindow(self, event=None):
		self.new = tk.Toplevel(self.master)
		st = TerminalSetup(self.new).settings()
		if(debugOn) : print("WINDOWSETTINGS: ", st)
		self.text.configure(bg= st[0], fg = [1], font = st[2])

	# History mechanism.

	def copy(self, event):
		if(debugOn) : print("COPY EVENT: ", event.num)
		if(event.num):
			try:
				win32clipboard.OpenClipboard()
				win32clipboard.EmptyClipboard()
				self.copypaste = self.text.selection_get()
				if(debugOn) : print(self.copypaste)
				win32clipboard.SetClipboardData(1, self.copypaste)
			except TclError:
				pass
			except Exception as e:
				print(e)
			finally:
				win32clipboard.CloseClipboard()
			#self.text.selection_clear()

	def paste(self, event):
		if(self.copypaste == "") :
			try:
				win32clipboard.OpenClipboard()
				self.copypaste = win32clipboard.GetClipboardData()
			except Exception as e:
				print(e)
			finally:
				win32clipboard.CloseClipboard()
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
	app = NewSetup(root)
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
	#root.after(1000, app.recv)
	tk.mainloop()

		
if __name__ == "__main__":
	start_console()
