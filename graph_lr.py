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
import matplotlib

import warnings
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser(description='Training')

parser.add_argument('-p', '--parallel', default=8, type=int,
                    help='Runs "p" genomes at once')

parser.add_argument('-d', '--downscale', default=8, type=int,
                    help='How much to reduce input dimensons (X / N)')

parser.add_argument('-g', '--game', default='DonkeyKongCountry-Snes', type=str,
                    help='Name of the game environment')

args = parser.parse_args()
assert args.parallel > 1, 'Parallel must be higher 2 or more'

fitnesses = []

def eval_genomes(genomes, config):
    env = retro.make(game=args.game)
    ob = env.reset()

    inx = int(ob.shape[0] / args.downscale)
    iny = int(ob.shape[1] / args.downscale)
    done = False

    # Model initialization
    model = neat.nn.RecurrentNetwork.create(genomes, config)

    current_max_fitness = 0
    fitness_current = 0
    frame = 0
    counter = 0

    # The downsampled frame that the network sees
    # cv2.namedWindow("network input", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("network input", 224,240) # Resize the above window

    while not done:
        frame += 1

        ob = cv2.resize(ob, (inx, iny))  # Ob is the current frame
        # Colors are not important for learning
        ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)

        ob = np.reshape(ob, (inx, iny))

        model_input = np.ndarray.flatten(ob)
        # Give an output for current frame from neural network
        neuralnet_output = model.activate(model_input)
        # Try given output from network in the game
        ob, rew, done, info = env.step(neuralnet_output)

        fitness_current += rew
        if fitness_current > current_max_fitness:
            current_max_fitness = fitness_current
            counter = 0
        else:
            counter += 1
            # count the frames until it successful

        # Train mario for max 250 frames
        if done or counter == 250:
            done = True
            #print(fitness_current)

        # genomes.fitness = fitness_current
    return fitness_current


file_prefix = "./checkpoints/DonkeyKongCountry-neat-"
for i in range(5):
    gen_num = str(i * 10 + 9)
    print('Running for gen:', gen_num)
    try:
        p = neat.Checkpointer.restore_checkpoint(file_prefix + gen_num)
    except:
        continue
    pe = neat.parallel.ParallelEvaluator(args.parallel, eval_genomes)
    winner = p.run(pe.evaluate, 1)
    fitnesses.append(winner.fitness)

print('end:', fitnesses)

with open('fitnesses.pkl', 'wb') as output:
    pickle.dump(fitnesses, output, 1)
