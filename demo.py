from display import DisplayGraph
from example import g
from math import inf
from time import sleep

# Demonstration of Dijkstra's algorithm animation with display.py

def dijkstra_animated(g, source):
    g.show()
    g.distribute()
    g.scale()
    g.redraw()

    unvisited = []
    for n in g.nodes:
        n.dist = inf
        n.prev = None
        n.colour = (0, 200, 200)
        unvisited.append(n)

    g.nodes[source].dist = 0
    g.nodes[source].colour = g.default_node_colour

    while len(unvisited) > 0:
        nxt = min(unvisited, key = lambda k: k.dist)
        unvisited.remove(nxt)
        nxt.colour = g.default_node_colour
        g.redraw()
        sleep(0.2)

        for e in g.get_neighbour_edges(nxt):
            e.colour = (200, 0, 0)
            g.redraw()
            sleep(0.2)
            alt = nxt.dist + e.cost
            other = g.nodes[e.other(nxt.name)]
            if alt < other.dist:
                other.dist = alt
                other.prev = nxt
            e.colour = (100, 100, 0)
        
        
g = DisplayGraph(g, show_labels = True, node_labels = 'dist', edge_labels = 'cost')
dijkstra_animated(g, 0)
g.run()
