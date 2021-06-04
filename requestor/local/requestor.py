#!/usr/bin/env python3

import json
import asyncio

from datetime import datetime
from typing import NamedTuple

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
INPUT_PATH = Path("data/fleets.json")
OUTPUT_PATH = Path("data/result.json")

# Golem Executor args
NETWORK = "rinkeby"
SUBNET = "devnet-beta.1"
DRIVER = "zksync"
BUDGET = 0.1
TASK_TIMEOUT = timedelta(minutes=10)


def main():
  ''' 
  Use Golem to get the battle result
  '''

  print('RUNNING FLEET BATTLE SIMUATION WITH LOCAL INPUT FILE')
  
  loop = asyncio.get_event_loop()
  task = loop.create_task(run_golem())

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
  
  context.send_file(str(INPUT_PATH), str(FLEETS_PATH))

  async for task in tasks:
    
    context.run(str(ENTRYPOINT_PATH))

    output_file = NamedTemporaryFile()
    context.download_file(str(RESULT_PATH), output_file.name)
    yield context.commit()

    task.accept_result(result=json.load(output_file))
    output_file.close()



async def run_golem():

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
    async for task in executor.submit(steps, data(INPUT_PATH)):
      # Every task object we receive here represents a computed task
      if task.result:
        result = task.result
        break

    if result:
      print(f"GOLEM FLEET BATTLE RESULT: {result}")
      save_result(result)
    else:
      print("NO GOLEM BATTLE RESULT!")
      
      

def save_result(result):
  with open(str(OUTPUT_PATH), 'w') as outfile:
    json.dump(result, outfile)
  
  
if __name__ == "__main__":
  main()
    
