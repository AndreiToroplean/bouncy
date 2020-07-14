import pygame as pg
import numpy as np


class Ball:
    def __init__(self, init_pos, len_der, env_bbox, radius, restitution, color):
        self.pos_der = []

        for index in range(len_der):
            if index == 0:
                self.pos_der.append(init_pos)
                continue
            self.pos_der.append(np.array((0.0, 0.0)))
        
        self.env_bbox = env_bbox

        self.radius = radius
        self.restitution = restitution
        
        self.color = color

    def run_physics_step(self, input_action):
        for index in reversed(range(len_der := len(self.pos_der))):
            if index == len_der-1:
                new_val = self.pos_der[index] + input_action
            else:
                new_val = self.pos_der[index] + self.pos_der[index+1]
            if index != 0:
                self.pos_der[index] = new_val

        new_val = self._collide(new_val, self.env_bbox.bottom, 1, +1)
        new_val = self._collide(new_val, self.env_bbox.top, 1, -1)
        new_val = self._collide(new_val, self.env_bbox.left, 0, -1)
        new_val = self._collide(new_val, self.env_bbox.right, 0, +1)
        self.pos_der[0] = new_val

    def _collide(self, new_pos, bound_env, dim, direction, threshold=0.1):
        if direction * new_pos[dim] + self.radius > direction * bound_env:
            try:
                self.pos_der[1][dim] *= -1 * self.restitution
            except IndexError:
                pass
            new_pos[dim] -= (
                (new_pos[dim] + direction * self.radius - bound_env) * (1 + self.restitution)
                + direction * threshold
                )
        return new_pos

    def draw(self, screen):
        pg.draw.circle(screen, self.color, np.floor(self.pos_der[0]).astype(np.intc), self.radius)
