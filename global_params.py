import pygame as pg

BLACK = pg.Color(0, 0, 0)
GREY = pg.Color(32, 32, 32)
WHITE = pg.Color(255, 255, 255)

FPS = 60
N_PHYSICS_SUBSTEPS = 10
INPUT_DERIVATIVE = 2

CAM_DAMPING_FACTOR = 10
BORDER_S_WIDTH = 1/4

BALL_RADIUS = 20
BALL_ACTION_FORCE = 1000.0
BALL_RESTITUTION = 0.75
BALL_FRICTION = 10

LATENCY_FACTOR = 10000

BOUND_OBST_WIDTH = 32, 256
BOUND_OBST_HEIGHT = BALL_RADIUS * 4, BALL_RADIUS * 16
BOUND_OBST_DIST = BOUND_OBST_WIDTH[1] + BALL_RADIUS * 4, 1024
MAX_N_OBSTS = 16

DEBUG = False
FULL_SCREEN = True

if DEBUG:
    FULL_SCREEN = False
