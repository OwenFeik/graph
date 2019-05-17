class Quadtree():
    def __init__(self, nodes, width, height, layer = 0, x = 0, y = 0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.nodes = nodes

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
                    
                    self.children.append(Quadtree(child_nodes, child_width, child_height, layer + 1, (x * child_width) + self.x, (y * child_height) + self.y))

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
            self.center_mass = None
            self.mass = 0

    def get_force(self, node, theta):
        if ((((self.center_mass[0] + n.x) ** 2) + ((self.center_mass[1] + n.y) ** 2)) ** (1 / 2)) / self.width < theta:
            
        # for c in self.children:
            # if c.center_mass

"""
Properties of a cell:
    layer: The cells width is equal to 1/2^layer of the total width
    x, y: The top left corner of this cell
    nodes: The nodes within the cell
    center of mass: The point where the mass (equal to len(nodes)) is concentrated

Process:
    Call quadtree() on graph. Then for each quarter of this graph
    that has more than one node, recursively call on that corner.

"""
