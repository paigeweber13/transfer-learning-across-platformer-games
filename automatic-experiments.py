import configparser
import logging
import os
import re
import subprocess
import time

logging.basicConfig(filename='automatic-experiments.log',level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config-feedforward')

# same for all
max_num_generations = 200
num_pixels_no_downsampling = 7168

def set_config(downsample=8, survival=0.2, pop_size=100):
    num_inputs = int(num_pixels_no_downsampling/downsample)

    # I don't know why, but these are special cases
    if downsample == 16:
        num_inputs = 224
    if downsample == 32:
        num_inputs = 56
    if downsample == 4:
        num_inputs = 3584
    # print('full match:', match.group(0))
    # print('num generations:', match.group(1))
    config['DefaultReproduction']['survival_threshold'] = str(survival)
    config['NEAT']['pop_size'] = str(pop_size)
    config['DefaultGenome']['num_inputs'] = str(num_inputs)
        
    with open('config-feedforward', 'w') as f:
        config.write(f)

def reset_config():
    set_config(downsample=8, survival=0.2, pop_size=100)

# pattern will be reused between iterations of run_train_parallel
pattern = re.compile(r"generation (\d+)")

# test running train parallel
def run_train_parallel(downsample, max_num_generations):
    NUM_THREADS = 8
    os.path.expandvars("$PATH")

    completed_process = subprocess.run(['python', 'train-parallel.py', '-d',
                                        str(downsample), '-g',  
                                        'SuperMarioWorld-Snes', '-r', 
                                        './replays', '-p', str(NUM_THREADS), 
                                        '-s', 'YoshiIsland1', '-e',
                                        str(max_num_generations)],
                                        capture_output=True)

    logging.debug(completed_process.stdout)
    logging.error(completed_process.stderr)

    reversed = completed_process.stdout[::-1]
    i = reversed.index(b' gninnuR ****** ')
    j = reversed.index(b'renniw gnivas')
    final_generation_stats = str(reversed[i:j:-1])
    # logging.debug(final_generation_stats)

    match = pattern.search(final_generation_stats)
    # print('full match:', match.group(0))
    # print('num generations:', match.group(1))
    return int(match.group(1))

def print_header():
    print('downsample', 'survival', 'pop_size', 
          'num_generations_before_success', 'total_time', 
          'time_per_generation', sep=',')

# run_train_parallel(8, 2)

# test downsample
status_string = 'testing different downsample sizes:'
logging.debug(status_string)
print(status_string)
reset_config()
print_header()

i = 32
while i > 3:
    logging.debug(i)
    set_config(downsample=i)
    start_time = time.time()
    num_generations_needed = run_train_parallel(i, max_num_generations)
    end_time = time.time()
    duration = end_time - start_time
    print(i, 0.2, 100, num_generations_needed, duration, 
          duration/num_generations_needed, sep=',')
    i = int(i/2)
    
# test survival rate
status_string = 'testing different survival rates:'
logging.debug(status_string)
print(status_string)
reset_config()
print_header()

j = 0.05
while j < 0.35:
    logging.debug(j)
    set_config(survival=i)
    start_time = time.time()
    num_generations_needed = run_train_parallel(i, max_num_generations)
    end_time = time.time()
    duration = end_time - start_time
    print(i, 0.2, 100, num_generations_needed, duration, 
          duration/num_generations_needed, sep=',')
    j += 0.05

# test pop_size
status_string = 'testing different population sizes:'
logging.debug(status_string)
print(status_string)
reset_config()
print_header()
reset_config()
k = 50
while k < 500:
    logging.debug(k)
    set_config(pop_size=i)
    start_time = time.time()
    num_generations_needed = run_train_parallel(i, max_num_generations)
    end_time = time.time()
    duration = end_time - start_time
    print(i, 0.2, 100, num_generations_needed, duration, 
          duration/num_generations_needed, sep=',')
    k *= 2

# test num generations...?
# l = 50
# while l < 500:
#     l *= 2
