#!/bin/bash

# Confirm with the user before proceeding
read -p "Are you sure you want to stop the docker-compose service and delete neo4j data and logs (excluding .gitignore files)? [y/N] " response
if [[ "$response" != "y" && "$response" != "Y" ]]; then
    echo "Operation cancelled."
    exit 1
fi

# Stop docker-compose
docker-compose down

# Check if the neo4j directories exist before attempting to remove them, and preserve the .gitignore file
if [ -d "../neo4j/data" ]; then
    find ../neo4j/data -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +
else
    echo "Warning: ../neo4j/data directory not found!"
fi

if [ -d "../neo4j/logs" ]; then
    find ../neo4j/logs -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +
else
    echo "Warning: ../neo4j/logs directory not found!"
fi

echo "Neo4j data and logs deleted successfully."
