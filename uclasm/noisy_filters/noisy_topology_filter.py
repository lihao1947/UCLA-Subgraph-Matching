import numpy as np
from functools import reduce
from operator import mul
from scipy.sparse import csr_matrix

# TODO: parallelize?
# TODO: get set of values taken by tmplt edges?

# TODO: better name for this helper function
def iter_adj_pairs(tmplt, world):
    for channel, tmplt_adj in tmplt.ch_to_adj.items():
        world_adj = world.ch_to_adj[channel]
        yield (tmplt_adj, world_adj)
        yield (tmplt_adj.T, world_adj.T)

def _noisy_topology_filter(tmplt, world, candidates_0, candidates, sign=1, changed_cands=None, f_upper_bound=4, current_node=None, current_node_cand=None):
    """
    For each pair of neighbors in the template, ensure that any candidate for
    one neighbor has a corresponding candidate for the other neighbor to which
    it is connected by sufficiently many edges in each channel and direction.

    changed_cands: boolean array indicating which nodes in the template have
                   candidates that have changed since last time this ran
    """
    #candidates = candidates_0
    if current_node is not None:
        neighbor_topo = np.zeros(tmplt.n_nodes, dtype=np.int32)

    for src_idx, dst_idx in tmplt.nbr_idx_pairs:
        if src_idx == dst_idx:
            continue
        if changed_cands is not None:
            # If neither the source nor destination has changed, there is no
            # point in filtering on this pair of nodes
            if not (changed_cands[src_idx] or changed_cands[dst_idx]):
                continue

        # get indicators of candidate nodes in the world adjacency matrices
        # threshold of missing_edges
        src_is_cand = candidates_0[src_idx]<=f_upper_bound
        dst_is_cand = candidates_0[dst_idx]<=f_upper_bound
        if np.sum(src_is_cand)<=0 or np.sum(dst_is_cand)<=0:
            continue
        # figure out which candidates have enough edges between them in world
        missing_edges = None
        missing_scalar = 0
        for tmplt_adj, world_adj in iter_adj_pairs(tmplt, world):
            tmplt_adj_val = tmplt_adj[src_idx, dst_idx]

            # # if there are no edges in this channel of the template, skip it
            if tmplt_adj_val == 0:
                continue

            # sub adjacency matrix corresponding to edges from the source
            # candidates to the destination candidates
            world_sub_adj = world_adj[:, dst_is_cand][src_is_cand, :].astype(np.int8)

            partial_missing_edges = world_sub_adj.minimum(tmplt_adj_val)
            missing_scalar += tmplt_adj_val
            if missing_edges is None:
                missing_edges = partial_missing_edges
            else:
                missing_edges += partial_missing_edges

        # print(missing_edges.shape)
        # # i,j element is 1 if cands i and j have enough edges between them
        # enough_edges = reduce(mul, enough_edges_list, 1)
        inter_result = (np.maximum(-missing_edges.A,candidates_0[dst_idx][dst_is_cand]-missing_scalar).min(axis=1)+missing_scalar)
        candidates[src_idx][src_is_cand] += sign * inter_result

        if current_node is not None:
            if src_idx==current_node:
                neighbor_topo[dst_idx] = inter_result[0]

        if src_idx != dst_idx:
            # dsts with at least one reasonable src
            # dst_matches = enough_edges.getnnz(axis=0) > 0
            inter_result2 = (np.maximum(-missing_edges.A, candidates_0[src_idx][src_is_cand].reshape(-1,1)-missing_scalar).min(axis=0)+missing_scalar)
            candidates[dst_idx][dst_is_cand] += sign * inter_result2

            if current_node is not None:
                if dst_idx==current_node:
                    neighbor_topo[src_idx] = inter_result2[0]

    #candidates = np.maximum(candidates, candidates_0)

    if current_node is not None:
        return tmplt, world, candidates, neighbor_topo
    else:
        return tmplt, world, candidates

def noisy_topology_filter(tmplt, world, candidates_0, candidates_0_old=None, candidates_old=None, changed_cands=None, f_upper_bound=4, current_node=None, current_node_cand=None):
    """
    For each pair of neighbors in the template, ensure that any candidate for
    one neighbor has a corresponding candidate for the other neighbor to which
    it is connected by sufficiently many edges in each channel and direction.

    changed_cands: boolean array indicating which nodes in the template have
                   candidates that have changed since last time this ran
    """
    if candidates_old is None or candidates_old is None or changed_cands is None:
        return _noisy_topology_filter(tmplt, world, candidates_0, np.zeros((tmplt.n_nodes, world.n_nodes), dtype=np.int64),f_upper_bound=f_upper_bound)

    tmplt, world, candidates = _noisy_topology_filter(tmplt, world, candidates_0_old, candidates_old, sign=-1, changed_cands = changed_cands, f_upper_bound=f_upper_bound)

    if current_node is not None:
        tmplt, world, candidates, neighbor_topo = _noisy_topology_filter(tmplt, world, candidates_0, candidates, sign=1, changed_cands = changed_cands, f_upper_bound=f_upper_bound, current_node=current_node, current_node_cand=current_node_cand)
        return tmplt, world, candidates, neighbor_topo
    else:
        tmplt, world, candidates = _noisy_topology_filter(tmplt, world, candidates_0, candidates, sign=1, changed_cands = changed_cands, f_upper_bound=f_upper_bound, current_node=current_node, current_node_cand=current_node_cand)
        return tmplt, world, candidates
