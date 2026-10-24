"""Retiming of the pinned full-identity word; Apache-2.0, OpenAI Codex assistance.

The scalar order and free-operator words stay fixed. Every changed transport
is independently lowered as an exact Clifford, including its absolute phase.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT/'research/kappa-rebuild/complex/full-identity-certificates'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)

def span(basis):
    out = {0}
    for x in basis:
        out |= {v ^ x for v in tuple(out)}
    return frozenset(out)

def gates(program):
    phase = None
    counters = Counter()
    result = {}
    for i, e in enumerate(program):
        if e[0] == 'phase':
            phase = e[1]
        if e[0] == 'scalar':
            g = e[1]
            roles = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
            if all(r[0] == 'L' for r in roles):
                key = (phase, counters[phase])
                result[key] = i
                counters[phase] += 1
    return result

def dual(g):
    g = deepcopy(g)
    if g[0] == 'add':
        g[1], g[2] = g[2], g[1]
        g[3] *= -1
    else:
        need(g[0] == 'scale', 'Reversible persistent scalar')
        g[2], g[3] = g[3], g[2]
    return g

def synthesize(c, program):
    current = c['start'][:]
    out = []
    def climb(r, f):
        old = current[r]
        if old == f:
            return
        need(span(c['frames'][old]) < span(c['frames'][f]), 'Nested positive retimed transport')
        out.append(['climb', 'retimed', r, old, f, len(c['frames'][f])-len(c['frames'][old])])
        current[r] = f
    i = 0
    while i < len(program):
        e = deepcopy(program[i]); i += 1
        if e[0] == 'climb':
            continue
        if e[0] == 'center':
            second = program[i]
            need(second[0] == 'center' and e[1] == second[1] == 0 and e[3] == second[2], 'Original center split')
            need(sorted((e[4], second[4])) == [3, 5], 'Original 3+5 center')
            e = ['center', 0, e[2], second[3], 8]; i += 1
        if e[0] == 'scalar':
            g = e[1]
            roles = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
            for r in roles:
                if r[0] == 'L':
                    climb(r[1], e[2])
        elif e[0] == 'warp':
            need(e[1][0] == 'L', 'Persistent source warp')
            climb(e[1][1], e[3]); current[e[1][1]] = e[4]
        elif e[0] in ('adapter', 'residual_adapter'):
            # Helper wrappers are recomputed on the new whole-job boundaries.
            role = e[2] if e[0] == 'adapter' else e[2]
            if role >= 224:
                continue
        out.append(e)
    for r, f in enumerate(c['final']):
        climb(r, f)
    return out

def run(changes=None, phase_check=True):
    c = read(BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    original = read(BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    changes = read(HERE/'CHANGES.json') if changes is None else changes
    for key, frame_key in (('entrances', 'start'), ('exits', 'final')):
        seen = set()
        for role, old, new in changes[key]:
            need(role not in seen and 224 <= role < 632 and c[frame_key][role] == old, 'Bound unique helper boundary')
            seen.add(role); c[frame_key][role] = new
    maps = {d: gates(p) for d, p in original.items()}
    need(set(maps['forward']) == set(maps['backward']), 'Both scalar orientations have the same contact inventory')
    for key in maps['forward']:
        f = original['forward'][maps['forward'][key]]
        b = original['backward'][maps['backward'][key]]
        need(b[1] == dual(f[1]) and b[2] == f[2], 'Actual inverse-transpose scalar correspondence')
    changed = deepcopy(original)
    seen = set()
    for phase, ordinal, old, new in changes['gates']:
        key = (phase, ordinal)
        need(key not in seen and key in maps['forward'], 'Bound unique retimed scalar contact')
        seen.add(key)
        for d in changed:
            e = changed[d][maps[d][key]]
            need(e[2] == old, 'Original scalar frame pin')
            e[2] = new
    programs = {d: synthesize(c, p) for d, p in changed.items()}
    V = load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'fresh_boundary_rows')
    X = load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'fresh_boundary_literal')
    checks = {}
    profiles = {}
    for d, p in programs.items():
        rows, receipt = X.literal_replay(V, c, p, d == 'backward')
        for r in range(632):
            need(rows['L', r] == V.expected(('L', r), [], d == 'backward', False), 'Every actual arbitrary-input endpoint, role '+str(r))
        profiles[d] = Counter({int(k): v for k, v in receipt['paid_profile'].items()})
        rebound = deepcopy(c)
        rebound['local_profile'] = dict(profiles[d])
        receipt['second_literal'] = V.replay(p, rebound, [], d == 'backward', False)
        checks[d] = receipt
    need(profiles['forward'] == profiles['backward'], 'Same complete native tariff in both orientations')
    H = Counter()
    for r in range(224, 632):
        a, b = c['start'][r], c['final'][r]
        need(span(c['frames'][a]) <= span(c['frames'][b]), 'Nested productive helper boundary')
        width = len(c['frames'][b])-len(c['frames'][a])
        need(width > 0, 'Every declared helper is independently productive')
        H[width] += 1
    physical = []
    if phase_check:
        ce = load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py', 'fresh_boundary_clifford')
        P = load(ROOT/'research/kappa-function-composition/complex/prune_native.py', 'fresh_boundary_lowering')
        N = X.N
        old_edges = {(e[3], e[4]) for e in original['forward'] if e[0] == 'climb'}
        new_edges = {(e[3], e[4]) for e in programs['forward'] if e[0] == 'climb'}
        helper_edges = {(c['start'][r], c['final'][r]) for r in range(224, 632)}
        for a, b in sorted((new_edges-old_edges) | helper_edges):
            op = ce.canonical_frame(9, c['frames'][a]).adjoint().then(ce.canonical_frame(9, c['frames'][b]))
            want = len(c['frames'][b])-len(c['frames'][a])
            directions = {}
            for d in ('forward', 'backward'):
                actual = P.conjugate(ce, op) if d == 'backward' else op
                rec = N.lower_exact(P, ce, actual)
                need(rec['rank'] == want, 'New physical Fourier rank including phase')
                directions[d] = rec
            physical.append({'old': a, 'new': b, 'rank': want, 'recipes': directions})
    return {'status': 'PASS_RETIMED_BOTH_ORIENTATIONS_ALL_632_COLUMNS',
            'helpers': dict(sorted(H.items())), 'paid': dict(sorted(profiles['forward'].items())),
            'changed_entrances': len(changes['entrances']), 'changed_exits': len(changes['exits']),
            'changed_scalar_frames': len(changes['gates']), 'native': checks,
            'new_physical_edges_and_boundaries': physical}, c, programs

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--skip-phase', action='store_true'); p.add_argument('--write-result', action='store_true'); args = p.parse_args()
    result, _, _ = run(phase_check=not args.skip_phase)
    if args.write_result:
        need(not args.skip_phase, 'Do not replace a complete phase receipt with a diagnostic')
        (HERE/'NATIVE-RESULT.json.gz').write_bytes(gzip.compress((json.dumps(result, indent=2, sort_keys=True)+'\n').encode(),mtime=0))
    print(json.dumps({k: v for k, v in result.items() if k not in ('native', 'new_physical_edges_and_boundaries')}, sort_keys=True))
