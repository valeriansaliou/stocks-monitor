#!/usr/bin/env sh

PARENT_DIR=$(dirname $(readlink -f "$0"))
cd $PARENT_DIR

# Initialize virtual environment
if [ ! -f "./env/bin/python" ]; then virtualenv -p /usr/bin/python env --system-site-packages; fi

# Install dependencies (retry in case of error)
./tools/setup.py install

if [ $? -eq 0 ]; then
    ./tools/setup.py install
fi

# Launch daemon
./tools/launch.py