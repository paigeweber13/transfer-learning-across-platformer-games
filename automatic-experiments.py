import configparser
import logging
import os
import subprocess

logging.basicConfig(filename='automatic-experiments.log',level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config-feedforward')

# same for all
max_num_generations = 200
num_pixels_no_downsampling = 7168

# defaults, might be changed
downsample = 8
survival = 0.2
pop_size = 100

def reset_config():
    config['DefaultReproduction']['survival_threshold'] = str(survival)
    config['NEAT']['pop_size'] = str(pop_size)
    config['DefaultGenome']['num_inputs'] = \
        str(int(num_pixels_no_downsampling/downsample))
    with open('config-feedforward', 'w') as f:
        config.write(f)

# test running train parallel
os.path.expandvars("$PATH")
completed_process = subprocess.run(['python', 'train-parallel.py', '-d',
                                    str(downsample), '-g',  
                                    'SuperMarioWorld-Snes', '-r', './replays',
                                    '-p', '8', '-s', 'YoshiIsland1', '-e',
                                    str(max_num_generations)],
                                    capture_output=True)
print(completed_process.stderr)

# test downsample
logging.debug('testing different downsample sizes:')
reset_config()
i = 32
while i > 3:
    logging.debug(i)
    i /= 2
    
# test survival rate
logging.debug('testing different survival rates:')
reset_config()
j = 0.05
while j < 0.35:
    logging.debug(j)
    j += 0.05

# test pop_size
logging.debug('testing different population sizes:')
reset_config()
k = 50
while k < 500:
    logging.debug(k)
    k *= 2

# test num generations...?
# l = 50
# while l < 500:
#     l *= 2
#     print(i, j, k, l, sep=', ')
