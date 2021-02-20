import zero_ad
import math
from functools import partial
from string import Template
from os import path
import json
import numpy as np
import time

game = zero_ad.ZeroAD('http://127.0.0.1:6000')

scriptdir = path.dirname(path.realpath(__file__))
scenario_config_path = path.join(scriptdir, 'scenarios', 'CavalryVsSpearmen.json')
with open(scenario_config_path, 'r') as f:
    cav_vs_spearmen_scenario = f.read()

scenario_config_path = path.join(scriptdir, 'scenarios', 'CavalryVsSlingers.json')
with open(scenario_config_path, 'r') as f:
    cav_vs_slingers_scenario = f.read()

with open(path.join(scriptdir, 'templates','modifier.js'), 'r') as f:
    modifier = Template(f.read())

def set_cavalry_repeat_time(game, scale_factor):
    code = modifier.substitute(parameter='Attack/Ranged/RepeatTime', multiplier=scale_factor)
    game.evaluate(code)

def set_cavalry_prepare_time(game, scale_factor):
    code = modifier.substitute(parameter='Attack/Ranged/PrepareTime', multiplier=scale_factor)
    game.evaluate(code)

def set_cavalry_attack_speed(game, scale_factor):
    set_cavalry_prepare_time(game, scale_factor)
    set_cavalry_repeat_time(game, scale_factor)

def get_winner(state):
    return next(( i for (i, data) in enumerate(state.data['players']) if data['state'] == 'won' ))
    
def run_scenario(config, modifier, value):
    state = game.reset(config)
    modifier(game, value)
    chat = zero_ad.actions.chat(f'Testing with repeat time scaled by {value}')
    game.step([chat])

    while state.data['players'][1]['state'] == 'active':
        state = game.step()

    return get_winner(state)

def run_kiting_scenario(config, modifier, value):
    max_steps = 2000
    step_count = 0
    state = game.reset(config)
    modifier(game, value)
    chat = zero_ad.actions.chat(f'Testing with repeat time scaled by {value}')
    game.step([chat])

    while state.data['players'][1]['state'] == 'active':
        state = game.step([kite(state)])
        state = [game.step() for _ in range(4)].pop()
        step_count += 5
        if step_count > max_steps:
            print('Stopping scenario: Exceeded episode duration limit.')
            return 2

    return get_winner(state)

def center(units):
    positions = np.array([unit.position() for unit in units])
    return np.mean(positions, axis=0)

def enemy_offset(state):
    player_units = state.units(owner=1)
    enemy_units = state.units(owner=2)
    player_center = center(player_units)
    nearest_offset = None
    nearest_dist = math.inf
    for unit in enemy_units:
        offset = np.array(unit.position()) - player_center
        dist = np.linalg.norm(offset)
        if dist < nearest_dist:
            nearest_offset = offset
            nearest_dist = dist

    return nearest_offset

def unit_distance(unit, position):
    offset = np.array(unit) - position
    return np.linalg.norm(offset)

def retreat(state):
    units = state.units(owner=1)
    center_pt = center(units)
    offset = enemy_offset(state)
    enemy_angle = math.atan2(offset[0], offset[1])
    angle = enemy_angle + math.pi/4
    dist = 50
    y = dist * math.sin(angle)
    x = dist * math.cos(angle)
    rel_position = np.array([y, x])
    position = list(center_pt - rel_position)
    return zero_ad.actions.walk(units, *position)

def attack(state):
    units = state.units(owner=1)
    center_pt = center(units)

    enemy_units = state.units(owner=2)
    enemy_positions = np.array([unit.position() for unit in enemy_units])
    dists = np.linalg.norm(enemy_positions - center_pt, ord=2, axis=1)
    closest_index = np.argmin(dists)
    closest_enemy = enemy_units[closest_index]

    return zero_ad.actions.attack(units, closest_enemy)

is_retreating = False
def kite(state):
    global is_retreating
    dist = np.linalg.norm(enemy_offset(state))
    if is_retreating and dist < 60:
        return retreat(state)
    elif dist < 30:
        is_retreating = True
        return retreat(state)
    else:
        is_retreating = False
        return attack(state)

def find_boundary(test_fn, precision=0.1):
    lower = 0.0001
    upper = 1.
    print('testing', lower)
    winner = test_fn(lower)
    assert winner == 1
    print(f'finding upper bound... ({upper})')
    while test_fn(upper) == winner:
        lower = upper
        upper *= 2
        print(f'finding upper bound... ({upper})')

    print(f'found an upper bound: {upper}')
    while upper - lower > precision:
        value = (upper + lower)/2
        print('testing', value, f'({lower} - {upper})')
        if test_fn(value) == winner:
            lower = value
        else:
            upper = value

    return (upper + lower)/2, winner

print('----- Deathball -----')
boundary, lower_winner = find_boundary(partial(run_scenario, cav_vs_spearmen_scenario, set_cavalry_attack_speed))
winner = 'player' if lower_winner == 1 else 'opponent'
print(f'cavalry vs spearmen: {winner} wins if it is below {boundary}')

boundary, lower_winner = find_boundary(partial(run_scenario, cav_vs_slingers_scenario, set_cavalry_attack_speed))
winner = 'player' if lower_winner == 1 else 'opponent'
print(f'cavalry vs slingers: {winner} wins if it is below {boundary}')

print('----- Kiting -----')
boundary, lower_winner = find_boundary(partial(run_kiting_scenario, cav_vs_spearmen_scenario, set_cavalry_attack_speed))
winner = 'player' if lower_winner == 1 else 'opponent'
print(f'cavalry vs spearmen: {winner} wins if it is below {boundary}')

boundary, lower_winner = find_boundary(partial(run_kiting_scenario, cav_vs_slingers_scenario, set_cavalry_attack_speed))
winner = 'player' if lower_winner == 1 else 'opponent'
print(f'cavalry vs slingers: {winner} wins if it is below {boundary}')
