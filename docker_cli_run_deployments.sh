#!/bin/bash
export SAHAFA_DIR=$(pwd)
docker compose run --entrypoint "sh ./run_deployment.sh" cli 