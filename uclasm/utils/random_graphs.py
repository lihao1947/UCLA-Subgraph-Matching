from random import random

import numpy as np
from scipy.sparse import csr_matrix

from uclasm.utils.data_structures import Graph


def coin_flip(p=0.5):
    """
    With probability p, this will return True, otherwise it will return False.
    """
    return random() <= p


def generate_random_graph(n, p):
    """
    Generate an Erdos-Renyi random graph. This is a simple graph
    with n vertices and the probability of two nodes being adjacent
    is p.

    Args:
        n (int): The number of nodes
        p (float): A value between 0 and 1 representing the probability
            two given nodes are adjacent
    Returns:
        Graph: A randomly generated graph
    """
    adj_mat = np.zeros((n,n))
    for i in range(n):
        for j in range(i):
            if coin_flip(p):
                adj_mat[i,j] = adj_mat[j,i] = 1
    name = '{}_{}'.format(n, p)

    return Graph(list(range(n)), ['0'], [csr_matrix(adj_mat)], name=name)

def random_digraph(n, p):
    """
    Generate a random graph on n vertices. The problem i is adjacent to j
    will be p.

    Args:
        n (int): The number of nodes
        p (float): A value between 0 and 1 representing the probability
            two given nodes are adjacent
    Returns:
        Graph: A randomly generated graph
    """
    adj_mat = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            # We do not allow self loops
            if i == j:
                continue
            if coin_flip(p):
                adj_mat[i,j] = 1
    name = '{}_{}'.format(n, p)

    return Graph(list(range(n)), ['0'], csr_matrix(adj_mat), name=name)
