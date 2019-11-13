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

args = parser.parse_args()
assert args.parallel > 1, 'Parallel must be higher 2 or more'

def eval_genomes(genomes, config):
    env = retro.make(game=args.game, state=args.state, record=args.record)
    ob = env.reset()

    inx = int(ob.shape[0]/args.downscale)
    iny = int(ob.shape[1]/args.downscale)
    done = False

    # Model initialization
    model = neat.nn.RecurrentNetwork.create(genomes,config)

    current_max_fitness = 0
    fitness_current = 0
    frame = 0
    counter = 0
    
    # The downsampled frame that the network sees
    # cv2.namedWindow("network input", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("network input", 224,240) # Resize the above window

    while not done:
        frame+=1

        ob = cv2.resize(ob,(inx,iny)) # Ob is the current frame
        ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY) # Colors are not important for learning

        ob = np.reshape(ob,(inx,iny))


        model_input = np.ndarray.flatten(ob)
        neuralnet_output = model.activate(model_input) # Give an output for current frame from neural network
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

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
# Save the process after each x frames
p.add_reporter(neat.Checkpointer(generation_interval=10,
    filename_prefix='checkpoints/SuperMarioBros-neat-'))


pe = neat.parallel.ParallelEvaluator(args.parallel, eval_genomes)
winner = p.run(pe.evaluate, args.generations)

print("-> saving winner")
with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
