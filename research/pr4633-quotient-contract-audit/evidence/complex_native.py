#!/usr/bin/env python3
"""Audit every distinct quotient climb/helper edge with native Clifford lowering."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys

root = Path.cwd()
sys.path.insert(0, str(root/'research/kappa-rebuild/complex'))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, root/path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v = load('research/complex-ambient-quotient/verify.py', 'quotient_verify')
ce = load('research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'audit_ce')
p = load('research/kappa-function-composition/complex/prune_native.py', 'audit_lower')
n = load('research/kappa-rebuild/complex/rebuild_native.py', 'audit_native')
word = json.load(gzip.open('research/complex-ambient-quotient/QUOTIENT-WORD.json.gz'))
programs = json.load(gzip.open('research/complex-ambient-quotient/QUOTIENT-PROGRAMS.json.gz'))
blank = dict(word, precondition=[], A=[], B=[], cut=[], compensation=[], cleanup=[], tail=[])
edges = set()
for direction in ('forward', 'backward'):
    for event in v.F.synthesize(blank, programs[direction]):
        if event[0] == 'climb':
            edges.add((event[3], event[4], event[5]))
for role in range(224, 632):
    a, b = word['start'][role], word['final'][role]
    edges.add((a, b, len(word['frames'][b])-len(word['frames'][a])))
frames = {i: ce.canonical_frame(9, basis) for i, basis in enumerate(word['frames'])}
failures = []
for index, (a, b, expected) in enumerate(sorted(edges), 1):
    op = frames[a].adjoint().then(frames[b])
    for direction in ('forward', 'backward'):
        actual = p.conjugate(ce, op) if direction == 'backward' else op
        receipt = n.lower_exact(p, ce, actual)
        if receipt['rank'] != expected:
            failures.append([a, b, direction, expected, receipt['rank']])
    if index % 100 == 0:
        print('edges', index, '/', len(edges), 'rank failures', len(failures), flush=True)
result = dict(distinct_edges=len(edges), orientations=2, failures=failures,
              scope='All distinct synthesized climb and helper-boundary transports; exact rank and absolute-phase recipe decoding. Does not check the outer main-port contract.')
Path(__file__).with_name('complex-native-result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
raise SystemExit(bool(failures))
