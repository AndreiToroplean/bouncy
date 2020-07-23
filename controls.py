import pygame as pg

from classes import Action


CONTROL_MAPS = [
    {
        pg.K_a: (0, Action.go_left),
        pg.K_d: (0, Action.go_right),
        pg.K_s: (1, Action.go_down),
        pg.K_w: (1, Action.go_up),
        },
    {
        pg.K_LEFT: (0, Action.go_left),
        pg.K_RIGHT: (0, Action.go_right),
        pg.K_DOWN: (1, Action.go_down),
        pg.K_UP: (1, Action.go_up),
        },
    ]
