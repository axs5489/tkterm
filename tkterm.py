# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 17:23:33 2021

@author: axs5489

A Tkinter-based serial console

This software is in the public domain and is provided without express or 
implied warranty. Permission to use, modify, or distribute the software
for any purpose is hereby granted."""

debugOn = True
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk
#from tk import filedialog as fd
from tkinter import TclError
from tkinter.scrolledtext import ScrolledText
from tkcolors import COLORS
from tkSetup import tkDialog, About, LogSetup, NewSetup, PortSetup, TerminalSetup, WindowSetup
from SerialPort import SerialPort
from win import listSerialPorts
from idlelib.redirector import WidgetRedirector
import serial
import threading
import time
import win32clipboard

REVISION = "$Revision: 1.0 $"
VERSION = REVISION.split()[1]

exitFlag = 0
DEFAULT = ('Courier', 12, 'normal', (0, 0, 0), (255, 255, 255))

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
		self.insert = self.redirector.register("insert", lambda *args, **kwargs: "break")
		self.delete = self.redirector.register("delete", lambda *args, **kwargs: "break")

class tkTermMaster(tkDialog):
	def __init__(self, master=None, comport = "COM1", baud = 115200, bg="blue", **kwargs):
		tkDialog.__init__(self, master)
		self.windows = [tk.Toplevel(self.master)]
		self.consoles = [SerialConsole(self.windows[-1], self, comport, **kwargs)]
		self.master.withdraw()

	def add(self, **st):
		self.windows.append(tk.Toplevel(self.master))
		self.consoles.append(SerialConsole(self.windows[-1], self, st))

	def remove(self, window):
		global exitFlag
		ind = self.windows.index(window)
		if(debugOn) : print("WINDOWER REMOVING INDEX", ind)
		self.windows.pop(ind)
		self.consoles.pop(ind)
		if(self.windows == []) : exitFlag = 1

	def recv(self, **st):
		global exitFlag
		if(st and debugOn):
			for k,v in enumerate(*st): print(k,v)

		if(exitFlag == 1) :
			exitFlag = 0
			self.close()
		for c in self.consoles:
			c.recv()
		self.after(500, self.recv)

class tkTermNotebook(tkDialog):
	def __init__(self, master=None, comport = None, baud = 115200, bg="blue", **kwargs):
		tkDialog.__init__(self, master)
		self.consoles = [SerialConsole(self, comport = comport, **kwargs)]

class SerialConsole(tkDialog):
	def __init__(self, master=None, windower = None, comport = None, baud = 115200,
			bg="blue", **kwargs):
		tkDialog.__init__(self, master)
		self.master.geometry("513x714")
		self.master.resizable(False, False)
		self.windower = windower
		if(comport == None):
			comport = listSerialPorts()[0]
		self.portset = ('COM1', '115200', '8 bit', 'none', '1 bit', 'none')
		self.termset = [True, '80x80']
		self.winset = DEFAULT
		self.index = 0

		# Command history
		self.strcopy = ""
		self.strpaste = ""
		self.history = []
		self.historyindex = None
		self.current = ""
		self.prefixes = ["$ ", "# ", "... ", ">>> ", ">> ", "> "]

		# Menu bar
		menubar = tk.Menu(self.master)
		self.master.config(menu=menubar)

		fileMenu = tk.Menu(menubar, tearoff=False)
		fileMenu.add_command(label="New", command=self.setNew)#, accelerator ="")
		fileMenu.add_command(label="Log", command=self.setLog)
		fileMenu.add_command(label="Send file", command=self.sendfile)
		fileMenu.add_separator()
		fileMenu.add_command(label="Exit", command=self.close)
		menubar.add_cascade(label="File", underline=0, menu=fileMenu)

		editMenu = tk.Menu(menubar, tearoff=False)
		editMenu.add_command(label="Reset", command=self.reset)
		menubar.add_cascade(label="Edit", underline=0, menu=editMenu)

		setupMenu = tk.Menu(menubar, tearoff=False)
		setupMenu.add_command(label="Serial Port", command=self.setPort)
		setupMenu.add_command(label="Terminal", command=self.setTerminal)
		setupMenu.add_command(label="Window", command=self.setWindow)
		menubar.add_cascade(label="Setup", underline=0, menu=setupMenu)

		helpMenu = tk.Menu(menubar, tearoff=False)
		helpMenu.add_command(label="About", command=self.about)
		menubar.add_cascade(label="Help", underline=0, menu=helpMenu)

		self.bind_all("<Control-n>", self.setNew)
		self.bind_all("<Control-l>", self.setLog)
		self.bind_all("<Control-q>", self.close)
		self.bind_all("<Control-r>", self.reset)
		self.bind_all("<Control-o>", self.setPort)
		self.bind_all("<Control-t>", self.setTerminal)
		self.bind_all("<Control-w>", self.setWindow)

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
		self.text.pack(fill=tk.BOTH, expand=1)
		self.updateWindow()

		# Scroll bar
#		self.scroll = tk.Scrollbar(self, command=self.text.yview)
#		self.text.config(yscrollcommand=self.scroll.set)
#		self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

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
		try:
			print(comport)
			if(isinstance(comport, str) and comport in listSerialPorts()):
				self.setupSerial(comport)
			elif(isinstance(comport, serial.Serial) or isinstance(comport, SerialPort)):
				self.handle = comport
			else:
				pass
		except Exception:
			self.handle = []
			self.setPort()
			#self.handle = SerialPort(comport, comport, asyncr=True)

		# Configurable options.
		self.options = {"stdoutcolour": "#7020c0",	#purple, print statements
						"stderrcolour": "#c03020",	#red/orange, errors
						"morecolour": "#a0d0f0",	#light blue
						"badcolour": "#e0b0b0",		#pastel red
						"runcolour": "#90d090"}		#pastel green, last python
		#self.config(**self.options)
		#self.config(**kwargs)

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

	def about(self, event=None):
		new = tk.Toplevel(self.master)
		About(new)

	def close(self, event=None):
		self.closeSerial()
		if(isinstance(self.windower, tkTermMaster)):
			self.windower.remove(self.master)
		elif(isinstance(self.windower, tkTermNotebook)):
			self.windower.remove(self.master)
		self.master.destroy()

	def closeSerial(self):
		if(hasattr(self, "handle")) :
			self.handle.close()
			del self.handle

	def reset(self, event=None):
		self.text.delete(1.0, "end")
		self.cmdentry.delete(0, len(self.cmdvar.get()))

	def recv(self, event=None):
		self.text.configure(state="normal")
		if(debugOn) : self.text.configure(bg = COLORS[self.index])
		self.index += 1
		if(hasattr(self, "handle") and self.handle != None) :
			for line in self.handle.flush():
				self.text.insert("end", line)
				self.text.insert("end", "\n")
		#self.text.configure(state="disabled")
		self.text.configure(state="readonly")

	def send(self, event=None):
		cmd = self.cmdvar.get()
		if(debugOn) : print(cmd)
		self.cmdentry.delete(0, len(self.cmdvar.get()))
		if(hasattr(self, "handle")) :
			if(cmd) :
				self.handle.send(cmd)
			else:
				self.handle.send("\n")

	def sendfile(self, event=None):
		pass #TODO

	def setPopup(self, wincls, **kwargs):
		winop = tk.Toplevel(self.master)
		return wincls(winop, kwargs).settings()

	def setLog(self, event=None):
		if(self.logfile == None) :
			new = tk.Toplevel(self.master)
			LogSetup(new)
		else:
			pass #TODO close log

	def setNew(self, event=None):
		ret = self.setPopup(NewSetup)
		if(ret != None) :
			#if(self.logfile != None) : self.setLog()
			if(debugOn) : print("NEW: ", ret)
			if(isinstance(self.windower, tkTermMaster)) :
				self.windower.add(comport = ret[0], baud = ret[1])
			elif(isinstance(self.windower, tkTermNotebook)) :
				self.windower.add(comport = ret[0], baud = ret[1])
			else:
				new = tk.Toplevel(self.master)
				SerialConsole(new, comport = ret[0], baud = ret[1])

	def setPort(self, event=None):
		ret = self.setPopup(PortSetup, iv = self.portset)
		if(ret != None) :
			if(debugOn) : print("PORT: ", ret)
			self.portset = ret
			self.setupSerial()

	def setTerminal(self, event=None):
		ret = self.setPopup(TerminalSetup, iv = self.termset)
		if(ret != None) :
			if(debugOn) : print("NEW TERMINAL")
			self.termset = ret
			#TODO configure terminal

	def setWindow(self, event=None):
		ret = self.setPopup(WindowSetup, iv = self.winset)
		if(ret != None) :
			self.winset = ret
			if(debugOn) : print("WINDOWSETTINGS: ", ret)
			self.updateWindow()

	def setupSerial(self, comport="COM1", baud=115200, data=8, par="N",
				 stop=1, xon=None, rts=None, **kwargs):
		if(comport in listSerialPorts()) :
			self.closeSerial()
			#try:
				#comport, baud, data, par, stop, xon, rts = []
			self.handle = SerialPort("tkTerm", comport, baud, data, par,
								 stop, xon, rts)
# 			except Exception as e:
# 				print("SERIAL PORT ERROR!", e)
# 				try:
# 					self.handle = serial.Serial(port=comport, baudrate=baud,
# 					bytesize=data, parity=par, stopbits=stop, timeout=3.0,
# 					rtscts=rts, xonxoff=xon, writeTimeout=3.0)
# 				except Exception as se:
# 					print("COM PORT ERROR!", se)
			self.master.title("tkTerm {}".format(comport))
			print(self.handle)
		else:
			print("NOT AN ACTIVE SERIAL PORT")
	
	def updateWindow(self):
		self.text.configure(bg = '#%02x%02x%02x'%self.winset[4],
					 fg = '#%02x%02x%02x'%self.winset[3],
					 font = self.winset[0:3])

	# History mechanism.

	def copy(self, event):
		if(debugOn) : print("COPY EVENT: ", event.num)
		if(event.num):
			try:
				win32clipboard.OpenClipboard()
				win32clipboard.EmptyClipboard()
				self.strcopy = self.text.selection_get()
				if(debugOn) : print(self.strcopy)
				win32clipboard.SetClipboardData(1, self.strcopy)
			except TclError:
				pass
			except Exception as e:
				print(e)
			finally:
				win32clipboard.CloseClipboard()
			#self.text.selection_clear()

	def paste(self, event):
		if(self.strcopy == "") :
			try:
				win32clipboard.OpenClipboard()
				self.strcopy = win32clipboard.GetClipboardData().strip()
			except Exception as e:
				print(e)
			finally:
				win32clipboard.CloseClipboard()
				#if(debugOn) : print("PASTE EVENT: ", self.strcopy)
		#else :
		self.strpaste = self.strcopy
		#print(self.strpaste)
		index = self.strpaste.find('\n')
		while(index != -1):
			self.cmdentry.insert("end", self.strpaste[0:index])
			self.strpaste = self.strpaste[index+1:]
			self.send()
			time.sleep(0.01)
			index = self.strpaste.find('\n')
		if(len(self.strpaste)) : self.cmdentry.insert("end", self.strpaste)

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
		c = SerialConsole(dict={})
		c.dict["console"] = c
		c.pack(fill=tk.BOTH, expand=1)
		c.master.title("tkTerm Console v%s" % VERSION)
		self.root.mainloop()

def start_console():
	root = tk.Tk()
	app = SerialConsole(root)
	app.pack(fill=tk.BOTH, expand=1)
	#app.master.title("tkTerm v%s" % VERSION)
	root.after(1000, app.recv)
	tk.mainloop()

def start_master():
	root = tk.Tk()
	app = tkTermMaster(root, comport = "COM35")
	app.pack(fill=tk.BOTH, expand=1)
	#app.master.title("tkTerm v%s" % VERSION)
	root.after(2000, app.recv)
	tk.mainloop()

def start_notebook():
	root = tk.Tk()
	app = tkTermNotebook(root)
	app.pack(fill=tk.BOTH, expand=1)
	#app.master.title("tkTerm v%s" % VERSION)
	root.after(1000, app.recv)
	tk.mainloop()

		
if __name__ == "__main__":
	#start_console()
	start_master()
	#start_notebook()
