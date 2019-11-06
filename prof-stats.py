import pstats
from pstats import SortKey

# to generate profiling data, run 
# `python -m cProfile -o prof.out neat-supermariobros.py`
p = pstats.Stats('prof.out')
p.strip_dirs().sort_stats('tottime').print_stats()
#p.strip_dirs().sort_stats('percall').print_stats()

