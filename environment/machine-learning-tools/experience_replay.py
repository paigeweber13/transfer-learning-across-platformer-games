import os
import struct
import numbers
import numpy as np

# Save array in text format
def save_array(file, array):
	if isinstance(array, numbers.Number):
		file.write(str(array) + '\n')
	else:
		file.write('array\n{0}\n'.format(len(array)))
		for elm in array:
			save_array(file, elm)

# Save array in binary format
def write_array_binary(file, value):
	if type(value) is list or type(value) is tuple or type(value) is np.ndarray:
		file.write((1).to_bytes(1, 'big'))
		file.write(len(value).to_bytes(4, 'big'))
		
		for elm in value:
			write_array_binary(file, elm)
	else:
		if not isinstance(value, numbers.Number):
			print(type(value))
		file.write((2).to_bytes(1, 'big'))
		file.write(bytearray(struct.pack("f", float(value))))

# Save all replays in text format		
def save_replays(path, replays):
	directory = os.path.dirname(path)
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	with open(path, 'wb') as file:
		write_array_binary(file, replays)

# Load array in text format
def load_array(file):
	line = file.readline().strip()
	if line == 'array':
		array = []
		length = int(file.readline().strip())
		
		for i in range(length):
			sub = load_array(file)
			array.append(sub)
		
		return array
	else:
		return float(line)

# Load array in binary format
def read_array_binary(file):
	type = int.from_bytes(file.read(1), 'big')
	if type == 1:
		length = int.from_bytes(file.read(4), 'big')
		array = []
		for i in range(length):
			array.append(read_array_binary(file))
		
		return array
	elif type == 2:
		val = struct.unpack("f", file.read(4))[0]
		return val
	else:
		raise Exception("Invalid array file")

# Load all replays, both text and binary formats
def load_replays(path, log, max_replays):
	replay_buffer = []
	log('Loading experience replay from "{0}"'.format(path))
	for filename in reversed(sorted(os.listdir(path))):
		filename = os.path.join(path, filename)
		log('Loading {0}'.format(filename))
		if filename.split('.')[1] == 'txt':
			with open(filename, 'r') as file:
				replays = load_array(file)		
		else:
			with open(filename, 'rb') as file:
				replays = read_array_binary(file)		
		
		global replay_buffer
		replay_buffer = replays + replay_buffer
		if len(replay_buffer) > max_replays:
			replay_buffer = replay_buffer[-max_replays:]
			return replay_buffer
			
	return replay_buffer