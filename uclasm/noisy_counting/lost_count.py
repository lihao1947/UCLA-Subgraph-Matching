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
    correspond = {}

    for idx in len(tmplt.nodes):
        correspond[tmplt.nodes[idx]] = signal[idx]
    
    for src_idx, dst_idx in tmplt.nbr_idx_pairs:
        
        src_is_cand = correspond[src_idx]
        dst_is_cand = correspond[dst_idx]

        enough_edges = None
        for tmplt_adj, world_adj in iter_adj_pairs(tmplt, world):
            tmplt_adj_val = tmplt_adj[src_idx, dst_idx]

            # if there are no edges in this channel of the template, skip it
            if tmplt_adj_val == 0:
                continue
                
            world_adj_val = world_adj[src_is_cand, dst_is_cand]
            
            missing_edge = world_adj_val - tmplt_adj_val 
            
            if missing_edge >= 0 :
                continue
            else:
                miss = miss + missing_edge
                
    print ("Signal miss", miss, "edges")
    return miss
