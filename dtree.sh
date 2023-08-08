#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Append to the PYTHONPATH
export PYTHONPATH="$DIR:$PYTHONPATH"

# Run DiscussionTrees as a python program
python3 discussion_trees "$@"