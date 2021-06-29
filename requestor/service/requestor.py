#!/usr/bin/env python3

import os
import os.path
import asyncio

from pathlib import Path

from yapapi import Golem
from yapapi.services import Service
from yapapi.log import enable_default_logger
from yapapi.payload import vm

# Golem args
NETWORK = "rinkeby"
SUBNET = "devnet-beta.2"
DRIVER = "zksync"
BUDGET = 0.1
MONITOR_INTERVAL_SEC = 5


class FleetBattleService(Service):
  INPUT_PATH = Path("data/fleets.json")
  OUTPUT_PATH = Path("data/result.json")
  FLEETS_PATH = Path("/golem/input/fleets.json")
  RESULT_PATH = Path("/golem/output/result.json")
  ENTRYPOINT_PATH = Path("/golem/entrypoint/worker.py")

  @staticmethod
  async def get_payload():
    return await vm.repo(
      image_hash="29a71cc7cdddfbfb911c04ac981296acae18651723516d58888fd01e",
      min_mem_gib=0.5,
      min_storage_gib=1.0,
    )

  async def start(self):
    print("*** STARTING SERVICE")
    yield self._ctx.commit()

  async def run(self):
    while True:

      # This causes the service to check for new data every second
      await asyncio.sleep(1)

      # Checks for a 'data/fleets.json' file.
      # If it exists, the service will process it, send back a 'data/result.json' file, and clean up the 'data/fleets.json' file.
      print("*** CHECKING FOR NEW DATA")
      if os.path.exists(str(self.INPUT_PATH)):

        print("*** SENDING FLEET DATA TO SERVICE")
        self._ctx.send_file(str(self.INPUT_PATH), str(self.FLEETS_PATH))

        # Run a battle simulation using the fleet data
        print("*** RUNNING SIM")
        self._ctx.run(str(self.ENTRYPOINT_PATH))

        # The battle simulation worker outputs its results to a file, 
        # so we need to download that file from the service provider to our local filesystem
        print("*** SAVING RESULT")
        self._ctx.download_file(str(self.RESULT_PATH), str(self.OUTPUT_PATH))

        # Wait for results
        future_results = yield self._ctx.commit()
        results = await future_results
        print(results)
        print("*** SIMULATION COMPLETE!")

        # Clean up the old processed fleet data
        try:
          os.remove(str(self.INPUT_PATH))
        except:
          print("*** FAILED TO REMOVE PROCESSED FLEET DATA")

      else:
        print("*** NO FLEET DATA FOUND... WAITING...")

      steps = self._ctx.commit()
      yield steps

  async def shutdown(self):
    print("*** SHUTTING DOWN SERVICE")
    yield self._ctx.commit()


def main():
  ''' 
  Use Golem to get the battle result
  '''

  print('RUNNING FLEET BATTLE SIMULATION SERVICE WITH LOCAL INPUT FILE')
  
  loop = asyncio.get_event_loop()
  task = loop.create_task(run_golem())

  # yapapi debug logging to a file
  enable_default_logger(log_file="yapapi.log")

  try:
    loop.run_until_complete(task)
  except KeyboardInterrupt:
    task.cancel()
    loop.run_until_complete(task)
    
    

async def run_golem():

  async with Golem(budget=BUDGET, subnet_tag=SUBNET) as golem:
    cluster = await golem.run_service(FleetBattleService, num_instances=1)

    print("*** CLUSTER IS UP!!!")
    print(cluster)

    # Monitor the service while it runs
    while True:
      for num, instance in enumerate(cluster.instances):
        print(f"Instance {num} is {instance.state.value} on {instance.provider_name}")
      await asyncio.sleep(MONITOR_INTERVAL_SEC)
      print("...")



if __name__ == "__main__":
  main()
    
