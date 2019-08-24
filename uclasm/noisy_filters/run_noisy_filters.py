import copy
import time
import numpy as np
from . import noisy_stats_filter
from . import noisy_topology_filter
# from . import label_noisy_filter
# from . import permutation_noisy_filter
from ..utils import summarize

# TODO: logging
def run_noisy_filters(tmplt, world, f_upper_bound=4, verbose=False):

    tmplt, world, candidates_0 = noisy_stats_filter(tmplt, world, verbose = True)

    tmplt, world, candidates_1 = noisy_topology_filter(tmplt, world, candidates_0, f_upper_bound=f_upper_bound)

    return tmplt, world, candidates_0, candidates_1
# def run_noisy_filters(tmplt, world, *,
#                 candidates=None,
#                 noisy_filters=None,
#                 verbose=False,
#                 max_iter=-1,
#                 init_changed_cands=None):
#     """
#     Repeatedly run the desired noisy_filters until the candidates converge
#     """
#
#     has_gt = len(set(tmplt.nodes) - set(world.nodes)) == 0
#
#     # Boolean matrix with i,j entry denoting whether world node j is a candidate
#     # for template node i
#     if candidates is None:
#         candidates = np.zeros((tmplt.n_nodes, world.n_nodes), dtype=np.int64)
#     # label_noisy_filter(tmplt, world, candidates)
#
#     if noisy_filters is None:
#         from . import all_noisy_filters
#         noisy_filters = all_noisy_filters
#
#     # Construct a list of the noisy_filters that have been run for reference when
#     # evaluating performance. This is appended to repeatedly in the loop below
#     noisy_filters_so_far = []
#
#     # index in `noisy_filters` of the noisy_filter we should run next
#     noisy_filter_idx = 0
#
#     # Each element of this list is a copy `cand_counts` from before the last
#     # time the corresponding noisy_filter was run.
#     old_cand_counts_list = [None for noisy_filter in noisy_filters]
#     cand_counts = candidates.sum(axis=1)
#     init_cand_counts = candidates.sum(axis=1)
#
#     if init_changed_cands is None:
#         init_changed_cands = np.ones(tmplt.nodes.shape, dtype=np.bool)
#
#     changed_cands = init_changed_cands
#
#     while noisy_filter_idx != len(noisy_filters) and len(noisy_filters_so_far) != max_iter:
#         noisy_filter = noisy_filters[noisy_filter_idx]
#
#         # Get cand counts from before last run of this noisy_filter
#         old_cand_counts = old_cand_counts_list[noisy_filter_idx]
#
#         # Update the cand counts for the current noisy_filter for next time it runs
#         old_cand_counts_list[noisy_filter_idx] = cand_counts
#
#         # Find the nodes whose candidates have changed since last time this
#         # noisy_filter was run
#         if old_cand_counts is not None:
#             changed_cands = cand_counts < old_cand_counts
#         else:
#             changed_cands = init_changed_cands | (cand_counts < init_cand_counts)
#
#         # If any template nodes have candidates that have changed since the
#         # last time this noisy_filter was run, go ahead and run the noisy_filter.
#         if np.any(changed_cands):
#             # TODO: create an object we can use like `with Timer()`
#             start_time = time.time()
#
#             # TODO: we could get rid of the `verbose` flag using a singleton
#             # logger that stores a global `verbose` property
#             if verbose:
#                 print("running", noisy_filter.__name__)
#
#             # Run whatever noisy_filter and the permutation noisy_filter
#             tmplt, world, candidates = noisy_filter(
#                 tmplt, world, candidates, changed_cands=changed_cands,
#                 verbose=verbose)
#             noisy_filters_so_far.append(noisy_filter.__name__.replace("_noisy_filter", ""))
#             tmplt, world, candidates = permutation_noisy_filter(
#                 tmplt, world, candidates)
#
#             # TODO: make logging less cumbersome
#             if verbose:
#                 end_time = time.time()
#                 summarize(tmplt, world, candidates, alert_missing=has_gt)
#                 print("after", noisy_filter.__name__,
#                       "on iteration", len(noisy_filters_so_far),
#                       "took", end_time - start_time, "seconds")
#                 print("noisy_filters so far: {}".format(" ".join(noisy_filters_so_far)))
#
#         cand_counts_after_noisy_filter = candidates.sum(axis=1)
#
#         # If any candidates have changed, start over from the first noisy_filter.
#         # Otherwise, move on to the next noisy_filter in the list on the next pass.
#         if np.any(cand_counts_after_noisy_filter < cand_counts):
#             noisy_filter_idx = 0
#         else:
#             noisy_filter_idx += 1
#
#         cand_counts = cand_counts_after_noisy_filter
#
#         # If some template node has no candidates, there are no isomorphisms
#         if np.any(cand_counts == 0):
#             candidates[:,:] = False
#             break
#
#         # Which world nodes are candidates for at least one template node?
#         is_cand_any = candidates.any(axis=0)
#
#         # If not all world nodes are candidates for at least one template node
#         if ~is_cand_any.all():
#             # Get rid of unnecessary world nodes
#             world = world.subgraph(is_cand_any)
#             candidates = candidates[:, is_cand_any]
#
#     if verbose:
#         print("noisy_filters are done.")
#
#     return tmplt, world, candidates
