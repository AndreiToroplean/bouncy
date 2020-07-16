import pygame as pg
import numpy as np

from global_params import BORDER_S_WIDTH, MAX_N_OBSTS
from obstacle import Obstacle
from rectangle import Rectangle


class World:
    def __init__(self, res):
        self._borders = [
            Rectangle(
                (-res[0] / 2, res[1] * (+0.5 - BORDER_S_WIDTH)),
                (res[0] / 2, res[1] * (+0.5)),
                ),
            Rectangle(
                (-res[0] / 2, res[1] * (-0.5)),
                (res[0] / 2, res[1] * (-0.5 + BORDER_S_WIDTH)),
                ),
            ]
        self._obstacles = []

    @property
    def colliders(self):
        rtn = self._borders.copy()
        for obstacle in self._obstacles:
            rtn += obstacle.colliders
        return rtn

    def draw(self, camera):
        for border in self._borders:
            camera.draw(border)

        for obstacle in self._obstacles:
            for collider in obstacle.colliders:
                camera.draw(collider)

    def update_borders(self, camera_w_pos):
        for border in self._borders:
            border.w_shift = camera_w_pos

    def spawn_obstacle(self, w_pos, w_size, res):
        if len(self._obstacles) == MAX_N_OBSTS:
            del self._obstacles[0]
        obstacle = Obstacle(w_pos, w_size, res)
        self._obstacles.append(obstacle)
