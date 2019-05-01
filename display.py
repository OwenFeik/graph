from graph import Graph # Base class
from math import inf, atan2, cos, sin, pi # Distibrution, drawing, calculations
from random import randint # Spread nodes out initially
from copy import deepcopy # Build from a graph without modifying original

from contextlib import redirect_stdout
with redirect_stdout(None): # Suppress pygame welcome message
    import pygame # Rendering engine
import pygame.freetype # Text

class DisplayGraph(Graph):
    def __init__(self, graph, width = 1000, height = 1000, show_labels = False, **kwargs):
        graph = deepcopy(graph)

        super().__init__(graph.nodes.nodes, graph.edges, graph.directed)
        
        self.width = width
        self.height = height

        self.show_labels = show_labels
    
        self.default_edge_colour = kwargs['default_edge_colour'] if kwargs.get('default_edge_colour') else (0, 70, 180)
        self.default_node_colour = kwargs['default_node_colour'] if kwargs.get('default_node_colour') else (0, 140, 30)
        self.text_colour = kwargs['text_colour'] if kwargs.get('text_colour') else (255, 255, 255)
        self.font_size = kwargs['font_size'] if kwargs.get('font_size') else 14
        self.node_labels = kwargs['node_labels'] if kwargs.get('node_labels') else 'label'
        self.edge_labels = kwargs['edge_labels'] if kwargs.get('edge_labels') else 'label'

        self.screen = None
        self.font = None

        for node in self.nodes:
            node.x = randint(int(width * 0.1), int(width * 0.9))
            node.y = randint(int(height * 0.1), int(height * 0.9))
            node.x_force = 0
            node.y_force = 0

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('Graph')
        pygame.display.set_icon(pygame.image.load('icon.png'))
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.freetype.Font(None, self.font_size)

        self.redraw()
        
    def redraw(self):
        self.screen.fill((0, 0, 0))

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
            

            if self.show_labels and hasattr(edge, self.edge_labels):
                if self.directed:
                    self.font.render_to(self.screen, mid_point, str(getattr(edge, self.edge_labels)), self.text_colour)

                else:
                    pygame.draw.circle(self.screen, colour, mid_point, 10, 0)

                    label = str(getattr(edge, self.edge_labels))
                    x_off = 2 * len(label) + 1
                    
                    self.font.render_to(self.screen, (mid_point[0] - x_off, mid_point[1] -5), str(getattr(edge, self.edge_labels)), self.text_colour)


        for n in self.nodes:
            colour = n.colour if hasattr(n, 'colour') else self.default_node_colour                

            if self.show_labels and hasattr(n, self.node_labels):
                self.font.render_to(self.screen, (n.x + 20, n.y - 5), str(getattr(n, self.node_labels)), self.text_colour)

            pygame.draw.circle(self.screen, colour, (n.x, n.y), 15, 0)
            if self.width > n.x > 0 and self.height > n.y > 0:
                self.font.render_to(self.screen, (n.x - 3, n.y - 5), str(n.name), self.text_colour)            


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

        self.redraw()

    def distribute(self, animate = True):
        total_force = inf
        prev = 0

        while total_force != prev:
            prev = total_force
            total_force = 0

            for node in self.nodes:
                node.x_force = 0
                node.y_force = 0
                for other in self.nodes:
                    if node != other:
                        r_squared = ((abs(node.x - other.x) ** 2) + (abs(node.y - other.y) ** 2))
                        if r_squared == 0:
                            force = max(self.width, self.height) ** (1 / 2)
                        else:
                            force = ((min(self.width, self.height) ** 2) / len(self.nodes)) / r_squared # k * (q1*q2)/r^2, where k is 1 (coulombs law)
                        direction = atan2((node.y - other.y), (node.x - other.x))
                        node.x_force += force * cos(direction)
                        node.y_force += force * sin(direction)

                        total_force += force

            for edge in self.edges:
                u = self.nodes[edge.u]
                v = self.nodes[edge.v]
                dist = ((abs(u.x - v.x) ** 2) + (abs(u.y - v.y) ** 2)) ** (1 / 2)
                force = -0.1 * abs((min(self.width, self.height) / 10) - dist) # Hookes law, where k is 0.1
    
                total_force += force

                direction = atan2((u.y - v.y), (u.x - v.x))
                
                u.x_force += force * cos(direction)
                u.y_force += force * sin(direction)
                v.x_force += force * cos(direction + pi) # Add pi, as force is in opposite direction
                v.y_force += force * sin(direction + pi)

            for node in self.nodes:
                node.x += int(node.x_force)
                node.y += int(node.y_force)

            if animate:
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
                            if ((m_x - n.x) ** 2 + (m_y - n.y) ** 2) ** (1 / 2) <= 10:
                                holding = n
                                offset = ((n.x - m_x), (n.y - m_y))
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        holding = None
                        self.distribute()
                    elif event.button == 3:
                        self.distribute()
                        self.scale()
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
