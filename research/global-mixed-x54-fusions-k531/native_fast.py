"""Run upstream replay_native.py unchanged except the 'phases' script path (parallel, byte-identical output)."""
import os, sys
from pathlib import Path
rn = Path(sys.argv[1]).resolve()
src = rn.read_text()
old = "base/'code/phases_full.py'"
assert src.count(old) == 1
src = src.replace(old, "Path(os.environ['FAST_PHASES_IMPL'])")
sys.argv = [str(rn)] + sys.argv[2:]
exec(compile(src, str(rn), 'exec'), {'__file__': str(rn), '__name__': '__main__'})
