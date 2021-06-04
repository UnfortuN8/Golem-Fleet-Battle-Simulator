import os
import json
import logging

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute, UTCDateTimeAttribute


logging.basicConfig()
log = logging.getLogger("pynamodb")
log.setLevel(logging.DEBUG)
log.propagate = True


class StateIndex(GlobalSecondaryIndex):
    """
    StateIndex global secondary index
    """
    class Meta:
      index_name = 'StateIndex'
      projection = AllProjection()

      # Ignored, but required due to a bug in pynamoDB
      # https://github.com/pynamodb/PynamoDB/issues/429
      read_capacity_units = 1
      write_capacity_units = 1

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    state = UnicodeAttribute(hash_key=True)


class Challenge(Model):
  """
  A DynamoDB Challenge Model
  """

  class Meta:
      table_name = f'golem-fleet-battle-simulator-example.Challenge'
      region = 'us-west-2'

  # Id
  id = UnicodeAttribute(hash_key=True)

  # Datetime the challenge was created
  created = UTCDateTimeAttribute()

  # Datetime the challenge was processed by golem
  golem_timestamp = UTCDateTimeAttribute(null=True)

  # Current State of the Challenge
  state = UnicodeAttribute(default='created')

  # The game type of the Challenge (vs, cpu)
  game_type = UnicodeAttribute(default='vs')

  # User Defined Name and Description
  name = UnicodeAttribute(default='Challenge')
  description = UnicodeAttribute(null=True)

  # Challenger
  challenger_id = UnicodeAttribute(null=True)
  challenger_name = UnicodeAttribute(null=True)
  challenger_token = UnicodeAttribute(null=True)
  challenger_fleet = JSONAttribute(null=True)
  
  # Challengee
  challengee_id = UnicodeAttribute(null=True)
  challengee_name = UnicodeAttribute(null=True)
  challengee_token = UnicodeAttribute(null=True)
  challengee_fleet = JSONAttribute(null=True)

  # Terms
  terms_units = NumberAttribute(null=True)
  terms_grid_width = NumberAttribute(null=True)
  terms_grid_height = NumberAttribute(null=True)
  terms_specials = JSONAttribute(null=True)
  terms_cpu_options = JSONAttribute(null=True)

  # Result
  result = JSONAttribute(null=True)

  # Indexes
  state_index = StateIndex()


