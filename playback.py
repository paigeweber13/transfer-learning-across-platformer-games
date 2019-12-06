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




imgarray = []
env = retro.make(game=args.game, state=args.state)

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

with open(args.playback, 'rb') as input_file:
    genome = pickle.load(input_file)

ob = env.reset()

if args.game == 'SuperMarioWorld-Snes':

    # Crop image to match Super Mario Bros
    ob = ob[:, 0:240, :]

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
    
    neuralnet_output = model.activate(imgarray)

    # Reduce the action space so that all games have the same sized action space
    if args.reduced_action:
        if args.game == "SuperMarioBros-Nes":
            neuralnet_output = _get_actions_smb(neuralnet_output)
        elif args.game == "SuperMarioWorld-Snes":
            neuralnet_output = _get_actions_smw(neuralnet_output)
    
    ob, rew, done, info = env.step(neuralnet_output)
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
