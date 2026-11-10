"""Authenticate and project only exact source geometry, never Gaussian values.

The retained Reference constructor prefix, interior method, Core.partition and
carve bodies are compiled unchanged from their pinned syntax trees. No ideal
Gaussian, dense solve, numerical Core or tape execution is asserted here.
"""
import ast
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
from types import SimpleNamespace

from guard import need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE = 'research/rational-unitary-fft/gaussian_reference.py'
CORE = 'research/rational-unitary-fft/core.py'
CARVE = 'research/capped-phase-fusion/evidence/gaussian_fast_ultra/check_capped_gauges.py'


def authenticate(overrides=None):
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    raw = {}
    for row in rows:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        need(path.is_file() and not path.is_symlink(), 'regular source input')
        body = (overrides or {}).get(row['path'], path.read_bytes())
        need(sha256(body).hexdigest() == row['sha256'], 'exact source SHA256: ' + row['path'])
        need(sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() == row['git_blob'],
             'exact source Git blob: ' + row['path'])
        raw[row['path']] = body
    return raw


def bind(overrides=None):
    raw = authenticate(overrides)
    reference = ast.parse(raw[REFERENCE])
    selected = [deepcopy(x) for x in reference.body
                if isinstance(x, (ast.FunctionDef, ast.ClassDef))
                and x.name in ('nearest_up', 'ReferenceSpec', 'Coordinates', 'SelectedAddresses')]
    need(len(selected) == 4, 'exact four source geometry definitions')
    original = next(x for x in reference.body if isinstance(x, ast.ClassDef) and x.name == 'Reference')
    init = deepcopy(next(x for x in original.body if isinstance(x, ast.FunctionDef) and x.name == '__init__'))
    cuts = [i for i, x in enumerate(init.body) if isinstance(x, ast.Assign)
            and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                    and t.value.id == 'self' and t.attr == 'exp' for t in x.targets)]
    need(len(cuts) == 1 and cuts[0] > 10, 'exact pre-exponential source constructor prefix')
    init.body = init.body[:cuts[0]]
    interior = deepcopy(next(x for x in original.body if isinstance(x, ast.FunctionDef) and x.name == 'interior'))
    geometry = deepcopy(original)
    geometry.name = 'Geometry'
    geometry.body = [init, interior]
    selected.append(geometry)
    core = ast.parse(raw[CORE])
    core_class = next(x for x in core.body if isinstance(x, ast.ClassDef) and x.name == 'Core')
    partition = deepcopy(next(x for x in core_class.body if isinstance(x, ast.FunctionDef) and x.name == 'partition'))
    carve_tree = ast.parse(raw[CARVE])
    carve = deepcopy(next(x for x in carve_tree.body if isinstance(x, ast.FunctionDef) and x.name == 'carve'))
    selected += [partition, carve]
    module = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
    namespace = {'__name__': __name__, 'need': need, 'Q': Fraction,
                 'rational': Fraction, 'dataclass': dataclass}
    exec(compile(module, '<authenticated production geometry projection>', 'exec', optimize=0), namespace)
    def run(source_size, excess, start, length, width, cap):
        # Only original geometry is constructed. Numerical source constructor
        # continuation is deliberately outside this projection's claimed scope.
        reference = namespace['Geometry']({}, source_size, excess, 1, 0, 0, 8)
        shell = SimpleNamespace(reference=reference, n=length,
                                coordinates=tuple(range(start, start + length)),
                                width=width, cap=cap, carve=namespace['carve'])
        pieces, cells = namespace['partition'](shell)
        return reference, pieces, cells
    return run, {name: sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
                 for name, node in [('reference_geometry', geometry), ('partition', partition), ('carve', carve)]}
