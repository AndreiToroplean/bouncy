import pygame as pg

pg.init()
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
clock = pg.time.Clock()

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)
FPS = 60


def main_loop():
    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return

        screen.fill(BLACK)
        pg.display.flip()
        clock.tick(FPS)


main_loop()
pg.quit()
