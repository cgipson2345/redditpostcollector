#!/bin/bash

# check for correct num of parameters
if [ $# -ne 2 ]; then
    echo "Usage: ./crawler.sh [num of json files] [num of posts]"
    exit 1
fi

# extract params
param1=$1
param2=$2

# execute the script with the params
python crawler.py "$param1" "$param2"

# make this script executable
chmod +x "$0"