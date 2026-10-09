#!/usr/bin/env python3
"""The bytes this package is allowed to depend on.

Two sources are pinned: #207's frontier certificate (the row pair the ladder is priced
against, taken verbatim from that submission's head) and the whole of #219's rung-1
package under `references/pr219-run1/`, which supplies rung 1 itself, the interval-moment
engine and the 47-constraint assembly.  Everything else in this directory is the work of
this package.
"""
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDORED_RUN1 = 'references/pr219-run1'

OWN = ('ledger3.py', 'run3.py', 'schedule66.py', 'schedule66.json', 'prototype66.py',
       'pins.py', 'obligations.json',
       'references/pr207-coordinated-crossover.certificate.json')


def pinned_paths():
    """Every file whose bytes this package is pinned to, as relative paths."""
    own = list(OWN)
    vendored = sorted(str(p.relative_to(HERE)).replace('\\', '/')
                      for p in (HERE / VENDORED_RUN1).rglob('*') if p.is_file())
    assert vendored, 'the vendored rung-1 package must be present'
    return own + vendored


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    return {name: digest(HERE / name) for name in pinned_paths()}
