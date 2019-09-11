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

    correspond = dict(zip(tmplt.nodes, signal))

    node_miss = np.zeros(tmplt.n_nodes)

    for src_idx, dst_idx in tmplt.nbr_idx_pairs:

        src_is_cand = correspond[tmplt.nodes[src_idx]]
        dst_is_cand = correspond[tmplt.nodes[dst_idx]]



        enough_edges = None
        missing_edge = 0
        for tmplt_adj, world_adj in iter_adj_pairs(tmplt, world):
            tmplt_adj_val = tmplt_adj[src_idx, dst_idx]

            # if there are no edges in this channel of the template, skip it
            if tmplt_adj_val == 0:
                continue

            world_adj_val = world_adj[src_is_cand, dst_is_cand]

            missing_edge += np.int8(world_adj_val) - tmplt_adj_val

        if missing_edge >= 0 :
            miss_dict[(world.nodes[src_is_cand],world.nodes[dst_is_cand])] = ''
        else:
            miss = miss - missing_edge

            node_miss[src_idx]-=missing_edge
            node_miss[dst_idx]-=missing_edge

            miss_dict[(world.nodes[src_is_cand],world.nodes[dst_is_cand])] = str(missing_edge)



    #miss_dict[(world.nodes[src_is_cand],world.nodes[dst_is_cand])]= "6"
    print ("Signal miss", miss, "edges")
    return miss, miss_dict, node_miss
