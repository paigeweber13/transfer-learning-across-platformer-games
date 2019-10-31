import Qmodel
import configparser
import sys
import os

configFilename = 'configs\\sample.cfg'

if len(sys.argv) >= 2:
	configFilename = sys.argv[1]
	
config = configparser.ConfigParser()
config.read(['defaults.cfg', configFilename])

# Whether or not to use the screen pixels as neural network input.
def get_pixels():
	return config.get('Model', 'Pixels').lower() != 'false'
	
if get_pixels():
	import screen_cap

# Creates a neural network model using data from the config file
def get_model(name, train):
	# Get the list of RNN layer sizes
	rnn_sizes = []
	layer = 1
	while True:
		try:
			size = int(config.get('RNN', 'Layer' + str(layer)))
			if size < 1:
				break
			rnn_sizes.append(size)
			layer = layer + 1
		except:
			break
			
	# Get the list of Dense layer sizes
	hidden_sizes = []
	layer = 1
	while True:
		try:
			size = int(config.get('Hidden', 'Layer' + str(layer)))
			if size < 1:
				break
			hidden_sizes.append(size)
			layer = layer + 1
		except:
			break
		
	# Gets the screen capture object
	if get_pixels():
		cap = screen_cap.screen_cap()
		num_inputs = cap.size()
	else:
		cap = None
		num_inputs = [15*15+23+3]


	conv_sizes = []
	
	# Get the list of CNN layer sizes
	layer = 1
	while True:
		try:
			layer_str = config.get('Conv', 'Layer' + str(layer))
			conv_sizes.append(eval(layer_str))
			layer += 1
		except:
			break
			
	print('RNN Sizes: ' + str(rnn_sizes))
	
	num_outputs = len(get_controller_sets())

	# Create the model
	model = Qmodel.model(
			name = name,
			num_inputs = num_inputs,
			rnn_sizes = rnn_sizes,
			conv_sizes = conv_sizes,
			hidden_sizes = hidden_sizes,
			num_outputs = num_outputs,
			seq_length = int(config.get('Train', 'SeqLength')),
			batch_size = int(config.get('Train', 'BatchSize')),
			base_learning_rate = float(config.get('Train', 'LearningRate')),
			lr_decay = get_lr_decay(),
			reward_discount = get_reward_discount(),
			grad_clip = get_grad_clip(),
			pixels = get_pixels(),
			reg_coeff = get_regularization(),
			train = train
		)
	
	return model, cap

# Gets the checkpoint directory
def get_checkpoint_dir():
	return config.get('Checkpoint', 'Dir')

# Gets a file/directory in the checkpoint directory
def get_checkpoint_file(filename):
	return os.path.join(config.get('Checkpoint', 'Dir'), filename)
	
# Gets the batch size
def get_batch_size():
	return int(config.get('Train', 'BatchSize'))

# Gets the RNN/Q Learning sequence length	
def get_sequence_length():
	return int(config.get('Train', 'SeqLength'))

# Gets the exponential decay rate for the learning rate. Applied every global step.
def get_lr_decay():
	return float(config.get('Train', 'LRDecay'))
	
# Gets the discount rate for Reinforcement Learning reward.
def get_reward_discount():
	return float(config.get('Train', 'RewardDiscount'))

# Get the number of recent experience replay sequences to retain in memory
def get_replay_sequences():
	return int(config.get('Train', 'ExperienceReplays'))

# Gets the number of in-game seconds to wait for each checkpoint
def get_checkpoint_seconds():
	return int(config.get('Train', 'CheckpointSeconds'))

# Gets the number of time steps per second. Should be divisible into 60.
def get_steps_per_second():
	return int(config.get('Model', 'StepsPerSecond'))
	
# Gets the list of numerical parameters to send to the emulator.
def get_emu_config():
	emu_config = dict(config.items('Emulator'))
	emu_config['discount'] = get_reward_discount()
	emu_config['steps_per_second'] = get_steps_per_second()
	
	if '--evaluate' in sys.argv:
		emu_config['tryhard_min'] = 100
		
	return emu_config

# Gets the maximum number of seconds to spend on each course before moving on.
def get_seconds_per_course():
	return int(config.get('Emulator', 'seconds_per_course'))
	
# Whether or not to track the position data in the experience replay files.
def track_position():
	return config.get('Emulator', 'track_position').lower() != 'false'
	
# Whether or not to use Double DQN.
def get_double_dqn():
	return config.get('Model', 'DoubleDQN').lower() != 'false'

# Whether or not to use prioritized experience replay.
def get_prioritized_experience_replay():
	return config.get('Train', 'PrioritizedExperienceReplay').lower() != 'false'

# Creates a lookup table of button combinations for indices
def get_controller_lookup():
	controllers = get_controller_sets()
			
	names = get_button_names()
	lookup = []
	for buttons in controllers:
		controller = []
		for name in names:
			if name in buttons:
				controller.append(1)
			else:
				controller.append(0)
				
		lookup.append(controller)
				
	return names, lookup

# Gets the names of all the buttons used
def get_button_names():
	return config.get('Controller', 'Order').strip().split()

# Gets the list of possible button combinations
def get_controller_sets():
	controllers = []

	idx = 1
	while True:
		try:
			buttons = config.get('Controller', 'Buttons' + str(idx)).strip().split()
			controllers.append(buttons)
			idx = idx + 1
		except:
			break
			
	
	# Default button combinations
	if len(controllers) == 0:
		controllers = [
			[],
			['B'],
			['Right'],
			['B', 'Right'],
			['Left'],
			['B', 'Left'],
		]
			
	return controllers

# Gets the gradient clip for gradient descent	
def get_grad_clip():
	return float(config.get('Train', 'GradClip'))

# Gets the regularization term coefficient
def get_regularization():
	return float(config.get('Train', 'Regularization'))