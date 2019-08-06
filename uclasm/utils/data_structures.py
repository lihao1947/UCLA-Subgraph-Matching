"""
Filtering algorithms expect data to come in the form of Graph objects
"""

import os

from uclasm.utils.misc import index_map
import scipy.sparse as sparse
import numpy as np
import networkx as nx

class Graph:
    def __init__(self, nodes, channels, adjs, labels=None, name=None):
        self.nodes = np.array(nodes)
        self.n_nodes = len(nodes)
        self.node_idxs = index_map(self.nodes)
        self.ch_to_adj = {ch: adj for ch, adj in zip(channels, adjs)}
        self.is_sparse = all([isinstance(adj, sparse.csr.csr_matrix) for adj in adjs])

        if labels is None:
            labels = [None]*len(nodes)
        self.labels = np.array(labels)


        self._composite_adj = None
        self._sym_composite_adj = None
        self._is_nbr = None
        self.name = name

        self.in_degree_array = None
        self.out_degree_array = None
        self.neighbors = []

    @property
    def composite_adj(self):
        if self._composite_adj is None:
            self._composite_adj = sum(self.ch_to_adj.values())

        return self._composite_adj

    @property
    def sym_composite_adj(self):
        if self._sym_composite_adj is None:
            self._sym_composite_adj = self.composite_adj + self.composite_adj.T

        return self._sym_composite_adj

    @property
    def is_nbr(self):
        if self._is_nbr is None:
            self._is_nbr = self.sym_composite_adj > 0

        return self._is_nbr

    @property
    def channels(self):
        return self.ch_to_adj.keys()

    @property
    def adjs(self):
        return self.ch_to_adj.values()

    @property
    def nbr_idx_pairs(self):
        """
        Returns a 2d array with 2 columns. Each row contains the node idxs of
        a pair of neighbors in the graph. Each pair is only returned once, so
        for example only one of (0,3) and (3,0) could appear as rows.
        """
        return np.argwhere(sparse.tril(self.is_nbr))

    @property
    def out_degree(self):
        if self.out_degree_array is not None:
            return self.out_degree_array
        else:
            self.out_degree_array = {channel: self.ch_to_adj[channel].sum(axis=1)
                                     for channel in self.channels}
            return self.out_degree_array

    @property
    def in_degree(self):
        if self.in_degree_array is not None:
            return self.in_degree_array
        else:
            self.in_degree_array = {channel: self.ch_to_adj[channel].sum(axis=0)
                                     for channel in self.channels}
            return self.in_degree_array

    def compute_neighbors(self):
        for i in range(self.n_nodes):
            # We grab first element since nonzero returns a tuple of 1 element
            self.neighbors.append(self.sym_composite_adj[i].nonzero()[0])

    def subgraph(self, node_idxs):
        """
        Returns the subgraph induced by candidates
        """

        # throw out nodes not belonging to the desired subgraph
        nodes = self.nodes[node_idxs]
        labels = self.labels[node_idxs]
        adjs = [adj[node_idxs, :][:, node_idxs] for adj in self.adjs]

        # Return a new graph object for the induced subgraph
        return Graph(nodes, self.channels, adjs, labels=labels)

    def sparsify(self):
        """
        Converts the stored adjacency matrices into sparse matrices in the
        csr_matrix format
        """
        if self.is_sparse:
            return
        for ch, adj in self.ch_to_adj.items():
            self.ch_to_adj[ch] = sparse.csr_matrix(adj)
        self.is_sparse = True

    def densify(self):
        """
        Converts the stored adjacency matrices into standard arrays.
        This only affects the matrices in self.ch_to_adj, not any other
        possible sparse representations of data.

        This will cause an error if the matrices are already dense.
        """
        if not self.is_sparse:
            return
        for ch, adj in self.ch_to_adj.items():
            self.ch_to_adj[ch] = adj.A
        self.is_sparse = False

    def convert_dtype(self, dtype):
        """
        Convert the stored adjacency matrices to the specified data type.
        """
        for ch, adj in self.ch_to_adj.items():
            self.ch_to_adj[ch] = adj.astype(dtype)

    def copy(self):
        """
        The only thing this bothers to copy is the adjacency matrices
        """
        return Graph(self.nodes, self.channels,
                     [adj.copy() for adj in self.adjs],
                     labels=self.labels)

    def get_n_edges(self):
        """
        Returns a dictionary mapping channels to the number of edges 
        in that channel.
        """
        edge_counts = {}
        for channel in self.channels:
            adj_mat = self.ch_to_adj[channel]

            count = 0
            for i, j in zip(*adj_mat.nonzero()):
                count += adj_mat[i,j]
            edge_counts[channel] = count

        return edge_counts

    def edge_iterator(self, channel=None):
        """
        This will iterate over all the edges in the graph in no particular
        order except it will list them channel by channel.

        It will yield a 4-tuple listing in order the channel, start node index,
        end node index, and the edge count.

        If you only want one channel, you may pass it in.
        """
        if channel is None:
            channels = self.channels
        else:
            channels = [channel]

        for channel in channels:
            adj_mat = self.ch_to_adj[channel]

            for i, j in zip(*adj_mat.nonzero()):
                edge_count = adj_mat[i,j]
                yield channel, i, j, edge_count


    def add_edge(self, channel, node_1, node_2, count=1):
        """
        Add an edge to the channel specified going from node_1 to node_2.
        count is the number of edges to add.
        """
        self.ch_to_adj[channel][node_1,node_2] += count

    def remove_edge(self, channel, node_1, node_2, count=1):
        """
        Remove an edge from channel specified going from node_1 to node_2.
        count is the number of edges to remove.
        """
        if count > self.ch_to_adj[channel][node_1,node_2]:
            raise ValueError("Specified count to remove is larger than number of edges")
        self.ch_to_adj[channel][node_1,node_2] -= count

    def write_channel_solnon(self, filename, channel):
        """
        Write out adjacency matrix for specific channel as adjacency list to a file.
        """
        with open(filename, 'w') as f:
            f.write(str(self.n_nodes) + '\n')

            adj_mat = self.ch_to_adj[channel]
            curr_index = 0
            curr_adj = []
            for (node_index, adjacent_index) in zip(*adj_mat.nonzero()):
                if node_index != curr_index:
                    # We write out number of adjacent nodes, then list of adjacent nodes
                    f.write(" ".join(map(str, [len(curr_adj)] + curr_adj)) + '\n')

                    for i in range(curr_index+1, node_index):
                        # For each index in between, these have no adjacent nodes
                        # So we write zero for each of these nodes
                        f.write("0\n")

                    curr_adj = []
                    curr_index = node_index

                curr_adj.append(adjacent_index)

            # Write out remaining nodes
            f.write(" ".join(map(str, [len(curr_adj)] + curr_adj)) + '\n')

            for i in range(curr_index+1, self.n_nodes):
                f.write('0\n')

    def _add_channel_to_name(self, filename, channel):
        """
        Helper function for appending a channel name to a filename
        """
        *name, ext = filename.split('.')
        name = '.'.join(name)
        new_name = name + '_' + str(channel) + '.' + ext
        return new_name


    def write_file_solnon(self, filename):
        """
        Writes out the graph in solnon format. This format is described as follows:
        Each graph is described in a text file. If the graph has n vertices, then the file has n+1 lines: 
        -The first line gives the number n of vertices.
        -The next n lines give, for each vertex, its number of successor nodes, 
         followed by the list of its successor nodes.

        If there are multiple channels, then it will create one file for each channel.
        """

        if len(list(self.channels)) > 1:
            filenames = [self._add_channel_to_name(filename, channel)
                         for channel in self.channels]

            for name, channel in zip(filenames, self.channels):
                self.write_channel_solnon(name, channel)
        else:
            # Extract sole channel
            channel = list(self.channels)[0]
            self.write_channel_solnon(filename, channel)

    def write_channel_gfd(self, filename, channel):
        """
        Write a single channel in gfd format.
        """
        with open(filename, 'w') as f:
            f.write('#{}\n'.format(self.name))
            f.write('{}\n'.format(self.n_nodes))
            for i in range(self.n_nodes):
                f.write('A\n') # A is a dummy label for each node since our graphs are unlabelled
            f.write('{}\n'.format(self.get_n_edges()[channel]))
            for _, fro, to, count in self.edge_iterator(channel):
                for i in range(count):
                    f.write('{} {}\n'.format(fro, to))

    def write_gfd(self, filename):
        """
        Writes the graph in the gfd format described in
        https://github.com/InfOmics/RI. Since our graphs are unlabelled, all
        nodes will have the same label (a dummy label "A").

        If there are multiple channels, it will create one file for each channel.

        Args:
            filename (str): The name of the file to write to
        """
        if len(list(self.channels)) > 1:
            filenames = [self.add_channel_to_name(filename, channel)
                         for channel in self.channels]
            
            for name, channel in zip(filenames, self.channels):
                self.write_channel_gfd(name, channel)
        else:
            channel = list(self.channels)[0]
            self.write_channel_gfd(filename, channel)


    def write_to_file(self, filename):
        """
        Writes the graph out in the following format:

        <Graph Name>
        <# Nodes>
        <# Channels>
        <Channel1>
        <# Edges in Channel1>
        <From1> <To1> <Count1>
        ...
        <FromN> <ToN> <CountN>
        <Channel2>
        <# Edges in Channel1>
        ...

        where <Fromi>, <Toi> <Counti> are the index of the source node,
        the index of the destination node, and the count of edges for the
        i-th edge in a given channel.
        """
        with open(filename, 'w') as f:
            f.write('{}\n'.format(self.name))
            f.write('{}\n'.format(self.n_nodes))
            f.write('{}\n'.format(len(list(self.channels))))
            for channel in self.channels:
                f.write('{}\n'.format(channel))
                f.write('{}\n'.format(self.get_n_edges()[channel]))
                for _, fro, to, count in self.edge_iterator(channel):
                    f.write('{} {} {}\n'.format(fro, to, count))

    def channel_to_networkx_graph(self, channel):
        """
        Convert the given channel into a networkx MultiDiGraph.
        """
        return nx.from_scipy_sparse_matrix(self.ch_to_adj[channel], parallel_edges=True)

    def to_networkx_graph(self):
        """
        Return a dictionary mapping channels to networkx MultiDiGraphs.
        """
        return {channel: self.channel_to_networkx_graph(channel) for channel in self.channels}

    def to_networkx_composite_graph(self):
        """
        Return a networkx-style MultiDiGraph from the sum of the adjacency
        matrices
        """
        comp_matrix = sum(self.ch_to_adj.values())
        return nx.from_scipy_sparse_matrix(comp_matrix, parallel_edges=True)

    def isolated_nodes(self):
        """
        Return the isolated nodes in the graph. 

        Returns (set): The set of isolated nodes
        """
        # We construct sets of nodes with 0 in degree and 0 out degree for each channel
        # Then we intersect them all
        sets = []
        for channel in self.channels:
            adj_mat = self.ch_to_adj[channel]
            outdegree = adj_mat.sum(axis=1).A
            indegree = adj_mat.sum(axis=0).A
            zero_out = set(np.where(outdegree == 0)[0])
            zero_in = set(np.where(indegree == 0)[0])
            sets.append(zero_out & zero_in)
        retval = sets[0].intersection(*sets[1:])
        return retval


def read_gfd(filename):
    with open(filename) as f:
        name = f.readline().rstrip()[1:]
        n_nodes = int(f.readline())
        # We ignore the labels for now
        for _ in range(n_nodes):
            f.readline()
        n_edges = int(f.readline())
        A = np.array((n_nodes, n_nodes))
        for _ in range(n_edges):
            fro, to = list(map(int, f.readline().rstrip().split()))
            A[fro,to] = 1
    return Graph(list(range(n_nodes)), ['0'], [sparse.csr_matrix(A)], name=name)


def read_from_file(filename):
    """
    Reads in a multichannel graph from a file in the format specified in
    write_to_file.
    """
    with open(filename) as f:
        name =  f.readline().rstrip()
        n_nodes = int(f.readline())
        n_channels = int(f.readline())
        channels = []
        adjs = []
        for i in range(n_channels):
            adj_mat = np.zeros((n_nodes, n_nodes))
            channel_name = f.readline().rstrip()
            channel_size = int(f.readline())
            seen = 0
            while seen < channel_size:
                fro, to, count = list(map(int, f.readline().rstrip().split()))
                adj_mat[fro,to] = count
                seen += count
            channels.append(channel_name)
            adjs.append(sparse.csr_matrix(adj_mat))

        nodes = list(range(n_nodes))
        return Graph(nodes, channels, adjs, name=name)
