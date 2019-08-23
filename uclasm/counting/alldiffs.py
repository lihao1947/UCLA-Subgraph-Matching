import numpy as np

from ..utils.misc import invert, values_map_to_same_key

matching = []
total_count = 0
solution_count = 1

# counts the number of ways to assign a particular node, recursing to
# incorporate ways to assign the next node, and so on
def recursive_alldiff_counter(node_to_cands_classes, cands_to_cand_counts,
                              verbose, open_file):

    global solution_count, total_count

    # no nodes left to assign
    if len(node_to_cands_classes) == 0:
        if verbose:
            print("\t\tMatch (count={}):".format(solution_count))
        
        print("Match:", file=open_file)
        for (t, w) in matching:
            print("{} -> {}".format(t, tuple(map(int, w))), file=open_file)
        total_count += solution_count
        if verbose:
            print("Total Solution Count: {}".format(total_count))
        return 1

    count = 0

    # give me an arbitrary unspecified nodeiable
    node, cands_classes = node_to_cands_classes.popitem()

    # for each way of assigning the given nodeiable
    for cands in cands_classes:
        cands = frozenset(cands)
        # how many ways to assign the nodeiable in this way are there?
        n_cands = cands_to_cand_counts[cands]
        if n_cands == 0:
            continue

        cands_to_cand_counts[cands] -= 1
        matching.append((node, cands))
        solution_count *= n_cands

        # number of ways to assign current node times number of ways to
        # assign the rest
        n_ways_to_assign_rest = recursive_alldiff_counter(
            node_to_cands_classes, cands_to_cand_counts, verbose, open_file)
        solution_count /= n_cands

        count += n_cands * n_ways_to_assign_rest

        # put the count back so we don't mess up the recursion
        cands_to_cand_counts[cands] += 1
        matching.pop()

    # put the list back so we don't mess up the recursion
    node_to_cands_classes[node] = cands_classes

    return count

def count_alldiffs(node_to_cands, verbose, open_file):
    """
    node_to_cands: dict(item, list)

    count the number of ways to assign nodes to cands without using any cand for
    more than one node. ie. count solns to alldiff problem, where the nodeiables
    are the keys of node_to_cands, and the domains are the values.
    """
    # TODO: can this function be vectorized?
    # TODO: does scipy have a solver for this already?

    # Check if any node has no cands
    if any(len(cands)==0 for cands in node_to_cands.values()):
        return 0

    # TODO: throwing out nodes with only one cand may not be necessary
    # if a node has only one possible cand, throw it out.
    node_to_cands = {node: cands for node, cands in node_to_cands.items()
                   if len(cands) > 1}

    unspec_nodes = list(node_to_cands.keys())

    # which nodes is each cand a cand for?
    cand_to_nodes = invert(node_to_cands)

    # gather sets of cands which have the same set of possible nodes.
    nodes_to_cands = values_map_to_same_key(cand_to_nodes)
    cands_to_cand_counts = {frozenset(cands): len(cands)
                          for nodes, cands in nodes_to_cands.items()}
    # This is a partition on the world nodes.
    # We say that two world nodes are equivalent if they are candidates
    # for the exact same template nodes. This allows us to interchange them.

    # Here we now map a node to the world node equivalence classes
    node_to_cands_classes = {
        node: [nodes_to_cands[nodes] for nodes in nodes_to_cands.keys() if node in nodes]
        for node in node_to_cands}

    return recursive_alldiff_counter(node_to_cands_classes, cands_to_cand_counts, verbose, open_file)
