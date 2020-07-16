import pygame as pg
import numpy as np

from global_params import WHITE


class Rectangle:
    def __init__(self, start_w_pos, end_w_pos, color=WHITE):
        self.w_bounds = np.array([start_w_pos, end_w_pos], float)
        self._w_size = self.w_bounds[1] - self.w_bounds[0]
        self.w_shift = np.array([0.0, 0.0])

        self.color = color

    @property
    def w_pos(self):
        return self.w_bounds[0] + self.w_shift

    @property
    def w_bounds_shifted(self):
        return self.w_bounds + self.w_shift

    def draw(self, screen, pix_shift):
        rect = pg.Rect(
            (pix_shift[0], pix_shift[1] - self._w_size[1]),
            self._w_size,
            )
        pg.draw.rect(screen, self.color, rect)
