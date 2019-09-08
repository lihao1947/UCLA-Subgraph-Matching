import numpy as np
from functools import reduce
from operator import mul

def iter_adj_pairs(tmplt, world):
    for channel, tmplt_adj in tmplt.ch_to_adj.items():
        world_adj = world.ch_to_adj[channel]
        yield (tmplt_adj, world_adj)
        yield (tmplt_adj.T, world_adj.T)

def count_missing_edges(tmplt, world, signal):
    miss = 0
    miss_dict = {}
    
    node_dict = {}
    
    
    correspond = dict(zip(tmplt.nodes, signal))
    
 
    for src_idx, dst_idx in tmplt.nbr_idx_pairs:
        
        src_is_cand = correspond[tmplt.nodes[src_idx]]
        dst_is_cand = correspond[tmplt.nodes[dst_idx]]
        missing_edge = 0
        
        
        enough_edges = None
        for tmplt_adj, world_adj in iter_adj_pairs(tmplt, world):
            tmplt_adj_val = tmplt_adj[src_idx, dst_idx]

            # if there are no edges in this channel of the template, skip it
            if tmplt_adj_val == 0:
                continue
                
            world_adj_val = world_adj[src_is_cand, dst_is_cand]
            
            if tmplt_adj_val - world_adj_val >= 0 :
                missing_edge = missing_edge + tmplt_adj_val - world_adj_val
            
            # print("template has", tmplt_adj_val ,"edges", tmplt.nodes[src_idx],tmplt.nodes[dst_idx])
            # print("world has", world_adj_val ,"edges", world.nodes[src_is_cand],world.nodes[dst_is_cand])
            # print("missing", missing_edge ,"edges")
            
        if missing_edge > 0 :
            miss = miss + missing_edge
            miss_dict[(world.nodes[src_is_cand],world.nodes[dst_is_cand])] = str(missing_edge)
            try:
                node_dict[world.nodes[src_is_cand]] += missing_edge
            except:
                node_dict[world.nodes[src_is_cand]] = missing_edge
            
            try:
                node_dict[world.nodes[dst_is_cand]] += missing_edge
            except:    
                node_dict[world.nodes[dst_is_cand]] = missing_edge
            
        else :
            miss_dict[(world.nodes[src_is_cand],world.nodes[dst_is_cand])] = ""
            try:
                node_dict[world.nodes[src_is_cand]] += 0
            except:
                node_dict[world.nodes[src_is_cand]] = 0
            
            try:
                node_dict[world.nodes[dst_is_cand]] += 0
            except:    
                node_dict[world.nodes[dst_is_cand]] = 0
        
    for key, val in node_dict.items():
        if val == 0:
            node_dict[key]= ""
        else:
            print("FOUND")
            node_dict[key]= str(val)
    

    print ("Signal miss", miss, "edges")
    return miss, miss_dict, node_dict, correspond
