from math import isclose

import pygame as pg
import numpy as np

from global_params import N_PHYSICS_SUBSTEPS, BALL_RESTITUTION, WHITE, BALL_FRICTION, FPS


class Ball:
    def __init__(self, init_w_pos, len_der, radius, color=WHITE):
        self.w_pos_der = []
        self._len_der = len_der

        for index in range(self._len_der):
            if index == 0:
                self.w_pos_der.append(init_w_pos)
                continue
            self.w_pos_der.append(np.array([0.0, 0.0]))

        self.radius = radius
        self._restitution = BALL_RESTITUTION
        self._friction_factor = BALL_FRICTION / (FPS * N_PHYSICS_SUBSTEPS)

        self.color = color

    @property
    def w_pos(self):
        return self.w_pos_der[0]

    @w_pos.setter
    def w_pos(self, value):
        self.w_pos_der[0] = value

    @property
    def w_vel(self):
        return self.w_pos_der[1]

    @w_vel.setter
    def w_vel(self, value):
        self.w_pos_der[1] = value

    @property
    def w_acc(self):
        return self.w_pos_der[2]

    @w_acc.setter
    def w_acc(self, value):
        self.w_pos_der[2] = value

    def _run_physics_step(self, colliders, threshold=0.01):
        for index in reversed(range(self._len_der - 1)):
            self.w_pos_der[index] = self.w_pos_der[index] + self.w_pos_der[index + 1]

        w_speed = np.linalg.norm(self.w_vel)
        if isclose(w_speed, 0.0):
            return

        for collider in colliders:

            bounds = collider.w_bounds_shifted
            closest_w_pos = (
                min(max(bounds[0][0], self.w_pos[0]), bounds[1][0]),
                min(max(bounds[0][1], self.w_pos[1]), bounds[1][1]),
                )
            w_dir = closest_w_pos - self.w_pos
            w_norm = np.linalg.norm(w_dir)
            if w_norm > self.radius:
                continue

            # r = d−2(d⋅n)n
            w_normal = -w_dir / w_norm
            self.w_vel = (self.w_vel - 2 * np.dot(self.w_vel, w_normal) * w_normal)
            self.w_vel *= self._restitution

            self.w_pos += (self.radius - w_norm) * (self.w_vel / w_speed) + threshold * w_normal

    def run_physics(self, input_action, colliders, n_substeps=N_PHYSICS_SUBSTEPS):
        if self._len_der >= 3:
            self.w_acc -= (self.w_vel * self._friction_factor) ** 2
        self.w_pos_der[-1] = input_action
        for _ in range(n_substeps):
            self._run_physics_step(colliders)

    def draw(self, screen, pix_shift):
        pg.draw.circle(screen, self.color, pix_shift, self.radius)
