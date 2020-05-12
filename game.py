import pygame as pg
import numpy as np

from ball import Ball

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)

FPS = 120
PHYSICS_SUBSTEPS = 10

INPUT_DERIVATIVE = 3

FULL_SCREEN = False
DEBUG = False


class Game:
    def __init__(self):
        pg.init()
        if FULL_SCREEN:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((800, 600))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(pg.font.get_default_font(), 24)

        self.len_der = INPUT_DERIVATIVE
        self.input_action_value = 1000.0 / (FPS * PHYSICS_SUBSTEPS) ** self.len_der
        self.input_action = np.array((0.0, 0.0))

        self.ball = Ball(
            init_pos=np.array(self.screen_rect.center, dtype=np.float64),

            len_der=self.len_der,

            env_bbox=self.screen_rect,

            radius=20,
            restitution=0.95,

            color=WHITE
            )

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
                self.input_acc[0] = -self.input_acc_value
                is_moving_horiz ^= True
            if keys_pressed[pg.K_RIGHT]:
                self.input_acc[0] = self.input_acc_value
                is_moving_horiz ^= True
            if not is_moving_horiz:
                self.input_acc[0] = 0.0

            is_moving_vert = False
            if keys_pressed[pg.K_DOWN]:
                self.input_acc[1] = self.input_acc_value
                is_moving_vert ^= True
            if keys_pressed[pg.K_UP]:
                self.input_acc[1] = -self.input_acc_value
                is_moving_vert ^= True
            if not is_moving_vert:
                self.input_acc[1] = 0.0

            # Logic
            for _ in range(PHYSICS_SUBSTEPS):
                self.ball.run_physics_step(self.input_action)

            # Graphics
            self.screen.fill(BLACK)

            self.ball.draw(self.screen)

            if DEBUG:
                fps_surf = self.font.render(f"{self.clock.get_fps():.1f}", True, WHITE)
                self.screen.blit(fps_surf, (20, 20))

            pg.display.flip()

            # Time
            self.clock.tick(FPS)
