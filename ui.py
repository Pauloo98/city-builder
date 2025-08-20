# ui.py
# Funções auxiliares de interface gráfica com pygame

import pygame as pg
from settings import COLORS

def draw_text(surface, text, x, y, size=20, color=COLORS["text"], center=False):
    font = pg.font.SysFont(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)

def draw_panel(surface, x, y, w, h, color=(50,50,60), border=4):
    rect = pg.Rect(x, y, w, h)
    pg.draw.rect(surface, color, rect, border_radius=8)
    pg.draw.rect(surface, (80,80,100), rect, width=border, border_radius=8)
    return rect
