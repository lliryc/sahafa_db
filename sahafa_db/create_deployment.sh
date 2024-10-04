#!/bin/bash

pip3 install prefect_aws
prefect work-pool ls | grep -q "default-work-pool" || (echo "Creating work pool 'default-work-pool'" && prefect work-pool create "default-work-pool")
cd flows
prefect deploy recording_flow.py:recording_flow \
#prefect deploy recording_flow.py:test_flow \
  -n "recording_flow_ae_az_ad_radio_studio1"  \
#  -n "test_flow"  \
  -p "default-work-pool" \
  -q "default" \
  --cron "0 */4 * * *" \
  --params '{"path": "media_guides/ae/ae-az/ad-radio", "program_key": "ad-radio-studio1"}'

# via prefect.yaml:
#prefect deploy -n github_stars_deployment 
