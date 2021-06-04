#!/bin/sh
# Deploys the aws resources by processing a Cloudformation template and building a stack

sam deploy \
  --region us-west-2 \
  --template-file template.yml \
  --stack-name golem-fleet-battle-simulator-example \
  --capabilities CAPABILITY_IAM