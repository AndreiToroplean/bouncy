import os
import json
import random
from math import log, exp
from queue import SimpleQueue

import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from controls import CONTROL_MAPS
from global_params import FPS, DEBUG, BORDER_S_WIDTH, C_DARK_GREY, C_RED, SETTINGS, SEED, SAVE_DIR, \
    DELAY_BEFORE_QUITTING, LOAD, SAVE, SCORE_EXPADD_FACTOR, SCORE_ADD_FACTOR, N_PLAYERS, SAVE_PATHS, BALLS_COLORS, \
    BALLS_DISTANCE, ENEMY_MIN_REMAP, SLOWMO_FACTOR
from rectangle import Rectangle
from classes import Action
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        if SEED is not None:
            random.seed(SEED)

        self._random_state = random.getstate()

        self._high_scores = [0 for _ in range(N_PLAYERS)]
        self._load()

        self._len_der = SETTINGS.INPUT_DERIVATIVE + 1
        self._action_force = SETTINGS.BALL_ACTION_FORCE / (FPS * SLOWMO_FACTOR) ** (self._len_der - 1)

        self._action_map = {
            Action.stay: 0,
            Action.go_right: +1,
            Action.go_left: -1,
            Action.go_up: +1,
            Action.go_down: -1,
            }

        self._actions = None
        self._actions_vecs = None
        self._camera = None
        self._res = None
        self._balls = None
        self._world = None
        self._latest_obstacle_w_pos = None
        self._enemy = None
        self._enemy_progress = None
        self._enemy_progress_adjusted = None
        self._enemy_moving = None
        self._scores = None
        self._actions_queue = None
        self._n_balls_alive = None
        self._death_time = None
        self._game_running = None

        self._initialize_game()

    def _initialize_game(self):
        random.setstate(self._random_state)

        self._actions = [[Action.stay, Action.stay] for _ in range(N_PLAYERS)]
        self._actions_vecs = [np.array([0.0, 0.0]) for _ in range(N_PLAYERS)]

        self._camera = Camera()
        self._res = self._camera.res

        self._balls = []
        distance_range = BALLS_DISTANCE * (N_PLAYERS-1)
        for i in range(N_PLAYERS):
            self._balls.append(Ball(
                init_w_pos=np.array([0.0, i * BALLS_DISTANCE - distance_range/2]),
                len_der=self._len_der,
                radius=SETTINGS.BALL_RADIUS,
                restitution=SETTINGS.BALL_RESTITUTION,
                friction=SETTINGS.BALL_FRICTION,
                color=BALLS_COLORS[i]
                ))

        self._world = World(self._res)

        self._latest_obstacle_w_pos = np.array([0.0, 0.0])
        self._world.spawn_obstacle(np.array([-self._res[0]/4, self._res[1]/2]), np.array([self._res[0]/8, 0.0]), self._res)

        self._enemy = Rectangle(*(self._camera.w_view - self._res * np.array([0.5, 0.0])), color=C_RED)
        self._enemy_progress = -self._res[0] * 1 / 4
        self._enemy_progress_adjusted = self._enemy_progress
        self._enemy_moving = False

        self._scores = [0 for _ in range(N_PLAYERS)]
        self._actions_queue = SimpleQueue()

        self._n_balls_alive = N_PLAYERS
        self._death_time = None

        self._game_running = True

    @property
    def _min_progress(self):
        return min([ball.progress for ball in self._balls if ball.alive])

    @property
    def _max_progress(self):
        return max([ball.progress for ball in self._balls if ball.alive])

    @property
    def _worst_ball(self):
        return min([(ball, ball.progress) for ball in self._balls if ball.alive], key=lambda x: x[1])[0]

    @property
    def _best_ball(self):
        return max([(ball, ball.progress) for ball in self._balls if ball.alive], key=lambda x: x[1])[0]

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

        actions = [[Action.stay, Action.stay] for _ in range(N_PLAYERS)]
        are_moving = [[False, False] for _ in range(N_PLAYERS)]

        for control_map, action, is_moving in zip(CONTROL_MAPS, actions, are_moving):
            for control, (dim, req_action) in control_map.items():
                if keys_pressed[control]:
                    if is_moving[dim]:
                        action[dim] = Action.stay
                    else:
                        action[dim] = req_action
                    is_moving[dim] ^= True

        self._actions_queue.put(actions)

        # Inputs application
        latency = log(max(1, self._max_progress * SETTINGS.LATENCY_FACTOR))
        while self._actions_queue.qsize() > latency:
            self._actions = self._actions_queue.get()

        for action, action_vec in zip(self._actions, self._actions_vecs):
            if self._death_time is None:
                action_vec[0] = self._action_map[action[0]] * self._action_force
                action_vec[1] = self._action_map[action[1]] * self._action_force
            else:
                action_vec[:] = self._action_map[Action.stay]

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
        for ball, action_vec in zip(self._balls, self._actions_vecs):
            ball.run_physics(action_vec, self._world.colliders, [b for b in self._balls if b is not ball and b.alive])

        # Enemy
        if self._death_time is None and self._camera.time > SETTINGS.ENEMY_WAIT:
            self._enemy_moving = True

        worst_ball = self._worst_ball
        enemy_distance = worst_ball.radius + worst_ball.progress - self._enemy_progress
        if self._enemy_moving:
            proximity_slowdown = SETTINGS.ENEMY_PROX_COMPENSATION_FACTOR * (1 - 1 / (enemy_distance + SETTINGS.ENEMY_PROX_BIAS + 1) ** SETTINGS.ENEMY_PROX_POW)
            self._enemy_progress += max(0, (SETTINGS.ENEMY_SPEED + log(max(1, SETTINGS.ENEMY_LOGADD_SPEED * self._max_progress))) * proximity_slowdown)

        border_pos = self._camera.w_view[0][0]
        enemy_border_rel_pos = self._enemy_progress - border_pos
        enemy_border_rel_pas_remapped = max(0, min(1, ((enemy_border_rel_pos - ENEMY_MIN_REMAP[0]) / (ENEMY_MIN_REMAP[1] - ENEMY_MIN_REMAP[0])))) ** ENEMY_MIN_REMAP[3] * (ENEMY_MIN_REMAP[1] - ENEMY_MIN_REMAP[2]) + ENEMY_MIN_REMAP[2]
        self._enemy_progress_adjusted = max(self._enemy_progress, border_pos + enemy_border_rel_pas_remapped)
        self._enemy.w_shift[0] = self._enemy_progress_adjusted
        enemy_distance_adjusted = worst_ball.radius + worst_ball.progress - self._enemy_progress_adjusted

        # Death
        if self._n_balls_alive != 0 and enemy_distance_adjusted < 0:
            self._n_balls_alive -= 1
            if self._n_balls_alive != 0:
                worst_ball.alive = False

        if self._death_time is None and self._n_balls_alive == 0:
            self._death_time = self._camera.time
            self._enemy_moving = False

        # Camera
        self._camera.req_move(self._best_ball.w_pos[0])

        # World
        self._world.update_borders(self._camera.w_pos)

        # Scores
        for i in range(N_PLAYERS):
            self._scores[i] = max(self._scores[i], int(self._balls[i].progress * SCORE_ADD_FACTOR + exp(self._balls[i].progress * SCORE_EXPADD_FACTOR)) - 1)
            self._high_scores[i] = max(self._high_scores[i], self._scores[i])

    def _draw_graphics(self):
        self._camera.empty_screen()

        for ball in self._balls:
            if not ball.alive:
                continue

            self._camera.draw(ball)

        self._camera.draw(self._enemy)

        self._world.draw(self._camera)

        self._camera.draw_scores(self._scores, self._high_scores)

        if DEBUG:
            self._camera.draw_debug_info()

        self._camera.flip_display_and_tick()

    def _load(self):
        try:
            os.makedirs(SAVE_DIR)
        except FileExistsError:
            pass

        if not LOAD:
            return

        for i in range(N_PLAYERS):
            try:
                with open(SAVE_PATHS[i]) as file:
                    data = json.load(file)
            except FileNotFoundError:
                pass
            else:
                self._high_scores[i] = data["high_score"]

                if i != 0:
                    continue

    def _save(self):
        if not SAVE:
            return

        for i in range(N_PLAYERS):
            data = {
                "high_score": self._high_scores[i],
                }

            with open(SAVE_PATHS[i], "w") as file:
                json.dump(data, file, indent=4)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def _end_screen(self):
        winner = 0
        for i, ball in enumerate(self._balls):
            if ball.alive:
                winner = i
                break
        self._camera.draw_end_screen(self._scores[0], winner)
        self._camera.flip_display_and_tick()
        while True:
            keys_pressed = pg.key.get_pressed()
            if keys_pressed[pg.K_ESCAPE] or pg.event.peek(pg.QUIT):
                return False
            elif keys_pressed[pg.K_RETURN] or keys_pressed[pg.K_KP_ENTER]:
                return True
