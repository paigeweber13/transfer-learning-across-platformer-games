import tensorflow as tf
import math

class model(object):
	def __init__(self, name, num_inputs, rnn_sizes, conv_sizes, hidden_sizes, num_outputs, seq_length, batch_size, base_learning_rate, lr_decay, reward_discount, grad_clip, pixels, reg_coeff, train):
		self.num_inputs = num_inputs
		self.seq_length = seq_length
		self.num_outputs = num_outputs
		self.dtype = tf.float32
		self.batch_size = batch_size
		self.conv_sizes = conv_sizes
		self.base_learning_rate = base_learning_rate
		self.lr_decay = lr_decay
		self.reward_discount = reward_discount
		self.grad_clip = grad_clip
		self.pixels = pixels
		self.reg_coeff = reg_coeff
		self.name = name
		
		# Build the model
		with tf.variable_scope(name):
			self.build_shared(rnn_sizes)

			self.build_sampler()
			if train:	
				self.build_training_sequence()
			
		self.accumulated_outputs = []
	
	# Creates and stores variables that are shared by the sampler and training sequence
	def build_shared(self, rnn_sizes):
		with tf.variable_scope('Shared'):
			self.layers = [tf.nn.rnn_cell.BasicLSTMCell(size, forget_bias=1.0, state_is_tuple=True) for size in rnn_sizes]
			self.outputW = tf.Variable(tf.truncated_normal([rnn_sizes[-1], self.num_outputs], stddev=1.0 / math.sqrt(float(rnn_sizes[-1]))), name = "OutputW")
			self.outputB = tf.Variable(tf.fill([self.num_outputs], 0.0), name = "OutputB")

	# Builds a convnet. Call first with sample=True, calls with sample=False will reuse the variables.
	def build_conv(self, input, sample):
		with tf.variable_scope('Conv'):
			activation = tf.nn.relu
			
			screens = input.get_shape()[0]
			
			if not self.pixels:
				# split out screen input and extra inputs
				input, extra_inputs = tf.split(input, [15*15, 23+3], 1)
				input = tf.reshape(input, [screens, 15, 15, 1])
			
			if sample:
				# Create a list of convnet outputs to use for debug display
				self.conv_out = []
		
			if self.pixels:
				# Put the 8 bit pixels into the [0,1) range
				conv = input / 256
			else:
				conv = input
			
			# Create convnet layers
			count = 0
			for type, (sizex, sizey), (stridex, stridey), filters in self.conv_sizes:
				count += 1
				if type == 'CONV':
					conv = tf.layers.conv2d(conv, filters, [sizey, sizex], [stridey, stridex], 'valid', 'channels_last', activation=activation, reuse=not sample, name='conv{0}'.format(count))
				elif type in ['AVG', 'MAX']:
					conv = tf.nn.pool(conv, [sizey, sizex], type, 'VALID', strides=[stridey, stridex])
				else:
					raise Exception('Unknown convolution layer type "{0}"'.format(type))
				
				if sample:
					self.conv_out.append(conv)
				
			# Flatten the final layer into a single dimension
			conv = tf.reshape(conv, [screens, -1])
				
			if not self.pixels:
				# merge conv output and extra inputs
				conv = tf.concat([conv, extra_inputs], 1)
				
			return conv
	
	# Builds the single time step sampler
	def build_sampler(self):
		with tf.variable_scope('Sample'):
			self.single_input = tf.placeholder(shape=[self.batch_size] + self.num_inputs, dtype = self.dtype)
		
		rnn_input = self.single_input
		
		# Create convnet layers
		if len(self.conv_sizes) > 0:
			rnn_input = self.build_conv(self.single_input, sample=True)
		
		with tf.variable_scope('Sample'):
			cell = tf.nn.rnn_cell.MultiRNNCell(self.layers, state_is_tuple=True)
			self.single_initial_state = state = cell.zero_state(self.batch_size, dtype = self.dtype)
			
			(cell_output, self.single_state_output) = cell(rnn_input, state)
			
			self.single_output = tf.matmul(cell_output, self.outputW) + self.outputB
	
	# Builds the training sequence
	def build_training_sequence(self):
		with tf.variable_scope('Train'):
			self.sequence_input = tf.placeholder(shape=[self.seq_length, self.batch_size] + self.num_inputs, dtype = self.dtype)
			self.labels = tf.placeholder(shape=[self.seq_length, self.batch_size, self.num_outputs], dtype = self.dtype)
			self.weights = tf.placeholder(shape=[self.seq_length, self.batch_size, self.num_outputs], dtype = self.dtype)
		
		rnn_input = self.sequence_input
		
		if len(self.conv_sizes) > 0:
			squished_sequence = tf.reshape(self.sequence_input, [self.seq_length * self.batch_size] + self.num_inputs)
			
			conv_out = self.build_conv(squished_sequence, sample=False)
			rnn_input = tf.reshape(conv_out, [self.seq_length, self.batch_size, -1])

		with tf.variable_scope('Train'):
			cell = tf.nn.rnn_cell.MultiRNNCell(self.layers, state_is_tuple=True)
			self.sequence_initial_state = state = cell.zero_state(self.batch_size, dtype = self.dtype)
			
			self.outputs = []
		
			with tf.variable_scope('Sequence'):
				for time_step in range(self.seq_length):
					if time_step > 0:
						tf.get_variable_scope().reuse_variables()
					(cell_output, state) = cell(rnn_input[time_step], state)
					
					output = tf.matmul(cell_output, self.outputW) + self.outputB
					self.outputs.append(output)
				
			self.sequence_final_state = state
			
			batch_labels = tf.split(self.labels, self.batch_size, 1)
			batch_outputs = tf.split(self.outputs, self.batch_size, 1)
			batch_weights = tf.split(self.weights, self.batch_size, 1)
			
			self.individual_costs = [tf.losses.mean_squared_error(
					batch_labels[b],
					batch_outputs[b],
					batch_weights[b],
			) for b in range(self.batch_size)]
			
			tvars = tf.trainable_variables(self.name)
			
			cost = tf.reduce_mean(self.individual_costs)
			#self.cost = tf.losses.mean_squared_error(
			#	self.labels,
			#	self.outputs,
			#	self.weights
			#)
			if self.reg_coeff > 0:
				reg_losses = [tf.contrib.layers.l2_regularizer(scale=1.0)(tvar) for tvar in tvars]
				print("Regularization losses:")
				print(reg_losses)
				print("End regularization losses.")
				cost += sum(reg_losses) * self.reg_coeff
			
			self.cost = cost
			
			print('Trainable variables for model:')
			for tvar in tvars:
				print(tvar)
			print('End trainable variables')
			grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, tvars), self.grad_clip)
			
			if len(self.conv_sizes) > 0:
				tvars2 = tf.trainable_variables(self.name)
				non_conv_tvars = []
				for v in tvars2:
					if 'Conv' not in v.name:
						non_conv_tvars.append(v)
						
				non_conv_grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, non_conv_tvars), self.grad_clip)
			
			self.learning_rate_var = tf.Variable(self.learning_rate(0), name='learning_rate')
			#optimizer = tf.train.AdamOptimizer()
			optimizer = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate_var)
			#optimizer = tf.train.RMSPropOptimizer(self.learning_rate_var, momentum=0.95, epsilon=0.01)
			self.train_op = optimizer.apply_gradients(
				zip(grads, tvars),
				global_step=tf.contrib.framework.get_or_create_global_step())
				
			if len(self.conv_sizes) > 0:
				self.non_conv_train_op = optimizer.apply_gradients(
					zip(non_conv_grads, non_conv_tvars),
					global_step=tf.contrib.framework.get_or_create_global_step())


	# Initializes the RNN state, stores the session
	def init(self, session):
		self.seq_state = session.run(self.sequence_initial_state)
		self.single_state = session.run(self.single_initial_state)
		self.session = session

	# Runs a single time step in the sampler
	def single_forward(self, inputs):
		single_feed_dict = {}
		for i, (c, h) in enumerate(self.single_initial_state):
			single_feed_dict[c] = self.single_state[i].c
			single_feed_dict[h] = self.single_state[i].h
		single_feed_dict[self.single_input] = inputs
		single_fetch = {
			"Q_Vals": self.single_output,
			"State": self.single_state_output,
		}
		
		if len(self.conv_sizes) > 0:
			single_fetch['conv'] = self.conv_out
		
		# Run neural network forward with screen and replay
		vals = self.session.run(single_fetch, single_feed_dict)
		
		# Get network output and LSTM state
		q_vals = vals["Q_Vals"]
		self.single_state = vals["State"]
		
		self.accumulated_outputs.append(q_vals)
		
		if len(self.conv_sizes) > 0:
			convs = vals['conv']
		else:
			convs = None
		
		return q_vals, convs
	
	# Runs a whole sequence and trains the network.
	def sequence_train(self, inputs, targets, weights, step, no_train=False):
		seq_feed_dict = {
			self.learning_rate_var: self.learning_rate(step)
		}
		seq_feed_dict[self.sequence_input] = inputs
			
		# Perform training op with the calculated targets
		seq_feed_dict[self.labels] = targets
		seq_feed_dict[self.weights] = weights
		for i, (c, h) in enumerate(self.sequence_initial_state):
			seq_feed_dict[c] = self.seq_state[i].c
			seq_feed_dict[h] = self.seq_state[i].h
			
		fetches = { 'final_state': self.sequence_final_state }
		
		if not no_train:
			#if self.conv_sizes != None and step <= 1:
			#	fetches['train'] = self.non_conv_train_op
			#else:
				fetches['train'] = self.train_op
			
		fetches['outputs'] = self.outputs
		fetches['error'] = self.individual_costs
			
		vals = self.session.run(fetches, seq_feed_dict)
		
		self.seq_state = vals['final_state']
		outputs = vals['outputs']
		error = vals['error']
		
		for t in range(len(outputs)):
			for b in range(len(outputs[0])):
				for q in range(len(outputs[0][0])):
					assert(outputs[t][b][q] == self.accumulated_outputs[t][b][q])
					
		self.accumulated_outputs = []
		
		return error
	
	# Gets the learning rate for the current global time step.
	def learning_rate(self, step):
		return self.base_learning_rate * (self.lr_decay ** step)