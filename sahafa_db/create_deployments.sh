
SAHAFA_DIR=$(pwd)
export SAHAFA_DIR
docker run -it --rm \
  -w /root \
  -v "${SAHAFA_DIR}:/root" \
  --network prefect-network \
  -e PREFECT_API_URL=http://server:4200/api \
  prefecthq/prefect:2.20.3-python3.11 \
prefect deploy -n github_stars_deployment -q default -p default-agent-pool flows/recording_flow.py:github_stars
