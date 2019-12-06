#!/bin/bash
qsub -q mamba -d $(pwd) -l nodes=2:ppn=16:gpus=1 -l walltime=10:00:00 $1

