#!/usr/bin/env python3
"""Ensure authenticated source execution cannot be replaced by cached bytecode."""
from pathlib import Path
import py_compile
import os
import tempfile
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent


def load(path, name):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def poison_cache(path, real_bytes):
    marker = b"raise RuntimeError('POISONED_CACHE_EXECUTED')\n"
    path.write_bytes(marker + b' ' * (len(real_bytes) - len(marker)))
    stamp = 1700000000
    os.utime(path, (stamp, stamp))
    py_compile.compile(str(path), doraise=True, invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    path.write_bytes(real_bytes)
    os.utime(path, (stamp, stamp))


def main():
    with tempfile.TemporaryDirectory(prefix='g20-free-frame-loader-') as folder:
        root = Path(folder)
        for name in ('verify.py', 'native_floor.py', 'review_geometry.py', 'review_distances.py'):
            (root / name).write_bytes((PACKAGE / name).read_bytes())
        poison_cache(root / 'native_floor.py', (PACKAGE / 'native_floor.py').read_bytes())
        poison_cache(root / 'review_geometry.py', (PACKAGE / 'review_geometry.py').read_bytes())
        primary = load(root / 'verify.py', 'primary_subject')
        native = primary.load_native()
        if not callable(native.native_graph):
            raise ValueError('Authenticated native source did not execute')
        independent = load(root / 'review_distances.py', 'independent_subject')
        if not callable(independent.catalogue):
            raise ValueError('Independent geometry source did not execute')
    print('PASS_AUTHENTICATED_SOURCE_IGNORES_TWO_POISONED_CACHES')


if __name__ == '__main__':
    main()
