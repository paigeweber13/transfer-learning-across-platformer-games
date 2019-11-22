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
parser.add_argument('-g', '--game', default='DonkeyKongCountry-Snes', type=str,
                    help='Name of the game environment')
parser.add_argument('-e', '--generations', default=100, type=int,
                    help='Number of generations to run')
parser.add_argument('-r', '--record', default=False, type=bool,
                    help='Record replays into "./replays"')
# parser.add_argument('-s', '--state', default='Level1-1', type=str,
#                    help='State for the game environment')

args = parser.parse_args()

# env = retro.make(game=args.game, state=args.state, record=args.record)
env = retro.make(game=args.game, record=args.record)
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:

        ob = env.reset()
        print(ob)
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
            #action = [0,0,0,0,0,0,1,1,1]
            oned_image = np.ndarray.flatten(ob)
            neuralnet_output = model.activate(oned_image) # Give an output for current frame from neural network
            
            #ob, rew, done, info = env.step(action) # Try given output from network in the game
            ob, rew, done, info = env.step(neuralnet_output) # Try given output from network in the game
            print(neuralnet_output)
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
                print(genome_id,fitness_current)

            genome.fitness = fitness_current

# Load in the changed config file
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     './config_feedforward')

if args.checkpoint == ' ':
    p = neat.Population(config)
else:
    print('-> Loading %s...' % args.checkpoint)
    p = neat.Checkpointer.restore_checkpoint("./checkpoints/" + args.checkpoint)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

# Save the process after each x frames
p.add_reporter(neat.Checkpointer(generation_interval=1000, filename_prefix='checkpoints/SuperMarioBros-neat-'))

winner = p.run(eval_genomes, args.generations)

# Display the winning genome.
print("-> Best genome: %s\n->Fitness: %s" % (winner.key, winner.fitness))
# visualize.draw_net(config, winner, True)
# visualize.plot_stats(stats, ylog=False, view=True)
# visualize.plot_species(stats, view=True)

print("-> saving winner")
with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
