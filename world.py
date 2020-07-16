import pygame as pg
import numpy as np

from obstacle import Obstacle
from rectangle import Rectangle


class World:
    def __init__(self, camera_pix_size):
        self._borders = [
            Rectangle(
                (-camera_pix_size[0]/2, camera_pix_size[1]*(+0.5-1/20)),
                (camera_pix_size[0]/2, camera_pix_size[1]*(+0.5)),
                ),
            Rectangle(
                (-camera_pix_size[0]/2, camera_pix_size[1]*(-0.5)),
                (camera_pix_size[0]/2, camera_pix_size[1]*(-0.5+1/20)),
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

    def spawn_obstacle(self, w_pos, w_size, camera_pix_size):
        obstacle = Obstacle(w_pos, w_size, camera_pix_size)
        self._obstacles.append(obstacle)
