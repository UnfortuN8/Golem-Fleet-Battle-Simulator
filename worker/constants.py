
""" 
Lambda functions for each of the operators that are in the unit/ship specs 
"""
MOD_OPERATOR_FUNCTIONS = {
  '==': lambda a, b : a == b,
  '>': lambda a, b : a > b,
  '<': lambda a, b : a < b,
  '*': lambda a, b : a * b,
  '+': lambda a, b : a + b
}

""" 
Specs for all the types of units/ships that can be in a fleet. 
"""
UNIT_TYPE_SPECS = {
  "bomber": {
    "stats": {
      "health" : 100,
      "base_dmg": 100,
      "modifiers": {
        "attack": [
          {
            "property": "type",
            "operator": "==",
            "match": "frigate",
            "action": {
              "operator": "*",
              "value": 2
            }
          }
        ],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "frigate",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  },
  "fighter": {
    "stats": {
      "health" : 100,
      "base_dmg": 100,
      "modifiers": {
        "attack": [
          {
            "property": "type",
            "operator": "==",
            "match": "bomber",
            "action": {
              "operator": "*",
              "value": 2
            }
          }
        ],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "bomber",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  },
  "frigate": {
    "stats": {
      "health" : 100,
      "base_dmg": 100,
      "modifiers": {
        "attack": [
          {
            "property": "type",
            "operator": "==",
            "match": "fighter",
            "action": {
              "operator": "*",
              "value": 2
            }
          }
        ],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "fighter",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  },
  "civilian": {
    "stats": {
      "health" : 1,
      "base_dmg": 0,
      "modifiers": {
        "attack": [],
        "defense": []
      }
    }
  },
  "flack": {
    "stats": {
      "health" : 1,
      "base_dmg": 1000,
      "skip": 1,
      "modifiers": {
        "attack": [
          {
            "property": "type",
            "operator": "==",
            "match": "dreadnought",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "bomber",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "fighter",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "frigate",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "mine",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  },
  "slug": {
    "stats": {
      "health" : 999999,
      "base_dmg": 0,
      "skip": 1,
      "modifiers": {
        "attack": [
          {
            "property": "type",
            "operator": "==",
            "match": "dreadnought",
            "action": {
              "operator": "+",
              "value": 1000
            }
          }
        ],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "bomber",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "fighter",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "frigate",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "mine",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "slug_missile",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "flack_missile",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  },
  "mine": {
    "stats": {
      "health" : 1,
      "base_dmg": 1000,
      "modifiers": {
        "attack": [],
        "defense": []
      }
    }
  },
  "dreadnought": {
    "stats": {
      "health" : 1000,
      "base_dmg": 1000,
      "modifiers": {
        "attack": [],
        "defense": [
          {
            "property": "type",
            "operator": "==",
            "match": "bomber",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "fighter",
            "action": {
              "operator": "*",
              "value": 0
            }
          },
          {
            "property": "type",
            "operator": "==",
            "match": "frigate",
            "action": {
              "operator": "*",
              "value": 0
            }
          }
        ]
      }
    }
  }
}