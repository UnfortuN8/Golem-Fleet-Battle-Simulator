import uuid
import pytz

from  datetime import datetime

from models.challenge import Challenge


def add_pending_fleet():
  """ Adds a new TEST challenge to the Challenge Table which already has both player's fleets in formation and is in the 'prepared' state. """

  # Create the challenge
  challenge = Challenge(id=str(uuid.uuid4()))

  # Set the creation time
  challenge.created = datetime.now(pytz.timezone('UTC'))

  # Add the challenge info
  challenge.name = 'Test Challenge'
  challenge.description = 'A test challenge created in the pending state'

  # Add the challenger info
  challenge_challenger = {}
  challenge.challenger_id = '1'
  challenge.challenger_name = 'Challenger'
  challenge.challenger_fleet = {"formation":[["1","2"],["3","4"],["5","6"],["7",None]],"manifest":{"7":{"type":"bomber"},"3":{"type":"bomber"},"4":{"type":"frigate"},"5":{"type":"bomber"},"1":{"type":"bomber"},"6":{"type":"frigate"},"2":{"type":"frigate"}}}

  # Add the challengee info
  challenge_challengee = {}
  challenge.challengee_id = '2'
  challenge.challengee_name = 'Challengee'
  challenge.challengee_fleet = {"formation":[["1","2"],["3","4"],["5","6"],["7",None]],"manifest":{"7":{"type":"frigate"},"3":{"type":"bomber"},"4":{"type":"bomber"},"5":{"type":"fighter"},"1":{"type":"bomber"},"6":{"type":"fighter"},"2":{"type":"bomber"}}}

  # Add the terms of the challenge
  challenge_terms = {}
  challenge.terms_units = 7
  challenge.terms_grid_width = 2
  challenge.terms_grid_height = 4
  challenge.terms_specials = None

  # Set the state
  challenge.state = 'prepared'

  # Save the challenge
  challenge.save()


if __name__ == "__main__":
  add_pending_fleet()
  