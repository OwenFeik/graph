from graph import Graph # Base class
from math import inf, atan2, cos, sin, pi # Distibrution, drawing, calculations
from random import randint, choice # Spread nodes out initially, create pseudo-edges to random node
from copy import deepcopy # Build from a graph without modifying original

from contextlib import redirect_stdout
with redirect_stdout(None): # Suppress pygame welcome message
    import pygame # Rendering engine
import pygame.freetype # Text

class DisplayGraph(Graph):
    background_colour = (0, 0, 0)
    text_colour = (255, 255, 255)
    font_size = 14
    show_edge_labels = False
    show_node_labels = False
    node_labels = 'label'
    edge_labels = 'label'
    edge_label_colour = (0, 0, 0)
    default_edge_colour = (255, 255, 255)
    default_node_colour = (0, 0, 0)
    node_border_colour = (255, 255, 255)
    circular_node_radius = 15
    node_shape = 'square'
    window_title = 'Graph'

    def __init__(self, graph, width = 1000, height = 1000, **kwargs):
        graph = deepcopy(graph)

        super().__init__(graph.nodes.nodes, graph.edges, graph.directed)
        
        self.width = width
        self.height = height
        self.screen = None
        self.font = None

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

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
                               
            pygame.draw.line(self.screen, colour, (u.x, u.y), (v.x, v.y), 3)

            mid_point = (int((u.x + v.x) / 2), int((u.y + v.y) / 2))

            if self.directed:
                direction = atan2((v.y - u.y), (v.x - u.x))
                tip_point = ((mid_point[0] + (cos(direction) * 20)), (mid_point[1] + (sin(direction) * 20)))
                left_point = ((mid_point[0] + (cos(direction - (pi / 2)) * 10)), (mid_point[1] + (sin(direction - (pi / 2)) * 10)))
                right_point = ((mid_point[0] + (cos(direction + (pi / 2)) * 10)), (mid_point[1] + (sin(direction + (pi / 2)) * 10)))

                pygame.draw.polygon(self.screen, colour, [tip_point, left_point, right_point])
            

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
                    pygame.draw.circle(self.screen, border_colour, (n.x, n.y), self.circular_node_radius + 3, 3)

                pygame.draw.circle(self.screen, colour, (n.x, n.y), self.circular_node_radius, 0)
                
                self.screen.blit(name, (n.x - (width // 2), n.y - (height // 2)))

            elif self.node_shape == 'square':
                x = n.x - (width // 2)
                y = n.y - (height // 2)
                rect = pygame.Rect(x, y, width + 10, height + 10)

                if border_colour: # If no border colour is specified, assume no borders desired
                    border_rect = pygame.Rect(x - 3, y - 3, width + 16, height + 16)
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

        for n in self.nodes:
            n.x -= adjust_x
            n.y -= adjust_y

    def distribute(self, animate = True):
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
                node.x += int(node._x_force)
                node.y += int(node._y_force)

            if animate:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                else:
                    self.redraw()

    def _run(self):
        running = True
        offset = (0, 0)
        holding = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for n in self.nodes:
                            m_x, m_y = event.pos

                            in_range = False
                            if self.node_shape == 'square' and (abs(m_x - n.x) <= n._x_size and abs(m_y - n.y) <= n._y_size):
                                in_range = True
                            if self.node_shape == 'circle' and ((m_x - n.x) ** 2 + (m_y - n.y) ** 2) ** (1 / 2) <= self.circular_node_radius:
                                in_range = True

                            if in_range:
                                holding = n
                                offset = ((n.x - m_x), (n.y - m_y))
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        holding = None
                    elif event.button == 3:
                        self.distribute()
                        self.scale()
                        self.redraw()
                elif event.type == pygame.MOUSEMOTION:
                    if holding:                
                        x, y = event.pos
                        holding.x = x + offset[0]
                        holding.y = y + offset[1]
                        self.redraw()
            
        pygame.quit()

    def run(self):
        self.init_window()
        self._run()

    def show(self):
        self.init_window()

    def close(self):
        pygame.quit()
