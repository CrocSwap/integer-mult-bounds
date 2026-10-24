"""gxpaths.py: the paths of this repository for the scripts of tools/gx/ (written for the release;
the working copies of the scripts used absolute paths of the author's machine).

  HERE  tools/gx/                     the scripts
  GEN   tools/gen/                    foldlib.py, foldgen.py (rate search and Lean text of the rate lemmas), templates/
  OUT   output root, default tools/gx/out/ (ignored by git); set the environment variable GX_OUT to change it.
        The generators write OUT/Work/GCert/Data/... (the Lean modules, same relative paths as in the
        repository), OUT/logs/*.json (figures passed from gxgen.py to gxrate.py) and OUT/cmp/*.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE)) + '/'
GEN = REPO + 'tools/gen'
OUT = os.path.abspath(os.environ.get('GX_OUT', REPO + 'tools/gx/out')).rstrip('/') + '/'
for _p in (GEN, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
for _d in ('Work/GCert/Data/Gen', 'logs', 'cmp'):
    os.makedirs(OUT + _d, exist_ok=True)
