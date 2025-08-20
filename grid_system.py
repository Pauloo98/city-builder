# grid_system.py
from typing import Optional, Tuple, Set, Dict
from time import time as now
import pygame as pg

from models import Cell, CityState
from config_game import CATALOG
from settings import GRID_SIZE, TILE, MARGIN_LEFT, MARGIN_TOP

# ---- Conversões grid/pixel
def grid_to_px(x, y): return (MARGIN_LEFT + x * (TILE + 2), MARGIN_TOP + y * (TILE + 2))

def px_to_grid(px, py):
    gx = (px - MARGIN_LEFT) // (TILE + 2)
    gy = (py - MARGIN_TOP) // (TILE + 2)
    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE: return int(gx), int(gy)
    return None

# ---- Inicialização do grid
def make_grid() -> list[list[Cell]]:
    return [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# ---- Helpers de contagem
def count_all(grid, tile_key: str) -> int:
    return sum(1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)
               if grid[y][x].occupied and grid[y][x].is_root and grid[y][x].btype == tile_key)

def count_buildings_by_tile_connected(grid, connected_gids: Set[str], tile_key: str) -> int:
    return sum(1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)
               if grid[y][x].occupied and grid[y][x].is_root and grid[y][x].btype == tile_key
               and (grid[y][x].group_id in connected_gids))

def has_building(grid, name: str) -> bool:
    tile = CATALOG[name]["tile"]
    return any(grid[y][x].occupied and grid[y][x].is_root and grid[y][x].btype == tile
               for y in range(GRID_SIZE) for x in range(GRID_SIZE))

# ---- Construção / demolição
def can_place(grid, x, y, w, h) -> bool:
    if x + w > GRID_SIZE or y + h > GRID_SIZE: return False
    for j in range(h):
        for i in range(w):
            if grid[y+j][x+i].occupied: return False
    return True

def place_build(grid, x, y, name: str) -> Tuple[bool, Optional[str]]:
    cfg = CATALOG[name]
    w, h, tile = cfg["w"], cfg["h"], cfg["tile"]
    if not can_place(grid, x, y, w, h): return False, "Área ocupada/insuficiente."
    gid = f"{int(now()*1000)}"
    grid[y][x] = Cell(tile, True, True, gid)
    for j in range(h):
        for i in range(w):
            if i==0 and j==0: continue
            grid[y+j][x+i] = Cell(tile, True, False, gid)
    return True, gid

def demolish_gid(grid, gid: str):
    for yy in range(GRID_SIZE):
        for xx in range(GRID_SIZE):
            if grid[yy][xx].group_id == gid:
                grid[yy][xx] = Cell()

def demolish_at(grid, x, y):
    c = grid[y][x]
    if not c.occupied: return None
    gid = c.group_id
    demolish_gid(grid, gid)
    return gid

# ---- Conectividade por rua ligada à Prefeitura
def neighbors4(x, y):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            yield nx, ny

def recompute_connectivity(grid) -> Tuple[Set[Tuple[int,int]], Set[str]]:
    connected_roads: Set[Tuple[int,int]] = set()
    connected_gids: Set[str] = set()
    halls = [(x,y) for y in range(GRID_SIZE) for x in range(GRID_SIZE)
             if grid[y][x].occupied and grid[y][x].btype == "city_hall"]
    if not halls: return connected_roads, connected_gids

    # ruas adjacentes à prefeitura
    seeds = []
    for (cx, cy) in halls:
        for nx, ny in neighbors4(cx, cy):
            if grid[ny][nx].occupied and grid[ny][nx].btype == "road":
                seeds.append((nx, ny))

    # BFS nas ruas
    stack = list(seeds)
    seen = set(stack)
    while stack:
        x, y = stack.pop()
        connected_roads.add((x, y))
        for nx, ny in neighbors4(x, y):
            if (nx, ny) in seen: continue
            if grid[ny][nx].occupied and grid[ny][nx].btype == "road":
                seen.add((nx, ny)); stack.append((nx, ny))

    # qualquer tile do grupo encostando numa rua conectada → grupo conectado
    road_set = connected_roads
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            c = grid[y][x]
            if not (c.occupied and c.btype != "road"): continue
            gid = c.group_id
            if not gid: continue
            for nx, ny in neighbors4(x, y):
                if (nx, ny) in road_set:
                    connected_gids.add(gid)
                    break

    return connected_roads, connected_gids
