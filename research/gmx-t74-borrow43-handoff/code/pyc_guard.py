"""Stale-bytecode guard (after PR2788, jeremydiviney: a verifier can execute a stale .pyc beside vendored sources instead of the authenticated source).
guard(root): reject any *.pyc or __pycache__ anywhere in the package tree (the manifest excludes them, so they would be unauthenticated).
selftest(): plant a stale unchecked-hash .pyc beside a copy of an authenticated source and show (a) guard rejects the tree, and (b) an interpreter run with a fresh
PYTHONPYCACHEPREFIX (what verify_release/verify.py set for every child) ignores the planted bytecode and runs the source."""
import os, py_compile, subprocess, sys, tempfile
from pathlib import Path


def stale(root):
    root = Path(root)
    return sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.suffix in ('.pyc', '.pyo') or p.name == '__pycache__')


def guard(root):
    found = stale(root)
    if found:
        raise SystemExit('stale bytecode in the package tree (unauthenticated): ' + ', '.join(found[:5]))


def selftest():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / 'src').mkdir()
        mod = t / 'src' / 'engine.py'
        mod.write_text("VALUE = 'authenticated source'\n")
        evil = t / 'evil.py'
        evil.write_text("VALUE = 'STALE BYTECODE'\n")
        cache = t / 'src' / '__pycache__'
        cache.mkdir()
        tag = sys.implementation.cache_tag
        py_compile.compile(str(evil), cfile=str(cache / ('engine.' + tag + '.pyc')), invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
        try:
            guard(t / 'src')
            raise SystemExit('pyc guard FAILED to reject a planted stale .pyc')
        except SystemExit as e:
            if 'stale bytecode' not in str(e):
                raise
        code = "import sys; sys.path.insert(0, %r); import engine; print(engine.VALUE)" % str(mod.parent)
        plain = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')).stdout.strip()
        pref = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(t / 'fresh-prefix'))).stdout.strip()
        if pref != 'authenticated source':
            raise SystemExit('PYTHONPYCACHEPREFIX did not isolate the stale .pyc: ' + pref)
        print('PYC-GUARD planted stale .pyc: tree guard rejected; plain interpreter ran %r; fresh-prefix interpreter ran %r' % (plain, pref), flush=True)


if __name__ == '__main__':
    selftest()
