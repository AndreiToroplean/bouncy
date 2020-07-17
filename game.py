import random
from enum import Enum
from queue import SimpleQueue

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import FPS, N_PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, DEBUG, \
    BALL_RADIUS, BOUND_OBST_DIST, BOUND_OBST_WIDTH, BOUND_OBST_HEIGHT, BORDER_S_WIDTH, BALL_ACTION_FORCE, LATENCY_FACTOR
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

        self._action_queue = SimpleQueue()

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

            is_moving_horiz = False
            if keys_pressed[pg.K_LEFT]:
                action_horiz = Action.go_left
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                action_horiz = Action.go_right
                is_moving_horiz ^= True
            if not is_moving_horiz:
                action_horiz = Action.stay_horiz

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                action_vert = Action.go_down
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                action_vert = Action.go_up
                is_moving_vert ^= True
            if not is_moving_vert:
                action_vert = Action.stay_vert

            self._action_queue.put((action_horiz, action_vert))

            # Inputs application
            if self._action_queue.qsize() > self._progress * LATENCY_FACTOR:
                action_horiz, action_vert = self._action_queue.get()
            else:
                action_horiz, action_vert = Action.stay_horiz, Action.stay_vert

            if action_horiz == Action.go_left:
                self._input_action[0] = -self._input_action_force
            elif action_horiz == Action.go_right:
                self._input_action[0] = self._input_action_force
            else:
                self._input_action[0] = 0.0

            if action_vert == Action.go_down:
                self._input_action[1] = -self._input_action_force
            elif action_vert == Action.go_up:
                self._input_action[1] = self._input_action_force
            else:
                self._input_action[1] = 0.0

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


class Action(Enum):
    go_right = 0
    go_left = 1
    stay_horiz = -1

    go_up = 2
    go_down = 3
    stay_vert = -2