"""Path setup shared by the tools: vendored PR1186 toolkit on sys.path, IMB_ROOT = repository root (the toolkit resolves
audit_local.py, the multicold moment engines and PR589-EXPECTED.json from main through it)."""
import os, sys
from pathlib import Path
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
ROOT = PKG.parents[1]
os.environ.setdefault('IMB_ROOT', str(ROOT))
sys.path.insert(0, str(PKG / 'vendor' / 'exact-frame-toolkit'))
sys.path.insert(0, str(TOOLS))
INPUTS = PKG / 'inputs'
BASE = INPUTS / 'gauge44-word-566.json.gz'
EXTRA = INPUTS / 'extra-word-566.json.gz'
STEP0 = INPUTS / 'step0-gauge44.json.gz'
