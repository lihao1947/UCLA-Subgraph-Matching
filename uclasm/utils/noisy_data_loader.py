#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:36:46 2019

@author: yanghuiwang
"""
    


def get_noisy(ori_graph,percentage=0.05,verbose=False):
    graph=ori_graph.copy()
    if(verbose==True):
        print("Before getting noisy, the world has",ori_graph.composite_adj.sum(), "edges")
    missing_edges={}
    channels=graph.ch_to_adj.keys()
    i_list = list(range(graph.n_nodes))
    j_list = list(range(graph.n_nodes))
    
    for channel in channels:
        np.random.shuffle(i_list)
        miss_edge=0
        adj=graph.ch_to_adj[channel]
        print("graph.n_nodes",graph.n_nodes)
        print("(adj>1).sum",(adj>1).data.sum())
        edge_count=adj.sum()
        threshold=percentage*edge_count
        adj=adj.todense() # change it to dense matrix for better runtime
        if(threshold<1):
            continue
        print("edge_count",edge_count,"threshold",threshold)

        count=0
        for i in i_list:
            if adj[i,:].sum==0:
                continue
            np.random.shuffle(j_list)            
            for j in j_list:
                if adj[i,j]>=1:
                    count+=1
                    adj[i,j]=adj[i,j]-1
                    miss_edge+=1     
                    if count%100==0:
                        print("Enter if",count)
                    break
            
            if(miss_edge>threshold):
                break
            
        missing_edges[channel]=miss_edge
        print("miss_edge",miss_edge,"missing_edges",missing_edges)
        graph.ch_to_adj[channel]=sparse.csr_matrix(adj) # change back to sparse matrix for further operations
    if(verbose==True):
        print("After getting noisy, the world has",graph.composite_adj.sum() ,"edges")
    return graph
 
