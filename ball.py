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

        self._collide(+self.radius, self.env_bbox.bottom, 1, lambda a, b: a > b)
        self._collide(-self.radius, self.env_bbox.top, 1, lambda a, b: a < b)
        self._collide(-self.radius, self.env_bbox.left, 0, lambda a, b: a < b)
        self._collide(+self.radius, self.env_bbox.right, 0, lambda a, b: a > b)

        # self._collide(self.env_bbox.bottom, 1, +1)
        # self._collide(self.env_bbox.top, 1, -1)
        # self._collide(self.env_bbox.left, 0, -1)
        # self._collide(self.env_bbox.right, 0, +1)

    def _collide(self, bound_obj_offset, bound_env, dim, cond):
        new_ball_pos = self.pos + self.vel
        if cond(self.pos[dim] + bound_obj_offset, bound_env):
            self.vel[dim] *= -1 * self.restitution
            new_ball_pos[dim] -= (self.pos[dim] + bound_obj_offset - bound_env) * (1 + self.restitution)
        self.pos = new_ball_pos

    # def _collide(self, bound_env, dim, direction):
    #     new_ball_pos = self.pos + self.vel
    #     if direction * (self.pos[dim] + self.radius) > direction * bound_env:
    #         self.vel[dim] *= -1 * self.restitution
    #         new_ball_pos[dim] -= (self.pos[dim] + direction * self.radius - bound_env) * (1 + self.restitution)
    #     self.pos = new_ball_pos

    def draw(self, screen):
        pg.draw.circle(screen, self.color, np.floor(self.pos).astype(np.intc), self.radius)
