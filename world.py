import pygame as pg
import numpy as np

from rectangle import Rectangle


class World:
    def __init__(self, camera_pix_size):
        self.borders = [
            Rectangle(
                (-camera_pix_size[0]/2, camera_pix_size[1]*(+0.5-1/20)),
                (camera_pix_size[0]/2, camera_pix_size[1]*(+0.5)),
                ),
            Rectangle(
                (-camera_pix_size[0]/2, camera_pix_size[1]*(-0.5+1/20)),
                (camera_pix_size[0]/2, camera_pix_size[1]*(-0.5)),
                ),
            ]

    def draw(self, camera):
        for border in self.borders:
            camera.draw(border)

    def update_borders(self, camera_w_pos):
        for border in self.borders:
            border.w_shift = camera_w_pos
