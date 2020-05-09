import pygame as pg
import numpy as np

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)
FPS = 60


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()

        self.pos = np.array(self.screen_rect.center, dtype=np.float64)
        self.vel = np.array((0.0, 0.0))
        self.acc = np.array((0.0, 0.2))

        self.radius = 50

    def __enter__(self):
        pg.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def main_loop(self):
        while True:
            # Inputs
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return

            # Logic
            self.vel += self.acc
            self.pos += self.vel

            # Graphics
            self.screen.fill(BLACK)

            ball_rect = pg.draw.circle(self.screen, GREY, self.pos.astype(np.intc), self.radius)

            pg.display.flip()

            # Time
            self.clock.tick(FPS)
