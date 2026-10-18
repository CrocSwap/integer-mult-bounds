"""Resolve the exact exported predecessor, with candidate modules first."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
for path in (ROOT/'predecessor'/'vendor', ROOT/'predecessor', ROOT):
    path=str(path)
    if path in sys.path: sys.path.remove(path)
    sys.path.insert(0,path)

import sources
sources.ROOT=ROOT.parents[1]
