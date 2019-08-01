# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 11:15:07 2019

@author: hexie
"""
from utils import data
import uclasm
import pickle
import matplotlib.pyplot as plt
from filters.attribute_filter_btn import attribute_filter


tmplts, world = data.pnnl_v6(0)
tmplt = tmplts[0]

isomo = pickle.load(open("astar_btn.pl","rb"))

print("The index of the world candidates isomorphism you want is: ")
print(world.nodes[isomo[0].state])
print("This isomo has a cost of: ")
print(isomo[0].loss)