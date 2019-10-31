class weight_balanced_tree(object):
	def __init__(self, weight_function, hash_function):
		self.weight_function = weight_function
		self.left = None
		self.leftW = 0
		self.right = None
		self.rightW = 0
		self.contains = set()
		self.node = None
		self.hash_function = hash_function
		
	def add(self, node):
		self.contains.add(self.hash_function(node))
	
		if self.left == None and self.right == None and self.node == None:
			# Empty leaf node
			self.node = node
		else:
			if self.node != None:
				# Non-empty leaf node, convert to branch node
				self.add_to_tree(self.node)
				self.node = None
				
			self.add_to_tree(node)
		
	def add_to_tree(self, node):
		if self.left == None:
			self.leftW = self.weight_function(node)
			self.left = weight_balanced_tree(self.weight_function, self.hash_function)
			self.left.add(node)
		elif self.right == None:
			self.rightW = self.weight_function(node)
			self.right = weight_balanced_tree(self.weight_function, self.hash_function)
			self.right.add(node)
		elif self.leftW < self.rightW:
			self.leftW += self.weight_function(node)
			self.left.add(node)
		else:
			self.rightW += self.weight_function(node)
			self.right.add(node)
	
	# Returns if this is a leaf node
	def remove(self, node):
		if self.node != None and self.hash_function(self.node) == self.hash_function(node):
			return True
		else:
			self.contains.remove(self.hash_function(node))
			
			if self.left != None and self.hash_function(node) in self.left.contains:
				self.leftW -= self.weight_function(node)
				if self.left.remove(node):
					self.left = None
					self.leftW = 0
				
				return False
				
			elif self.right != None and self.hash_function(node) in self.right.contains:
				self.rightW -= self.weight_function(node)
				if self.right.remove(node):
					self.right = None
					self.rightW = 0
				
				return False
				
			else:
				raise Exception('Tried to remove node that doesn\'t exist')
	
	def sample(self, p):
		if self.node != None:
			return self.node
	
		total = float(self.leftW + self.rightW)
		pleft = self.leftW / total
		pright = 1 - pleft
		
		if p < pleft:
			if self.left == None:
				print(pleft, pright, p, self.leftW, self.rightW)
			return self.left.sample(p / pleft)
		else:
			if self.right == None:
				print(pleft, pright, p, self.leftW, self.rightW)
			return self.right.sample((p - pleft) / pright)

	def size(self):
		return len(self.contains)
		
	def has(self, node):
		return self.hash_function(node) in self.contains