import random
from copy import deepcopy
from enum import Enum
from math import log
from queue import SimpleQueue

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import FPS, N_PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, DEBUG, \
    BALL_RADIUS, BOUND_OBST_DIST, BOUND_OBST_WIDTH, BOUND_OBST_HEIGHT, BORDER_S_WIDTH, BALL_ACTION_FORCE, \
    LATENCY_FACTOR, GREY, RED, ENEMY_SPEED, ENEMY_WAIT, ENEMY_ADD_SPEED
from rectangle import Rectangle
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        # random.seed(0)

        self._camera = Camera()
        self._res = self._camera.pix_size

        self._len_der = INPUT_DERIVATIVE + 1
        self._action_force = BALL_ACTION_FORCE / (FPS * N_PHYSICS_SUBSTEPS) ** (self._len_der - 1)
        self._action_vec = np.array([0.0, 0.0])
        self._action_vec_phantom = np.array([0.0, 0.0])

        self._action_queue = SimpleQueue()
        self._action = Action.stay_horiz, Action.stay_vert

        self._action_map = {
            Action.go_right: +1,
            Action.go_left: -1,
            Action.go_up: +1,
            Action.go_down: -1,
            Action.stay_horiz: 0,
            Action.stay_vert: 0,
            }

        self._ball = Ball(
            init_w_pos=np.array([0.0, 0.0]),
            len_der=self._len_der,
            radius=BALL_RADIUS,
            )

        self._ball_phantom = deepcopy(self._ball)
        self._ball_phantom.color = GREY

        self._world = World(self._res)

        self._latest_obstacle_w_pos = np.array([0.0, 0.0])
        self._world.spawn_obstacle(np.array([-self._res[0]/4, 0.0]), np.array([-self._res[0]/8, 0.0]), self._res)

        self._enemy = Rectangle(*self._camera.w_view, color=RED)
        self._enemy.w_shift = np.array([-self._res[0] * 3/4, 0])
        self._enemy_moving = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    @property
    def _progress(self):
        return self._ball.w_pos[0]

    def main_loop(self):
        while True:
            # Inputs
            keys_pressed = pg.key.get_pressed()

            if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
                return
            action = [Action.stay_horiz, Action.stay_vert]
            is_moving_horiz = False
            if keys_pressed[pg.K_LEFT]:
                action[0] = Action.go_left
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                action[0] = Action.go_right
                is_moving_horiz ^= True
            if not is_moving_horiz:
                action[0] = Action.stay_horiz

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                action[1] = Action.go_down
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                action[1] = Action.go_up
                is_moving_vert ^= True
            if not is_moving_vert:
                action[1] = Action.stay_vert

            self._action_queue.put(action)

            # Inputs application
            if self._action_queue.qsize() > log(max(1, self._progress * LATENCY_FACTOR)):
                self._action = self._action_queue.get()

            self._action_vec[0] = self._action_map[self._action[0]] * self._action_force
            self._action_vec[1] = self._action_map[self._action[1]] * self._action_force

            self._action_vec_phantom[0] = self._action_map[action[0]] * self._action_force
            self._action_vec_phantom[1] = self._action_map[action[1]] * self._action_force

            # Logic
            # Obstacles
            if self._camera.w_view[1][0] > self._latest_obstacle_w_pos[0] + BOUND_OBST_DIST[0] - BOUND_OBST_WIDTH[1]/2:
                height_bound = (self._res[1] * (0.5-BORDER_S_WIDTH) - BALL_RADIUS)
                w_pos = np.array([
                    self._latest_obstacle_w_pos[0] + BOUND_OBST_DIST[0] + random.randint(0, BOUND_OBST_DIST[1] - BOUND_OBST_DIST[0]),
                    random.randint(-height_bound, height_bound),
                    ])
                w_size = np.array([
                    random.randint(*BOUND_OBST_WIDTH),
                    random.randint(*BOUND_OBST_HEIGHT),
                    ])
                self._world.spawn_obstacle(w_pos, w_size, self._res)
                self._latest_obstacle_w_pos = w_pos

            # Balls physics
            self._ball.run_physics(self._action_vec, self._world.colliders)
            self._ball_phantom.run_physics(self._action_vec_phantom, self._world.colliders)

            # Enemy
            if pg.time.get_ticks() > ENEMY_WAIT:
                self._enemy_moving = True
            if self._enemy_moving:
                self._enemy.w_shift[0] += ENEMY_SPEED + log(max(1, ENEMY_ADD_SPEED * self._progress))

            if self._enemy.w_view[1][0] - self._ball.radius > self._ball.w_pos[0]:
                return

            if not ((self._camera.w_view[0] < self._ball_phantom.w_pos).all()
                    and (self._ball_phantom.w_pos < self._camera.w_view[1]).all()):
                for index in range(self._len_der):
                    self._ball_phantom.w_pos_der[index][:] = self._ball.w_pos_der[index]

            self._camera.req_move(self._ball.w_pos)
            self._world.update_borders(self._camera.w_pos)

            # Graphics
            self._camera.empty_screen()

            self._camera.draw(self._ball_phantom)
            self._camera.draw(self._ball)

            self._camera.draw(self._enemy)

            self._world.draw(self._camera)

            if DEBUG:
                self._camera.draw_debug_info()

            self._camera.flip_display_and_tick()


class Action(Enum):
    go_right = 0
    go_left = 1
    stay_horiz = -1

    go_up = 2
    go_down = 3
    stay_vert = -2