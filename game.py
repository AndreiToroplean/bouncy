import os
import json
import random
from copy import deepcopy
from enum import Enum
from math import log
from queue import SimpleQueue

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import FPS, N_PHYSICS_SUBSTEPS, DEBUG, BORDER_S_WIDTH, DARK_GREY, RED, SETTINGS, SEED, SAVES_DIR, \
    SAVE_PATH, DELAY_BEFORE_QUITTING
from rectangle import Rectangle
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        if SEED is not None:
            random.seed(SEED)

        self._camera = Camera()
        self._res = self._camera.res

        # Loading
        try:
            os.makedirs(SAVES_DIR)
        except FileExistsError:
            pass

        try:
            with open(SAVE_PATH) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass
        else:
            seed = data["seed"]
            difficulty_preset_nb = data["difficulty_preset_nb"]

            if seed is not None:
                random.seed(seed)
            SETTINGS.set_difficulty(difficulty_preset_nb)

            self._camera.high_score = data["high_score"]

        self._len_der = SETTINGS.INPUT_DERIVATIVE + 1
        self._action_force = SETTINGS.BALL_ACTION_FORCE / (FPS * N_PHYSICS_SUBSTEPS) ** (self._len_der - 1)
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
            radius=SETTINGS.BALL_RADIUS,
            restitution=SETTINGS.BALL_RESTITUTION,
            friction=SETTINGS.BALL_FRICTION,
            )

        self._ball_phantom = deepcopy(self._ball)
        self._ball_phantom.color = DARK_GREY

        self._world = World(self._res)

        self._latest_obstacle_w_pos = np.array([0.0, 0.0])
        self._world.spawn_obstacle(np.array([-self._res[0]/4, 0.0]), np.array([-self._res[0]/8, 0.0]), self._res)

        self._enemy = Rectangle(*self._camera.w_view, color=RED)
        self._enemy.w_shift = np.array([-self._res[0] * 3/4, 0])
        self._enemy_moving = False

        self._score = 0

        self._death_time = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        data = {
            "seed": SEED,
            "difficulty_preset_nb": SETTINGS.DIFFICULTY_PRESET_NB,
            "high_score": max(self._camera.high_score, self._score)
            }

        with open(SAVE_PATH, "w") as file:
            json.dump(data, file, indent=4)

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
            if self._action_queue.qsize() > log(max(1, self._progress * SETTINGS.LATENCY_FACTOR)):
                self._action = self._action_queue.get()

            if self._death_time is None:
                self._action_vec[0] = self._action_map[self._action[0]] * self._action_force
                self._action_vec[1] = self._action_map[self._action[1]] * self._action_force

                self._action_vec_phantom[0] = self._action_map[action[0]] * self._action_force
                self._action_vec_phantom[1] = self._action_map[action[1]] * self._action_force

            else:
                no_action_vec = np.array([0.0, 0.0])
                self._action_vec = no_action_vec
                self._action_vec_phantom = no_action_vec

            # Logic
            #   Obstacles
            if self._camera.w_view[1][0] > self._latest_obstacle_w_pos[0] + SETTINGS.BOUND_OBST_DIST[0] - SETTINGS.BOUND_OBST_WIDTH[1]/2:
                height_bound = (self._res[1] * (0.5-BORDER_S_WIDTH) - SETTINGS.BALL_RADIUS)
                w_pos = np.array([
                    self._latest_obstacle_w_pos[0] + SETTINGS.BOUND_OBST_DIST[0] + random.randint(0, SETTINGS.BOUND_OBST_DIST[1] - SETTINGS.BOUND_OBST_DIST[0]),
                    random.randint(-height_bound, height_bound),
                    ])
                w_size = np.array([
                    random.randint(*SETTINGS.BOUND_OBST_WIDTH),
                    random.randint(*SETTINGS.BOUND_OBST_HEIGHT),
                    ])
                self._world.spawn_obstacle(w_pos, w_size, self._res)
                self._latest_obstacle_w_pos = w_pos

            #   Balls physics
            self._ball.run_physics(self._action_vec, self._world.colliders)
            self._ball_phantom.run_physics(self._action_vec_phantom, self._world.colliders)

            if not ((self._camera.w_view[0] < self._ball_phantom.w_pos).all()
                    and (self._ball_phantom.w_pos < self._camera.w_view[1]).all()):
                for index in range(self._len_der):
                    self._ball_phantom.w_pos_der[index][:] = self._ball.w_pos_der[index]

            #   Enemy
            if self._death_time is None and self._camera.time > SETTINGS.ENEMY_WAIT:
                self._enemy_moving = True

            if self._enemy_moving:
                self._enemy.w_shift[0] += SETTINGS.ENEMY_SPEED + log(max(1, SETTINGS.ENEMY_ADD_SPEED * self._progress))

            if self._death_time is None and self._enemy.w_view[1][0] - self._ball.radius > self._ball.w_pos[0]:
                self._death_time = self._camera.time
                self._enemy_moving = False

            if self._death_time is not None and self._camera.time - self._death_time > DELAY_BEFORE_QUITTING:
                return

            #   Camera
            self._camera.req_move(self._ball.w_pos)

            #   World
            self._world.update_borders(self._camera.w_pos)

            #   Score
            self._score = max(self._score, int(self._progress))

            # Graphics
            self._camera.empty_screen()

            self._camera.draw(self._ball_phantom)
            self._camera.draw(self._ball)

            self._camera.draw(self._enemy)

            self._world.draw(self._camera)

            self._camera.draw_score(self._score)

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