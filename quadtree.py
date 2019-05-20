from math import atan2, sin, cos

class Quadtree():
    def __init__(self, nodes, width, height, layer = 0, x = 0, y = 0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.nodes = nodes

        self.empty = True
        self.leaf = False
        self.children = []
        if len(self.nodes) > 1:
            child_width = width / 2
            child_height = height / 2
            for y in range(2):
                for x in range(2):
                    child_nodes = []
                    for n in nodes:
                        in_range_x = ((child_width * x) + self.x) <= n.x < ((child_width * (x + 1)) + self.x)
                        in_range_y = ((child_height * y) + self.y) <= n.y < ((child_height * (y + 1)) + self.y)
                        if in_range_x and in_range_y:
                            child_nodes.append(n)
                    
                    if child_nodes:
                        self.empty = False
                        self.children.append(Quadtree(child_nodes, child_width, child_height, layer + 1, (x * child_width) + self.x, (y * child_height) + self.y))
        elif len(self.nodes) == 1:
            self.leaf = True
            self.empty = False

        if self.children:
            self.mass = sum([c.mass for c in self.children])
            x_center = sum([c.center_mass[0] * c.mass for c in self.children if c.mass]) / self.mass
            y_center = sum([c.center_mass[1] * c.mass for c in self.children if c.mass]) / self.mass
            self.center_mass = x_center, y_center
        elif self.nodes:
            n = self.nodes[0]
            self.center_mass = (n.x, n.y)
            self.mass = 1
        else:
            self.center_mass = (0, 0)
            self.mass = 0
        
    def apply_force(self, node, theta):
        x, y = self.center_mass

        if self.leaf and self.nodes[0] == node:
            return

        r_squared = (abs(node.x - x) ** 2) + (abs(node.y - y) ** 2)
        if r_squared == 0:
            return

        sd_ratio = self.width / (r_squared ** (1 / 2))
        if (((sd_ratio <= theta) or self.leaf) and (not self.empty)) :
            force = (100000 * self.mass) / r_squared
            direction = atan2((node.y - y), (node.x - x))

            node._x_force += force * cos(direction)
            node._y_force += force * sin(direction)
        elif self.children:
            for c in self.children:
                c.apply_force(node, theta)
            