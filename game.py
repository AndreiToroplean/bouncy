import pygame as pg
import numpy as np

from ball import Ball
from camera import Camera
from global_params import WHITE, FPS, N_PHYSICS_SUBSTEPS, INPUT_DERIVATIVE, DEBUG
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        self._camera = Camera()

        self._len_der = INPUT_DERIVATIVE
        self._input_action_value = 1000.0 / (FPS * N_PHYSICS_SUBSTEPS) ** self._len_der
        self._input_action = np.array([0.0, 0.0])

        self._ball = Ball(
            init_w_pos=np.array([0.0, 0.0]),

            len_der=self._len_der,

            radius=20,
            restitution=0.75,

            color=WHITE
            )

        self._world = World(self._camera.pix_size)

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
                self._input_action[0] = -self._input_action_value
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                self._input_action[0] = self._input_action_value
                is_moving_horiz ^= True
            if not is_moving_horiz:
                self._input_action[0] = 0.0

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                self._input_action[1] = -self._input_action_value
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                self._input_action[1] = self._input_action_value
                is_moving_vert ^= True
            if not is_moving_vert:
                self._input_action[1] = 0.0

            # Logic
            self._ball.run_physics(self._input_action)
            self._camera.req_move(self._ball.w_pos)
            self._world.update_borders(self._camera.w_pos)

            # Graphics
            self._camera.empty_screen()
            self._world.draw(self._camera)

            self._camera.draw(self._ball)

            if DEBUG:
                self._camera.draw_debug_info()

            self._camera.flip_display_and_tick()
