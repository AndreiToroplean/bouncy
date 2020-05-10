import pygame as pg
import numpy as np

from ball import Ball

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)
FPS = 120
PHYSICS_SUBSTEPS = 10


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        # self.screen = pg.display.set_mode((800, 600))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(pg.font.get_default_font(), 24)

        self.input_acc_value = 1000.0 / (FPS * PHYSICS_SUBSTEPS)**2
        self.input_acc = np.array((0.0, 0.0))

        self.ball = Ball(
            init_pos=np.array(self.screen_rect.center, dtype=np.float64),
            init_vel=np.array((0.0, 0.0)),
            init_acc=np.array((0.0, 2000.0 / (FPS*PHYSICS_SUBSTEPS)**2)),

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
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.QUIT:
                    return

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.input_acc[0] = -self.input_acc_value
                    if event.key == pg.K_RIGHT:
                        self.input_acc[0] = self.input_acc_value
                    if event.key == pg.K_DOWN:
                        self.input_acc[1] = self.input_acc_value
                    if event.key == pg.K_UP:
                        self.input_acc[1] = -self.input_acc_value

                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                        self.input_acc[0] = 0.0
                    if event.key == pg.K_DOWN or event.key == pg.K_UP:
                        self.input_acc[1] = 0.0

            # Logic
            for _ in range(PHYSICS_SUBSTEPS):
                self.ball.run_physics_step(self.input_acc)

            # Graphics
            self.screen.fill(BLACK)

            self.ball.draw(self.screen)

            fps_surf = self.font.render(f"{self.clock.get_fps():.1f}", True, WHITE)
            self.screen.blit(fps_surf, (20, 20))
            pg.display.flip()

            # Time
            self.clock.tick(FPS)
