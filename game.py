import random

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import FPS, N_PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, DEBUG, \
    BALL_RADIUS, BOUND_OBST_DIST, BOUND_OBST_WIDTH, BOUND_OBST_HEIGHT, BORDER_S_WIDTH, BALL_ACTION_FORCE
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        random.seed(0)

        self._camera = Camera()
        self._res = self._camera.pix_size

        self._len_der = INPUT_DERIVATIVE + 1
        self._input_action_force = BALL_ACTION_FORCE / (FPS * N_PHYSICS_SUBSTEPS) ** (self._len_der - 1)
        self._input_action = np.array([0.0, 0.0])

        self._ball = Ball(
            init_w_pos=np.array([0.0, 0.0]),
            len_der=self._len_der,
            radius=BALL_RADIUS,
            )

        self._world = World(self._res)

        self._latest_obstacle_w_pos = np.array([0.0, 0.0])
        self._world.spawn_obstacle(np.array([-400.0, 0]), np.array([200.0, 0.0]), self._res)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def main_loop(self):
        while True:
            # Inputs
            keys_pressed = pg.key.get_pressed()

            if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
                return

            is_moving_horiz = False
            if keys_pressed[pg.K_LEFT]:
                self._input_action[0] = -self._input_action_force
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                self._input_action[0] = self._input_action_force
                is_moving_horiz ^= True
            if not is_moving_horiz:
                self._input_action[0] = 0.0

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                self._input_action[1] = -self._input_action_force
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                self._input_action[1] = self._input_action_force
                is_moving_vert ^= True
            if not is_moving_vert:
                self._input_action[1] = 0.0

            # Logic
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

            self._ball.run_physics(self._input_action, self._world.colliders)
            self._camera.req_move(self._ball.w_pos)
            self._world.update_borders(self._camera.w_pos)

            # Graphics
            self._camera.empty_screen()
            self._world.draw(self._camera)

            self._camera.draw(self._ball)

            if DEBUG:
                self._camera.draw_debug_info()

            self._camera.flip_display_and_tick()
