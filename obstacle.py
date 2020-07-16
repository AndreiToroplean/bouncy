import pygame as pg
import numpy as np

from rectangle import Rectangle


class Obstacle:
    def __init__(self, w_pos, w_size, camera_pix_size):
        self._w_pos = w_pos
        self._w_size = w_size

        y_min = self._w_pos[1] - self._w_size[1] / 2
        y_max = self._w_pos[1] + self._w_size[1] / 2
        self.colliders = []
        if y_min > -camera_pix_size[1]/2:
            self.colliders.append(Rectangle(
                np.array([self._w_pos[0] - self._w_size[0]/2, -camera_pix_size[1]/2]),
                np.array([self._w_pos[0] + self._w_size[0]/2, y_min]),
                ))
        if y_max < camera_pix_size[1]/2:
            self.colliders.append(Rectangle(
                np.array([self._w_pos[0] - self._w_size[0]/2, y_max]),
                np.array([self._w_pos[0] + self._w_size[0]/2, camera_pix_size[1]/2]),
                ))
