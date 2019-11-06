import glob
import os
import retro
import numpy as np # For image-matrix/vector operations
import cv2 # For image reduction
import neat
import pickle

# os.system("python -m retro.import ./roms")


env = retro.make(game='SuperMarioBros-Nes', state='Level1-1',
        record='./replays')
# env = retro.make(game='SuperMarioBros-Nes', state='Level1-1')

oned_image = []

def eval_genomes(genomes, config):

    for genome_id, genome in genomes:
        
        ob = env.reset() # First image
        random_action = env.action_space.sample()
        inx,iny,inc = env.observation_space.shape # inc = color
        # image reduction for faster processing
        inx = int(inx/8)
        iny = int(iny/8)
        # 20 Networks
        net = neat.nn.RecurrentNetwork.create(genome,config)
        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0
        
        done = False

        while not done:
            env.render() # Optional
            frame+=1

            ob = cv2.resize(ob,(inx,iny)) # Ob is the current frame
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY) # Colors are not important for learning
            ob = np.reshape(ob,(inx,iny))
            
            oned_image = np.ndarray.flatten(ob)
            neuralnet_output = net.activate(oned_image) # Give an output for current frame from neural network
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

# restore most recent checkpoint, if they exist:
list_of_files = glob.glob('./checkpoints/*') 
if len(list_of_files) > 0:
    print('loading most recent checkpoint...')
    latest_file = max(list_of_files, key=os.path.getctime)
    p = neat.Checkpointer.restore_checkpoint(latest_file)
else:
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

