from math import isclose, pi

import pygame as pg
import numpy as np

from global_params import N_PHYSICS_SUBSTEPS, C_WHITE, FPS


class Ball:
    def __init__(self, init_w_pos, len_der, radius, restitution, friction, color=C_WHITE):
        self.w_pos_der = []
        self._len_der = len_der

        for index in range(self._len_der):
            if index == 0:
                self.w_pos_der.append(init_w_pos)
                continue
            self.w_pos_der.append(np.array([0.0, 0.0]))

        self.radius = radius
        self._restitution = restitution
        self._friction_factor = friction / (FPS * N_PHYSICS_SUBSTEPS)

        self.color = color

        self.alive = True

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

    @property
    def progress(self):
        return self.w_pos[0]

    @property
    def mass(self):
        return pi * self.radius ** 2

    def _run_physics_step(self, colliders, other_balls, *, n_substeps, threshold=1.0):
        # Movement
        for index in reversed(range(self._len_der - 1)):
            self.w_pos_der[index] = self.w_pos_der[index] + self.w_pos_der[index + 1]

        w_speed = np.linalg.norm(self.w_vel)
        if isclose(w_speed, 0.0):
            return

        # Friction
        if self._len_der >= 3 :
            self.w_acc -= (self.w_vel / w_speed) * ((w_speed * self._friction_factor) ** 2) / n_substeps

        # Collecting collision data
        collision_data = []
        for collider in colliders:
            bounds = collider.w_bounds_shifted
            other_w_pos = (
                min(max(bounds[0][0], self.w_pos[0]), bounds[1][0]),
                min(max(bounds[0][1], self.w_pos[1]), bounds[1][1]),
                )
            collision_dist = self.radius
            collision_data.append((other_w_pos, collision_dist, None))

        for ball in other_balls:
            other_w_pos = ball.w_pos
            collision_dist = self.radius + ball.radius
            collision_data.append((other_w_pos, collision_dist, ball))

        # Collisions
        for other_w_pos, collision_dist, obj in collision_data:
            w_dir = other_w_pos - self.w_pos
            w_norm = np.linalg.norm(w_dir)
            if w_norm > collision_dist:
                continue

            w_normal = -w_dir / w_norm
            w_vel_exchange = np.dot(self.w_vel, w_normal) * self._restitution * w_normal
            w_pos_adjustment = (collision_dist - w_norm) * (self.w_vel / w_speed) + threshold * w_normal
            if obj is None:
                self.w_vel -= 2 * w_vel_exchange
                self.w_pos += w_pos_adjustment
            else:
                self.w_vel -= w_vel_exchange
                obj.w_vel += w_vel_exchange
                self.w_pos += w_pos_adjustment * 0.5

    def run_physics(self, input_action, colliders, other_balls, *, n_substeps=N_PHYSICS_SUBSTEPS):
        self.w_pos_der[-1] = input_action
        for _ in range(n_substeps):
            self._run_physics_step(colliders, other_balls, n_substeps=n_substeps)

    def draw(self, screen, pix_shift):
        pg.draw.circle(screen, self.color, pix_shift, self.radius)
