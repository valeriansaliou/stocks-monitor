#!/usr/bin/env python2

import os, sys


os.chdir(os.path.join(os.path.dirname(__file__), '../'))

args = sys.argv[1:] if len(sys.argv) > 1 else []
return_code = 1 if os.system('. ./env/bin/activate; ./src/main.py %s' % ' '.join(args)) else 0

sys.exit(return_code)