#!/usr/bin/env python3

import boto3
import json
import uuid
import copy
import time
import pytz
import asyncio

from datetime import datetime
from typing import NamedTuple
from pynamodb.exceptions import DoesNotExist
from models.challenge import Challenge

from datetime import timedelta
from pathlib import Path
from typing import AsyncIterable, Iterator
from tempfile import NamedTemporaryFile

from yapapi import Executor, Task, WorkContext
from yapapi.log import enable_default_logger, log_event_repr, log_summary
from yapapi.package import vm


# Worker paths
FLEETS_PATH = Path("/golem/input/fleets.json")
RESULT_PATH = Path("/golem/output/result.json")
ENTRYPOINT_PATH = Path("/golem/entrypoint/worker.py")

# Data paths
DATA_PATH = Path("data/fleets.json")
OUTPUT_PATH = Path("data/result.json")

# Golem Executor args
NETWORK = "rinkeby"
SUBNET = "devnet-beta.1"
DRIVER = "zksync"
BUDGET = 0.1
TASK_TIMEOUT = timedelta(minutes=10)


def main():
  
  print('STARTING TO POLL FOR PREPARED CHALLENGES...')
  
  # Loop forever
  while True:
    
    try:
      
      print(f'POLLING!\n')

      # Get prepared challenges
      prepared_challenges = get_prepared_challenges()
      
      if prepared_challenges:
      
        # Get results using Golem
        get_results(prepared_challenges)

    except Exception as e:
      print(f'GENERAL ERROR: {e}')
      
    # Sleep for 10 seconds
    print(f'SLEEPING...\n\n')
    time.sleep(10) 
        


def get_prepared_challenges():
  ''' 
  Checks our challenge index for challenges in the 'prepared' state the search parameters and returns them
  '''
  
  # Query our index for matching challenges
  challenges_in_prepared_state = Challenge.state_index.query('prepared')

  print(f'PREPARED CHALLENGES: challenges_in_prepared_state')

  # Return the matching challenge models
  return challenges_in_prepared_state
  


def get_results(prepared_challenges):
  ''' 
  Get fleet battle results
  '''

  for challenge in prepared_challenges:
    
    if not challenge.result:
      
      print(f'CHALLENGE {challenge.id} NEEDS A RESULT')
      
      determine_battle_result_w_golem(
        challenge=challenge,
        challenger_fleet=copy.deepcopy(challenge.challenger_fleet),
        challengee_fleet=copy.deepcopy(challenge.challengee_fleet)
      )

    else:
      print(f'CHALLENGE {challenge.id} HAD RESULT')


####################
# GOLEM
####################


def determine_battle_result_w_golem(challenge, challenger_fleet, challengee_fleet):
  ''' 
  Use Golem to get the battle result
  '''
  
  with open(str(DATA_PATH), 'w') as outfile:
    json.dump({'challenger':challenger_fleet, 'challengee': challengee_fleet}, outfile)
  
  loop = asyncio.get_event_loop()
  task = loop.create_task(run_golem(challenge))

  # yapapi debug logging to a file
  enable_default_logger(log_file="yapapi.log")

  try:
    loop.run_until_complete(task)
  except KeyboardInterrupt:
    # Make sure Executor is closed gracefully before exiting
    task.cancel()
    loop.run_until_complete(task)
    
    
    
def data(fleets_file: Path) -> Iterator[Task]:
  """
  Return an iterator of `Task` objects.
  """
  with fleets_file.open() as f:
    yield Task(data=json.load(f))



async def steps(context: WorkContext, tasks: AsyncIterable[Task]):
  """Prepare a sequence of steps which need to happen for a task to be computed.
  `WorkContext` is a utility which allows us to define a series of commands to
  interact with a provider.
  Tasks are provided from a common, asynchronous queue.
  The signature of this function cannot change, as it's used internally by `Executor`.
  """
  
  context.send_file(str(DATA_PATH), str(FLEETS_PATH))

  async for task in tasks:
    
    context.run(str(ENTRYPOINT_PATH))

    output_file = NamedTemporaryFile()
    context.download_file(str(RESULT_PATH), output_file.name)
    yield context.commit()

    task.accept_result(result=json.load(output_file))
    output_file.close()



async def run_golem(challenge):

  # Set of parameters for the VM run by each of the providers
  package = await vm.repo(
    image_hash="29a71cc7cdddfbfb911c04ac981296acae18651723516d58888fd01e",
    min_mem_gib=1.0,
    min_storage_gib=1.0,
  )

  executor = Executor(
    package=package,
    max_workers=1,
    budget=BUDGET,
    network=NETWORK,
    driver=DRIVER,
    subnet_tag=SUBNET,
    event_consumer=log_summary(log_event_repr),
    timeout=TASK_TIMEOUT,
  )

  result = ""
  async with executor:
    async for task in executor.submit(steps, data(DATA_PATH)):
      # Every task object we receive here represents a computed task
      if task.result:
        result = task.result
        break

    if result:
      print(f"GOLEM BATTLE RESULT: {result}")
      set_result(result, challenge)
    else:
      print("NO GOLEM BATTLE RESULT.")
      
      

def set_result(result, challenge):
  challenge.result = result
  challenge.state = 'complete'
  challenge.golem_timestamp = datetime.now(pytz.timezone('UTC'))
  challenge.save(Challenge.state == 'prepared')
  print("RESULT SAVED")
  
  
if __name__ == "__main__":
  main()
    
