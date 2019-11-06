import argparse 
import retro
import numpy as np
import cv2 
import neat
import pickle

parser = argparse.ArgumentParser(description='Training')
# Network/training arguments
parser.add_argument('-d', '--downsample', default=8, type=int,
                    help='How much to downsample the resolution for the network input')
parser.add_argument('-g', '--game', default='SuperMarioBros-Nes', type=str,
                    help='Game environment')
parser.add_argument('--record', default=False, type=bool,
                    help='Record replays into "./replays"')
parser.add_argument('--render', default=True, type=bool,
                    help='Choose to render the screen')
parser.add_argument('--render-freq', dest='render_freq', default=1, type=int,
                    help='Render the screen every N generations')
parser.add_argument('-s', '--state', default='Level1-1', type=str,
                    help='State for the game environment')
parser.add_argument('--greyscale', default=True, type=bool,
                    help='RGB to greyscale for the network input')

args = parser.parse_args()


env = retro.make(game=args.game, state=args.state, record=args.record)

oned_image = []
generation = -1

def eval_genomes(genomes, config):
    global generation
    generation += 1
    for genome_id, genome in genomes:
        
        ob = env.reset() # First image
        #random_action = env.action_space.sample()
        inx,iny,inc = env.observation_space.shape # inc = color

        # image reduction for faster processing
        assert isinstance(args.downsample, int), '--downsample must be an integer value.'
        inx = int(inx/args.downsample)
        iny = int(iny/args.downsample)

        # Model initialization
        model = neat.nn.RecurrentNetwork.create(genome,config)
        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0
        
        done = False
        cv2.namedWindow("network input", cv2.WINDOW_NORMAL)
        #cv2.resizeWindow("network input", 224,240)
        while not done:
            
            if args.render:
                if generation % args.render_freq == 0:
                    env.render() # Optional
            frame+=1

            ob = cv2.resize(ob,(inx,iny)) # Ob is the current frame
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY) # Colors are not important for learning
            cv2.imshow('network input', ob)
            cv2.waitKey(1)
            ob = np.reshape(ob,(inx,iny))


            oned_image = np.ndarray.flatten(ob)
            neuralnet_output = model.activate(oned_image) # Give an output for current frame from neural network
            ob, rew, done, info = env.step(neuralnet_output) # Try given output from network in the game

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
            
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     './config_feedforward')
p = neat.Population(config)
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
# Save the process after each x frames
p.add_reporter(neat.Checkpointer(generation_interval=1000,
    filename_prefix='checkpoints/SuperMarioBros-neat-'))

winner = p.run(eval_genomes)

with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
