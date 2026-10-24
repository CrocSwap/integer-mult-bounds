#!/usr/bin/env python3
"""Execute frozen assertion-based reviewer scripts without removing assertions.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
Explicit optimize=0 preserves their actual checks under the optimized wrapper.
Only independent census/precision scripts use this adapter; no candidate code.
"""
import sys,types
from pathlib import Path
p=Path(sys.argv[1]).resolve();sys.argv=sys.argv[1:];sys.path.insert(0,str(p.parent))
if p.name=='check_precision_5387.py':
 q=p.parent/'check_precision.py';m=types.ModuleType('check_precision');m.__file__=str(q);sys.modules['check_precision']=m
 exec(compile(q.read_bytes(),str(q),'exec',optimize=0),m.__dict__)
exec(compile(p.read_bytes(),str(p),'exec',optimize=0),{'__name__':'__main__','__file__':str(p)})
