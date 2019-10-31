import traceback
import socket
import config

class game_client(object):
	def __init__(self, header, config, expected_inputs, controller_lookup, button_names):
		self.header = header
		self.expected_inputs = expected_inputs
		self.expected_buttons = len(button_names)
		self.config = config
		self.controller_lookup = controller_lookup
		self.button_names = button_names

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		port = 2222
		self.server.bind((socket.gethostname(), port))
		print("Hostname: %s Port: %d" % (socket.gethostname(), port))
		self.server.listen(1)

		
	def listen(self):
		while True:
			try:
				print('Listening for connection...')
				(self.clientsocket, self.address) = self.server.accept()
				print('Connection received.')
				
				self.send_header()
				self.send_config(config.get_emu_config())
				self.send_controller_lookup()
				break
			except:
				print('Exception occurred while listening for client.')
				print(traceback.print_exc())
				if self.clientsocket != None:
					self.clientsocket.send(b"close")
					self.clientsocket.close()
		
	def send_header(self):
		self.clientsocket.send((str(len(self.header)) + "\n").encode())
		for param in self.header:
			self.clientsocket.send((str(param) + "\n").encode())
			
	def send_config(self, config):
		for k in config:
			self.send_line(k)
			self.send_line(config[k])
		self.send_line('end')
				
	def receive_line(self):
		line = ""
		while not line.endswith('\n'):
			new_data = self.clientsocket.recv(1).decode('ascii')
			if len(new_data) == 0:
				raise Exception()
			line += new_data
			
		return line.strip()
		
	def receive(self):
		while True:
			try:
				screen = self.receive_line()
				controller = self.receive_line()
				reward = self.receive_line()
				do_display = self.receive_line()
				if config.track_position():
					pos = self.receive_line()					
				
				screen = [float(v) for v in screen.split(' ')]
				assert(len(screen) == self.expected_inputs)
				
				if config.track_position():
					pos = [int(v) for v in pos.split(' ')]
					assert(len(pos) == 3)
				else:
					pos = None
					
				controller = [int(v) for v in controller.split(' ')]
				assert(len(controller) == self.expected_buttons)
				
				reward = float(reward)
				do_display = int(do_display)
				
				return screen, controller, reward, do_display, pos
				
			except:
				print("Exception occurred. Closing connection.")
				print(traceback.print_exc())
				self.clientsocket.send(b"close")
				self.clientsocket.close()
				self.listen()
	
	def send_q(self, q_vals):
		for q in q_vals:
			self.send_line(q)
		self.send_line('end')

	def send_probs(self, probs):
		for p in probs:
			self.send_line(p)
		self.send_line('end')
			
	def send_line(self, line):
		try:
			self.clientsocket.send((str(line) + '\n').encode())
		except:
			print("Exception occurred. Closing connection.")
			print(traceback.print_exc())
			self.clientsocket.send(b"close")
			self.clientsocket.close()
			self.listen()
			
	def send_buttons(self, buttons):
		self.send_line(' '.join(['1' if button else '0' for button in buttons]))
		
	def send_controller_lookup(self):
		for buttons in self.controller_lookup:
			for i in range(len(self.button_names)):
				self.send_line(self.button_names[i])
				if buttons[i] == 0:
					self.send_line('false')
				else:
					self.send_line('true')
			
			self.send_line('done')
		
		self.send_line('end')
		