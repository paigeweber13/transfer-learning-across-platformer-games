import threading
import time

def worker():
	global sum
	global done
	print('Worker starting')
	for i in range(count):
		sum += i
		
	done = True
		

for i in range(5):
	t = threading.Thread(target=worker)
	sum = 0
	count = 10000000
	done = False

	print('Starting thread')
	t.start()

	while not done:
		print(sum)
		time.sleep(0.1)
		
		
	print('Task done')
	print(sum)