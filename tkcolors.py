# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 20:09:45 2021

@author: axs5489
"""
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk

COLORS = ['old lace', 'linen', 'seashell', 'LavenderBlush2','seashell2',
	'LavenderBlush3', 'ivory3', 'seashell3','mint cream', 'azure', 'alice blue',
	'azure2', 'honeydew2', 'azure3', 'honeydew3', 'azure4', 'honeydew4', 'ivory4',
	'LavenderBlush4','ivory', 'light yellow', 'cornsilk', 'antique white',
	'papaya whip', 'blanched almond','light goldenrod yellow', 'lemon chiffon',
	'ivory2', 'LightYellow2', 'cornsilk2', 'LemonChiffon2', 'LightYellow3', 'cornsilk3',
	'LemonChiffon3', 'LightYellow4', 'cornsilk4', 'LemonChiffon4',
	'bisque', 'peach puff', 'AntiqueWhite2', 'bisque2', 'PeachPuff2', 'AntiqueWhite3',
	'bisque3', 'PeachPuff3', 'MistyRose4', 'AntiqueWhite4', 'bisque4', 'PeachPuff4',
	'wheat1', 'navajo white', 'burlywood1', 'wheat2', 'NavajoWhite2', 'burlywood2',
	'wheat3', 'NavajoWhite3', 'burlywood3', 'wheat4', 'NavajoWhite4', 'burlywood4',
	'lavender',
	'lavender blush', 'misty rose', 'MistyRose2', 'MistyRose3',
	'light cyan', 'LightCyan2', 'LightCyan3', 'LightCyan4',
	'SlateGray1', 'SlateGray2', 'SlateGray3', 'SlateGray4',
	'slate gray', 'light slate gray',
	'light steel blue', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
	'LightSkyBlue1', 'LightSkyBlue2', 'LightSkyBlue3', 'LightSkyBlue4',
	'sky blue', 'light sky blue', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4',
	'SteelBlue1', 'SteelBlue2', 'SteelBlue3', 'steel blue', 'SteelBlue4',
	'RoyalBlue1', 'RoyalBlue2', 'royal blue', 'RoyalBlue3', 'RoyalBlue4',
	'blue', 'blue2', 'medium blue', 'blue4', 'navy', 'midnight blue',
	'cornflower blue', 'dodger blue', 'dodgerBlue2', 'dodgerBlue3', 'dodgerBlue4',
	'deep sky blue', 'deepSkyBlue2', 'deepSkyBlue3', 'deepSkyBlue4',
	'LightBlue1', 'powder blue', 'light blue', 'LightBlue2', 'LightBlue3',
	'PaleTurquoise1', 'pale turquoise', 'PaleTurquoise3', 'PaleTurquoise4',
	'CadetBlue1', 'CadetBlue2', 'CadetBlue3', 'cadet blue', 'CadetBlue4',
	'darkSlateGray1', 'darkSlateGray2', 'darkSlateGray3', 'darkSlateGray4', 'dark slate gray',
	'cyan', 'turquoise1', 'cyan2', 'turquoise2', 'turquoise', 'medium turquoise',
	'cyan3', 'dark turquoise', 'turquoise3', 'light sea green', 'cyan4', 'turquoise4',
	'aquamarine', 'aquamarine2', 'medium aquamarine', 'aquamarine4',
	'darkSeaGreen1', 'darkSeaGreen2', 'darkSeaGreen3', 'dark sea green', 'darkSeaGreen4',
	'pale green', 'light green', 'PaleGreen3', 'PaleGreen4',
	'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'medium sea green', 'sea green',
	'medium spring green', 'spring green', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
	'chartreuse', 'lawn green', 'chartreuse2', 'chartreuse3', 'chartreuse4',
	'green1', 'green2', 'green3', 'green4', 'green', 'dark green', 'lime green', 'forest green',
	'darkOliveGreen1', 'darkOliveGreen2', 'darkOliveGreen3', 'darkOliveGreen4', 'dark olive green',
	'green yellow', 'Olivedrab1', 'Olivedrab2', 'Olivedrab3', 'olive drab', 'Olivedrab4',
	'yellow', 'yellow2', 'yellow3', 'yellow4',
	'gold', 'gold2', 'gold3', 'gold4', 'pale goldenrod',
	'khaki1', 'LightGoldenrod1', 'khaki', 'light goldenrod', 'khaki3', 'LightGoldenrod3',
	'dark khaki', 'khaki4', 'LightGoldenrod4',
	'goldenrod1', 'goldenrod2', 'goldenrod', 'goldenrod3', 'dark goldenrod', 'darkGoldenrod4', 'goldenrod4',
	'darkGoldenrod1', 'darkGoldenrod2', 'darkGoldenrod3',
	'IndianRed1', 'IndianRed2', 'indian red', 'IndianRed3', 'IndianRed4',
	'sienna', 'sienna1', 'sienna2', 'sienna3', 'sienna4',
	'tan', 'sandy brown','tan1','tan2', 'tan3', 'tan4',
	'chocolate1', 'chocolate2', 'chocolate', 'chocolate4', 'light salmon', 'dark salmon',
	'salmon', 'salmon1', 'salmon2', 'LightSalmon3', 'salmon3', 'LightSalmon4', 'salmon4',
	'orange', 'orange2', 'orange3', 'orange4', 'dark orange', 'darkOrange1', 'darkOrange2', 'darkOrange3', 'darkOrange4',
	'orange red', 'OrangeRed2', 'OrangeRed3', 'OrangeRed4',
	'light coral', 'coral', 'coral1', 'coral2', 'coral3', 'coral4',
	'tomato', 'tomato2', 'tomato3', 'tomato4',
	'brown1', 'brown2', 'brown3', 'brown', 'brown4',
	'firebrick1', 'firebrick2', 'firebrick3', 'firebrick', 'firebrick4',
	'red', 'red2', 'red3', 'red4', 'maroon',
	'hot pink', 'HotPink2', 'HotPink3', 'HotPink4',
	'deep pink', 'deepPink2', 'deepPink3', 'deepPink4',
	'thistle',  'thistle1', 'thistle2', 'thistle3', 'thistle4',
	'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'rosy brown', 'RosyBrown4',
	'pink', 'light pink', 'LightPink1', 'pink2', 'LightPink2', 'pink3','LightPink3', 'pink4', 'LightPink4',
	'pale violet red', 'PaleVioletRed1', 'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4',
	'magenta', 'magenta2', 'magenta3', 'magenta4', 'purple',
	'medium violet red',
	'violet red', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
	'maroon1', 'maroon2', 'maroon3', 'maroon4',
	'plum1', 'plum2', 'plum3', 'plum4', 'orchid1', 'orchid2', 'orchid3', 'orchid4',
	'MediumOrchid1', 'MediumOrchid2', 'medium orchid', 'MediumOrchid3', 'MediumOrchid4',
	'darkOrchid1', 'darkOrchid2', 'darkOrchid', 'darkOrchid4',
	'purple1', 'purple2', 'blue violet', 'purple3', 'purple4', 'dark violet',
	'medium purple', 'MediumPurple1', 'MediumPurple2', 'MediumPurple3', 'MediumPurple4',
	'light slate blue', 'medium slate blue', 'slate blue', 'dark slate blue', 'black',
	'gray1' ,'gray2' ,'gray3' ,'gray4' ,'gray5' ,'gray6' ,'gray7' ,'gray8' ,'gray9' ,'gray10',
	'gray11','gray12','gray13','gray14','gray15','gray16','gray17','gray18','gray19','gray20',
	'gray21','gray22','gray23','gray24','gray25','gray26','gray27','gray28','gray29','gray30',
	'gray31','gray32','gray33','gray34','gray35','gray36','gray37','gray38','gray39','gray40',
	'gray41','gray42','gray43','gray44','gray45','gray46','gray47','gray48','gray49','gray',
	'gray51','gray52','gray53','gray54','gray55','gray56','gray57','gray58','gray59','gray60',
	'gray61','gray62','gray63','gray64','gray65','gray66','gray67','gray68','gray69','gray70',
	'gray71','gray72','gray73','gray74','gray75','gray76','gray77','gray78','gray79','gray80',
	'gray81','gray82','light grey','gray83','gray84','gray85','gray86','gray87','gray88','gray89','gray90',
	'gray91','gray92','gray93','gray94','gray95','gray96','gray97','gray98','gray99',
	'white', 'snow', 'snow2', 'snow3']

DUPLICATE_COLORS = ['gray0', 'dim gray', 'gray50', 'seashell4', 'floral white',
		'snow4', 'white smoke', 'ghost white', 'gainsboro',
		'pink1', 'saddle brown', 'yellow green']

MAX_ROWS = 36
FONT_SIZE = 18 # (pixels)
arr = []

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Named colour chart")
	row = 0
	col = 0
	for i, color in enumerate(COLORS):
		e = tk.Label(root, text=color, background=color,
				#width=16,
				font=(None, -FONT_SIZE))
		e.grid(row=row, column=col, sticky=tk.E+tk.W)
		c = e.winfo_rgb(color)
		#print(i, "\t",color, "\t", int(c[0]/256), "\t", int(c[1]/256), "\t", int(c[2]/256))
		arr.append([color, int(c[0]/256), int(c[1]/256), int(c[2]/256)])
		#print(arr.pop())
		row += 1
		if (row > MAX_ROWS):
			row = 0
			col += 1

	mindis = [255, "", 0, 0, 0]
	dist = []
	rl,gl,bl = (100, 40, 0)
	for i, r in enumerate(arr):
		c,r,g,b = r
		dist.append(abs(rl - r) + abs(gl - g) + abs(bl - b))
		if(dist[i] < mindis[0]) : mindis = [dist[i], c, r, g, b]
		s = r+g+b
		if(i<360) :
			print(i, c, "\t",r, "\t",g, "\t",b, "  IS PRETTY CLOSE TO : ")
			for i2, rs in enumerate(arr):
				cs,rs,gs,bs = rs
				ss = rs+gs+bs
				if(c != cs and i2>i and "gray" not in c) :
					if((abs(r - rs) < 10 and abs(g - gs) < 10 and abs(b - bs) < 10)):# or abs(s -ss)<10) :
						print(cs, "\t", rs, "\t", gs, "\t", bs)
	print(mindis)
	root.mainloop()
