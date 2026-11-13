"""Fresh-source launcher for the retained binder or independent review."""
from pathlib import Path
import atexit
import runpy
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_IMPORT_CACHE = tempfile.TemporaryDirectory(prefix='literal-rounded-binding-')
atexit.register(_IMPORT_CACHE.cleanup)
prefix = Path(_IMPORT_CACHE.name) / 'required-absent'
if prefix.exists():
    raise ValueError('source import cache prefix must be absent')
sys.pycache_prefix = str(prefix)
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
target = HERE / 'bind_source.py'
if sys.argv[1:2] == ['--review']:
    sys.argv.pop(1)
    target = HERE / 'review/check_rounded_root.py'
runpy.run_path(str(target), run_name='__main__')
