from noisy_stats_filter import noisy_stats_filter
from noisy_topology_filter import noisy_topology_filter

from Xie.stats_filter_noisy import stats_filter_noisy as Xie_stats
from Xie.topology_filter_noisy import topology_filter_noisy as Xie_topology

from utils import data
import uclasm
import time
import numpy as np

import matplotlib.pyplot as plt


print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_rw()
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

tmplt, world, candidates_0 = noisy_stats_filter(tmplt, world, verbose = True)

print(candidates_0)

tmplt, world, candidates_1 = noisy_topology_filter(tmplt, world, candidates_0)

print(candidates_1)

candidates = np.ones((tmplt.n_nodes, world.n_nodes), dtype=np.bool)
tmplt, world, candidates_x0 = Xie_stats(tmplt, world, candidates, verbose = True)
tmplt, world, candidates_x1 = Xie_topology(tmplt, world, candidates_x0, verbose = True)
