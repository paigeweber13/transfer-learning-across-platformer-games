import tensorflow as tf
import math
import Qmodel
from game_client import game_client
import numpy as np
import DisplayNetwork
import time
import datetime
import random
import threading

from experience_replay import load_replays, save_replays
from weight_balanced_tree import weight_balanced_tree
import config
import sys

def get_option(opt, default):
	if opt in sys.argv and sys.argv.index(opt) < len(sys.argv) - 1:
		return int(sys.argv[sys.argv.index(opt)+1])
	else:
		return default

button_names, controller_lookup = config.get_controller_lookup()

NumOutputs = len(controller_lookup)
AsynchronousTraining = False
Pixels = config.get_pixels()

if Pixels:
	# Use screen capture as neural network input
	cap = screen_cap.screen_cap()
	NumInputs = cap.size()
	ConvSizes = []
else:
	# Use programmatically extracted tilemap as network input
	NumInputs = [15*15+23+3]
	ConvSizes = None

Double = config.get_double_dqn()
if Double:
	# Use double DQN
	modelA, cap = config.get_model('modelA', train=True)
	modelB, cap = config.get_model('modelB', train=True)
else:
	# Use single DQN
	model, cap = config.get_model('model', train=True)

PrioritizedReplay = config.get_prioritized_experience_replay()

# Used for Prioritized Replay and to reduce duplicate replays
def replay_hash(r):
	return r[3]
	
def replay_weight(r):
	return r[4]
	
current_id = 0
	
if PrioritizedReplay:
	replay_tree = weight_balanced_tree(lambda r: replay_weight, replay_hash)
else:
	Replays = config.get_replay_sequences()
	replay_buffer = []
	replay_segment = []

# Add a new experience to the replay buffer
def add_replay(replay):
	global replay_buffer
	replay_buffer.append(replay)
	if len(replay_buffer) > Replays:
		replay_buffer = replay_buffer[1:]
		
	global replay_segment
	replay_segment.append(replay)

# Get a random experience replay
def get_replay():
	if PrioritizedReplay:
		if replay_tree.size() == 0:
			return None
		else:
			return replay_tree.sample(random.random())	
	else:
		global replay_buffer
		if len(replay_buffer) == 0:
			return None
		else:
			return replay_buffer[random.randint(0, len(replay_buffer)-1)]

# Get n random experience replays.			
def get_replays(n):
	global replay_buffer
	
	available = replay_tree.size() if PrioritizedReplay else len(replay_buffer)
	
	replays = []
	used = {}
	
	while len(replays) < n and len(replays) < available:
		replay = get_replay()
		if replay_hash(replay) in used:
			continue
		
		used[replay_hash(replay)] = True
		replays.append(replay)
		
	while len(replays) < n:
		replays.append(get_replay())
		
	return replays

# Get controller index from a set of buttons
def reverse_lookup(buttons):
	global controller_lookup
	for i in range(NumOutputs):
		match = True
		for j in range(len(buttons)):
			if buttons[j] != controller_lookup[i][j]:
				match = False
				break

		if match:
			return i
			
	raise Exception('Tried to lookup invalid buttons: {0}'.format(buttons))

# Extract the Q targets for gradient descent
def get_q_targets(rewards, actions_taken, greedy_q_vals, target_q_vals, live = False):
	labels = []
	weights = []
		
	global total_target_delta
	global num_targets
	
	# Calculate q-learning targets
	for time_step in range(config.get_sequence_length()-1):
		max_reward = rewards[time_step+1]
		coefficient = config.get_reward_discount()
		
		# Calculate on-policy reward
		greedy_time_step = time_step+1
		
		#while greedy_time_step < seq_length-1 and int(actions_taken[greedy_time_step+1]) == greedy_action:
		while greedy_time_step < config.get_sequence_length() - 1:
			# Get the greedy policy action and value
			greedy_action = np.argmax(greedy_q_vals[greedy_time_step])
			greedy_q = greedy_q_vals[greedy_time_step][greedy_action]

			# Get the experienced action and value
			behavior = int(actions_taken[greedy_time_step+1])
			behavior_q = greedy_q_vals[greedy_time_step][behavior]

			if behavior_q >= greedy_q:
				# On-policy action was taken
				max_reward += coefficient * rewards[greedy_time_step+1]
				coefficient *= config.get_reward_discount()
				greedy_time_step += 1
				continue
			else:
				# Off-policy action was taken
				break
		
		# Get the Q target
		greedy_action = np.argmax(greedy_q_vals[greedy_time_step])
		q_estimate = target_q_vals[greedy_time_step][greedy_action]
		max_reward += coefficient * q_estimate
		
		if live:
			total_target_delta += max_reward - greedy_q_vals[time_step][int(actions_taken[time_step+1])]
			num_targets += 1
		
		# Only perform gradient descent on the action that was taken
		weight = np.zeros(NumOutputs)
		weight[int(actions_taken[time_step+1])] = 1
		label = np.zeros(NumOutputs)
		label[int(actions_taken[time_step+1])] = max_reward
		
		weights.append(weight)
		labels.append(label)
		
	weights.append(np.zeros(NumOutputs))
	labels.append(np.zeros(NumOutputs))
	
	return labels, weights

# Get gradient descent labels and weights for an entire sequence	
def	get_labels(replays, rewards, actions_taken, greedy_q_vals, target_q_vals):
	labels = [[] for _ in range(config.get_sequence_length())]
	weights = [[] for _ in range(config.get_sequence_length())]
	
	for i in range(config.get_batch_size()):
		if i > 0:
			replay = replays[i-1]
		else:
			replay = None
			
		if replay == None:
			r_actions_taken = actions_taken
			r_rewards = rewards
		else:
			r_actions_taken = replay[1]
			r_rewards = replay[2]
	
		r_labels, r_weights = get_q_targets(r_rewards, r_actions_taken, greedy_q_vals[i], target_q_vals[i], i == 0)
		
		for step in range(config.get_sequence_length()):
			labels[step].append(r_labels[step])
			weights[step].append(r_weights[step])
			
	return labels, weights

# Log to screen and file
log_file_name = config.get_checkpoint_file('log.txt')
def log(s):
	print(s)
	with open(log_file_name, 'a') as file:
		file.write(s + '\n')

init = tf.global_variables_initializer()
saver = tf.train.Saver()

with tf.Session() as session:
	# Get the latest checkpoint
	if '--ignore_checkpoint' in sys.argv:
		last_checkpoint = None
	else:
		last_checkpoint = tf.train.latest_checkpoint(config.get_checkpoint_dir())
		
	# Reload the checkpoint data if it exists
	if last_checkpoint != None and not Pixels:
		log("Restoring session from " + last_checkpoint)
		saver.restore(session, last_checkpoint)
		global_step = int(last_checkpoint.split("-")[-1])
		current_id = global_step * config.get_steps_per_second() * config.get_checkpoint_seconds()
		if not PrioritizedReplay and '--evaluate' not in sys.argv:
			replay_buffer = load_replays(config.get_checkpoint_file('experience_replay'), log, Replays)
			
			# Add unique ids if they don't already have them
			for i in range(len(replay_buffer)):
				if len(replay_buffer[i]) <= 3:
					x, y, z = replay_buffer[i]
					replay_buffer[i] = x, y, z, current_id
					current_id += 1
					
		log('{0} replay sequences loaded.'.format(len(replay_buffer)))
	else:
		# Initialize a new session
		session.run(init)
		global_step = 0
	
	# Initialize the model(s)
	if Double:
		modelA.init(session)
		modelB.init(session)
	else:
		model.init(session)

	# Create a server for the emulator client to connect to
	client = game_client(
		header = [
			15,		# Width
			15,		# Height
			23,		# Extra Inputs
			3,		# Buttons
			1.05,	# Skew
			0.3,	# Tilt Shift
			24,		# Input Resolution
		],
		config = config.get_emu_config(),
		expected_inputs = 15*15+23,
		controller_lookup = controller_lookup,
		button_names = button_names,
	)
	client.listen()
	
	# Initialize the pygame neural network display
	display = DisplayNetwork.Display(15, 15, controller_lookup) 

	total_reward = 0
	total_steps = 0
	
	global total_target_delta
	global num_targets
	
	total_target_delta = 0
	num_targets = 0
	
	last_step = get_option('--until', 1000000000)
	
	while global_step < last_step:
		# Save a checkpoint periodically
		if total_steps >= config.get_steps_per_second()*config.get_checkpoint_seconds():
			global_step = global_step + 1
			
			if '--evaluate' not in sys.argv:
				# Save the checkpoint
				saver.save(session, config.get_checkpoint_file('mariq'), global_step=global_step, write_meta_graph=False)
				if not PrioritizedReplay and not Pixels:
					global replay_segment
					save_replays(config.get_checkpoint_file('experience_replay\step{0:04d}.exr'.format(global_step)), replay_segment)
					replay_segment = []

			# Compute average reward per second
			avg_reward = config.get_steps_per_second() * total_reward / total_steps
			
			if Double:
				lr = modelA.learning_rate(global_step)
			else:
				lr = model.learning_rate(global_step)

			# Display the average reward
			if '--evaluate' in sys.argv:
				log('Evaluating at step {0}. Avg {1:.3f} reward/sec.'.format(global_step, avg_reward, lr))
			else:
				log('Saving model at step {0}. Avg {1:.3f} reward/sec. Learning rate decayed to {2:.3f}'.format(global_step, avg_reward, lr))
			
			
			# Reset average reward
			total_reward = 0
			total_steps = 0
	
		# Initialize all the arrays for this sequence
		actions_taken = []
		rewards = []
		screens = []
		positions = []
		input_sequence = []
		
		if Double:
			batch_q_valsA = [[] for _ in range(config.get_batch_size())]
			batch_q_valsB = [[] for _ in range(config.get_batch_size())]
		else:
			batch_q_vals = [[] for _ in range(config.get_batch_size())]
			
		# Get the replays to fill up the batch
		#replays = [get_replay() for _ in range(config.get_batch_size()-1)]
		replays = get_replays(config.get_batch_size()-1)
		
		for time_step in range(config.get_sequence_length()):
			# Get the experience data from the client
			screen, controller, reward, do_display, pos = client.receive()
			
			# Feed controller inputs into the neural network
			screen += controller
			
			displayScreen = screen
			
			# Get the screen capture if necessary
			if Pixels:
				screen = cap.get()
			
			# Look up the q index for the controller presses
			action_index = reverse_lookup(controller)				

			# Store the experience data
			actions_taken.append(action_index)
			screens.append(screen)
			rewards.append(reward)
			positions.append(pos)
			
			if do_display == 1:
				if display == None:
					display = DisplayNetwork.Display(15, 15, controller_lookup) 
			else:
				if display != None:
					display.close()
					display = None


			# For calculating average reward
			total_reward += reward
			total_steps += 1					
			
			# Create a batch out of the current screen and experience replays
			inputs = [screen]
			for i in range(len(replays)):
				if replays[i] == None:
					inputs.append(screen)
				else:
					r_screens = replays[i][0]
					inputs.append(r_screens[time_step])
			
			input_sequence.append(inputs)
			
			# Perform neural network forward pass for the batch
			if Double:
				outputA, convs = modelA.single_forward(inputs)
				outputB, convs = modelB.single_forward(inputs)
				
				# Store values for q target generation
				for i in range(config.get_batch_size()):
					q_valsA = outputA[i]
					q_valsB = outputB[i]
					
					batch_q_valsA[i].append(q_valsA)
					batch_q_valsB[i].append(q_valsB)
				
				q_vals = outputA[0]
				
				# Get the best buttons to send the to game
				greedy_buttons = controller_lookup[np.argmax(q_vals)]
				client.send_q(q_vals)
				
				probs = outputA[0]
				client.send_probs(probs)

				if display != None:
					# Update the pygame neural network display
					display.update(displayScreen, modelA.single_state, greedy_buttons, outputA[0], reward, convs)

			else:
				output, convs = model.single_forward(inputs)
			
				# Store values for q target generation
				for i in range(config.get_batch_size()):
					q_vals = output[i]
					batch_q_vals[i].append(q_vals)
				
				q_vals = output[0]
				
				# Get the best buttons to send the to game
				greedy_buttons = controller_lookup[np.argmax(q_vals)]
				client.send_q(q_vals)
				
				probs = output[0]
				client.send_probs(probs)

				if display != None:
					# Update the pygame neural network display
					display.update(displayScreen, model.single_state, greedy_buttons, output[0], reward, convs)

		if '--evaluate' not in sys.argv:
			# Train the network(s)
			if Double:
				labels, weights = get_labels(replays, rewards, actions_taken, batch_q_valsA, batch_q_valsB)
				errors = modelA.sequence_train(input_sequence, labels, weights, global_step)
				
				# Run forward on the secondary model to keep its state in sync
				modelB.sequence_train(input_sequence, labels, weights, global_step, no_train=True)
			else:
				# Get the labels to train the model
				labels, weights = get_labels(replays, rewards, actions_taken, batch_q_vals, batch_q_vals)
				if AsynchronousTraining:
					t = threading.Thread(target = lambda: model.sequence_train(input_sequence, labels, weights, global_step))
					t.start()
				else:
					errors = model.sequence_train(input_sequence, labels, weights, global_step)
		
		# Re-insert the replays into the prioritized replay, with updated errors
		if PrioritizedReplay:
			for i in range(config.get_batch_size()):
				if i == 0:
					# Insert new experience
					r_screens = screens
					r_actions_taken = actions_taken
					r_rewards = rewards
					r_id = current_id
					if config.track_position():
						r_positions = positions
						replay_tree.add((screens, actions_taken, rewards, current_id, errors[0], r_positions))
					else:
						replay_tree.add((screens, actions_taken, rewards, current_id, errors[0]))
					current_id += 1
				else:
					# Re-insert the old experience with new error value
					if replays[i-1] == None:
						break
						
					if replay_tree.has(replays[i-1]):
						replay_tree.remove(replays[i-1])
					
						r_screens = replays[i-1][0]
						r_actions_taken = replays[i-1][1]
						r_rewards = replays[i-1][2]
						r_id = replays[i-1][3]
							
						#print(r_id, errors[i])
				
						if config.track_position():
							r_positions = replays[i-1][5]
							replay_tree.add((r_screens, r_actions_taken, r_rewards, current_id, errors[i], r_positions))
						else:
							replay_tree.add((r_screens, r_actions_taken, r_rewards, current_id, errors[i]))
						current_id += 1
		else:
			# No Prioritized Replay
			# Store the experience for future replay
			if config.track_position():
				add_replay((screens, actions_taken, rewards, current_id, positions))
			else:
				add_replay((screens, actions_taken, rewards, current_id))
			current_id += 1
		
		if Double:
			# Swap the two networks sometimes
			if random.random() > 0.5:
				modelA, modelB = modelB, modelA
				
		#print('Average target delta: {0}'.format(total_target_delta / num_targets))
		total_target_delta = 0
		num_targets = 0
