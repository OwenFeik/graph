from graph import Graph
from math import inf, atan2, cos, sin, pi
from random import randint
from copy import deepcopy

from contextlib import redirect_stdout
with redirect_stdout(None): # Suppress pygame welcome message
    import pygame
import pygame.freetype

class DisplayGraph(Graph):
    def __init__(self, graph, width, height):
        graph = deepcopy(graph)
        super().__init__([n.ident for n in graph.nodes], [(e.u, e.v) for e in graph.edges], graph.directed)
        
        self.width = width
        self.height = height
    
        self.screen = None
        self.font = None

        for node in self.nodes:
            node.x = randint(0, width)
            node.y = randint(0, height)
            node.x_force = 0
            node.y_force = 0

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('Graph')
        pygame.display.set_icon(pygame.image.load('icon.png'))
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.freetype.Font(None, 14)
        
    def redraw(self):
        self.screen.fill((0, 0, 0))

        for edge in self.edges:
            u = (self.nodes[edge.u].x, self.nodes[edge.u].y)
            v = (self.nodes[edge.v].x, self.nodes[edge.v].y)
            
            colour = edge.colour if hasattr(edge, 'colour') else (0, 70, 180)
                               
            pygame.draw.line(self.screen, colour, u, v, 3)

        for n in self.nodes:
            colour = n.colour if hasattr(n, 'colour') else (0, 140, 30)                

            pygame.draw.circle(self.screen, colour, (n.x, n.y), 10, 0)
            if self.width > n.x > 0 and self.height > n.y > 0:
                self.font.render_to(self.screen, (n.x + 20, n.y - 5), str(n.name), (255, 255, 255))            


        pygame.display.update()

    # def scale(self):
    #     x = [n.x for n in self.nodes]
    #     x = max(x) - min(x)
    #     x = (self.height / x) * 0.8 # 80 % of screen width
        
    #     y = [n.y for n in self.nodes]
    #     y = max(y) - min(y)
    #     y = (self.height / y) * 0.8 # 80 % of screen height

    #     for n in self.nodes:
    #         n.x = int(n.x * x)
    #         n.y = int(n.y * y)

    #         print(f'{n.x}, {n.y}')

            

    #     self.redraw()

    def distribute(self):
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
                        force = ((min(self.width, self.height) ** 2) / len(self.nodes)) / ((abs(node.x - other.x) ** 2) + (abs(node.y - other.y) ** 2)) # k * (q1*q2)/r^2, where k is 1 (coulombs law)
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

            self.redraw()

    def show(self):
        self.init_window()
        self.redraw()

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
                        # self.scale()
                elif event.type == pygame.MOUSEMOTION:
                    if holding:                
                        x, y = event.pos
                        holding.x = x + offset[0]
                        holding.y = y + offset[1]
                        self.redraw()
            
        pygame.quit()
