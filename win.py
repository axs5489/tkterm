# -*- coding: utf-8 -*-
"""
Created on Thu May 07 17:35:39 2020

@author: asasson
"""

import os
import sys
import ctypes
import glob
import serial
from serial.serialutil import SerialException
import shutil
import time
import win32api
import win32com.client


def timeExpired(startTime, numSec=45):
	""" Checks if a certain number of seconds has passed since startTime"""
	return ((time.perf_counter() - startTime) < numSec)

def validatePort(tport, debugOn = False):
	""" Given a port, validate if connected"""
	if debugOn : print("{}".format(tport))
	try:
		p = serial.Serial(port = tport,baudrate = 115200,timeout = 3)
		if debugOn : print(p.port," ",p.isOpen())
		buf = ""
		for i in range(10):
			try:
				p.write("\n".encode('utf-8'))
				p.write(b'ascii\r')
				buf += p.readline()
				if(buf.find("\n") or buf.find("\r")):
					break
			except:
				if debugOn : print("Serial Error")
			time.sleep(5)
		p.close()
		return True
	except serial.SerialException:
		if debugOn : print(tport, " already open")
		if(p.isOpen()) :
			p.close()
		return -1
	except:
		print("ERROR")
		if(p.isOpen()) :
			p.close()
		return -2
	return False

def listSerialPorts():
	""" Cross-platform available serial port lister"""
	if sys.platform.startswith('win'):
		ports = ['COM' + str(i + 1) for i in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this is to exclude your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		import glob
		ports = glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except (OSError, SerialException):
			pass
	return result

def driveReady(drive):
	""" Validates a Drive"""
	returnValue = 0
	oldError = win32api.SetErrorMode( 1 )
	try:
		win32api.GetVolumeInformation(drive)
	except:
		returnValue = 0
	else:
		returnValue = 1

	win32api.SetErrorMode(oldError)
	return returnValue

def getDrives():
	""" Generates a list of volume names"""
	# First, let's make a list of all active drive letters
	drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]

	# Now, let's parse the list and generate a list of volume names
	list = [drive for drive in drives if driveReady(drive)]
	return list

def getDriveVolumeName(driveLetter):
	""" Returns USB Drive Name by Letter ('D:\\') """
	objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
	objSWbemServices = objWMIService.ConnectServer(".","root\cimv2")
	
	LogicalDisk_DeviceID = driveLetter[0:driveLetter.find('\\')]
	#print(LogicalDisk_DeviceID)
	
	# 4. Win32_LogicalDisk
	colItems = objSWbemServices.ExecQuery("SELECT * from Win32_LogicalDisk WHERE DeviceID=\"" + LogicalDisk_DeviceID + "\"")
	#print('LogicalDisk VolumeName:', colItems[0].VolumeName)
	#print(colItems[0].VolumeName, '(' + LogicalDisk_DeviceID + ')')
	return colItems[0].VolumeName

def findDrive(search, timeout=20):
	""" Basic search of drives by name """
	for retries in range(1,timeout):
		for drive in getDrives():
			volume = getDriveVolumeName(drive)
			if(volume.find(search)) :
				return drive
		time.sleep(1)
	return -1

def copyFile(src,dst):
	""" Copies a file from src to base directory of dst drive """
	if(dst not in getDrives()) : dst = findDrive(dst)
	if(dst in getDrives()) :
		src = os.path.normpath(src)
		dir,file = os.path.split(src)
		if file : shutil.copyfile(src,os.path.join(dst,file))
		return 1
	return 0

def transferFile(src,dst,filename):
	""" Copy file from drive to PC filesystem """
	if(src not in getDrives()) : src = findDrive(src)
	if(src in getDrives()) :
		try:
			dir,tail = os.path.split(dst)
			shutil.copyfile(os.path.join(src,filename),os.path.join(dir,filename))
			return 1
		except:
			print("File not found")
			return 0
	else: print("Drive not found")
	return -1

def getConfig(fileaddr = "C:\\Harris\\config.txt", debugOn = False):
	""" Checks for a computer configuration file and returns dictionary of settings"""
	try:
		file = open(fileaddr,"r")
		if debugOn : print("File Opened")
		lcfg = file.readlines()
		dcfg = {'NUM' : len(lcfg)}
		if debugOn : print(lcfg)
		for line in lcfg:
			try:
				if(line[0] is '#'):
					pass
				else:
					ki = line.index(' ')
					vi1 = line.index('\'') + 1
					vi2 = line.index('\'', vi1)
					if debugOn : print(ki, line[0:ki])
					if debugOn : print(vi1, vi2)
					if debugOn : print(line[vi1:vi2])
					if(vi2 > vi1) : dcfg[line[0:ki]] = line[vi1:vi2]
			except ValueError:
				print("Line Error in Config File")
		file.close()
		return dcfg
	except:
		print("File Error")
		if (not file.closed) : file.close()

def newConfig(filepath = "C:\\Harris\\config.txt"):
	""" Writes a default computer configuration file if one is not there"""
	if(os.path.exists(filepath)) :
		print("File already made")
		return (-1)

	try:
		file = open(filepath,"w")
		print("File Opened")
		file.write("ADU = ''")
		file.write("STP = 'COM1'")
		file.write("RCR = ''")
		file.write("RCB = ''")
		file.write("RED = ''")
		file.write("BLK = ''")
		file.write("PM = 'GPIB0::14::INSTR'")
		file.write("SIG = ''")
		file.write("SA = ''")
		file.write("NA = ''")
		file.write("SCP = ''")
		file.close()
		return 1
	except:
		print("File Error")
		if (not file.closed) : file.close()

if __name__ == "__main__":
	drives = getDrives()
	for d in drives:
		dName = getDriveVolumeName(d)
		print(d, dName)
	ports = listSerialPorts()
	print(ports)
