import pygame as pg
import numpy as np


class Ball:
    def __init__(self, color, pos, radius):
        self.color = color
        self.pos = pos
        self.vel = np.array((0, 0))
        self.acc = np.array((0, -10))

        self.radius = radius
