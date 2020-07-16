import pygame as pg

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(128, 128, 128)
WHITE = pg.Color(255, 255, 255)

FPS = 120
N_PHYSICS_SUBSTEPS = 10
INPUT_DERIVATIVE = 2

CAM_DAMPING_FACTOR = 10

DEBUG = True
FULL_SCREEN = True

if DEBUG:
    FULL_SCREEN = False
