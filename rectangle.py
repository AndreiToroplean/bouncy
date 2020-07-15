from collections import namedtuple

import pygame as pg
import numpy as np

from global_params import WHITE


class Rectangle:
    def __init__(self, start_w_pos, end_w_pos, color=WHITE):
        self._w_bounds = np.array([start_w_pos, end_w_pos], float)
        self._w_size = self._w_bounds[1] - self._w_bounds[0]
        self.w_shift = np.array([0.0, 0.0])

        self.color = color

    def _get_bound(self, dir_, dim):
        return self._w_bounds[(-dir_+1)//2, dim], dim, dir_

    @property
    def right(self):
        return self._get_bound(dir_=-1, dim=0)

    @property
    def top(self):
        return self._get_bound(dir_=-1, dim=1)

    @property
    def left(self):
        return self._get_bound(dir_=+1, dim=0)

    @property
    def bottom(self):
        return self._get_bound(dir_=+1, dim=1)

    # bottom, 1, +1)
    # top, 1, -1)
    # left, 0, +1)
    # right, 0, -1)

    @property
    def w_pos(self):
        return self._w_bounds[0] + self.w_shift

    def draw(self, screen, pix_shift):
        rect = pg.Rect(
            (pix_shift[0], pix_shift[1] - self._w_size[1]),
            self._w_size,
            )
        pg.draw.rect(screen, self.color, rect)
