#!/usr/bin/env python3
"""Run frozen source with assertions intact, including direct spec-file loaders.

The outer wrapper may run under -O; every .py source inside private scratch is
compiled with optimize=0, without loading or creating mathematical bytecode.
"""
import sys
if not sys.flags.isolated:
    import posix
    posix.execv(sys.executable, [sys.executable, '-I',
        *(['-O'] * sys.flags.optimize), '-B', *sys.argv])
import importlib.machinery
from pathlib import Path
import os

sys.dont_write_bytecode = True
root = Path(sys.argv[1]).resolve()
engine = (root / sys.argv[2]).resolve()
if not root.is_dir() or not engine.is_file() or not engine.is_relative_to(root):
    raise ValueError('Engine outside private scratch')

_original_get_code = importlib.machinery.SourceFileLoader.get_code


def source_only_get_code(self, fullname):
    path = Path(self.path).resolve()
    if path.suffix == '.py' and path.is_relative_to(root):
        raw = self.get_data(self.path)
        return compile(raw, self.path, 'exec', dont_inherit=True, optimize=0)
    return _original_get_code(self, fullname)


# Patch the loader class itself: spec_from_file_location(...).loader.exec_module
# need not pass through sys.meta_path, so a meta-path finder alone is inadequate.
importlib.machinery.SourceFileLoader.get_code = source_only_get_code
sys.path.insert(0, str(engine.parent))
sys.argv = [str(engine), *sys.argv[3:]]
os.chdir(root)
exec(compile(engine.read_bytes(), str(engine), 'exec',
             dont_inherit=True, optimize=0),
     {'__name__': '__main__', '__file__': str(engine)})
