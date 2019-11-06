import retro
import numpy as np
import cv2 
import neat
import pickle
import argparse

parser = argparse.ArgumentParser(description='Training')
# Network/training arguments
parser.add_argument('-d', '--downscale', default=8, type=int,
                    help='How much to reduce input dimensons (X / N)')
parser.add_argument('-g', '--game', default='SuperMarioBros-Nes', type=str,
                    help='Name of the game environment')
parser.add_argument('-p', '--playback', default='winner.pkl', type=str,
                    help='Path to pickle file to playback')
parser.add_argument('-s', '--state', default='Level1-1', type=str,
                    help='State for the game environment')

args = parser.parse_args()

imgarray = []
env = retro.make(game=args.game, state=args.state)

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config_feedforward')

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

with open(args.playback, 'rb') as input_file:
    genome = pickle.load(input_file)

ob = env.reset()

inx = int(ob.shape[0]/args.downscale)
iny = int(ob.shape[1]/args.downscale)

model = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

current_max_fitness = 0
fitness_current = 0
frame = 0
counter = 0

# The downsampled frame that the network sees
cv2.namedWindow("network input", cv2.WINDOW_NORMAL)

done = False
while not done:
    env.render()
    frame += 1

    ob = cv2.resize(ob, (inx, iny))
    ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)

    # Scaled input
    cv2.imshow('network input', ob)
    cv2.waitKey(1)

    ob = np.reshape(ob, (inx,iny))

    for x in ob:
        for y in x:
            imgarray.append(y)
    
    nnOutput = net.activate(imgarray)
    
    ob, rew, done, info = env.step(nnOutput)
    imgarray.clear()
    
    fitness_current += rew
    if fitness_current>current_max_fitness:
        current_max_fitness = fitness_current
        counter = 0
    else:
        counter+=1
        # count the frames until it successful

    # Train mario for max 250 frames
    if done or counter == 250:
        done = True 
        print(fitness_current)