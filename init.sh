#!/usr/bin/env sh

# Initialize virtual environment
if [ ! -f "./env/bin/python" ]; then virtualenv -p /usr/bin/python env --system-site-packages; fi

# Install dependencies
./tools/setup.py install

# Launch daemon
./tools/launch.py