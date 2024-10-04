#!/bin/bash
cd flows
prefect deployment run 'Recording flow/recording_flow_ae_az_ad_radio_studio1'

#prefect deployment apply github_stars_deployment.yaml