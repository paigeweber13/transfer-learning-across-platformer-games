#!/bin/bash
qsub -q mamba -d $(pwd) -l nodes=1:ppn=16:gpus=1 -l walltime=00:30:00 $1

