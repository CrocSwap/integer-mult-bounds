#!/usr/bin/env python3
"""Run dfd25d's Git-blob-pinned small stage fences on the e264 overlay."""
from fractions import Fraction
from hashlib import sha1
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
machine=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(machine))
sys.path.insert(1,str(HERE/'dfd'))
from upstream import install
install()
from installations import BINARY_C,DYADIC_ENDPOINT,PROFILES
assert BINARY_C==Fraction(287039844436133239,2**66)
assert PROFILES['dyadic-endpoint'] is DYADIC_ENDPOINT
for name,expected in {
    'check_stage_inventory.py':'69ced8d2018ad04c71e69e7aec524e1457549d14',
    'check_stage_fences.py':'f26151d58c78f98779f8408f5d6e9fe133f2615b',
    'STAGE-STORE.md':'8ee02945d5ce723df3e5171cdc2f0ef70b595ec3',
    'lean/StageStore.lean':'8c425a0e7580542ff4ee0d3734eea76bb02cf5b5',
}.items():
    data=(HERE/'dfd'/name).read_bytes()
    actual=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert actual==expected, name
runpy.run_path(str(HERE/'dfd'/'check_stage_fences.py'),run_name='__main__')
print('PASS_DFD_STAGE_FENCES_ON_E264_ENDPOINT',flush=True)
