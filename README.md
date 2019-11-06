## Learning to play games using OpenAI gym-retro with NEAT
NEAT (NeuroEvolution of Augmenting Topologies) is a method developed by Kenneth O. Stanley for evolving arbitrary neural networks. 

For further information regarding general concepts and theory, please see Selected Publications on Stanley's [website](http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf).

### Training
The training files can run with default arguments

#### Single-threaded
This will train using a single cpu core as well as render the OpenAI environment and downsampled network input. 

For help:
```bash
python3 train.py -h
```
Format:
```bash
python3 train.py -c <checkpoint-filepath> -d <downscale rate> -g <game-env> -e <number-of-generations> -r <record (bool)> -s <state>
```
#### Multi-threaded
This will train using <i>p</i> number of threads. This will not do any rendering.
For help:
```bash
python3 train-parallel.py -h
```
Format:
```bash
python3 train-parallel.py -c <checkpoint-filepath> -d <downscale rate> -g <game-env> -e <number-of-generations> -p <number of threads> -r <record (bool)> -s <state>
```

#### Playback
This will playback the winning genome (or any genome saved in the pickle format)
```bash
python3 playback.py -d <downscale rate> -g <game> -p <path-to-winner.pkl> -s <state>
```

### Additional References
[retro-gym](https://github.com/openai/retro)

[neat-python](https://github.com/CodeReclaimers/neat-python)

[Medium blog post](https://medium.com/datadriveninvestor/super-mario-bros-reinforcement-learning-77d6615a805e)


