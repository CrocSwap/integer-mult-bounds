# SPDX-License-Identifier: Apache-2.0
"""Opt-in physical-domain adapter for the pinned packing relaxation; no realizability claim.
Prepared by ywz65 with OpenAI Codex assistance.
"""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def exact(value, name):
    need(type(value) is int or type(value) is Q, name + ' must be an int or Fraction')
    return Q(value)

def inputs(local, m, families, stages, centre, R=None, unpaid=1, grid=Q(1, 10**15)):
    for name, value in [('m', m), ('families', families), ('stages', stages), ('unpaid', unpaid)]:
        need(type(value) is int, name + ' must be an integer')
    need(m >= 2 and families > 0 and stages > 0, 'positive width, families and stages')
    need(1 <= unpaid < m, 'unpaid coordinates must lie in [1,m)')
    centre = exact(centre, 'centre')
    need(centre >= 0, 'centre charge must be nonnegative')
    grid = exact(grid, 'grid')
    need(0 < grid <= Q(1, 20), 'grid must lie in (0,1/20]')
    need(isinstance(local, dict), 'local must be a rank-count mapping')
    for r, n in local.items():
        need(type(r) is int and 0 < r < m, 'local ranks must be integers in (0,m)')
        need(exact(n, 'count') >= 0, 'local counts must be nonnegative')
    if R is not None:
        need(type(R) is int and R >= 1 and 2 * R * R < m * m,
             'idle rank must be a positive integer satisfying the halving guard')
    mass = sum(r * Q(n) for r, n in local.items())
    need(mass <= (m - unpaid) * Q(families, stages) + centre, 'local mass exceeds coverage')
    return dict(local=local, m=m, families=families, stages=stages, centre=centre,
                R=R, unpaid=unpaid, grid=grid)

def implementation():
    source = 'research/complex-local-word-ceiling/ceiling.py'
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    row, = [r for r in rows if r['path'] == source]
    path = ROOT / source
    need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'calculator source drift')
    spec = importlib.util.spec_from_file_location('pinned_ceiling', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def ceiling(local, m, families, stages, centre, R=None, unpaid=1, grid=Q(1, 10**15)):
    checked = inputs(local, m, families, stages, centre, R, unpaid, grid)
    return implementation().ceiling(**checked)
