from noisy_stats_filter import noisy_stats_filter

from utils import data
import uclasm
import time

import matplotlib.pyplot as plt


print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_v6()
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

tmplt, world, candidates = noisy_stats_filter(tmplt, world, verbose = True)

print(candidates)
