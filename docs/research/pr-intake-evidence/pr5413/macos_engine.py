"""Maintainer-only Darwin resource compatibility, not a mathematical edit."""
import resource
import runpy
import sys
import json
import os

original = resource.setrlimit

def compatible_setrlimit(which, limits):
    try:
        return original(which, limits)
    except ValueError:
        if sys.platform != 'darwin' or which != resource.RLIMIT_AS:
            raise
        with open(os.environ['MAINTAINER_RLIMIT_TRACE'], 'a') as out:
            out.write(json.dumps({'pid': os.getpid(), 'argv': sys.argv,
                                  'rejected_RLIMIT_AS': list(limits),
                                  'fallback': 'external sampled descendant RSS guard'}) + '\n')

resource.setrlimit = compatible_setrlimit
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
