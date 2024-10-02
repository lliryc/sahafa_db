#!/bin/bash
pip3 install prefect-aws
prefect work-pool ls | grep -q "default-work-pool" || (echo "Creating work pool 'default-work-pool'" && prefect work-pool create "default-work-pool")
cd flows
#prefect deploy recording_flow.py:github_stars \
#  -n "github_stars_deployment"  \
#  -p "default-work-pool" \
#  -q "default" \
#  --interval 300
  
# via prefect.yaml:
prefect deploy -n github_stars_deployment 
