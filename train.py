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


parser = argparse.ArgumentParser(description='Training')
# Network/training arguments
parser.add_argument('-c', '--checkpoint', default='', type=str,
                    help='Path to checkpoint file')
parser.add_argument('-d', '--downscale', default=8, type=int,
                    help='How much to reduce input dimensons (X / N)')
parser.add_argument('-g', '--game', default='SuperMarioBros-Nes', type=str,
                    help='Name of the game environment')
parser.add_argument('-e', '--generations', default=100, type=int,
                    help='Number of generations to run')
parser.add_argument('-r', '--record', default=False, type=bool,
                    help='Record replays into "./replays"')
parser.add_argument('-s', '--state', default='Level1-1', type=str,
                    help='State for the game environment')
parser.add_argument('--debug', default='', type=str,
                    help='Allow verbose debug prints')
parser.add_argument('--reduced-action', dest="reduced_action", default='', type=str,
                    help='Reduces the action space for each game')
args = parser.parse_args()

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
env = retro.make(game=args.game, state=args.state, record=args.record)
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:

        ob = env.reset()
        if args.debug:
            if args.reduced_action:
                print("-> Using reduced action space...")
            print("Original observation space shape: ",ob.shape)
        #print(env.action_space)

        if game == 'SuperMarioWorld-Snes':
            # Crop image to match Super Mario Bros
            ob = ob[:, 0:240, :]
            if args.debug:
                print("-> Cropping SMW to fit SMB...")
                print("Cropped observation space shape: ", ob.shape)

            # Remove '.state' from state name for saving file
            state = args.state[0:-6]
        
        inx = int(ob.shape[0]/args.downscale)
        iny = int(ob.shape[1]/args.downscale)
        done = False

        # Model initialization
        model = neat.nn.RecurrentNetwork.create(genome,config)

        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0

        # The downsampled frame that the network sees
        cv2.namedWindow("network input", cv2.WINDOW_NORMAL)
        while not done:
            env.render()
            frame+=1
            
            ob = cv2.resize(ob,(inx,iny)) # Ob is the current frame
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY) # Colors are not important for learning

            # displays the input to the model (downsampled frames)
            cv2.imshow('network input', ob)
            cv2.waitKey(1)
            ob = np.reshape(ob,(inx,iny))
            #print(ob.shape)
            flattend_ob = np.ndarray.flatten(ob)
            #print(flattend_ob.shape)
            neuralnet_output = model.activate(flattend_ob) # Give an output for current frame from neural network

            # Reduce the action space so that all games have the same sized action space
            if args.reduced_action:
                if args.game == "SuperMarioBros-Nes":
                    neuralnet_output = _get_actions_smb(neuralnet_output)
                elif args.game == "SuperMarioWorld-Snes":
                    neuralnet_output = _get_actions_smw(neuralnet_output)
            
            ob, rew, done, info = env.step(neuralnet_output) # Try given output from network in the game
            
            fitness_current += rew
            if fitness_current>current_max_fitness:
                current_max_fitness = fitness_current
                counter = 0
            else:
                # count the frames until it successful
                counter+=1
                
            # Train mario for max 250 frames
            if done or counter == 250:
                done = True 
                print(genome_id,fitness_current)

            genome.fitness = fitness_current

# Load in the changed config file
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     './config-feedforward')

if args.checkpoint:
    print('-> Loading %s...' % args.checkpoint)
    p = neat.Checkpointer.restore_checkpoint(args.checkpoint)
else:
    p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

# Save the process after each x frames
if args.reduced_action:
    game += '(REDUCED)'
output_path = 'checkpoints/' + game + "/" + state + "/" + datetime.now().strftime("%m.%d.%y@%H:%M") + "/"
output_file = "checkpoint-"
if not os.path.exists(output_path):
    os.makedirs(output_path)
    os.makedirs(output_path + "/winner/")
p.add_reporter(neat.Checkpointer(generation_interval=10, filename_prefix=output_path + output_file))

winner = p.run(eval_genomes, args.generations)

# Display the winning genome.
print("-> Best genome: %s\n->Fitness: %s" % (winner.key, winner.fitness))
# visualize.draw_net(config, winner, True)
# visualize.plot_stats(stats, ylog=False, view=True)
# visualize.plot_species(stats, view=True)

print("-> saving winner")
with open(output_path + "/winner/" + state + '.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
