import random
from weight_balanced_tree import weight_balanced_tree

tree = weight_balanced_tree(lambda x: x, lambda x: x)

for i in range(10):
	tree.add(i)
	
tree.remove(3)
tree.remove(9)
	
print(tree.leftW + tree.rightW)
print(tree.contains)
p = [0 for i in range(10)]
for t in range(10000):
	i = tree.sample(random.random())
	p[i] += 1
	
print(p)