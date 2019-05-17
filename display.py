from graph import Graph # Base class
from math import inf, atan2, cos, sin, pi # Distibrution, drawing, calculations
from random import randint, choice # Spread nodes out initially, create pseudo-edges to random node
from copy import deepcopy # Build from a graph without modifying original
from quadtree import Quadtree

from contextlib import redirect_stdout
with redirect_stdout(None): # Suppress pygame welcome message
    import pygame # Rendering engine
import pygame.freetype # Text
import pygame.gfxdraw # Antialiased edges

class DisplayGraph(Graph):
    background_colour = (0, 0, 0) # Background of the graph window
    circular_node_radius = 15 # Radius of circular nodes, square nodes are based on text size
    default_edge_colour = (255, 255, 255) # Colour edges are drawn if they don't have a colour attribute
    default_node_colour = (0, 0, 0) # As above, for nodes
    edge_label_colour = (0, 0, 0) # Colour of labels on edges
    edge_labels = 'label' # Attribute of edges to be printed as labels
    edge_width = 3 # Width of edges between nodes
    font_size = 14 # Font size for labels
    node_border_colour = (255, 255, 255) # Border colour for the nodes
    node_border_width = 3 # Width of borders around nodes
    node_labels = 'label' # Attribute of the nodes associated with their label
    node_shape = 'square' # Square nodes look better overall
    node_text_padding = 5 # Space to leave between text and border of square nodes
    show_edge_labels = False # Show edge labels such as cost on edges
    show_node_labels = False # Show labels next to nodes such as distance etc
    text_colour = (255, 255, 255) # Colour of text for labels
    window_title = 'Graph' # Caption at top of window

    def __init__(self, graph, width = 1000, height = 1000, **kwargs):
        graph = deepcopy(graph) # Leave original graph as is
        super().__init__(graph.nodes.nodes, graph.edges, graph.directed) # Make the parent a clone of the original 
        
        self.width = width # Window width
        self.height = height # and height
        self.screen = None # Pygame window used for display
        self.font = None # Pygame font renderer

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        self.running = False
        self.distributing = False # Prevent recursively calling distribution
        self.holding = None
        self.holding_offset = (0, 0)

        if 'show_labels' in kwargs:
            self.show_node_labels = kwargs['show_labels']
            self.show_edge_labels = kwargs['show_labels']
        if 'colour_theme' in kwargs:
            theme = kwargs['colour_theme'] 
            if theme == 'dark':
                self.background_colour = (0, 0, 0)
                self.text_colour = (255, 255, 255)
                self.edge_label_colour = (0, 0, 0)
                self.default_edge_colour = (255, 255, 255)
                self.default_node_colour = (0, 0, 0)
                self.node_border_colour = (255, 255, 255)
            elif theme == 'light':
                self.background_colour = (255, 255, 255)
                self.text_colour = (0, 0, 0)
                self.edge_label_colour = (255, 255, 255)
                self.default_edge_colour = (0, 0, 0)
                self.default_node_colour = (255, 255, 255)
                self.node_border_colour = (0, 0, 0)
            elif theme == 'colourful_dark':
                self.background_colour = (0, 0, 0)
                self.text_colour = (255, 255, 255)
                self.edge_label_colour = (255, 255, 255)
                self.default_edge_colour = (0, 70, 180)
                self.default_node_colour = (0, 140, 30)
                self.node_border_colour = None

        for node in self.nodes:
            node.x = randint(int(width * 0.1), int(width * 0.9))
            node.y = randint(int(height * 0.1), int(height * 0.9))
            node._x_force = 0
            node._y_force = 0

        q = Quadtree(self.nodes, self.width, self.height)
        print()


    def init_window(self):
        pygame.init()
        pygame.display.set_caption(self.window_title)
        pygame.display.set_icon(pygame.image.load('icon.png'))
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.freetype.Font(None, self.font_size)

        self.redraw()
        
    def redraw(self):
        self.screen.fill(self.background_colour)

        for edge in self.edges:
            u = self.nodes[edge.u]
            v = self.nodes[edge.v]
            
            colour = edge.colour if hasattr(edge, 'colour') else self.default_edge_colour

            r = self.edge_width / 2

            direction = atan2((v.y - u.y), (v.x - u.x))

            u1 = int(u.x + (cos(direction + (pi / 2)) * r)), int(u.y + (sin(direction + (pi / 2)) * r))
            u2 = int(u.x + (cos(direction - (pi / 2)) * r)), int(u.y + (sin(direction - (pi / 2)) * r))
            v1 = int(v.x + (cos(direction + (pi / 2)) * r)), int(v.y + (sin(direction + (pi / 2)) * r))
            v2 = int(v.x + (cos(direction - (pi / 2)) * r)), int(v.y + (sin(direction - (pi / 2)) * r))
            
            pygame.gfxdraw.aapolygon(self.screen, [u1, u2, v2, v1], colour) # To anti-alias the line
            pygame.gfxdraw.filled_polygon(self.screen, [u1, u2, v2, v1], colour) # Draw a polygon between two points on each node

            if self.directed:
                mid_point = (int((u.x + v.x) / 2), int((u.y + v.y) / 2))
                tip_point = ((mid_point[0] + (cos(direction) * 30)), (mid_point[1] + (sin(direction) * 30)))
                left_point = ((mid_point[0] + (cos(direction - (pi / 2)) * 10)), (mid_point[1] + (sin(direction - (pi / 2)) * 10)))
                # right_point = ((mid_point[0] + (cos(direction + (pi / 2)) * 10)), (mid_point[1] + (sin(direction + (pi / 2)) * 10)))

                pygame.draw.polygon(self.screen, colour, [tip_point, left_point, mid_point])
            

            if self.show_edge_labels and hasattr(edge, self.edge_labels):
                if self.directed:
                    self.font.render_to(self.screen, mid_point, str(getattr(edge, self.edge_labels)), self.text_colour)
                else:
                    pygame.draw.circle(self.screen, colour, mid_point, 10, 0)

                    label = str(getattr(edge, self.edge_labels))
                    x_off = -3 - ((len(label) // 2) * 3)
                    
                    self.font.render_to(self.screen, (mid_point[0] + x_off, mid_point[1] -5), label, self.edge_label_colour)


        for n in self.nodes:
            colour = n.colour if hasattr(n, 'colour') else self.default_node_colour                
            border_colour = n.border_colour if hasattr(n, 'border_colour') else self.node_border_colour
            text_colour = n.text_colour if hasattr(n, 'text_colour') else self.text_colour

            name = self.font.render(str(n.name), text_colour)[0] # name is a pygame 'surface'
            width, height = name.get_size()

            if self.node_shape == 'circle':
                if border_colour: # If no border colour is specified, assume no borders desired
                    r = self.circular_node_radius + self.node_border_width
                    pygame.gfxdraw.aacircle(self.screen, n.x, n.y, r, border_colour)
                    pygame.gfxdraw.filled_circle(self.screen, n.x, n.y, r, border_colour)

                pygame.gfxdraw.aacircle(self.screen, n.x, n.y, self.circular_node_radius, colour) # Use an aacircle to avoid jagged edges
                pygame.gfxdraw.filled_circle(self.screen, n.x, n.y, self.circular_node_radius, colour) # Fill into the anti-aliased border
                
                self.screen.blit(name, (n.x - (width // 2), n.y - (height // 2))) # Print the node name into the center of the circle

            elif self.node_shape == 'square':
                x = n.x - (width // 2)
                y = n.y - (height // 2)
                p = self.node_text_padding * 2
                width += p
                height += p
                rect = pygame.Rect(x, y, width, height)

                if border_colour: # If no border colour is specified, assume no borders desired
                    p = self.node_border_width * 2
                    border_rect = pygame.Rect(x - self.node_border_width, y - self.node_border_width, width + p, height + p)
                    pygame.draw.rect(self.screen, border_colour, border_rect)
                
                pygame.draw.rect(self.screen, colour, rect)

                self.screen.blit(name, (x + 5, y + 5))

                n._y_size = (height + 16) // 2 # Used to check whether the node has been clicked
                n._x_size = (width + 16) // 2 # as above

        pygame.display.update()

    def scale(self):
        x = [n.x for n in self.nodes]
        x = max(x) - min(x)
        x = (self.height / x) * 0.8 # 80 % of screen width
        
        y = [n.y for n in self.nodes]
        y = max(y) - min(y)
        y = (self.height / y) * 0.8 # 80 % of screen height

        for n in self.nodes:
            n.x = int(n.x * x)
            n.y = int(n.y * y)
            
        adjust_x = int(min([n.x for n in self.nodes]) - (0.1 * self.width))
        adjust_y = int(min([n.y for n in self.nodes]) - (0.1 * self.height))

        for n in self.nodes: # Shift scaled graph to fit on screen
            n.x -= adjust_x
            n.y -= adjust_y

    def distribute(self, animate = True):
        self.distributing = True
        
        total_force = inf
        prev = 0

        pseudo_edges = [] # Edges that ensure lonely nodes don't get flung into the void
        for node in self.nodes:
            if self.degree(node) == 0:
                if len(self.edges) == 0:
                    pseudo_edges.append((node, choice(self.nodes)))
                else:
                    lowest_degree_nodes = []
                    lowest_degree = inf
                    for n in self.nodes:
                        d = self.degree(n)
                        if 0 < d < lowest_degree:
                            lowest_degree_nodes = [n]
                        elif d == lowest_degree:
                            lowest_degree_nodes.append(n)
                    pseudo_edges.append((node, choice(lowest_degree_nodes)))

        running = True
        while running and total_force != prev:
            prev = total_force
            total_force = 0

            for node in self.nodes:
                if hasattr(node, '_fixed') and node._fixed:
                    continue
                node._x_force = 0
                node._y_force = 0
                for other in self.nodes:
                    if node != other:
                        r_squared = ((abs(node.x - other.x) ** 2) + (abs(node.y - other.y) ** 2))
                        if r_squared == 0:
                            force = max(self.width, self.height) ** (1 / 2)
                        else:
                            force = ((min(self.width, self.height) ** 2) / len(self.nodes)) / r_squared # k * (q1*q2)/r^2, where k is 1 (coulombs law)
                        direction = atan2((node.y - other.y), (node.x - other.x))
                        node._x_force += force * cos(direction)
                        node._y_force += force * sin(direction)

                        total_force += force

            for edge in self.edges + pseudo_edges:
                if type(edge) == tuple: # Pseudo edges are tuples of (u, v)
                    u = edge[0]
                    v = edge[1]
                else: # While self.edges are Edge objects
                    u = self.nodes[edge.u]
                    v = self.nodes[edge.v]
                dist = ((abs(u.x - v.x) ** 2) + (abs(u.y - v.y) ** 2)) ** (1 / 2)
                force = (-1 / len(self.nodes)) * abs((min(self.width, self.height) / 10) - dist) # Hookes law, where k is 1/|v|
                # Scale k to avoid 'singularity' situation
    
                total_force += force

                direction = atan2((u.y - v.y), (u.x - v.x))
                
                u._x_force += force * cos(direction)
                u._y_force += force * sin(direction)
                v._x_force += force * cos(direction + pi) # Add pi, as force is in opposite direction
                v._y_force += force * sin(direction + pi)

            for node in self.nodes:
                if hasattr(node, '_fixed') and node._fixed:
                    continue
                node.x += int(node._x_force)
                node.y += int(node._y_force)

            if animate:
                self.handle_pygame_events()
                self.redraw()                
        
        self.distributing = False

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for n in self.nodes:
                        m_x, m_y = event.pos

                        in_range = False
                        if self.node_shape == 'square' and (abs(m_x - n.x) <= n._x_size and abs(m_y - n.y) <= n._y_size): # If it's a square, check if the mouse position is within it's box
                            in_range = True
                        if self.node_shape == 'circle' and ((m_x - n.x) ** 2 + (m_y - n.y) ** 2) ** (1 / 2) <= self.circular_node_radius: # For a circle, just check against the radius
                            in_range = True

                        if in_range:
                            self.holding = n
                            self.holding._fixed = True # While the user holds the node, fix it for redistribution
                            self.holding_offset = ((n.x - m_x), (n.y - m_y))
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.holding:
                        self.holding._fixed = False
                        self.holding = None
                elif event.button == 3:
                    if not self.distributing:
                        self.distribute()
                    self.scale()
                    self.redraw()
            elif event.type == pygame.MOUSEMOTION:
                if self.holding:                
                    x, y = event.pos
                    self.holding.x = x + self.holding_offset[0]
                    self.holding.y = y + self.holding_offset[1]
                    if not self.distributing:
                        self.distribute()

    def _run(self):
        while self.running:
            self.handle_pygame_events()
        pygame.quit()

    def run(self):
        self.running = True
        self.init_window()
        self._run()

    def show(self):
        self.init_window()

    def close(self):
        pygame.quit()
