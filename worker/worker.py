#!/usr/bin/env python3

import json
import uuid
import copy

from pathlib import Path
from typing import NamedTuple

from constants import MOD_OPERATOR_FUNCTIONS, UNIT_TYPE_SPECS

ENCODING = "utf-8"

FLEETS_PATH = Path("/golem/input/fleets.json")
RESULT_PATH = Path("/golem/output/result.json")

# FOR TESTING
#FLEETS_PATH = Path("../test/data/fleets.json")
#RESULT_PATH = Path("../test/data/result.json")


class FleetBattleResult(NamedTuple):
  """ Determines the result of a battle between two fleets """
  final_attacking_fleet_formation: dict
  final_attacking_fleet_unit_map: dict
  final_defending_fleet_formation: dict
  final_defending_fleet_unit_map: dict
  attacking_fleet_waves: list
  attacking_fleet_enemy_kills: int
  attacking_fleet_civilian_kills: int
  defending_fleet_enemy_kills: int
  defending_fleet_civilian_kills: int


def determine_battle_result(challenger_fleet, challengee_fleet):
  """ Determines the result of a battle between two fleets """

  # Save the initial state of the fleets
  initial = {
    'challenger': copy.deepcopy(challenger_fleet),
    'challengee': copy.deepcopy(challengee_fleet)
  }

  # Get the unit lookup tables for each fleet
  challenger_fleet_unit_map = challenger_fleet.get('manifest')
  challengee_fleet_unit_map = challengee_fleet.get('manifest')
  
  # Get the formations
  challenger_fleet_formation = challenger_fleet.get('formation')
  challengee_fleet_formation = challengee_fleet.get('formation')

   # Set initial values of all comsumable properties of all units in both fleets
  for unit_key in challenger_fleet_unit_map.keys():
    challenger_fleet_unit_map[unit_key]['health'] = UNIT_TYPE_SPECS[challenger_fleet_unit_map[unit_key]['type']]['stats']['health']
    challenger_fleet_unit_map[unit_key]['skip'] = UNIT_TYPE_SPECS[challenger_fleet_unit_map[unit_key]['type']]['stats'].get('skip', 0)
  for unit_key in challengee_fleet_unit_map.keys():
    challengee_fleet_unit_map[unit_key]['health'] = UNIT_TYPE_SPECS[challengee_fleet_unit_map[unit_key]['type']]['stats']['health']
    challengee_fleet_unit_map[unit_key]['skip'] = UNIT_TYPE_SPECS[challengee_fleet_unit_map[unit_key]['type']]['stats'].get('skip', 0)

  challenger_view_battle_result = process_fleet_to_fleet_action(
    attacking_fleet_formation=copy.deepcopy(challenger_fleet_formation), 
    attacking_fleet_unit_map=copy.deepcopy(challenger_fleet_unit_map), 
    defending_fleet_formation=copy.deepcopy(challengee_fleet_formation), 
    defending_fleet_unit_map=copy.deepcopy(challengee_fleet_unit_map), 
    attacking_fleet_is_challenger=True)

  challengee_view_battle_result = process_fleet_to_fleet_action(
    attacking_fleet_formation=copy.deepcopy(challengee_fleet_formation), 
    attacking_fleet_unit_map=copy.deepcopy(challengee_fleet_unit_map), 
    defending_fleet_formation=copy.deepcopy(challenger_fleet_formation), 
    defending_fleet_unit_map=copy.deepcopy(challenger_fleet_unit_map), 
    attacking_fleet_is_challenger=False)

  return {
    'initial': initial,
    'final': {
      'challenger': {
        'formation': challenger_view_battle_result.final_attacking_fleet_formation,
        'manifest': challenger_view_battle_result.final_attacking_fleet_unit_map,
      },
      'challengee': {
        'formation': challengee_view_battle_result.final_attacking_fleet_formation,
        'manifest': challengee_view_battle_result.final_attacking_fleet_unit_map
      }
    },
    'waves': {
      'challenger': challenger_view_battle_result.attacking_fleet_waves,
      'challengee': challengee_view_battle_result.attacking_fleet_waves
    },
    'score': {
      'challenger': {
        'kills': challenger_view_battle_result.attacking_fleet_enemy_kills,
        'civilians': challenger_view_battle_result.attacking_fleet_civilian_kills
      },
      'challengee': {
        'kills': challengee_view_battle_result.attacking_fleet_enemy_kills,
        'civilians': challengee_view_battle_result.attacking_fleet_civilian_kills,
      }
    },
    'winner': ('challenger' if challenger_view_battle_result.attacking_fleet_enemy_kills > challenger_view_battle_result.defending_fleet_enemy_kills else ('challengee' if challenger_view_battle_result.attacking_fleet_enemy_kills < challenger_view_battle_result.defending_fleet_enemy_kills else 'tie'))
  }



def process_fleet_to_fleet_action (attacking_fleet_formation, attacking_fleet_unit_map, defending_fleet_formation, defending_fleet_unit_map, attacking_fleet_is_challenger=True):
  """ Processes the interactions between two fleets in waves  """


  # We will save the results of each round as a wave
  waves = []
  defender_enemy_kills = 0
  defender_civ_kills = 0
  attacker_enemy_kills = 0
  attacker_civ_kills = 0

  # Go through each row in the attacking fleet. Starting with the front one.
  for atr_fl_row_idx, atr_fl_row in enumerate(attacking_fleet_formation):

    # We will save interactions between units in the wave
    interactions = []
  
    # Go through each row in the challengee fleet, front to back, with the same challenger fleet row.
    for dfr_fl_row_idx in range(len(defending_fleet_formation)):

      # Get a reversed row of the defender formation since they are coming AT the attacker fleet
      reversed_dfr_row = copy.deepcopy(defending_fleet_formation[dfr_fl_row_idx])
      reversed_dfr_row.reverse()

      # Go through each unit in the row and have them battle the unit in the same spot in the row
      for unit_idx, atr_fl_unit_id in enumerate(atr_fl_row):

        # Get the cooresponding unit in the defending fleet
        dfr_fl_unit_id = reversed_dfr_row[unit_idx]

        # Get data on both units via their ids
        atr_fl_unit = attacking_fleet_unit_map.get(atr_fl_unit_id, {})
        dfr_fl_unit = defending_fleet_unit_map.get(dfr_fl_unit_id, {})
      
        # Have the two ships battle and get their new states
        atr_fl_unit, dfr_fl_unit = process_unit_to_unit_action(atr_fl_unit, dfr_fl_unit)
        
        # Check for destroyed ships, count them, and remove them from the formations
        killed = None
        if (atr_fl_unit and atr_fl_unit['health'] <= 0):
          atr_fl_unit['health'] = 0
          defender_enemy_kills += 1
          defender_civ_kills += (1 if atr_fl_unit['type'] == 'civilian' else 0)
          attacking_fleet_formation[atr_fl_row_idx][unit_idx] = None
          killed = 'attacker'
        if (dfr_fl_unit and dfr_fl_unit['health'] <= 0):
          dfr_fl_unit['health'] = 0
          attacker_enemy_kills += 1
          attacker_civ_kills += (1 if dfr_fl_unit['type'] == 'civilian' else 0)
          dfr_unit_index = [dfr_unit_id for dfr_unit_id in defending_fleet_formation[dfr_fl_row_idx]].index(dfr_fl_unit_id)
          defending_fleet_formation[dfr_fl_row_idx][dfr_unit_index] = None
          killed = 'defender' if not killed else 'both'

        if (atr_fl_unit and dfr_fl_unit):
          interactions.append(
            {
              'attackerUnit': atr_fl_unit_id,
              'defenderUnit': dfr_fl_unit_id,
              'killed': killed
            }
          )

    waves.append(
      {
        'attackerRow': atr_fl_row_idx,
        'attackerFleet': {
          'manifest': attacking_fleet_unit_map,
          'formation': copy.deepcopy(attacking_fleet_formation)
        },
        'defenderFleet': {
          'manifest': defending_fleet_unit_map,
          'formation': copy.deepcopy(defending_fleet_formation)
        },
        'interactions': interactions
      }
    )

  return FleetBattleResult(
    final_attacking_fleet_formation=attacking_fleet_formation,
    final_attacking_fleet_unit_map=attacking_fleet_unit_map,
    final_defending_fleet_formation=defending_fleet_formation,
    final_defending_fleet_unit_map=defending_fleet_unit_map,
    attacking_fleet_waves=waves,
    attacking_fleet_enemy_kills=attacker_enemy_kills,
    attacking_fleet_civilian_kills=attacker_civ_kills,
    defending_fleet_enemy_kills=defender_enemy_kills,
    defending_fleet_civilian_kills=defender_civ_kills
  )
        


def process_unit_to_unit_action(unit1, unit2):
  """ Determines the result of a battle between two units """
  
  # If either unit doesn't exist, return both units unchanged
  if (not unit1 or not unit2):
    return (unit1, unit2)

  # Retrieve the stats of the two units
  unit1_stats = UNIT_TYPE_SPECS[unit1.get('type')]['stats']
  unit2_stats = UNIT_TYPE_SPECS[unit2.get('type')]['stats']
  
  # Calculate the base damage each unit could take
  unit1_damage = unit2_stats['base_dmg']
  unit2_damage = unit1_stats['base_dmg']

  # Check if either unit will avoid battle with a 'skip' 
  unit1_skips = unit1.get('skip')
  unit2_skips = unit2.get('skip')

  if unit1_skips > 0 or unit2_skips > 0:

    # If either unit can skip battle, decrement the skip property on both units
    unit1['skip'] = unit1_skips - 1 if unit1_skips > 0 else 0
    unit2['skip'] = unit2_skips - 1 if unit2_skips > 0 else 0

  else:
  
    # Calculate the attack modifier effects
    for attack_modifier in unit1_stats['modifiers']['attack']:
      if MOD_OPERATOR_FUNCTIONS[attack_modifier['operator']](unit2[attack_modifier['property']], attack_modifier['match']):
        unit2_damage = MOD_OPERATOR_FUNCTIONS[attack_modifier['action']['operator']](unit2_damage, attack_modifier['action']['value'])
    for attack_modifier in unit2_stats['modifiers']['attack']:
      if MOD_OPERATOR_FUNCTIONS[attack_modifier['operator']](unit1[attack_modifier['property']], attack_modifier['match']):
        unit1_damage = MOD_OPERATOR_FUNCTIONS[attack_modifier['action']['operator']](unit1_damage, attack_modifier['action']['value'])
        
    # Calculate the defense modifier effects
    for defense_modifier in unit1_stats['modifiers']['defense']:
      if MOD_OPERATOR_FUNCTIONS[defense_modifier['operator']](unit2[defense_modifier['property']], defense_modifier['match']):
        unit1_damage = MOD_OPERATOR_FUNCTIONS[defense_modifier['action']['operator']](unit1_damage, defense_modifier['action']['value'])
    for defense_modifier in unit2_stats['modifiers']['defense']:
      if MOD_OPERATOR_FUNCTIONS[defense_modifier['operator']](unit1[defense_modifier['property']], defense_modifier['match']):
        unit2_damage = MOD_OPERATOR_FUNCTIONS[defense_modifier['action']['operator']](unit2_damage, defense_modifier['action']['value'])
    
    # Set the new health values
    unit1_previous_health = unit1.get('health') or unit1_stats.get('health')
    unit2_previous_health = unit2.get('health') or unit2_stats.get('health')
    unit1['health'] = unit1_previous_health - unit1_damage
    unit2['health'] = unit2_previous_health - unit2_damage
  
  # Return the updated units
  return (unit1, unit2)





if __name__ == "__main__":
  result = ""

  with FLEETS_PATH.open() as f:
    fleets = json.load(f)
    result = determine_battle_result(challenger_fleet=fleets.get('challenger'), challengee_fleet=fleets.get('challengee'))
    
  with RESULT_PATH.open(mode="w", encoding=ENCODING) as f:
    json.dump(result, f)
