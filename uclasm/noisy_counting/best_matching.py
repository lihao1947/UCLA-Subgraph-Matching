from ..noisy_filters import run_noisy_filters, cheap_noisy_filters, all_noisy_filters, noisy_topology_filter
from ..utils.misc import invert, values_map_to_same_key, one_hot
from ..utils.graph_ops import get_node_cover
import numpy as np
from functools import reduce
from heapq import heappush, heappop
import uclasm
import pickle
from .. import INF1

# TODO: count how many isomorphisms each background node participates in.
# TODO: switch from recursive to iterative implementation for readability
class State():
    """A node class for A* Pathfinding"""

    def __init__(self):
        self.state = None
        self.loss = None
        self.n_determined = 0
        self.candidates_0 = None
        self.candidates_1 = None

        # self.g = 0
        # self.h = 0
        self.f = 0

    def copy(self):
        r = State()
        r.state = self.state.copy()
        r.loss = self.loss.copy()
        r.n_determined = self.n_determined
        r.candidates_0 = self.candidates_0.copy()
        r.candidates_1 = self.candidates_1.copy()
        r.f = self.f
        return r

    def is_end(self):
        return self.n_determined == len(self.state)

    def __lt__(self, other):
        return (self.f < other.f) or ((self.f == other.f) and (self.n_determined>other.n_determined))

def A_star_best_matching(tmplt, world, candidates_0, candidates_1,num_isomorphism=10,width_constraint=1):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    solution = []
    # Create start and end node
    start_state = State()
    start_state.state = -1*np.ones(tmplt.n_nodes, dtype=np.int32)
    start_state.loss = np.zeros(tmplt.n_nodes, dtype=np.int32)
    start_state.n_determined = 0
    start_state.candidates_0 = candidates_0
    start_state.candidates_1 = candidates_1
    # start_state.g = start_state.h =
    start_state.f = 0



    # Initialize both open and closed list
    open_list = []
    closed_list = {}

    # Add the start node
    heappush(open_list, start_state)

    # Loop until you find the end
    while len(open_list) > 0:
        pickle.dump(open_list, open("cache1.pl", "wb"))
        # Get the current node
        # Pop current off open list, add to closed list
        current_state = heappop(open_list)
        # closed_list.append(current_state)

        # Found the goal
        if current_state.is_end():
            solution.append(current_state)
            if len(solution)>num_isomorphism:
                return solution
            continue

        current_candidates = np.maximum(current_state.candidates_0, current_state.candidates_1)

       # Choose the node with least number of zeors, i.e. most possible exact matches, then continue.
       # If there is only one exact match, then just go ahead and use this one.
        try_node_candidates = None
        zero_remain=[]
        for tmplt_node_idx, tmplt_node in enumerate(tmplt.nodes):
            zeros = len(world.nodes) - np.count_nonzero(candidates_1[tmplt_node_idx])
            if zeros == 1:
                try_node_candidates = current_candidates[tmplt_node_idx]
                try_node = tmplt_node_idx
                continue
            zero_remain.append(zeros)
        
        if try_node_candidates is None:
            val, idx = min((val, idx) for (idx, val) in enumerate(zero_remain))
            try_node_candidates = current_candidates[idx]
            try_node = idx

        for world_node_ind in np.argsort(try_node_candidates):
            # need more consideration
            if try_node_candidates[world_node_ind]>width_constraint:
                break

            new_state = current_state.copy()
            new_state.state[try_node] = world_node_ind
            new_state.n_determined += 1
            new_state.loss[try_node] = np.maximum(new_state.candidates_0[try_node,world_node_ind],new_state.candidates_1[try_node,world_node_ind])

            for try_node_adj in np.argwhere(tmplt.sym_composite_adj[try_node]):
                if new_state.state[try_node_adj[1]]==-1:
                    continue
                for channel, tmplt_adj in tmplt.ch_to_adj.items():
                    world_adj = world.ch_to_adj[channel]
                    new_state.loss[try_node_adj[1]] -= np.maximum(np.int32(tmplt_adj[try_node,try_node_adj[1]])-np.int32(world_adj[world_node_ind,new_state.state[try_node_adj[1]]]),0)

                    new_state.loss[try_node_adj[1]] -= np.maximum(np.int32(tmplt_adj.T[try_node,try_node_adj[1]])-np.int32(world_adj.T[world_node_ind,new_state.state[try_node_adj[1]]]),0)

                    new_state.loss[try_node_adj[1]] = np.maximum(0,new_state.loss[try_node_adj[1]])

            new_state.f = np.sum(new_state.loss)

            candidates_0_old = new_state.candidates_0.copy()

            new_state.candidates_0[:,world_node_ind] = INF1
            new_state.candidates_0[try_node] = (1-one_hot(world_node_ind, world.n_nodes))*INF1

            new_state.candidates_1 = noisy_topology_filter(tmplt, world, new_state.candidates_0, candidates_0_old=candidates_0_old, candidates_old=new_state.candidates_1, changed_cands=one_hot(try_node, tmplt.n_nodes))[2]

            # Add the child to the open list
            heappush(open_list, new_state)

# def A_star_best_matching(tmplt, world, candidates_0, candidates_1,
#                                   unspec_cover, verbose):
#     # If the node cover is empty, the unspec nodes are disconnected. Thus, we
#     # can skip straight to counting solutions to the alldiff constraint problem
#     if len(unspec_cover) == 0:
#         # Elimination noisy_filter is not needed here and would be a waste of time
#         run_noisy_filters(tmplt, world, candidates=candidates, noisy_filters=cheap_noisy_filters,
#                     verbose=False, init_changed_cands=init_changed_cands)
#         node_to_cands = {node: world.nodes[candidates[idx]]
#                          for idx, node in enumerate(tmplt.nodes)}
#         return count_alldiffs(node_to_cands)
#
#     run_noisy_filters(tmplt, world, candidates=candidates, noisy_filters=all_noisy_filters,
#                 verbose=False, init_changed_cands=init_changed_cands)
#
#     # Since the node cover is not empty, we first choose some valid
#     # assignment of the unspecified nodes one at a time until the remaining
#     # unspecified nodes are disconnected.
#     n_isomorphisms = 0
#     node_idx = unspec_cover[0]
#     cand_idxs = np.argwhere(candidates[node_idx]).flat
#
#     for i, cand_idx in enumerate(cand_idxs):
#         candidates_copy = candidates.copy()
#         candidates_copy[node_idx] = one_hot(cand_idx, world.n_nodes)
#
#         # recurse to make assignment for the next node in the unspecified cover
#         n_isomorphisms += recursive_isomorphism_counter(
#             tmplt, world, candidates_copy, unspec_cover=unspec_cover[1:],
#             verbose=verbose, init_changed_cands=one_hot(node_idx, tmplt.n_nodes))
#
#         # TODO: more useful progress summary
#         if verbose:
#             print("depth {}: {} of {}".format(len(unspec_cover), i, len(cand_idxs)), n_isomorphisms)
#
#     return n_isomorphisms


def best_matching(tmplt, world, *, candidates=None, verbose=True):
    """
    counts the number of ways to assign template nodes to world nodes such that
    edges between template nodes also appear between the corresponding world
    nodes. Does not factor in the number of ways to assign the edges. Only
    counts the number of assignments between nodes.

    if the set of unspecified template nodes is too large or too densely
    connected, this code may never finish.
    """

    # if candidates is None:
    #     tmplt, world, candidates = uclasm.run_noisy_filters(
    #         tmplt, world, noisy_filters=uclasm.all_noisy_filters, verbose=True)
    tmplt, world, candidates_0, candidates_1 = uclasm.run_noisy_filters(tmplt, world)
    #candidates = np.max(candidates_0, candidates_1)

    #unspec_nodes = np.where(candidates.sum(axis=1) > 1)[0]
    unspec_nodes = range(tmplt.n_nodes)
    unspec_cover = get_node_cover(tmplt.subgraph(unspec_nodes))

    # Send zeros to init_changed_cands since we already just ran the noisy_filters
    return A_star_best_matching(
        tmplt, world, candidates_0, candidates_1, width_constraint=0)
