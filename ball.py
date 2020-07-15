import pygame as pg
import numpy as np

from global_params import N_PHYSICS_SUBSTEPS


class Ball:
    def __init__(self, init_w_pos, len_der, radius, restitution, color):
        self.w_pos_der = []
        self._len_der = len_der

        for index in range(self._len_der):
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

    def _run_physics_step(self, colliders):
        for index in reversed(range(self._len_der - 1)):
            new_val = self.w_pos_der[index] + self.w_pos_der[index + 1]
            if index != 0:
                self.w_pos_der[index] = new_val

        for collider in colliders:
            pass
            if self.w_pos_der[1][1] > 0:
                new_val = self._collide(new_val, *collider.bottom, collider.top[0])
            elif self.w_pos_der[1][1] < 0:
                new_val = self._collide(new_val, *collider.top, collider.bottom[0])
            if self.w_pos_der[1][0] > 0:
                new_val = self._collide(new_val, *collider.left, collider.right[0])
            elif self.w_pos_der[1][0] < 0:
                new_val = self._collide(new_val, *collider.right, collider.left[0])

        self.w_pos = new_val

    def run_physics(self, input_action, colliders, n_substeps=N_PHYSICS_SUBSTEPS):
        self.w_pos_der[-1] = input_action
        for _ in range(n_substeps):
            self._run_physics_step(colliders)

    def _collide(self, new_pos, bound, dim, dir_, other_bound, threshold=0.1):
        if dir_ * other_bound > dir_ * new_pos[dim] + self.radius > dir_ * bound:
            try:
                self.w_pos_der[1][dim] *= -1 * self.restitution
            except IndexError:
                pass
            new_pos[dim] -= (
                    (new_pos[dim] + dir_ * self.radius - bound) * (1 + self.restitution)
                    + dir_ * threshold
                )
        return new_pos

    def draw(self, screen, pix_shift):
        pg.draw.circle(screen, self.color, pix_shift, self.radius)
