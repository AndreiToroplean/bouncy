import os

import pygame as pg

from settings import Settings
from classes import DifficultyPreset

DEBUG = False
FULL_SCREEN = True
DEBUG_RES = 1280, 720

if DEBUG:
    FULL_SCREEN = False

N_PLAYERS = 2

C_BLACK = pg.Color(0, 0, 0)
C_DARK_GREY = pg.Color(32, 32, 32)
C_WHITE = pg.Color(255, 255, 255)
C_RED = pg.Color(255, 0, 0)

C_LIME_GREEN = pg.Color(196, 255, 128)
C_YELLOW = pg.Color(255, 255, 64)

C_LIGHT_GREEN = pg.Color(128, 255, 128)
C_LIGHT_BLUE = pg.Color(128, 196, 255)

C_END = pg.Color(150, 50, 50)

FPS = 60
DELAY_BEFORE_QUITTING = 1000
N_PHYSICS_SUBSTEPS = 10
MAX_N_OBSTS = 16

BORDER_S_WIDTH = 1 / 4
CAM_DAMPING_FACTOR = 8

SCORE_ADD_FACTOR = 1.0
SCORE_EXPADD_FACTOR = 0.00002

SEED = 0
DIFFICULTY_PRESET = DifficultyPreset.der_2
SETTINGS = Settings(difficulty_preset=DIFFICULTY_PRESET, fps=FPS)

LOAD = True
SAVE = True

if DIFFICULTY_PRESET == DifficultyPreset.test:
    LOAD = False
    SAVE = False

SAVE_DIR = "saves"
SAVE_PROFILES = [
    "p1_l2",
    "p2_l2",
    ]
SAVE_PATHS = [os.path.join(SAVE_DIR, f"{save_profile}.json") for save_profile in SAVE_PROFILES]

BALLS_COLORS = [
    (C_WHITE, ),
    (C_LIGHT_BLUE, C_LIGHT_GREEN),
    ][N_PLAYERS-1]

BALLS_DISTANCE = 80
ENEMY_MIN_REMAP = -2000, 300, 20, 4
