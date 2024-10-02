#!/bin/bash
export SAHAFA_DIR=$(pwd)
docker compose run --entrypoint "sh ./create_deployment.sh" cli 
