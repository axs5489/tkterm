# -*- coding: utf-8 -*-
'''
Created on Sat Apr 10 15:56:24 2021

@author: axs5489
'''

debugOn = True
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk
from tkinter import font, ttk
from win import listSerialPorts


PORTS = ['COM1']
SPEEDS = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400,
		   57600, 115200, 230400, 460800, 921600]
FONTS = ['Arial', 'Calibri', 'Cambria', 'Comic Sans', 'Courier', 'Georgia', 'Helvetica', 'Impact', 'Ink Free', 'Terminal', 'Times', 'Verdana']
SIZES = list(range(10,20))
WEIGHT = ['normal', 'bold']

SIMPLE_COLORS = ['white', 'light grey', 'gray60', 'gray40', 'black',
 '#ffdcaa', 'burlywood', 'burlywood4', 'sienna', 'OrangeRed4',
 '#ffb8b0', '#ff8080', '#ff4040', '#ff0000', 'red3',
 '#ffc8a0', '#ffa06e', '#ff8040', '#ff5c00', 'OrangeRed3',
 'burlywood1', '#ffbe55', '#ffb420', '#ff8c00','dark orange3',

 '#ffffc0', '#ffff80', 'yellow', 'gold','#c8a000',
 '#aaffc8', 'SeaGReen1', 'SeaGReen3', 'chartreuse4', 'dark green',
 '#a0ffff', '#6affff', 'cyan', 'cyan3', '#0064a0',
 '#a0dcff', '#80c0ff', '#4060ff', 'blue2', 'dark blue',
 '#e6c8e6', '#d896d8', 'MediumOrchid', 'dark violet', 'purple']


class tkDialog(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master)
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.close)
		self.pack(fill=tk.BOTH, expand=1)
		self.returnNone = True 		# Return nothing on close by default

	def onOK(self):
		self.returnNone = False 	# RETURN SOMETHING
		self.close()

	def close(self, event=None):
		self.master.destroy()


class ColorScale(tk.Frame):
	def __init__(self, master=None, name='', **kwargs):
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


class About(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title('About tkTerm')
		self.master.geometry('400x600')
		self.master.resizable(False, False)


class NewSetup(tkDialog):
	YBUT = 100
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title('New Console Settings')
		self.master.geometry('230x150')
		self.master.resizable(False, False)

		self.l_speed = tk.Label(self, text = 'Speed:')
		self.l_speed.place(x=30, y=20)
		self.speed = tk.StringVar()
		self.box = ttk.Combobox(self, width=10, state='readonly',
							values = SPEEDS, textvariable = self.speed)
		self.box.current(11)
		self.box.place(x=100, y=20)
		self.l_ports = tk.Label(self, text = 'Port(s):')
		self.l_ports.place(x=30, y=50)
		self.port = tk.StringVar()
		self.portsel = ttk.Combobox(self, width=10, state='readonly',
							values = PORTS, textvariable = self.port)
		self.portsel.place(x=100, y=50)
		self.refresh()

		self.b_cancel = tk.Button(self, text = 'Cancel', command = self.close, width = 6)
		self.b_cancel.place(x=30, y=self.YBUT)
		self.b_refresh = tk.Button(self, text = 'Refresh', command = self.refresh, width = 6)
		self.b_refresh.place(x=90, y=self.YBUT)
		self.b_ok = tk.Button(self, text = 'Ok', command = self.onOK, width = 6)
		self.b_ok.place(x=150, y=self.YBUT)

	def refresh(self):
		global PORTS
		PORTS = []
		pl = listSerialPorts()
		print(pl)
		if(pl == []) :
			PORTS.append('COM1')
		else:
			for p in pl : PORTS.append(p)
		print("GLOBAL PORTS: ", PORTS)
		self.portsel['values'] = PORTS
		self.port.set(PORTS[0])

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = (self.port.get()[2:-3], int(self.speed.get()))
		if(debugOn) : print(t)
		return t


class PortSetup(tkDialog):
	XLABEL = 30
	XOPT = 120
	YBUT = 210
	FONT= ('calibri', 12)
	DATA = ['7 bit', '8 bit']
	PARITY = ['none', 'odd', 'even', 'mark', 'space']
	STOP = ['1 bit', '2 bit']
	FLOW = ['none', 'Xon/Xoff', 'RTS/CTS', 'DSR/DTR']
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title('Serial Port Setup')
		self.master.geometry('230x250')
		self.master.resizable(False, False)
		self.index = 0
		self.labels = [None, None, None, None, None, None]
		self.vars = [None, None, None, None, None, None]
		self.boxes = [None, None, None, None, None, None]
		self.types = [str, int, int, str, int, str]

		self.addOption('Port:', PORTS, 20)
		self.addOption('Speed:', SPEEDS, 50, 11)
		self.addOption('Data:', self.DATA, 80, 1)
		self.addOption('Parity:', self.PARITY, 110)
		self.addOption('Stop bits:', self.STOP, 140)
		self.addOption('Flow control:', self.FLOW, 170)
		self.refresh()

		self.b_cancel = tk.Button(self, text = 'Cancel', command = self.close, width = 6)
		self.b_cancel.place(x=30, y=self.YBUT)
		self.b_refresh = tk.Button(self, text = 'Refresh', command = self.refresh, width = 6)
		self.b_refresh.place(x=90, y=self.YBUT)
		self.b_ok = tk.Button(self, text = 'Ok', command = self.onOK, width = 6)
		self.b_ok.place(x=150, y=self.YBUT)

	def addOption(self, lbl, lst, y, dflt=0):
		self.labels[self.index] = tk.Label(self, text = lbl)
		self.labels[self.index].place(x=self.XLABEL, y=y)
		self.vars[self.index] = tk.StringVar()
		self.boxes[self.index] = ttk.Combobox(self, width=10, state='readonly',
							values = lst, textvariable = self.vars[self.index])
		self.boxes[self.index].current(dflt)
		self.boxes[self.index].place(x=self.XOPT, y=y)
		self.index += 1

	def refresh(self):
		global PORTS
		PORTS = []
		pl = listSerialPorts()
		if(pl == []) :
			PORTS.append('COM1')
		else:
			for p in pl : PORTS.append(p)
		print("GLOBAL PORTS: ", PORTS)
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
		self.master.wm_title('tkTerm Log Setup')
		self.master.geometry('400x600')
		self.master.resizable(False, False)


class TerminalSetup(tkDialog):
	def __init__(self, master=None, **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title('tkTerm Terminal Settings')
		self.master.geometry('430x460')
		self.master.resizable(False, False)

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = tuple(self.tksettings)
		if(debugOn) : print(t)
		return t


class WindowSetup(tkDialog):
	def __init__(self, master=None,
			   st=('Courier', 14, 'normal', (0, 0, 0),(255, 255, 255)), **kwargs):
		tkDialog.__init__(self, master)
		self.master.wm_title('tkTerm Window Settings')
		self.master.geometry('430x460')
		self.master.resizable(False, False)
		self.tksettings = list(st)
		self.tksettings.append((0, 0, 0))
		self.tksettings.append((255, 255, 255))

		self.red = ColorScale(self, 'RED:')
		self.green = ColorScale(self, 'GREEN:')
		self.blue = ColorScale(self, 'BLUE:')
		self.sampleframe = tk.Frame(self, width=120, height=120)
		self.sample = tk.Label(self.sampleframe, font = self.tksettings[0:3],
						 text = 'ABC', relief=tk.SUNKEN, width = 12, height = 9)
		self.sample.pack(fill=tk.BOTH, expand=1)
		self.updateSample()

		self.v_active = tk.IntVar()
		self.v_size = tk.IntVar()
		self.v_font = tk.StringVar()
		self.v_weight = tk.StringVar()
		self.l_font = tk.Label(self, width = 5, text = 'Font:')
		self.l_size = tk.Label(self, width = 5, text = 'Size:')
		self.font =ttk.Combobox(self, width=8, state='readonly',
							values = FONTS, textvariable = self.v_font)
		self.fontsize =ttk.Combobox(self, width=8, state='readonly',
							values = SIZES, textvariable = self.v_size)
		self.text = tk.Radiobutton(self, text = 'Text',
							 variable=self.v_active, value=1, command=self.sel)
		self.background = tk.Radiobutton(self, text = 'Background',
							 variable=self.v_active, value=2, command=self.sel)
		self.b_bold = tk.Checkbutton(self, text = 'Bold', command = self.updateFont, width = 6,
							   onvalue = 'bold', offvalue = 'normal', variable = self.v_weight)
		self.b_reverse = tk.Button(self, text = 'Reverse', command = self.reverse, width = 6)
		self.text.invoke()
		if(self.tksettings[2] == 'normal') : self.b_bold.deselect()
		elif(self.tksettings[2] == 'bold') : self.b_bold.select()
		self.font.current(FONTS.index(self.tksettings[0]))
		self.fontsize.current(SIZES.index(self.tksettings[1]))
		self.font.bind('<<ComboboxSelected>>', self.updateFont)
		self.fontsize.bind('<<ComboboxSelected>>', self.updateFont)

		self.text.grid(row=0, column=1, columnspan = 5, padx=5, sticky='W')
		self.background.grid(row=1, column=1, columnspan = 5, padx=5, sticky='W')
		self.l_font.grid(row=0, column=4, columnspan = 2, sticky='W')
		self.l_size.grid(row=1, column=4, columnspan = 2, sticky='W')
		self.font.grid(row=0, column=5, columnspan = 3, sticky='W')
		self.fontsize.grid(row=1, column=5, columnspan = 3, sticky='W')
		self.b_bold.grid(row=0, column=8, columnspan = 3, pady=10)
		self.b_reverse.grid(row=1, column=8, columnspan = 3, pady=10)
		self.red.grid(row=2, column=0, columnspan = 8, padx=5)
		self.green.grid(row=3, column=0, columnspan = 8, padx=5)
		self.blue.grid(row=4, column=0, columnspan = 8, padx=5)
		self.sampleframe.grid(row=2, column=8, columnspan = 3, rowspan = 3, pady=10, sticky='E')
		#self.sampleframe.grid_propagate(0)
		self.sampleframe.pack_propagate(0)

		for r in range(5):
			for c in range(10):
				index = r + 5*c
				#print(index)
				#print(SIMPLE_COLORS[index])
				button = tk.Button(self, bg = SIMPLE_COLORS[index], width =2,
						 command=lambda i=index: self.updateRGBpreset(i))
				button.grid(row=5+r, column=c+1, pady=5)

		self.b_cancel = tk.Button(self, text = 'Cancel', command = self.close, width = 6)
		self.b_ok = tk.Button(self, text = 'Ok', command = self.onOK, width = 6)
		self.b_cancel.grid(row=11, column=4, columnspan = 2, pady=10)
		self.b_ok.grid(row=11, column=6, columnspan = 2, pady=10)

	def refresh(self):
		self.updateSample()
		self.updateScales()

	def reverse(self):
		t = self.tksettings[3]
		self.tksettings[3] = self.tksettings[4]
		self.tksettings[4] = t
		self.refresh()

	def sel(self):
		self.active = self.v_active.get()
		if(debugOn) : print(self.tksettings[self.active + 2])
		self.updateScales()

	def updateFont(self, event=None):
		#if(debugOn) : print('Font ', self.v_font.get(), self.v_size.get(), self.v_weight.get())
		self.tksettings[0] = self.v_font.get()
		self.tksettings[1] = int(self.v_size.get())
		self.tksettings[2] = self.v_weight.get()
		self.sample.configure(font = self.tksettings[0:3])

	def updateSample(self):
		self.sample.configure(fg = '#%02x%02x%02x'%(self.tksettings[3]))
		self.sample.configure(bg = '#%02x%02x%02x'%(self.tksettings[4]))

	def updateScales(self):
		self.red.scale.set(self.tksettings[self.active + 2][0])
		self.green.scale.set(self.tksettings[self.active + 2][1])
		self.blue.scale.set(self.tksettings[self.active + 2][2])

	def updateRGBcontinuous(self):
		self.tksettings[self.active + 2] = (self.red.get(),
									self.green.get(), self.blue.get())
		self.updateSample()

	def updateRGBpreset(self, index):
		colorname = SIMPLE_COLORS[index]
		color = tuple(int(v/256) for v in self.winfo_rgb(colorname))
		if(debugOn) : print('#%02x%02x%02x'% color)
		self.red.scale.set(color[0])
		self.green.scale.set(color[1])
		self.blue.scale.set(color[2])

		if(self.active == 1):
			self.sample.configure(fg = colorname)
		elif(self.active == 2):
			self.sample.configure(bg = colorname)

	def settings(self):
		self.master.deiconify()
		self.master.wait_window()
		if(self.returnNone) : return None
		t = tuple(self.tksettings)
		if(debugOn) : print(t)
		return t


		
if __name__ == '__main__':
	test = 2
	root = tk.Tk()
	#print(font.families())
	if(test == 1) :
		app = NewSetup(root)
	elif(test == 2) :
		app = PortSetup(root)
	elif(test == 3) :
		app = LogSetup(root)
	elif(test == 4) :
		app = TerminalSetup(root)
	elif(test == 5) :
		app = WindowSetup(root)
	elif(test == 6) :
		app = About(root)
	app.pack(fill=tk.BOTH, expand=1)
	if(hasattr(app, 'recv')) :
		print('Entered')
		root.after(1000, app.recv)
	tk.mainloop()
