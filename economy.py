# economy.py
import math, random
from typing import Tuple, Set
from models import CityState
from grid_system import count_all, count_buildings_by_tile_connected
from config_game import (
    PROD_POWER_PER, PROD_WATER_PER, CONS_POWER_PER_DAY, CONS_WATER_PER_DAY,
    CAP_PER, JOBS_PER, BASE_UNIT_VALUE, PARTICIPATION_ADULT, PARTICIPATION_ELDER,
    ONEOFF_DECAY_PER_HOUR, UPKEEP_PER_MIN
)

def central_bank_connected(state: CityState, grid, connected_gids: Set[str]) -> bool:
    return count_buildings_by_tile_connected(grid, connected_gids, "central_bank") > 0

def refresh_treasury_cap(state: CityState, grid, connected_gids: Set[str]):
    com  = count_buildings_by_tile_connected(grid, connected_gids, "commercial")
    ind  = count_buildings_by_tile_connected(grid, connected_gids, "industrial")
    farm = count_buildings_by_tile_connected(grid, connected_gids, "farm")
    base_cap = CAP_PER["commercial"]*com + CAP_PER["industrial"]*ind + CAP_PER["farm"]*farm
    if central_bank_connected(state, grid, connected_gids): base_cap *= 1.5
    state.treasury_cap = float(base_cap)

def update_labor_market(state: CityState, grid, connected_gids: Set[str]) -> Tuple[int,int,int,int,int,int,int]:
    com  = count_buildings_by_tile_connected(grid, connected_gids, "commercial")
    ind  = count_buildings_by_tile_connected(grid, connected_gids, "industrial")
    farm = count_buildings_by_tile_connected(grid, connected_gids, "farm")

    jobs_com  = JOBS_PER["commercial"] * com
    jobs_ind  = JOBS_PER["industrial"] * ind
    jobs_farm = JOBS_PER["farm"] * farm

    labor_total = int(round(
        state.pop_adult * PARTICIPATION_ADULT + state.pop_elder * PARTICIPATION_ELDER
    ))
    total_jobs = jobs_com + jobs_ind + jobs_farm
    if total_jobs <= 0 or labor_total <= 0:
        labor_com = labor_ind = labor_farm = 0
        state.unemployment = 100.0 if labor_total > 0 else 0.0
        return jobs_com, jobs_ind, jobs_farm, labor_total, labor_com, labor_ind, labor_farm

    labor_com  = int(round(labor_total * (jobs_com  / total_jobs)))
    labor_ind  = int(round(labor_total * (jobs_ind  / total_jobs)))
    labor_farm = labor_total - labor_com - labor_ind
    emp = min(labor_com, jobs_com) + min(labor_ind, jobs_ind) + min(labor_farm, jobs_farm)
    state.unemployment = max(0.0, 1.0 - (emp / max(1, labor_total))) * 100.0
    return jobs_com, jobs_ind, jobs_farm, labor_total, labor_com, labor_ind, labor_farm

def recompute_resources(state: CityState, grid, connected_gids: Set[str]):
    # capacidade
    usinas = count_buildings_by_tile_connected(grid, connected_gids, "utility")
    etas   = count_buildings_by_tile_connected(grid, connected_gids, "water_plant")
    state.power_cap = 10.0 + usinas * PROD_POWER_PER["utility"]
    state.water_cap = 10.0 + etas   * PROD_WATER_PER["water_plant"]

    # consumo diário aprox
    def count_by_tile(tile):
        return count_all(grid, tile)

    counts = {
        "residential": count_by_tile("residential"),
        "commercial":  count_by_tile("commercial"),
        "industrial":  count_by_tile("industrial"),
        "farm":        count_by_tile("farm"),
        "university":  count_by_tile("university"),
        "park":        count_by_tile("park"),
        "city_hall":   count_by_tile("city_hall"),
        "central_bank":count_by_tile("central_bank"),
        "police":      count_by_tile("police"),
        "hospital":    count_by_tile("hospital"),
    }

    power_use_day = sum(CONS_POWER_PER_DAY.get(k,0)*v for k,v in counts.items())
    water_use_day = sum(CONS_WATER_PER_DAY.get(k,0)*v for k,v in counts.items())

    power_use_inst = power_use_day + state.power_use_once
    water_use_inst = water_use_day + state.water_use_once

    state.power_pct = max(0.0, min(100.0, (state.power_cap - power_use_inst) / max(1.0, state.power_cap) * 100.0))
    state.water_pct = max(0.0, min(100.0, (state.water_cap - water_use_inst) / max(1.0, state.water_cap) * 100.0))

def update_happiness_daily(state: CityState, grid, connected_gids: Set[str], grid_size: int):
    target = grid_size*grid_size*0.6
    dens = state.population / max(1.0, target)
    superlot = max(0.0, (dens - 1.0)) * 1.0
    serv_pen = (max(0, 60 - state.power_pct)/60.0 + max(0, 60 - state.water_pct)/60.0) * 1.0
    pen_un = max(0.0, (state.unemployment - 5)/5.0) * 1.5
    pen_inf = max(0.0, (state.inflation - 6)/4.0) * 1.0
    pol_pen = state.polution_penalty
    parks = count_buildings_by_tile_connected(grid, connected_gids, "park")
    bonus_park = min(2.0, 0.2 * parks)
    delta = - (pen_un + pen_inf + serv_pen + superlot + pol_pen) + bonus_park
    state.happiness = max(0.0, min(100.0, state.happiness + delta))

def socio_env_hourly(state: CityState, grid, connected_gids: Set[str]):
    roads = count_all(grid, "road")
    inds  = count_all(grid, "industrial")
    blgts = count_all(grid, "blight")
    parks = count_all(grid, "park")
    state.polution_penalty = max(0.0, (inds*3 + blgts*2 + roads*0.05 - parks*0.5) / 20.0)

    police = count_buildings_by_tile_connected(grid, connected_gids, "police")
    base_crime = 5.0 + 0.5*state.unemployment + blgts*3.0 - police*8.0
    state.crime = max(0.0, min(100.0, 0.7*state.crime + 0.3*max(0.0, base_crime) + random.uniform(-1,1)))

    hospitals = count_buildings_by_tile_connected(grid, connected_gids, "hospital")
    health_base = 70 + hospitals*4 - state.polution_penalty*8 - (100-state.power_pct)/10 - (100-state.water_pct)/10
    state.health = max(0.0, min(100.0, 0.7*state.health + 0.3*health_base))

def income_tick_per_second(state: CityState, grid, connected_gids: Set[str]):
    com  = count_buildings_by_tile_connected(grid, connected_gids, "commercial")
    ind  = count_buildings_by_tile_connected(grid, connected_gids, "industrial")
    farm = count_buildings_by_tile_connected(grid, connected_gids, "farm")
    if (com + ind + farm) == 0: return

    demand_units = state.population // 5
    supply_units = com + 2*ind + 1*farm
    served = min(demand_units, supply_units)
    if served <= 0: return

    traffic_penalty = max(0.7, 1 - state.traffic/200.0)
    crime_penalty   = max(0.7, 1 - state.crime/150.0)
    health_bonus    = 0.9 + 0.1*(state.health/100.0)

    eff_base = (0.6 + 0.4 * state.happiness/100.0) \
             * (0.5 + 0.5 * state.power_pct/100.0) \
             * (0.5 + 0.5 * state.water_pct/100.0) \
             * traffic_penalty * crime_penalty * health_bonus

    denom = max(0.0003, (com + 2*ind + 1*farm) + 0.0003)
    share_com  = (com   + 0.0001) / denom
    share_ind  = (2*ind + 0.0001) / denom
    share_farm = (1*farm+ 0.0001) / denom

    f_lit  = 0.6 + 0.4*(state.literacy/100.0)
    f_ind  = 0.85 + 0.15*(state.literacy/100.0)
    f_farm = 0.7

    rate_per_min = served * BASE_UNIT_VALUE * eff_base * (share_com*f_lit + share_ind*f_ind + share_farm*f_farm)
    state.treasury_pending = min(state.treasury_cap, state.treasury_pending + rate_per_min/60.0)

def inflation_hourly(state: CityState, grid, connected_gids: Set[str]):
    com  = count_buildings_by_tile_connected(grid, connected_gids, "commercial")
    ind  = count_buildings_by_tile_connected(grid, connected_gids, "industrial")
    farm = count_buildings_by_tile_connected(grid, connected_gids, "farm")
    demand_index = state.population // 5
    supply_index = com + 2*ind + 1*farm
    gap = demand_index - supply_index
    a = 1.2
    b = 0.8 if count_buildings_by_tile_connected(grid, connected_gids, "central_bank")>0 else 0.0
    g = 0.2 * (farm/6.0)
    noise = (0.1 - 0.2*random.random()) + ((0.1 - 0.2*random.random()) if farm>0 else 0.0)
    delta = a*math.tanh(gap/10.0) - b - g + noise
    state.inflation = max(0.0, min(40.0, state.inflation + delta))

def upkeep_minutely(state: CityState, grid):
    roads = count_all(grid, "road")
    drain = 0
    drain += UPKEEP_PER_MIN["road"](roads)
    for key in ("central_bank","university","police","hospital","water_plant"):
        if count_all(grid, key): drain += UPKEEP_PER_MIN[key]
    if drain: state.money = max(0, state.money - drain)

def decay_oneoff_resources(state: CityState):
    state.power_use_once *= (1.0 - ONEOFF_DECAY_PER_HOUR/24.0)
    state.water_use_once *= (1.0 - ONEOFF_DECAY_PER_HOUR/24.0)
