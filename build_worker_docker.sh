#!/bin/bash

docker build -t chelliryc/sahafa_prefect_worker:v0.2.0  -f Dockerfile-worker .

docker push chelliryc/sahafa_prefect_worker:v0.2.0
