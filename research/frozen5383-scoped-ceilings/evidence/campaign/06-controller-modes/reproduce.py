#!/usr/bin/env python3
"""Recompute without mutating immutable producer receipts; about 15 seconds."""
import contextlib,importlib.util,io,json,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def strip_runtime(x):
 if isinstance(x,dict):return {str(k):strip_runtime(v) for k,v in x.items() if k not in ('runtime_seconds','feasibility_sha256')}
 if isinstance(x,list):return [strip_runtime(v) for v in x]
 return x
with tempfile.TemporaryDirectory(prefix='p16-modes-replay-') as tmp:
 t=Path(tmp)
 with contextlib.redirect_stdout(io.StringIO()):
  screen=load('screen').main(t/'feasibility.json'); exact=load('certify').main(t/'feasibility.json',t/'exact.json')
 assert strip_runtime(screen)==strip_runtime(json.loads((HERE/'FEASIBILITY-v1.json').read_text()))
 assert strip_runtime(exact)==strip_runtime(json.loads((HERE/'EXACT-SCREEN-v1.json').read_text()))
 print('PASS: exact 562-entry endpoint/invoice table and all1683 changed-allocation target signs reproduced; producer files untouched')
