# import os
import retro
import numpy as np # For image-matrix/vector operations
import cv2 # For image reduction
import neat
import pickle

# os.system("python -m retro.import ./roms")

#print('all available games:')
# list of all available envs is also here:
# https://github.com/openai/retro/tree/master/retro/data/stable
#print(retro.data.list_games())

print('testing super mario bros env:')
env = retro.make(game='SuperMarioBros-Nes', state='Level1-1', record=True)
oned_image = []

# env.reset()

# done = False

# while not done:
#     env.render()
    
#     #action = env.action_space.sample()
#     action = [0,0,1,0,0,0,0,1,0,1,0,0]

    
#     ob, rew, done, info = env.step(action)
#     print("Action ", action, "Reward ", rew)


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
p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
# Save the process after each 10 frames
p.add_reporter(neat.Checkpointer(10))

winner = p.run(eval_genomes)

with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
