# Machine Learning in Super Mario Kart
Group project for ITCS 6156, Fall 2019

# Set-up
 - install [anaconda](https://repo.anaconda.com/archive/Anaconda3-2019.07-Windows-x86_64.exe)
 - using the anaconda prompt, `cd` to wherever you cloned this repository
 - create an environment by using `conda env create -f environment.yml`
 - activate that environment using `conda activate 
   super-mario-kart-ml-ai-comparison`. This will need to be done every time you
   work on this project.
 - Follow SethBling's instructions:
    - [Instructions for MarIQ](https://docs.google.com/document/d/1uxzeSMqj56YGWh8LkzfNriuGvA3aWU3olg-MSCgWuSI/edit)
    - [Instructions for MariFlow](https://docs.google.com/document/d/1p4ZOtziLmhf0jPbZTTaFxSKdYqE91dYcTNqTVdd6es4/edit)
    - when he tells you to download BizHawk stuff, put that in the BizHawk
      folder.
    - when he tells you to download his stuff, put that in the SethBling folder.
    - when running the neural network, use defaults.cfg, not config/sample.cfg
    - I had to change 'Pixels' to 'pixels' in QLearning/defaults.cfg

# Findings
We're trying to decipher SethBling's code and how to use it. Here are some
notes on things that we've discovered so far.

## Getting environment info:
lines 341 of learn.py is the following:
    for time_step in range(config.get_sequence_length()):
        # Get the experience data from the client
        screen, controller, reward, do_display, pos = client.receive()
(see also lines 258-274)

the client object seems to be what provides information from the emulator...
This game client is stored in game_client.py and it seems to be the server that
the lua script connects to.
