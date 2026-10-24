#!/usr/bin/env python3
"""Run an exact independent reviewer script with its assertions preserved.

Chris R / Clear1nsight; substantial OpenAI Codex assistance; Apache-2.0.
This adapter executes no candidate/predecessor evaluator. Explicit need/raise
checks remain active, and compile(optimize=0) preserves any source assertions.
"""
import sys
from pathlib import Path
p=Path(sys.argv[1]).resolve();sys.argv=sys.argv[1:];sys.path.insert(0,str(p.parent))
exec(compile(p.read_bytes(),str(p),'exec',optimize=0),{'__name__':'__main__','__file__':str(p)})
