#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:36:46 2019

@author: yanghuiwang
"""
import numpy as np
import scipy.sparse as sparse

def get_noisy(ori_graph,percentage=0.01,verbose=False):
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
        threshold=int(percentage*edge_count)
        adj=adj.todense() # change it to dense matrix for better runtime
        if(threshold<1):
            continue
        print("edge_count",edge_count,"threshold",threshold)

        removed = np.zeros(graph.n_nodes)
        remove_upper_bound = np.zeros(graph.n_nodes)

        for i in range(graph.n_nodes):
            n_edge_i = np.sum(graph.sym_composite_adj[i])
            if n_edge_i*percentage*2<1:
                remove_upper_bound[i] = 0
            else:
                remove_upper_bound[i] = np.random.randint(int(n_edge_i*percentage*2))

        for edge_idx in range(threshold):
            while True:
                i = np.random.randint(graph.n_nodes)
                j = np.random.randint(graph.n_nodes)
                if adj[i,j]>=1:
                    adj[i,j]=adj[i,j]-1
                    break
        # count=0
        # for i in i_list:
        #     if adj[i,:].sum==0:
        #         continue
        #     np.random.shuffle(j_list)
        #     for j in j_list:
        #         if adj[i,j]>=1:
        #             count+=1
        #             adj[i,j]=adj[i,j]-1
        #             miss_edge+=1
        #             if count%100==0:
        #                 print("Enter if",count)
        #             break
        #
        #     if(miss_edge>threshold):
        #         break

        missing_edges[channel]=miss_edge
        print("miss_edge",miss_edge,"missing_edges",missing_edges)
        graph.ch_to_adj[channel]=sparse.csr_matrix(adj) # change back to sparse matrix for further operations
    if(verbose==True):
        print("After getting noisy, the world has",graph.composite_adj.sum() ,"edges")
    return graph

def get_noisy_template_number(ori_graph,edge_number=2,verbose=False):
    graph=ori_graph.copy()
    if(verbose==True):
        print("Before getting noisy, the world has",ori_graph.composite_adj.sum(), "edges")
    missing_edges={}
    channels=graph.ch_to_adj.keys()
    num_channels = len(channels)
    channels_add = np.zeros(num_channels)
    for edge_idx in range(edge_number):
        channels_add[np.random.randint(num_channels)] += 1
    i_list = list(range(graph.n_nodes))
    j_list = list(range(graph.n_nodes))

    for channel_idx, channel in enumerate(channels):
        np.random.shuffle(i_list)
        miss_edge=0
        adj=graph.ch_to_adj[channel]
        edge_count=adj.sum()
        threshold=int(channels_add[channel_idx])
        print(channel, threshold)
        adj=adj.todense() # change it to dense matrix for better runtime
        if(threshold<1):
            continue

        for edge_idx in range(threshold):
            while True:
                i = np.random.randint(graph.n_nodes)
                j = np.random.randint(graph.n_nodes)
                if True:
                    adj[i,j]+=1
                    break

        graph.ch_to_adj[channel]=sparse.csr_matrix(adj) # change back to sparse matrix for further operations
    if(verbose==True):
        print("After getting noisy, the world has",graph.composite_adj.sum() ,"edges")
    return graph

def get_noisy_new(ori_graph,percentage=0.01,verbose=False):
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
        threshold=int(percentage*edge_count)
        adj=adj.todense() # change it to dense matrix for better runtime
        if(threshold<1):
            continue
        # print("edge_count",edge_count,"threshold",threshold)

        removed = np.zeros(graph.n_nodes)
        need_remove = np.zeros(graph.n_nodes)

        for i in range(graph.n_nodes):
            n_edge_i = np.sum(graph.sym_composite_adj[i])*percentage
            need_remove[i] = np.random.randint(n_edge_i+1)

        for i in range(graph.n_nodes):
            while need_remove[i]>removed[i]:
                j = np.random.randint(graph.n_nodes)
                d = np.random.randint(2)
                if d==0:
                    if adj[i,j]>=1:
                        adj[i,j]=adj[i,j]-1
                        removed[i]+=1
                        removed[j]+=1
                else:
                    if adj[j,i]>=1:
                        adj[j,i]=adj[j,i]-1
                        removed[i]+=1
                        removed[j]+=1
        # for edge_idx in range(threshold):
        #     while True:
        #         i = np.random.randint(graph.n_nodes)
        #         j = np.random.randint(graph.n_nodes)
        #         if adj[i,j]>=1:
        #             adj[i,j]=adj[i,j]-1
        #             break
        # count=0
        # for i in i_list:
        #     if adj[i,:].sum==0:
        #         continue
        #     np.random.shuffle(j_list)
        #     for j in j_list:
        #         if adj[i,j]>=1:
        #             count+=1
        #             adj[i,j]=adj[i,j]-1
        #             miss_edge+=1
        #             if count%100==0:
        #                 print("Enter if",count)
        #             break
        #
        #     if(miss_edge>threshold):
        #         break

        missing_edges[channel]=miss_edge
        print("miss_edge",miss_edge,"missing_edges",missing_edges)
        graph.ch_to_adj[channel]=sparse.csr_matrix(adj) # change back to sparse matrix for further operations
    if(verbose==True):
        print("After getting noisy, the world has",graph.composite_adj.sum() ,"edges")
    return graph
