import pygame as pg
import numpy as np

from global_params import N_PHYSICS_SUBSTEPS


class Ball:
    def __init__(self, init_w_pos, len_der, radius, restitution, color):
        self.w_pos_der = []

        for index in range(len_der):
            if index == 0:
                self.w_pos_der.append(init_w_pos)
                continue
            self.w_pos_der.append(np.array([0.0, 0.0]))

        self.radius = radius
        self.restitution = restitution

        self.color = color

    @property
    def w_pos(self):
        return self.w_pos_der[0]

    @w_pos.setter
    def w_pos(self, value):
        self.w_pos_der[0] = value

    def _run_physics_step(self, input_action):
        for index in reversed(range(len_der := len(self.w_pos_der))):
            if index == len_der-1:
                new_val = self.w_pos_der[index] + input_action
            else:
                new_val = self.w_pos_der[index] + self.w_pos_der[index + 1]
            if index != 0:
                self.w_pos_der[index] = new_val

        # new_val = self._collide(new_val, self.env_bbox.bottom, 1, +1)
        # new_val = self._collide(new_val, self.env_bbox.top, 1, -1)
        # new_val = self._collide(new_val, self.env_bbox.left, 0, -1)
        # new_val = self._collide(new_val, self.env_bbox.right, 0, +1)
        self.w_pos = new_val

    def run_physics(self, input_action, n_substeps=N_PHYSICS_SUBSTEPS):
        for _ in range(n_substeps):
            self._run_physics_step(input_action)

    def _collide(self, new_pos, bound_env, dim, direction, threshold=0.1):
        if direction * new_pos[dim] + self.radius > direction * bound_env:
            try:
                self.w_pos_der[1][dim] *= -1 * self.restitution
            except IndexError:
                pass
            new_pos[dim] -= (
                (new_pos[dim] + direction * self.radius - bound_env) * (1 + self.restitution)
                + direction * threshold
                )
        return new_pos

    def draw(self, screen, pix_shift):
        pg.draw.circle(screen, self.color, pix_shift, self.radius)
