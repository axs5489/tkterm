"""
 SerialPort: ASCII Serial Port class
"""
import serial
import time
import re
import queue
import threading
import win32pipe
import win32file

class SerialPipe(object):
	""" This class mimics the python serial interface, but instead of 
		reading/writing data to a physical Serial Port device, it 
		reads/writes to the device through a proxy via a Named Pipe. 
		
		This is used in conjunction with the SerialProxy program which
		actually connects to the physical Serial Port and then provides
		multiple connections via a named pipe (\\.\pipe\COMx).
		"""
	def __init__(self,name,timeout):
		self.handle = win32file.CreateFile(name,
				  win32file.GENERIC_READ | win32file.GENERIC_WRITE,
				  0, None, win32file.OPEN_EXISTING, 0, None)
		self.timeout = timeout

	def close(self):
		""" Closes the Serial Port Pipe. """
		win32file.CloseHandle(self.handle)
		self.handle = None

	def write(self, data):
		""" Writes data to the Serial Port Pipe. """
		win32file.WriteFile(self.handle, data)

	def readline(self):
		""" Reads a single line from the Serial Port Pipe. """
		if self.timeout > 0:
			start_time = time.time()
			total_num_bytes = 0
			while (time.time() - start_time) < self.timeout:
				(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)
				if numBytes>0:
					# look for the line-end. if found, read up to (and including) the line-end
					# if never found and we time-out, just read everything available...
					lineEndIdx = pipeData.find('\n')
					if( lineEndIdx >= 0 ):
						numBytes = lineEndIdx + 1
						break

					# if we did get some NEW bytes (but still no newline), reset the start-time 
					# so that we don't prematurely give up if there's more data coming
					if numBytes > total_num_bytes:
						total_num_bytes = numBytes
						start_time = time.time()
				time.sleep(0.1)
		else:
			(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)

		if numBytes>0:
			data = win32file.ReadFile(self.handle, numBytes)
			line = data[1]
		else:
			line = ''
		return line
	 
	def flushInput(self):
		""" Flush's the Serial Port Pipe receive buffer. """
		# TBD: Don't do this since it has threading issues which cause us to 
		#	  block indefinitely. Instead, rely on the async Queue flush to handle this.
		#(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)
		#if numBytes>0:
		#	data = win32file.ReadFile(self.handle, numBytes)
		pass

def async_serial_receive(handle,q,stop):
	""" This is the Asynchronous serial port read thread handler function. """
	while True:
		# Read a line from the serial port. If data available, this will timeout 
		# after handle.timeout seconds and return ''.
		try:
			s = handle.readline()
		except Exception as e:
			print("Error reading from serial port!: ", e)
			s = None
		
		# If the read returned a line, then add it to the queue. Do some checking 
		# to roll old messages off the end of the queue if necessary.
		if s:
			if q.full():
				q.get()
			q.put(s.strip())
		else:
			time.sleep(1)
		# Call the stop function to see if the parent thread is trying to
		# terminate this helper thread
		if stop():
			break

class SerialPort(object):
	""" This class encapsulates an ASCII Serial Port and provides 2 distinct
		modes of read operation:
			1) Synchronous: All physical serial port hardware reads are handled 
				synchronously on the caller thread.
			2) Asynchronous: All physical reads are handled by a background 
				helper thread, which logs and buffers the data. Users of the 
				SerialPortDevice read data synchronously on the caller's thread 
				from this buffer (and not the serial port hardware directly). 
				Using this mode, all data received from the serial port can be 
				logged, and long delays between when the physical data comes in 
				and when the caller gets the data are possible without losing data.
			Note that all writes are synchronous.
	"""
	class Timeout(Exception):
		""" Exception signifying a serial port read/wait Timeout. """
		pass

	class ThreadLockTimeout(Exception):
		"""	Exception signifying a thread was blocked from getting access to the serial device"""
		pass

	def __init__(self, name, port, baud=115200, data=8, parity="N", stop=1,
			  xonxoff=0, rtscts=0, asyncr=False, tx_term='\n', echos=True):
		""" SerialPortDevice Constructor.
				port: a "COMn" string
				baud: the baud rate to use
				async: True=use an asynchronous background thread for all reads
		"""
		if name:
			self._name = name
		else:
			self._name = port
		# Try to open the Serial Port. First, open it directly. If this 
		# failes, then attempt to open it via the Proxy named pipe. If that
		# also fails, throw the error.
		try:
			self.handle = serial.Serial(port=port, baudrate=baud, bytesize=8,
				parity="N", stopbits=1, timeout=3.0, writeTimeout=3.0, xonxoff=0, rtscts=0)
		except Exception as e:
			print("Couldn't connect directly to %s - %s"%(port,e))
			try:
				self.handle = SerialPipe(r'\\.\pipe\%s'%port, timeout=3.0)
			except:
				raise Exception("Error opening Serial Port: %s!!" % port)

		# If Asynchronous, setup and start the helper thread
		# Pass a lambda function that just returns the stop flag to support 
		# stopping the thread.
		self._async = asyncr
		if self._async:
			self.stop = False
			self.q = queue.Queue(maxsize=4096)
			self.t = threading.Thread(target=async_serial_receive, args=(self.handle, self.q, lambda:self.stop))
			# Make the thread a Daemon so that we don't hang at the end of a 
			# script if we forget to close the Serial Port
			self.t.daemon = True
			self.t.start()
		
		self.port = port
		self._lock = threading.RLock()  # re-entrant lock object for thread safe writes
		self.tx_terminator = tx_term #'\n'
		self.echos = echos

	def __del__(self):
		self.close()

	def close(self):
		""" Closes the serial port and stops the Asynchronous read-thread. """
		if hasattr(self,'_async') and self._async:
			self.stop = True
			self.t.join()
		if hasattr(self,'handle'):
			self.handle.close()
		if hasattr(self,'port'):
			print("SerialPortDevice: Port Closed: %s"%(self.port))

	def send(self,sendStr):
		""" Writes the given string to the serial port. """
		self._get_mutex()
		try:
			self.handle.write((sendStr + self.tx_terminator).encode())
		except serial.writeTimeoutError:
			# write() timed-out for some reason - try to send another 
			# tx_terminator to see if that gets things through... if not,
			# then, we'll just except again
			self.handle.write(self.tx_terminator.encode())
		finally:
			self._release_lock()

	def send_and_wait(self,sendStr,waitStr,timeout=10,timeoutException=True,useRegex=False,caseSensitive=False):
		""" Writes a string to the serial port, then waits for the given 
			response string. If the response timesout (after 'timeout' seconds),
			an exception is thrown.
				sendStr: string to write to the serial port
				waitStr: sub string or regex to wait on (if this string matches
						 any part of a read line, return)
				timeout: timeout in seconds
				timeoutException: if True and timed-out, raise the Timeout 
						 exception; otherwise return ''
				useRegex: if True, treat waitStr as a regex expression; if false
						 treat it normally (regex expressions are ignored)
				caseSensitive: if True, the wait is case-sensitive
			Returns the full line containing the waitStr (or '' if timed-out 
				and timeoutException==False)
		"""
		self._get_mutex()
		self.flush_recv()
		self.send(sendStr)

		# If this port supports echo'ing of the sends, wait for the read-back
		# before continuing.
		if self.echos:
			self.waitFor(sendStr.strip(),timeout,False,False)

		try:
			return self.waitFor(waitStr,timeout,timeoutException,useRegex,caseSensitive)
		except SerialPort.Timeout:
			raise SerialPort.Timeout("SerialPortDevice.send_and_wait() timed out. Command: '%s', waited for: '%s'" % (sendStr, waitStr))
		finally:
			self._release_lock()

	def recv(self, pub=True):
		""" Reads a line from the serial port. """
		# If Asynchronous, read from the Queue (that is filled by the read
		# thread). If Synchronous, read from the serial port directly.
		if self._async:
			try:
				return self.q.get(timeout=self.handle.timeout)
			except queue.Empty:
				return ''
		else:
			s = self.handle.readline().strip().decode()
			if pub : print(s)
			return s
	
	def flush(self, pub=False):
		lines = []
		if self._async:
			pass
		else:
			while self.handle.inWaiting() > 0:
				lines.append(self.recv(pub))
				time.sleep(0.05)
		return lines

	def flush_recv(self):
		""" Flushes the serial port's receive buffer. """
		# If Asynchronous, drain the Queue until it is empty.
		# Otherwise, directly Flush the serial port.
		if self._async:
			try:
				loopcount = 10e3 # safety feature
				while loopcount>0:
					if self.q.empty():
						break
					self.q.get_nowait()
					loopcount -= 1
				else:
					print("flush_recv timed out! (qsize=%s)!"%self.q.qsize())
			except queue.Empty:
				pass
		else:
			self.handle.flushInput()

	def waitFor(self,waitStr,timeout=10,timeoutException=True,useRegex=False,caseSensitive=False):
		""" Reads from the serial port until waitStr is matched.
				waitStr: sub string or regex to wait on (if this string matches any part of a read line, return)
				timeout: timeout in seconds
				timeoutException: if True and timed-out, raise the Timeout exception; otherwise return ''
				useRegex: if True, treat waitStr as a regex expression; if false
						 treat it normally (regex expressions are ignored)
				caseSensitive: if True, the wait is case-sensitive
			Returns the full line containing the waitStr (or '' if timed-out 
				and timeoutException==False)
		"""
		start_time = time.time()
		if useRegex:
			rg = re.compile(waitStr,re.IGNORECASE if not caseSensitive else 0)
			while (time.time() - start_time) < timeout:
				s = self.recv()
				#print(s)
				if s is not None:
					m = rg.search(s)
					if m:
						return s.strip()
		else:
			while (time.time() - start_time) < timeout:
				s = self.recv()
				if s is not None:
					s = s if caseSensitive else s.lower()
					waitStr = waitStr if caseSensitive else waitStr.lower()
					if s.find(waitStr) >= 0:
						return s.strip()

		if timeoutException:
			raise SerialPort.Timeout("SerialPort.waitfor() timed out waiting for '%s'" % waitStr)
		else:
			return ''

	def lock(self, timeout=15):
		"""	Method to lock a serial port device so that atomic writes can be performed.  The lock is re-entrant so the
		thread that owns the lock can perform writes on the serial device any number of times.
			timeout (sec): Time to wait while trying to acquire the mutex
		"""
		self._get_mutex(timeout)

	def release(self):
		"""	Method to release a lock on the serial device """
		self._release_lock()

	def _release_lock(self):
		self._lock.release()

	def _get_mutex(self, timeout=10):
		"""	Private method to get mutex lock prior to writing data to serial port.  This call is blocking.
		Args:
			timeout (int): Number of seconds to wait before throwing Timeout exception
		Raises:
			Timeout
		"""
		attempts = 0
		wait_time = 0.1	 # seconds
		elapsed_time = 0
		start_time = time.time()
		lock_status = self._lock.acquire(0)  # attempt to get the lock
		if lock_status:
			return
		else:
			# another thread locked the serial port so we'll wait and try again
			while not lock_status:
				elapsed_time = time.time() - start_time
				if elapsed_time > timeout:
					raise SerialPort.ThreadLockTimeout("Timed out waiting for mutex")
				else:
					time.sleep(wait_time)
					attempts += 1
					lock_status = self._lock.acquire(0)
