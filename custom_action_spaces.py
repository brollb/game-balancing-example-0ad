from zero_ad_rl.env.base import ZeroADEnv
from ray.tune.registry import register_env
from zero_ad_rl.train import create_parser, run
from zero_ad_rl.env import scenarios

import zero_ad
from zero_ad_rl.env.base import ActionBuilder, RewardBuilder
from gym.spaces import Discrete
import numpy as np
import math

def center(units):  # Helper method that we will use later!
    positions = np.array([ unit.position() for unit in units ])
    return np.mean(positions, axis=0)

class AttackMove(ActionBuilder):
    def __init__(self):
        space = Discrete(5)
        super().__init__(space)  

    def to_json(self, action_index, state):
        if action_index == 4:
            return self.attack(state)
        else:
            circle_ratio = action_index/4
            return self.move(state, 2 * math.pi * circle_ratio)  # FIXME: update the blog

    def move(self, state, angle):
        units = state.units(owner=1)
        center_pt = center(units)
        distance = 15
        offset = distance * np.array([math.cos(angle), math.sin(angle)])
        position = list(center_pt + offset)

        return zero_ad.actions.walk(units, *position)

    def attack(self, state):
        units = state.units(owner=1)
        center_pt = center(units)

        enemy_units = state.units(owner=2)
        enemy_positions = np.array([unit.position() for unit in enemy_units])
        dists = np.linalg.norm(enemy_positions - center_pt, ord=2, axis=1)
        closest_index = np.argmin(dists)
        closest_enemy = enemy_units[closest_index]

        return zero_ad.actions.attack(units, closest_enemy)

from zero_ad_rl.env.base import StateBuilder
import numpy as np
from gym.spaces import Box

def center(units):
    positions = np.array([ unit.position() for unit in units ])
    return np.mean(positions, axis=0)

class EnemyDisplacement(StateBuilder):
    def __init__(self):
        space = Box(-1., 1., shape=(2,), dtype=np.float32)
        super().__init__(space)

    def from_json(self, state):
        player_units = state.units(owner=1)
        enemy_units = state.units(owner=2)
        if len(enemy_units) == 0 or len(player_units) == 0:
            return np.array([1, 1])

        max_distance = 80
        displacement = center(enemy_units) - center(player_units)
        # Normalize (and make sure we handle any states where there are no units for one team)
        normalized_displacement = displacement/max_distance
        return np.array([ min(d, 1.) for d in normalized_displacement ])

# TODO: Explore reward shaping?
from zero_ad_rl.env.base import RewardBuilder, WinLoseReward
class DamageDifference(RewardBuilder):
    def __init__(self, caution=4.0):
        self.enemy_count = None
        self.player_count = None
        self.caution = caution

    def reset(self, state):
        player_units = state.units(owner=1)
        enemy_units = state.units(owner=2)
        self.enemy_count = len(enemy_units)
        self.player_count = len(player_units)

    def __call__(self, prev_state, state):
        player_units = state.units(owner=1)
        enemy_units = state.units(owner=2)

        damage_dealt = sum(( enemy.health(ratio=True) for enemy in enemy_units )) / self.enemy_count
        damage_received = sum(( player.health(ratio=True) for player in player_units )) / self.player_count

        return damage_dealt - (self.caution * damage_received)

from itertools import repeat

class SumRewards(RewardBuilder):
    def __init__(self, *builders, weights=repeat(1)):
        self.rewards = builders
        self.weights = weights

    def reset(self, state):
        for reward in self.rewards:
            reward.reset(state);

    def __call__(self, prev_state, state):
        reward = sum( weight*reward_fn(prev_state, state) for (weight, reward_fn) in zip(self.weights, self.rewards) )
        return reward

reward_builder = SumRewards(DamageDifference(), WinLoseReward(), weights=(1, 5))
address = 'http://127.0.0.1:6000'
scenario_config = scenarios.load_config('CavalryVsInfantry')
register_env('CavVsInfDirections', lambda c: ZeroADEnv(address, scenario_config, AttackMove(), EnemyDisplacement(), reward_builder))

parser = create_parser()
args = parser.parse_args()
run(args, parser)
