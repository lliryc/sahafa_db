SAHAFA_DIR=$(pwd)
export SAHAFA_DIR
docker compose --profile server --profile minio --profile worker down --remove-orphans