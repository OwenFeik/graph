import cv2
from random import randint
from example import g

base = cv2.imread('base.png')

for node in g.nodes:
    node.x = randint(0, 1000)
    node.y = randint(0, 1000)
    cv2.circle(base, (node.x, node.y), 3, (0, 255, 0))

for edge in g.edges:
    u = (g.nodes[edge.u].x, g.nodes[edge.u].y)
    v = (g.nodes[edge.v].x, g.nodes[edge.v].y)
    cv2.line(base, u, v, (0, 0, 255))

while True:
    cv2.imshow('base', base)
    cv2.waitKey(0)
