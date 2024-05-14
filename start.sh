#!/bin/bash

# Start Docker if not already running
sudo systemctl start docker

# Check if Docker is running
if sudo systemctl is-active --quiet docker; then
    echo "Docker is running."
else
    echo "Failed to start Docker."
    exit 1
fi

# Change directory to /artifacts
cd artifacts
dir

docker-compose up -d
if [ $? -eq 0 ]; then
    echo "docker-compose ran successfully."
else
    echo "Failed to run docker-compose."
    exit 1
fi


sleep 10

python api.py