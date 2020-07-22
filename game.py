import os
import json
import random
from copy import deepcopy
from enum import Enum
from math import log, exp
from queue import SimpleQueue

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import FPS, N_PHYSICS_SUBSTEPS, DEBUG, BORDER_S_WIDTH, C_DARK_GREY, C_RED, SETTINGS, SEED, SAVES_DIR, \
    SAVE_PATH, DELAY_BEFORE_QUITTING, LOAD, SAVE, SCORE_EXPADD_FACTOR, SCORE_ADD_FACTOR
from rectangle import Rectangle
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        self._high_score = 0
        self._seed = SEED

        self._load()

        if self._seed is not None:
            random.seed(self._seed)

        self._random_state = random.getstate()

        self._len_der = SETTINGS.INPUT_DERIVATIVE + 1
        self._action_force = SETTINGS.BALL_ACTION_FORCE / (FPS * N_PHYSICS_SUBSTEPS) ** (self._len_der - 1)
        self._action_vec = np.array([0.0, 0.0])

        self._action = Action.stay_horiz, Action.stay_vert

        self._action_map = {
            Action.go_right: +1,
            Action.go_left: -1,
            Action.go_up: +1,
            Action.go_down: -1,
            Action.stay_horiz: 0,
            Action.stay_vert: 0,
            }

        self._camera = None
        self._res = None
        self._ball = None
        self._world = None
        self._latest_obstacle_w_pos = None
        self._enemy = None
        self._enemy_progress = None
        self._enemy_moving = None
        self._score = None
        self._action_queue = None
        self._death_time = None
        self._game_running = None

        self._initialize_game()

    def _initialize_game(self):
        random.setstate(self._random_state)

        self._camera = Camera()
        self._res = self._camera.res

        self._ball = Ball(
            init_w_pos=np.array([0.0, 0.0]),
            len_der=self._len_der,
            radius=SETTINGS.BALL_RADIUS,
            restitution=SETTINGS.BALL_RESTITUTION,
            friction=SETTINGS.BALL_FRICTION,
            )

        self._world = World(self._res)

        self._latest_obstacle_w_pos = np.array([0.0, 0.0])
        self._world.spawn_obstacle(np.array([-self._res[0] / 4, 0.0]), np.array([self._res[0] / 8, 0.0]), self._res)

        self._enemy = Rectangle(*(self._camera.w_view - self._res * np.array([0.5, 0.0])), color=C_RED)
        self._enemy_progress = -self._res[0] * 1 / 4
        self._enemy_moving = False

        self._score = 0
        self._action_queue = SimpleQueue()

        self._death_time = None

        self._game_running = True

    @property
    def _progress(self):
        return self._ball.w_pos[0]

    def main_loop(self):
        while True:
            # Inputs
            keep_playing = self.get_inputs()
            if not keep_playing:
                self._save()
                return False

            # Logic
            self._apply_logic()

            if self._death_time is not None and self._camera.time - self._death_time > DELAY_BEFORE_QUITTING:
                self._game_running = False

            # Graphics
            self._draw_graphics()

            if not self._game_running:
                self._save()
                play_again = self._end_screen()
                if not play_again:
                    return False

                self._initialize_game()

    def get_inputs(self):
        """Gets player inputs and returns a boolean of whether we keep playing. """
        keys_pressed = pg.key.get_pressed()

        if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
            return False

        action = [Action.stay_horiz, Action.stay_vert]
        is_moving_horiz = False
        if keys_pressed[pg.K_LEFT] or keys_pressed[pg.K_a]:
            action[0] = Action.go_left
            is_moving_horiz ^= True
        if keys_pressed[pg.K_RIGHT] or keys_pressed[pg.K_d]:
            action[0] = Action.go_right
            is_moving_horiz ^= True
        if not is_moving_horiz:
            action[0] = Action.stay_horiz

        is_moving_vert = False
        if keys_pressed[pg.K_DOWN] or keys_pressed[pg.K_s]:
            action[1] = Action.go_down
            is_moving_vert ^= True
        if keys_pressed[pg.K_UP] or keys_pressed[pg.K_w]:
            action[1] = Action.go_up
            is_moving_vert ^= True
        if not is_moving_vert:
            action[1] = Action.stay_vert

        self._action_queue.put(action)

        # Inputs application
        latency = log(max(1, self._progress * SETTINGS.LATENCY_FACTOR))
        while self._action_queue.qsize() > latency:
            self._action = self._action_queue.get()

        if self._death_time is None:
            self._action_vec[0] = self._action_map[self._action[0]] * self._action_force
            self._action_vec[1] = self._action_map[self._action[1]] * self._action_force

        else:
            no_action_vec = np.array([0.0, 0.0])
            self._action_vec[:] = no_action_vec

        return True

    def _apply_logic(self):
        # Obstacles
        if self._camera.w_view[1][0] > self._latest_obstacle_w_pos[0] + SETTINGS.BOUND_OBST_DIST[0] - \
                SETTINGS.BOUND_OBST_WIDTH[1] / 2:
            height_bound = (self._res[1] * (0.5 - BORDER_S_WIDTH) - SETTINGS.BALL_RADIUS)
            w_pos = np.array([
                self._latest_obstacle_w_pos[0] + SETTINGS.BOUND_OBST_DIST[0] + random.randint(0,
                    SETTINGS.BOUND_OBST_DIST[1] - SETTINGS.BOUND_OBST_DIST[0]),
                random.randint(-height_bound, height_bound),
                ])
            w_size = np.array([
                random.randint(*SETTINGS.BOUND_OBST_WIDTH),
                random.randint(*SETTINGS.BOUND_OBST_HEIGHT),
                ])
            self._world.spawn_obstacle(w_pos, w_size, self._res)
            self._latest_obstacle_w_pos = w_pos

        # Balls physics
        self._ball.run_physics(self._action_vec, self._world.colliders)

        # Enemy
        if self._death_time is None and self._camera.time > SETTINGS.ENEMY_WAIT:
            self._enemy_moving = True

        enemy_distance = self._ball.radius + self._ball.w_pos[0] - self._enemy_progress
        if self._enemy_moving:
            proximity_slowdown = SETTINGS.ENEMY_PROX_COMPENSATION_FACTOR * (1 - 1 / (enemy_distance + SETTINGS.ENEMY_PROX_BIAS + 1) ** SETTINGS.ENEMY_PROX_POW)
            self._enemy_progress += max(0, (SETTINGS.ENEMY_SPEED + log(max(1, SETTINGS.ENEMY_LOGADD_SPEED * self._progress))) * proximity_slowdown)
        self._enemy.w_shift[0] = self._enemy_progress

        # Death
        if self._death_time is None and enemy_distance < 0:
            self._death_time = self._camera.time
            self._enemy_moving = False

        # Camera
        self._camera.req_move(self._ball.w_pos[0])

        # World
        self._world.update_borders(self._camera.w_pos)

        # Score
        self._score = max(self._score, int(self._progress * SCORE_ADD_FACTOR + exp(self._progress * SCORE_EXPADD_FACTOR)) - 1)
        self._high_score = max(self._high_score, self._score)

    def _draw_graphics(self):
        self._camera.empty_screen()

        self._camera.draw(self._ball)

        self._camera.draw(self._enemy)

        self._world.draw(self._camera)

        self._camera.draw_score(self._score, self._high_score)

        if DEBUG:
            self._camera.draw_debug_info()

        self._camera.flip_display_and_tick()

    def _load(self):
        try:
            os.makedirs(SAVES_DIR)
        except FileExistsError:
            pass

        if not LOAD:
            return

        try:
            with open(SAVE_PATH) as file:
                data = json.load(file)
        except FileNotFoundError:
            pass
        else:
            self._seed = data["seed"]
            difficulty_preset_nb = data["difficulty_preset_nb"]
            SETTINGS.set_difficulty(difficulty_preset_nb)

            self._high_score = data["high_score"]

    def _save(self):
        if not SAVE:
            return

        data = {
            "seed": self._seed,
            "difficulty_preset_nb": SETTINGS.DIFFICULTY_PRESET_NB,
            "high_score": self._high_score,
            }

        with open(SAVE_PATH, "w") as file:
            json.dump(data, file, indent=4)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def _end_screen(self):
        self._camera.draw_end_screen(self._score)
        self._camera.flip_display_and_tick()
        while True:
            keys_pressed = pg.key.get_pressed()
            if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
                return False
            elif keys_pressed[pg.K_RETURN] or keys_pressed[pg.K_KP_ENTER]:
                return True


class Action(Enum):
    go_right = 0
    go_left = 1
    stay_horiz = -1

    go_up = 2
    go_down = 3
    stay_vert = -2
