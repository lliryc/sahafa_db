#!/bin/bash
cd flows
prefect deployment run 'GitHub Stars/github_stars_deployment' --param repos='["lliryc/media_agents"]'
  
#prefect deployment apply github_stars_deployment.yaml