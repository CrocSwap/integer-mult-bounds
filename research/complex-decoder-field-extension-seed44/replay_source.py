"""Replay exactly the PR968 facts used by this extension, with assertions enabled.

Original mathematical model and implementations: themilkman216, PR968;
prepared wrapper for @woklerx with substantial Codex assistance, Apache-2.0.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys

if not __debug__:raise SystemExit('predecessor assertions must be enabled')
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent
# Pairwise-era PR968 model; production verify.py ships the neighborhood enumerator.
source=here.parents[1]/'research/frame-pair-enumeration-production/baseline.py'
spec=importlib.util.spec_from_file_location('credited_pr968',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with contextlib.redirect_stdout(io.StringIO()) as captured:
    m.section_a()
    census,weights=m.section_b()
    orbit=m.section_c(weights)
    example=None
    for frame in m.frames_in(m.P112):
        pairs=m.frame_pair_solutions(m.FRAME0,list(frame))
        if pairs:
            example={'F1':list(frame),'pairs':pairs[0]}
            break
    if example is None:raise ValueError('missing attaining frame pair')
    chain=m.section_e([],example)
if m.FAILS:raise ValueError('predecessor replay failures: '+repr(m.FAILS))
print(json.dumps({'census':census,'d7_orbit':orbit,'chain':chain,'example':example,
                  'root_lines':m.LINES,'pairing_rows':m.NROW,'frame0':m.FRAME0,
                  'log':captured.getvalue().splitlines(),'scope':'Sections A/B/C and E with first exact frame pair; no full frame census, pricing or full original package replay.'},sort_keys=True))
