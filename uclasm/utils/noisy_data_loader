#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:36:46 2019

@author: yanghuiwang
"""

import numpy as np
# add noise to the template
def get_noisy(ori_graph,percentage=0.05,verbose=False):
    graph=ori_graph.copy()
    if(verbose==True):
        print("Before getting noisy, the template has",ori_graph.composite_adj.sum(), "edges")
    missing_edges={}
    channels=graph.ch_to_adj.keys()
    i_list = list(range(graph.n_nodes))
    j_list = list(range(graph.n_nodes))
    
    for channel in channels:
        np.random.shuffle(i_list)
        add_edge=0
        adj=graph.ch_to_adj[channel]
        edge_count=adj.sum()
        threshold=percentage*edge_count
        if(threshold<1):
            continue
        #print("edge_count",edge_count,"threshold",threshold)
#        while add_edge< threshold:
#            print("turue")
        for i in i_list:
#                if adj[i,:].sum==0:
#                    continue
            #try:
            np.random.shuffle(j_list)
            for j in j_list[:5]: # parametrize this number??
                adj[i,j]=adj[i,j]+1
                add_edge+=1
                if(add_edge>threshold):
                    break
            if(add_edge>threshold):
                    break
#                except:add_edge
#                    for j in j_list[:len(adj[i,:].data)]:
#                        adj[i,j]=adj[i,j]+1
#                        miss_edge+=1
#                compliment=adj[adj<0].sum()
#                miss_edge+=compliment
#                adj[adj<0]=0
        missing_edges[channel]=add_edge
        #print("add_edge",add_edge,"missing_edges",missing_edges)
        graph.ch_to_adj[channel]=adj
    if(verbose==True):
        print("After getting noisy, the template has",graph.composite_adj.sum() ,"edges")
    return graph
  
