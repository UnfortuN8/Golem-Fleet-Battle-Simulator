
  
# Golem Fleet Battle Simulator

Golem Fleet Battle Simulator is a system for calculating the results of a battle between two opposing starship fleets on the Golem network and is used in the iOS game Rock Paper Frigate to determine the result of PvP fleet battles.

More information on Rock Paper Frigate can be found at [rockpaperfrigate.com](https://rockpaperfrigate.com)
 
<div align="center">
  <br/>
  <img src="https://rockpaperfrigate.com/img/rpf-formation-help.gif" align="center" alt="Bomber">
</div>


## Table of contents


*  [Fleet Battles Explained](#fleet-battles-explained)
*  [Project Structure](#project-structure)
*  [Setup](#setup)

  

## Fleet Battles Explained

  
In the game Rock Paper Frigate, players can challenge each other to starship fleet battles by choosing battle terms (such as number of ships per fleet and type of ships allowed), building a formation of ships, and then watching both fleets battle to determine a winner.

PvP in the game is designed to be played “in the background”, as a lot of progress depends on actions by the other player. A player might choose their formation right after accepting a challenge, but choose not to view the battle right away. This creates an opportunity for lazy calculation of battles via the Golem network!

Fleets can contain a single ship... or thousands! And there are currently 8 different types of ships, each with their own strengths, weaknesses, and abilities. Fleets battle by flying directly into each other, so one of the fleet formations will be rotated 180 degrees, and as both fleets fly through each other, opposing ships that collide will fight! The result of a 1 to 1 ship battle depends on both ships stats, and one, both, or neither ship may be destroyed. Non-destroyed ships will continue to fly with the fleet and may interact with more ships as the fleets continue to pass through one another. The fleet that destroys the most of their opponent's ships wins the battle.

Further complicating the battle calculation is that the simulation is run twice! Once for each player. This way of processing the battle doesn't change the final result, but let's each player watch the battle as if their fleet is the one attacking and in easy to follow "waves", instead of a messy, instantly concluding, explosion of ships smashing into each other!

  
  
<div align="center">
  <br/>
  <img src="https://rockpaperfrigate.com/img/fighter.gif" align="center" alt="Fighter">
</div>
  
  

## Project Structure


* docker - Folder containing a Dockerfile for a python:3.8.7-slim image with the worker code copied into it. Also contains scripts to build the worker image and upload it to the Yagna repository.

* requestor - Code for running requesters that send fleet data to Golem providers and retrieve battle results. There are 2 requestors in this directory, one that uses local files for input/output, and another that uses AWS DynamoDB.

* requestor/local - Requestor that reads a local file for input and outputs a file for the result.

* requestor/aws - Requestor that polls a dynamodb index looking for challenges with 'pending' battle results and saves the results back to the dynamodb table.

* requestor/service - Requestor that uses the Golem Service Model to vastly reduce latency. Also reads a local file for input and outputs a file for the result.

* worker - Code that is sent to providers in order to calculate battle results.

* worker/constants.py - All the ship types that can be placed in fleets and their stats.

* worker/worker.py - Worker code.


<div align="center">
  <br/>
  <img src="https://rockpaperfrigate.com/img/frigate.gif" align="center" alt="Frigate">
</div>

  

## Setup

A prerequisite to running this project is that the local environment is setup for Golem as a requestor. Refer to https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development for instructions.

  
### Building and Deploying the Worker Image

Providers need a image containing the worker code so they know how to run the battle simulation.

There's already an image built, uploaded, and set in the requester code, so this step is only necessary if you want to modify the worker code. Otherwise, feel free to skip this step.


1. From the top of project directory run:

-  `./docker/scripts/build_worker_image.sh `

2. Then to deploy the image to the Yagna repository run:

-  `./docker/scripts/deploy_worker_image.sh`

3. Note the "hash link" returned from the last command and set it to the image_hash property in the requestor.py code you want to run.

  
### Simulating a Fleet Battle via a Local Fleet File

The simplest way to run a fleet battle simulation is by using a fleet.json file as input for the simulation. When you run this example, a file located at `requestor/local/data/fleet.json` will be used as input for the simulation and a result will be saved at `requestor/local/data/result.json`.


1. Start by installing the requirements for this requestor script. From the project directory run (Note: You may want to install these dependancies within a virtual environment, but that's outside the scope of this example.):

-  `cd requestor/local`

-  `pip3 install -r requirements.txt`

2. With the dependancies installed, now you can run the requestor!

-  `python3 requestor.py`

3. When the script exits you should have just run a starship fleet battle simulation on the Golem Network! Everything that happened in the battle, as well as the final state of both fleets, should have been printed in the script output and saved to `requestor/local/data/result.json`


### Simulating Fleet Battles by Polling a DynamoDB Index for Un-Calculated Battles

This requester integrates with a AWS DynamoDB table and polls an index on the table to find challenges that have a battle that needs a result to be calculated. This is determined by if the challenge is in a 'prepared' state. If a prepared challenge is found, the fleet data is pulled from the table and a simulation is run on the Golem network. Once finished, the battle result is saved back to the challenge in the table and the challenge is set to the 'complete' state.


1. Start by installing the requirements for this requestor script. From the project directory run (Note: You may want to install these dependancies within a virtual environment, but that's outside the scope of this example.):

-  `cd requestor/aws`

-  `pip3 install -r requirements.txt`

  
2. This requestor requires a dynamodb table to be set up in AWS. This means you'll need an AWS account, an environment with credentials to the account, and permission to create cloudformation stacks and dynamodb tables. AWS setup is outside the scope of this readme however, so you may want to check out https://aws.amazon.com to learn how to get started with AWS.
 

3. If you do have a correctly setup AWS envronment, this project has a cloudformation template that will create the dynamodb table and index you need to run this requestor. To create a stack called `golem-fleet-battle-simulator-example` with a single dynamodb table, go to the`requestor/aws` directory and run:

-  `./deploy_aws.sh`

3. Now you should have an empty dynamodb table called `golem-fleet-battle-simulator-example.Challenge` in AWS. You may want to open a browser to the AWS console to view the table for the next steps.  

4. Time to run the requestor. Once you do, it will start polling your dynamodb index and looping every 10 seconds.

-  `python3 requestor.py`

5. We both know that its hitting an empty table. So in a separate terminal, run this helper script to add a 'prepared' challenge to your table and kick off your requester.

-  `python3 add_pending_challenge.py`

6. In a few seconds, you should see your requestor script detect the new challenge via the index, pull the challenge's fleet data, calculate the battle result via the Golem network, and save the result back into the challenge in dynamodb.


### Simulating a Fleet Battle via a Local Fleet File using the Service Model

Another way of processing fleet battles on Golem is using the Service Model. Requestors using this model can setup a service on the network that runs continuously and can accept and process work immediately with little latency.

This requestor uses the same input and output files as the 'local' requestor.  When you run this example, a file located at `requestor/service/data/fleet.json` will be used as input for the simulation and a result will be saved at `requestor/service/data/result.json`.


1. Start by installing the requirements for this requestor script. From the project directory run (Note: You may want to install these dependancies within a virtual environment, but that's outside the scope of this example.):

-  `cd requestor/service`

-  `pip3 install -r requirements.txt`

2. With the dependancies installed, now you can run the requestor!

-  `python3 requestor.py`

3. The requestor will setup a service on 1 provider and then monitor the service. You will start to see log statrements saying 'NO FLEET DATA FOUND... WAITING...'.

4. The service is now waiting for data to be sent to it to process. To generate some fleet data, open another shell terminal at the same directory and run:

-  `./add_new_fleet_data.sh`

5. The script will copy the file at `data/example_fleets.json` to `data/fleets.json`, the place where the requestor is looking for data, and you should see the previous terminal running the requestor detect the data. The service will then process the fleet data and a result will be saved at `requestor/service/data/result.json`.

6. Since this requestor setup a service, you'll see that the provider is still up and ready for more data! If you would like to send it more, simply run `./add_new_fleet_data.sh` again, or edit the `data/example_fleets.json` file before you do, to change the fleets and get different results!
