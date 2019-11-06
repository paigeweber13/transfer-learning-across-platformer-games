import pstats
from pstats import SortKey

p = pstats.Stats('prof.out')
p.strip_dirs().sort_stats('cumtime').print_stats()
p.strip_dirs().sort_stats('time').print_stats()

