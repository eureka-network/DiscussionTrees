#!/bin/bash

# Project name (must match COMPOSE_PROJECT_NAME in .env)
PROJECT_NAME="dt_project"

# Get the directory of the current script
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go up to root directory
DIR="$( cd "$SCRIPTS_DIR/.." && pwd )"

# Change to root directory
cd "$DIR"

# Check if the neo4j service for the specific project is running
if ! docker-compose ps | grep -q "${PROJECT_NAME}_neo4j.*Up"; then
    echo "Starting docker-compose services..."
    docker-compose up -d
else
    echo "Docker-compose services are already running."
fi

# Check if conda environment 'dt' is activated, if not, activate it
if [[ "$CONDA_DEFAULT_ENV" != "dt" ]]; then
    echo "Activating conda environment 'dt'..."
    # Activate Conda environment. This assumes Conda is installed and 'dt' environment exists
    eval "$(conda shell.bash hook)"
    conda activate dt
else
    echo "Conda environment 'dt' is already activated."
fi

# Append to the PYTHONPATH
export PYTHONPATH="$DIR:$PYTHONPATH"

# Run DiscussionTrees as a python program
python3 discussion_trees "$@"
