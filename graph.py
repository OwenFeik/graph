class Graph():
    def __init__(self, nodes = None, edges = None, directed = False):
        self._nodes = NodeList(nodes) if nodes is not None else NodeList([]) # NodeList is more flexible than a list
        
        self.directed = directed
        self.edges = []
        if type(edges)==list: # edges is a list of edges
            for edge in edges:
                self.add_edge(edge)
        elif type(edges) in [float, int] and 0 <= edges <= 1: # edges is the probability that a given edge exists ([0, 1])
            from random import random

            failed = [] # ensure an undirected graph doesn't contain (u, v) and (v, u)
            for u in self._nodes:
                for v in self._nodes:
                    if u == v:
                        continue

                    edge = (u.name, v.name)
                    if random() <= edges and not edge in failed and not self.has_edge(edge):
                        self.add_edge(edge)
                    else:
                        failed.append((u.name, v.name))
                        if not self.directed: # (u, v) and (v, u) are different in a directed graph
                            failed.append((v.name, u.name)) # but the same in an undirected graph

    @property
    def nodes(self):
        return self._nodes.nodes

    def add_node(self, node):
        self._nodes.add_node(node)

    def has_node(self, node):
        return node in self._nodes

    def get_node(self, node):
        return self._nodes[node]

    def get_neighbours(self, node):
        n = self._nodes[node].name # If node is not the name, get the name

        neighbours = []
        for edge in self.edges:
            if n in [edge.u, edge.v]:
                if n == edge.u:
                    neighbours.append(self._nodes[edge.v])
                elif n == edge.v:
                    neighbours.append(self._nodes[edge.u])

        return neighbours

    def get_neighbour_edges(self, node):
        n = self._nodes[node].name # If node is not the name, get the name

        neighbour_edges = []
        for edge in self.edges:
            if n in [edge.u, edge.v]:
                neighbour_edges.append(edge)
        
        return neighbour_edges

    def degree(self, node, direction = None):
        n = self._nodes[node].name
        
        degree = 0
        if self.directed and direction:
            if direction.lower() == 'in':
                for edge in self.edges:
                    if n == edge.v:
                        degree += 1
            elif direction.lower() == 'out':
                for edge in self.edges:
                    if n == edge.u:
                        degree += 1
            else:
                raise ValueError('Acceptable directions for degree are \'in\' and \'out\'')
        else:
            degree = len(self.get_neighbours(n))
        
        return degree

    def add_edge(self, edge):
        if self.has_edge(edge):
            raise ValueError('Each edge in a graph must be unique.')

        if type(edge) == Edge:
            if self.has_node(edge.u) and self.has_node(edge.v):
                self.edges.append(edge)
            else:
                raise ValueError(f'An edge must be between two nodes in the graph.')
        elif type(edge) in [tuple, list]:
            if len(edge) != 2:
                raise ValueError(f'An edge connects 2 nodes, therefore {edge} is inadmissable. To add other args, use a dict.')
            else:
                if self.has_node(edge[0]) and self.has_node(edge[1]):
                    self.edges.append(Edge(edge[0], edge[1]))
                else:
                    raise ValueError(f'An edge must be between two nodes in the graph.')
        elif type(edge) == dict:
            if self.has_node(edge.get('u')) and self.has_node(edge.get('v')):
                self.edges.append(Edge(**edge))
            else:
                raise ValueError(f'A dict must contain a key \'u\' and a key \'v\', nodes in the graph. {edge} is not admissable.')
        else:
            raise TypeError(f'Type {type(edge)} is inadmissable as an edge.')

    def has_edge(self, edge):
        if not self.edges:
            return False

        if self.directed:
            edges = [(e.u, e.v) for e in self.edges]
        else:
            edges = [(e.u, e.v) for e in self.edges]
            edges.extend([(e.v, e.u) for e in self.edges])
        
        if type(edge) == Edge:
            return (edge.u, edge.v) in edges
        elif type(edge) in [tuple, list]:
            return tuple(edge) in edges
        elif type(edge) == dict:
            return (edge.get('u'), edge.get('v')) in edges
        else:
            raise TypeError(f'Type {type(edge)} is inadmissable as an edge.')

    def get_edge(self, edge):
        if type(edge) == Edge:
            t_edge = (edge.u, edge.v)
        elif type(edge) in [tuple, list]:
            t_edge = tuple(edge)
        elif type(edge) == dict:
            t_edge = (edge.get('u'), edge.get('v'))
        else:
            raise TypeError(f'Type {type(edge)} is inadmissable as an edge.')
        
        if self.directed:
            for e in self.edges:
                if (e.u, e.v) == t_edge:
                    return e
        else:
            for e in self.edges:
                if t_edge in [(e.u, e.v), (e.v, e.u)]:
                    return e

        return None


class Node():
    def __init__(self, name, **kwargs):
        self.name = name
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def __str__(self):
        return self.name

    @property
    def ident(self): # Backward compatability
        return self.name


class NodeList():
    def __init__(self, nodes):
        self.nodes = []
        if type(nodes) == list:
            for node in nodes:
                self.add_node(node)
        elif type(nodes) == int:
            for i in range(nodes):
                self.add_node(i)

    def __contains__(self, n):
        return self.has_node(n)

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return self.nodes.__iter__()

    def __getitem__(self, key):
        return self.get_node(key)

    def add_node(self, node):
        if self.has_node(node):
            raise ValueError('Each node in a graph must be unique.')

        if type(node) in [str, int, float]:
            self.nodes.append(Node(node))
        elif type(node) == Node:
            self.nodes.append(node)
        elif type(node) == dict:
            if type(node.get('name')) in [str, int, float]:
                self.nodes.append(Node(**node))
            else:
                raise ValueError(f'A dict must contain a key \'name\', a str, int or float.')
        else:
            raise TypeError(f'Type {type(node)} can\'t be parsed as a node.')


    def has_node(self, node):
        if type(node) == Node:
            return node in self.nodes
        elif type(node) in [str, int, float]:
            return node in [n.name for n in self.nodes]
        elif type(node) == dict:
            return node.get('name') in [n.name for n in self.nodes]
        else:
            raise TypeError(f'Type {type(node)} is inadmissable as a node.')

    def get_node(self, node):
        if type(node) == Node:
            for n in self.nodes:
                if n.name == node.name:
                    return n
        elif type(node) in [str, int, float]:
            for n in self.nodes:
                if n.name == node:
                    return n
        elif type(node) == dict:
            name = node.get('name')
            if name is not None:
                for n in self.nodes:
                    if n.name == name:
                        return n
        else:
            raise TypeError(f'Type {type(node)} is inadmissable as a node.')


class Edge():
    def __init__(self, u, v, **kwargs):
        self.u = u
        self.v = v
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def other(self, node):
        if self.u == node:
            return self.v
        elif self.v == node:
            return self.u
        else:
            raise ValueError('Argument \'node\' should be a node on the edge.')

    @property
    def a(self): # Backward compatability
        return self.u

    @property
    def b(self): # Backward compatability
        return self.v
