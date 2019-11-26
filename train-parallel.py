import argparse 
import retro
import numpy as np
import cv2 
import neat
import pickle
import fileinput
import sys
import glob
import visualize
from datetime import datetime
import os
from shutil import copyfile
import glob

parser = argparse.ArgumentParser(description='Training')
# Network/training arguments
parser.add_argument('-c', '--checkpoint', default=' ', type=str,
                    help='Path to checkpoint file')
parser.add_argument('-d', '--downscale', default=8, type=int,
                    help='How much to reduce input dimensons (X / N)')
parser.add_argument('-e', '--generations', default=100, type=int,
                    help='Number of generations to run')
parser.add_argument('-g', '--game', default='SuperMarioBros-Nes', type=str,
                    help='Name of the game environment')
parser.add_argument('-p', '--parallel', default=2, type=int,
                    help='Runs "p" genomes at once')
parser.add_argument('-r', '--record', default=False, type=str,
                    help='Record replays into "./replays"')
parser.add_argument('-s', '--state', default='Level1-1', type=str,
                    help='State for the game environment')
parser.add_argument('--debug', default='', type=str,
                    help='Allow verbose debug prints')
parser.add_argument('--reduced-action', dest="reduced_action", default='', type=str,
                    help='Reduces the action space for each game')

args = parser.parse_args()
assert args.parallel > 1, 'Parallel must be higher 2 or more'


def _get_actions_smb(a):
    return actions_smb[a.index(max(a))]

def _get_actions_smw(a):
    return actions_smw[a.index(max(a))]

actions_smb = [
            # Move right
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            # Jump
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
            # Move right and jump
            [0, 0, 0, 0, 0, 0, 0, 1, 1],
            # Stand still
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

actions_smw = [
            # Move right
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            # Jump
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
            # Move right and jump
            [0, 0, 0, 0, 0, 0, 0, 1, 1],
            # Stand still
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

state = args.state
game = args.game
def eval_genomes(genomes, config):
    env = retro.make(game=args.game, state=args.state, record=args.record)
    ob = env.reset()

    if args.debug:
        print("Original observation space shape: ",ob.shape)

    if game == 'SuperMarioWorld-Snes':
        # Crop image to match Super Mario Bros
        ob = ob[:, 0:240, :]

        # Remove '.state' from state name for saving file
        state = args.state[0:-6]

    if args.debug:
        print("Cropped observation space shape: ", ob.shape)

    inx = int(ob.shape[0]/args.downscale)
    iny = int(ob.shape[1]/args.downscale)
    done = False

    # Model initialization
    model = neat.nn.RecurrentNetwork.create(genomes,config)

    current_max_fitness = 0
    fitness_current = 0
    frame = 0
    counter = 0
    
    while not done:
        frame+=1

        ob = cv2.resize(ob,(inx,iny)) # Ob is the current frame
        ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY) # Colors are not important for learning

        ob = np.reshape(ob,(inx,iny))

        model_input = np.ndarray.flatten(ob)
        neuralnet_output = model.activate(model_input) # Give an output for current frame from neural network

        # Reduce the action space so that all games have the same sized action space
        if args.reduced_action:
            if args.game == "SuperMarioBros-Nes":
                neuralnet_output = _get_actions_smb(neuralnet_output)
            elif args.game == "SuperMarioWorld-Snes":
                neuralnet_output = _get_actions_smw(neuralnet_output)

        ob, rew, done, info = env.step(neuralnet_output) # Try given output from network in the game

        fitness_current += rew
        if fitness_current > current_max_fitness:
            current_max_fitness = fitness_current
            counter = 0
        else:
            counter+=1
            # count the frames until it successful

        # Train mario for max 250 frames
        if done or counter == 250:
            done = True 
            print(fitness_current)

        #genomes.fitness = fitness_current
    return fitness_current


# Load in the changed config file
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     './config-feedforward')

if args.checkpoint == ' ':
    p = neat.Population(config)
else:

    print('-> Loading %s...' % args.checkpoint)
    p = neat.Checkpointer.restore_checkpoint(args.checkpoint)


if args.reduced_action:
    print("-> Using reduced action space...")
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
# Save the process after each x frames
# Save the process after each x frames
if args.reduced_action:
    game += '(REDUCED)'
output_path = 'checkpoints/' + game + "/" + state + "/" + datetime.now().strftime("%m.%d.%y@%H:%M") + "/"
output_file = "checkpoint-"
if not os.path.exists(output_path):
    os.makedirs(output_path)
    os.makedirs(output_path + "/winner/")
    copyfile("config-feedforward", output_path + "config-feedforward")
p.add_reporter(neat.Checkpointer(generation_interval=100, filename_prefix=output_path + output_file))

pe = neat.parallel.ParallelEvaluator(args.parallel, eval_genomes)
winner = p.run(pe.evaluate, args.generations)

print("-> saving winner")
with open(output_path + "/winner/" + state + '.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)

print("-> cleaning up checkpoints...")
CWD = os.getcwd()
os.chdir(output_path)
results = []
for file in glob.glob("checkpoint-*"):
    results.append(file)

results.sort()
results = results[0:-1]
for i in results:
    os.remove(i)
