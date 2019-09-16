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

tmplt1 = pickle.load(open("noisy_tmplt_2.pl","rb"))
tmplt2 = pickle.load(open("noisy_tmplt_3.pl","rb"))

isomo = pickle.load(open("0.002percent_missing.pl","rb"))



signal = isomo[0].state
miss1, miss_dict1, node_dict1, correspond1 = uclasm.count_missing_edges(tmplt1, world, signal)
miss2, miss_dict2, node_dict2, correspond2 = uclasm.count_missing_edges(tmplt2, world, signal)

convert = {}
count = 0
for x in node_dict1.keys():
    convert[x] = count
    count = count+1

edge_label = {}
me1=[]
me2=[]
for key,val in miss_dict1.items():
    edge_label[(convert[key[0]],convert[key[1]])]=val
    if val is not "":
        me1.append((convert[key[0]],convert[key[1]]))
for key,val in miss_dict2.items():
    if val is not "":
        edge_label[(convert[key[0]],convert[key[1]])]=val
        me2.append((convert[key[0]],convert[key[1]]))
record = []
#
for key, val in edge_label.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
    if val is not "":
        record.append(key[0])
        record.append(key[1])

print("The index of the world candidates isomorphism you want is: ")
print(world.nodes[isomo[0].state])
print("This isomo has a cost of: ")
print(isomo[0].loss)

# import IPython
# IPython.embed()
plot_lost_edge(tmplt1, miss_dict1, node_dict1, "tmplt_noise_2", record=record, me=me1)
plot_lost_edge(tmplt2, miss_dict2, node_dict2, "tmplt_noise_3", record=record, me=me2)
