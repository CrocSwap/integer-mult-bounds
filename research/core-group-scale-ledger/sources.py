"""Authenticated allocation and literal Reference identity-hole branch only."""
import ast
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
from types import ModuleType

from ledger import need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE = 'research/rational-unitary-fft/gaussian_reference.py'
OUTER = 'research/unconditional-batched-crt/PROOF.md'
GAUSSIAN = 'research/unconditional-batched-crt/GAUSSIAN.md'
BRIDGE = 'retained/bridge/bridge_allocation.py'


def authenticate(overrides=None):
    rows = json.loads((HERE/'SOURCES.json').read_text())['files']
    raw = {}
    for row in rows:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']
        need(path.is_file() and not path.is_symlink(), 'regular live source input')
        body = (overrides or {}).get(row['path'], path.read_bytes())
        need(sha256(body).hexdigest() == row['sha256'], 'canonical source SHA256')
        need(sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == row['git_blob'],
             'canonical source Git blob')
        raw[row['path']] = body
    for row in json.loads((HERE/'DEPENDENCIES.json').read_text())['files']:
        path = HERE/row['retained_path']
        need(path.is_file() and not path.is_symlink(), 'regular retained public source')
        body = (overrides or {}).get(row['retained_path'], path.read_bytes())
        need(sha256(body).hexdigest() == row['sha256'], 'public bridge source SHA256')
        need(sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == row['git_blob'],
             'public bridge source Git blob')
        raw[row['retained_path']] = body
    return raw


def bridge(raw):
    module = ModuleType('_retained_scale_bridge')
    sys.modules[module.__name__] = module
    exec(compile(raw[BRIDGE], '<authenticated public bridge allocation>', 'exec', optimize=0),
         module.__dict__)
    return module


def hole_geometry(raw):
    tree = ast.parse(raw[REFERENCE])
    definitions = [deepcopy(x) for x in tree.body
                   if isinstance(x, (ast.FunctionDef, ast.ClassDef))
                   and x.name in ('nearest_up', 'ReferenceSpec', 'Entry', 'Coordinates', 'SelectedAddresses')]
    need(len(definitions) == 5, 'five original coordinate/entry definitions')
    original = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Reference')
    init = deepcopy(next(x for x in original.body if isinstance(x, ast.FunctionDef) and x.name == '__init__'))
    cuts = [i for i, x in enumerate(init.body) if isinstance(x, ast.Assign)
            and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                    and t.value.id == 'self' and t.attr == 'exp' for t in x.targets)]
    need(len(cuts) == 1, 'original pre-exponential constructor boundary')
    init.body = init.body[:cuts[0]]
    narrow = deepcopy(next(x for x in original.body if isinstance(x, ast.FunctionDef) and x.name == '_narrow'))
    projected = deepcopy(original)
    projected.name = 'HoleGeometry'
    projected.body = [init, narrow]
    definitions.append(projected)
    namespace = {'__name__': __name__, 'need': need, 'Q': Q, 'rational': Q, 'dataclass': dataclass}
    exec(compile(ast.fix_missing_locations(ast.Module(body=definitions, type_ignores=[])),
                 '<original geometry and full unchanged narrow method>', 'exec', optimize=0), namespace)
    return namespace['HoleGeometry'], sha256(ast.dump(projected, include_attributes=False).encode()).hexdigest()


def source_sites(raw):
    outer, gaussian = raw[OUTER].decode(), raw[GAUSSIAN].decode()
    markers = {
        'original_compression_target': 'P_s F_s = D N^-1 C P_t F_t S_gauss.',
        'existing_completed_normalizers': 'Normalize the completed S_gauss and D N^-1 C factors by dyadic powers',
        'existing_restoration': 'an accumulated compensating scale 2^gamma, gamma=O(d log p)=o(p).',
        'actual_global_axes': 'd=Theta(p^epsilon), epsilon=1-10^-30.',
    }
    for name, marker in markers.items():
        need(marker in outer, 'exact outer source site: '+name)
    more = {'per_axis_budget': 'Divide each completed per-axis map by a sufficient dyadic p^100 bound.',
            'group_scan': 'Combine the normalizers within group diagonals, with one scan per group.',
            'alpha_upper_bound': 'Eventually 4log(16p)<=a<=5log(16p).'}
    for name, marker in more.items():
        need(marker in gaussian, 'exact Gaussian source site: '+name)
    return list(markers)+list(more)
