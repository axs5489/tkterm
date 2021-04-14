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
from tkcolors import SIMPLE_COLORS
from win import listSerialPorts


PORTS = ["COM1"]
SPEEDS = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400,
		   57600, 115200, 230400, 460800, 921600]
FONTS = ["Calibri", "Terminal"]
SIZES = list(range(10,20))

class LabelFrame(tk.Frame):
	def __init__(self, master=None, font = ("Calibri", 10), text="", size="100x50", **kwargs):
		tk.Frame.__init__(self, master)
		self.master = master
		self.pack(fill=tk.BOTH, expand=1)
		self.master.geometry(size)
		self.master.resizable(False, False)
		self.label = tk.Label(self, font = font, text = text)#, width = 12, height = 9)
		self.label.place(x=25, y=25, anchor="center")

	def configure(self, *args, **kwargs):
		return self.label.configure(args, kwargs)

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
		t = (self.port.get(), int(self.speed.get()))
		if(debugOn) : print(t)
		return t

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
		self.types = [str, int, int, str, int, str]

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
		t = tuple(self.types[i](s.get()[0]) if i in [2,4]
			else self.types[i](s.get())
			for i, s in enumerate(self.vars))
		if(debugOn) : print(t)
		return t

class LogSetup(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Log tkTerm Console")
		self.master.geometry("400x600")
		self.master.resizable(False, False)



class ColorScale(tk.Frame):
	def __init__(self, master=None, name="", **kwargs):
		tk.Frame.__init__(self, master, width = 100, height = 20)
		self.master = master
		#self.pack(fill=tk.BOTH, expand=1)

		self.l_name = tk.Label(self, width = 5, text = name)
		self.l_value = tk.Label(self, width = 4, text =0)
		self.scale = tk.Scale(self, from_= 0, to = 255, #label=name,
			orient=tk.HORIZONTAL, length = 200, showvalue=0, #tickinterval=20,
			resolution=1, command=self.updateLabel)

		self.l_name.grid()
		self.l_value.grid(row=0, column=1)
		self.scale.grid(row=0, column=2)

	def updateLabel(self, value):
		self.l_value.config(text = value)
		self.master.updateRGBcontinuous()

	def get(self):
		return int(self.scale.get())

class TerminalSetup(tkDialog):
	def __init__(self, master=None, font=("Terminal", 14), **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("Terminal tkTerm Console")
		self.master.geometry("430x460")
		self.master.resizable(False, False)
		self.types = [str, int, int, str, int, str]

		self.v_active = tk.IntVar()
		self.v_size = tk.IntVar()
		self.v_font = tk.StringVar()
		self.l_font = tk.Label(self, width = 5, text = "Font:")
		self.l_size = tk.Label(self, width = 5, text = "Size:")
		self.font =ttk.Combobox(self, width=8, state="readonly",
							values = FONTS, textvariable = self.v_font)
		self.fontsize =ttk.Combobox(self, width=8, state="readonly",
							values = SIZES, textvariable = self.v_size)
		self.text = tk.Radiobutton(self, text = "Text",
							 variable=self.v_active, value=1, command=self.sel)
		self.background = tk.Radiobutton(self, text = "Background",
							 variable=self.v_active, value=2, command=self.sel)
		self.text.invoke()
		self.font.current(0)
		self.fontsize.current(0)
		self.font.bind('<<ComboboxSelected>>', self.updateFont)
		self.fontsize.bind('<<ComboboxSelected>>', self.updateFont)
		self.settings = list(font)
		self.settings.append((0, 0, 0))
		self.settings.append((255, 255, 255))

		self.red = ColorScale(self, "RED:")
		self.green = ColorScale(self, "GREEN:")
		self.blue = ColorScale(self, "BLUE:")
		self.sample = tk.Label(self, font = font, text = "ABC", width = 12, height = 9)
		self.updateSample()

		self.text.grid(row=0, column=1, columnspan = 5, padx=5, sticky="W")
		self.background.grid(row=1, column=1, columnspan = 5, padx=5, sticky="W")
		self.l_font.grid(row=0, column=4, columnspan = 2, sticky="W")
		self.l_size.grid(row=1, column=4, columnspan = 2, sticky="W")
		self.font.grid(row=0, column=5, columnspan = 3, sticky="W")
		self.fontsize.grid(row=1, column=5, columnspan = 3, sticky="W")
		self.red.grid(row=2, column=0, columnspan = 8, padx=5)
		self.green.grid(row=3, column=0, columnspan = 8, padx=5)
		self.blue.grid(row=4, column=0, columnspan = 8, padx=5)
		self.sample.grid(row=0, column=8, columnspan = 3, rowspan = 5, pady=10, sticky="E")

		for r in range(6):
			for c in range(10):
				index = 10*r + c
				#print(index)
				button = tk.Button(self, bg = SIMPLE_COLORS[index], width =2,
						 command=lambda i=index: self.updateRGBpreset(i))
				button.grid(row=5+r, column=c+1, pady=5)

		self.b_cancel = tk.Button(self, text = "Cancel", command = self.close, width = 6)
		self.b_ok = tk.Button(self, text = "Ok", command = self.onOK, width = 6)
		self.b_cancel.grid(row=11, column=4, columnspan = 2, pady=10)
		self.b_ok.grid(row=11, column=6, columnspan = 2, pady=10)

	def updateSample(self):
		self.sample.configure(fg = "#%02x%02x%02x"%(self.settings[2]))
		self.sample.configure(bg = "#%02x%02x%02x"%(self.settings[3]))

	def updateRGBcontinuous(self):
		self.settings[self.active + 1] = (self.red.get(),
									self.green.get(), self.blue.get())
		self.updateSample()

	def updateFont(self, event):
		print("Font ", self.v_font.get(), self.v_size.get())
		self.settings[0] = self.v_font.get()
		self.settings[1] = int(self.v_size.get())
		self.sample.configure(font = (self.settings[0], self.settings[1]))

	def updateRGBpreset(self, index):
		colorname = SIMPLE_COLORS[index]
		color = self.winfo_rgb(colorname)
		self.red.scale.set(color[0]/256)
		self.green.scale.set(color[1]/256)
		self.blue.scale.set(color[2]/256)
		if(self.active == 1):
			self.sample.configure(fg = colorname)
		elif(self.active == 2):
			self.sample.configure(bg = colorname)

	def sel(self):
		self.active = self.v_active.get()
		color = self.settings[self.active + 1]
		self.red.scale.set(color[0])
		self.green.scale.set(color[1])
		self.blue.scale.set(color[2])


	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = tuple(i.get() for i in self.vars)
		if(debugOn) : print(t)
		return t


class About(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title("About tkTerm")
		self.master.geometry("400x600")
		self.master.resizable(False, False)

		
if __name__ == "__main__":
	test = 4
	root = tk.Tk()
	if(test == 1) :
		app = NewSetup(root)
	elif(test == 2) :
		app = PortSetup(root)
	elif(test == 3) :
		app = LogSetup(root)
	elif(test == 4) :
		app = TerminalSetup(root)
	elif(test == 5) :
		app = About(root)
	elif(test == 6) :
		app = LabelFrame(root, text = "ABC")
	app.pack(fill=tk.BOTH, expand=1)
	tk.mainloop()
