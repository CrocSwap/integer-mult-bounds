# SPDX-License-Identifier: Apache-2.0
# Adapted from PR3605; retained attribution in UPSTREAM-SOURCE-CREDITS.md.
import sys
if not __debug__ or sys.flags.optimize:
 raise RuntimeError("Enabled assertions required before owner replay")
"""Solver-independent integer primal check of the new aggregate owner flow.

Standard library only. Source geometry is read from the attributed frozen source
template through its retained window routine; literal copied owners are checked
separately. This certifies one finite primal, not LP optimality.
"""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,hashlib,os
if not __debug__:
 raise SystemExit('unoptimized Python required by retained owner engines')
HERE=Path(__file__).resolve().parent
if not os.environ.get('OWNER_SOURCE_REPO'):
 raise SystemExit('OWNER_SOURCE_REPO must identify the declared source checkout or export')
ROOT=Path(os.environ['OWNER_SOURCE_REPO']).resolve()
P=ROOT/'research/coupled-carrier-cap740'
# Authenticate every imported predecessor before executing any of its code.
_pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
for _rel,_digest in _pins['repo_files'].items():
 _path=ROOT/_rel
 if not _path.is_file() or _path.is_symlink() or hashlib.sha256(_path.read_bytes()).hexdigest()!=_digest:
  raise ValueError('stale retained source '+_rel)
import types
common=types.ModuleType('staged_owner_retained_common');common.__file__=str(P/'common.py')
exec(compile((P/'common.py').read_bytes(),common.__file__,'exec'),common.__dict__)
W=(4,5,6,7,8,9);INV=Counter(dict(zip(W,(26,2,18,52,97,213))))
LOCAL={1:2439,2:726,3:224,4:102,5:20,8:8}
