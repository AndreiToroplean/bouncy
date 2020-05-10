import pygame as pg
import numpy as np


class Ball:
    def __init__(self, init_pos, init_vel, init_acc, env_bbox, radius, restitution, color):
        self.pos = init_pos
        self.vel = init_vel
        self.acc = init_acc
        
        self.env_bbox = env_bbox

        self.radius = radius
        self.restitution = restitution
        
        self.color = color

    def run_physics_step(self, input_acc):
        self.vel += self.acc + input_acc

        new_pos = self.pos + self.vel
        new_pos = self._collide(new_pos, self.env_bbox.bottom, 1, +1)
        new_pos = self._collide(new_pos, self.env_bbox.top, 1, -1)
        new_pos = self._collide(new_pos, self.env_bbox.left, 0, -1)
        new_pos = self._collide(new_pos, self.env_bbox.right, 0, +1)
        self.pos = new_pos

    def _collide(self, new_pos, bound_env, dim, direction, threshold=0.1):
        if direction * new_pos[dim] + self.radius > direction * bound_env:
            self.vel[dim] *= -1 * self.restitution
            new_pos[dim] -= (
                (new_pos[dim] + direction * self.radius - bound_env) * (1 + self.restitution)
                + direction * threshold
                )
        return new_pos

    def draw(self, screen):
        pg.draw.circle(screen, self.color, np.floor(self.pos).astype(np.intc), self.radius)
