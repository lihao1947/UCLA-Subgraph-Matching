# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 11:15:07 2019

@author: hexie
"""
from utils import data
import uclasm
import pickle
import matplotlib.pyplot as plt
# from filters.attribute_filter_btn import attribute_filter
from plotting.plot_noise import plot_lost_edge


tmplts, world = data.pnnl_v6(0)
tmplt = tmplts[0]

tmplt = pickle.load(open("noisy_tmplt_6.pl","rb"))

isomo = pickle.load(open("6_add.pl","rb"))



signal = isomo[0].state
miss, miss_dict, node_dict, correspond = uclasm.count_missing_edges(tmplt, world, signal)


print("The index of the world candidates isomorphism you want is: ")
print(world.nodes[isomo[0].state])
print("This isomo has a cost of: ")
print(isomo[0].loss)

# import IPython
# IPython.embed()
plot_lost_edge(tmplt, miss_dict, node_dict, "test_lost_edge")
