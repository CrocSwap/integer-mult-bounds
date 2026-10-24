#!/usr/bin/env python3
"""PR4633 endpoint audit; Apache-2.0, substantial OpenAI Codex assistance.

Exact finite geometry and contract checks. All float roots are pricing screens.
No new kappa, physical lowering or complete outer admission is claimed.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    pins = read(HERE/'SOURCES.json')['files']
    for row in pins:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']; raw = path.read_bytes()
        need(not path.is_symlink(), 'Source alias')
        need(sha256(raw).hexdigest() == row['sha256'], 'Source SHA256: '+row['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'Source Git blob')
    vendors = read(HERE/'VENDORED.json')['files']
    for row in vendors:
        path = HERE/row['local_path']; raw = path.read_bytes()
        need(not path.is_symlink(), 'Vendored source alias')
        need(sha256(raw).hexdigest() == row['sha256'], 'Vendored source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'Vendored original Git blob')
    return sum(row['usage'] == 'input' for row in pins)+len(vendors)


def rational_basis(vectors):
    pivots, kept = {}, []
    for vector in vectors:
        row = list(map(Q, vector))
        for p, basis in sorted(pivots.items()):
            amount = row[p]; row = [x-amount*y for x, y in zip(row, basis)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            scale = row[p]; pivots[p] = [x/scale for x in row]; kept.append(vector)
    return kept


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def histogram(values):
    return {str(k): v for k, v in sorted(Counter(values).items())}


def bit_contract(frames, start, final):
    bad = []
    for p in range(111):
        P, X, Y0, Y = [frames[f] for f in (start[p], final[p], start[111+p], final[111+p])]
        if [len(rational_basis(F)) for F in (P, X, Y0, Y)] != [1, 8, 0, 7] or len(rational_basis(P+Y)) != 8:
            bad.append(p)
    return bad


def binary_contract(frames, start, final, ports, ambient):
    bad, widths, intersections = [], [], []
    for p in range(ports):
        P, X, Y0, Y = [span(frames[f]) for f in (start[p], final[p], start[ports+p], final[ports+p])]
        d = lambda F: len(F).bit_length()-1
        widths.extend((d(X)-d(P), d(Y)-d(Y0))); intersections.append(d(P & Y))
        if [d(P), d(X), d(Y0), d(Y)] != [1, ambient, 0, ambient-1] or P & Y != {0}:
            bad.append(p)
    return {'accepted': ports-len(bad), 'rejected': len(bad),
            'main_widths': histogram(widths), 'intersection_dimensions': histogram(intersections)}


def validate_binary_frames(artifact):
    F = artifact['frame_bases']; dims = {int(f): d for f, d in artifact['frame_dims'].items()}
    need(set(dims) == set(range(len(F))), 'Complete frame dimensions')
    for f, basis in enumerate(F):
        need(all(isinstance(v, int) and 0 < v < 256 for v in basis), 'Eight binary axes')
        need(len(span(basis)) == 2**len(basis) and len(basis) == dims[f], 'Frame basis and dimension')
    for op, x, old, new, rank, z in artifact['records']:
        if op == 0:
            need(span(F[old]) <= span(F[new]), 'Nested MOVE')
            need(rank == dims[new]-dims[old] >= 0, 'Actual MOVE rank')


def rejected(fn):
    try:
        fn()
    except (ValueError, AssertionError):
        return True
    return False


def run():
    pins = authenticate()
    B = load(HERE/'vendor/bit-ambient-quotient/build.py', 'audit4633_builder')
    B.SOURCE = BIT  # Bind the unchanged vendored builder to its original source inputs.
    V = load(HERE/'vendor/bit-ambient-quotient/verify.py', 'audit4633_logical_replay')
    source = read(BIT/'WORD.json.gz'); raw = read(BIT/'records/frames.json')['frames']
    rational = {int(f): row['B'] for f, row in raw.items()}; ds = {int(f): row['dim'] for f, row in raw.items()}
    records = list(struct.iter_unpack('<6i', (BIT/'records/249-records.bin').read_bytes()))
    need(not bit_contract(rational, source['start'], source['final']), 'All 111 rational source ports')
    profiles = [V.replay(records, source['start'], source['final'], ds, reverse)[0] for reverse in (False, True)]
    need(profiles[0] == profiles[1] == V.LOCAL, 'Source logical map and complete invoice')
    reduced = {int(f): sorted(B.dedupe(B.frame_vectors(row['A']))) for f, row in raw.items()}
    mod2_source = binary_contract(reduced, source['start'], source['final'], 111, 8)
    need(mod2_source['accepted'] == 8, 'GF(2) reduction loses 103 rational complements')
    roots = [rational[source['start'][p]][0] for p in range(111)]
    need(len({tuple(v) for v in roots}) == 111, 'Distinct rational entrance representatives')
    need(len({span(reduced[source['start'][p]]) for p in range(111)}) == 22, '22 reduced entrance lines')
    u = roots[8]; normal = raw[str(source['final'][111+8])]['A'][0]
    dot = sum(a*b for a, b in zip(u, normal))
    need(dot == 4 and dot % 2 == 0, 'Rational complement becomes binary containment')
    quotient_rows = {}
    for name, artifact in [('headline_kernel_150', B.build([150])),
                           ('submitted_kernel_150_102_255', read(HERE/'vendor/bit-ambient-quotient/QUOTIENT-BIT-WORD.json.gz'))]:
        validate_binary_frames(artifact); dims = {int(f): d for f, d in artifact['frame_dims'].items()}
        replay = [V.replay(artifact['records'], artifact['start'], artifact['final'], dims, reverse)[0] for reverse in (False, True)]
        need(replay[0] == replay[1], 'Both quotient logical directions')
        contract = binary_contract(dict(enumerate(artifact['frame_bases'])), artifact['start'], artifact['final'], 111, 8)
        need(contract['rejected'] == 111, 'No BIT port satisfies the block-7 call')
        main_mass = sum(dims[artifact['final'][r]]-dims[artifact['start'][r]] for r in range(222))
        helper_mass = sum(dims[artifact['final'][r]]-dims[artifact['start'][r]] for r in range(222, 661))
        copy_mass = sum(abs(dims[c]-dims[f]) for op, x, y, c, f, z in artifact['records'] if op == 2)
        paid_mass = V.rank_mass(replay[0])
        need(paid_mass == main_mass+helper_mass+copy_mass, 'MOVE telescope plus owned COPY cost')
        T, P, surplus, _ = V.invoice({8: 439}, replay[0])
        quotient_rows[name] = {**contract, 'kernel': artifact['kernel_basis'], 'logical_replay': True,
            'paid_mass': paid_mass, 'main_mass': main_mass, 'helper_mass': helper_mass,
            'copy_mass': copy_mass, 'mispriced_surplus': surplus, 'mispriced_float_screen': V.admissible_kappa(T, P)}
    # Any monotone frame contraction fixing all entrance lines fixes every source frame.
    lower, upper_codim = {}, {}
    normals = [raw[str(source['final'][111+p])]['A'][0] for p in range(111)]
    for f, row in raw.items():
        need(len(rational_basis(row['B'])) == row['dim'] and
             len(rational_basis(row['A'])) == 8-row['dim'], 'Source rational frame ranks')
        need(all(sum(a*b for a, b in zip(n, u)) == 0 for n in row['A'] for u in row['B']),
             'Source rational kernel and image agree')
        inside = [u for u in roots if all(sum(a*b for a, b in zip(n, u)) == 0 for n in row['A'])]
        lower[int(f)] = len(rational_basis(inside))
        containing = [n for n in normals if all(sum(a*b for a, b in zip(n, u)) == 0 for u in row['B'])]
        upper_codim[int(f)] = len(rational_basis(containing))
    need(lower == ds and len(lower) == 636, '636 source frames forced by fixed entrance lines')
    upper = {f: 8-d for f, d in upper_codim.items()}
    need(all(upper[source[k][r]] == ds[source[k][r]] for k in ('start', 'final') for r in range(661)), 'Expansion endpoints')
    expanded_records = [(op, x, y, c, upper[c]-upper[y], z) if op == 0 else (op, x, y, c, f, z) for op, x, y, c, f, z in records]
    expanded_profiles = [V.replay(expanded_records, source['start'], source['final'], upper, reverse)[0] for reverse in (False, True)]
    need(expanded_profiles[0] == expanded_profiles[1], 'Expansion both logical directions')
    T, P, expanded_surplus, _ = V.invoice({8: 439}, expanded_profiles[0])
    expanded_screen = V.admissible_kappa(T, P)
    need(expanded_screen < .00346424, 'Expansion does not repair the gain')
    J = load(ROOT/'research/joint-helper-lattice/native_joint.py', 'audit4633_complex_source')
    original, *_ = J.construct(); complex_word = read(HERE/'vendor/complex-ambient-quotient/QUOTIENT-WORD.json.gz')
    complex_source = binary_contract(dict(enumerate(original['frames'])), original['start'], original['final'], 112, 9)
    complex_quotient = binary_contract(dict(enumerate(complex_word['frames'])), complex_word['start'], complex_word['final'], 112, 9)
    need(complex_source['accepted'] == 112 and complex_quotient['accepted'] == 0, 'Complex contract')
    need(complex_quotient['main_widths'] == {'7': 168, '8': 56}, 'Complex widths')
    artifact = read(HERE/'vendor/bit-ambient-quotient/QUOTIENT-BIT-WORD.json.gz')
    bad = deepcopy(artifact); next(e for e in bad['records'] if e[0] == 0)[4] += 1
    bad_basis = deepcopy(artifact); bad_basis['frame_bases'][0] = [1, 1]
    wrong_start = list(source['start']); wrong_start[0] = source['start'][111]
    omitted = list(records); omitted.pop(next(i for i, e in enumerate(omitted) if e[0] == 1 and e[3] & 1))
    spoofed = deepcopy(artifact); spoofed['main_widths'] = {'7': 222}
    controls = {'wrong_move_rank': rejected(lambda: validate_binary_frames(bad)),
        'dependent_frame_basis': rejected(lambda: validate_binary_frames(bad_basis)),
        'changed_source_entrance': bool(bit_contract(rational, wrong_start, source['final'])),
        'omitted_source_add': rejected(lambda: V.replay(omitted, source['start'], source['final'], ds, False)),
        'spoofed_main_width_metadata': binary_contract(dict(enumerate(spoofed['frame_bases'])), spoofed['start'], spoofed['final'], 111, 8)['rejected'] == 111}
    need(all(controls.values()), 'Semantic mutation controls')
    # For any nonzero k-dimensional kernel, a hyperplane image has dimension
    # h-k or h-k-1. Re-padding full images yields h; proper images are <= h-2.
    for h in (8, 9):
        for k in range(1, h):
            need(h-1 not in {h if d == h-k else d for d in (h-k, h-k-1)}, 'Padded hyperplane obstruction')
    return {'status': 'PASS_PR4633_CONTRACT_AUDIT_NO_NEW_KAPPA', 'reviewed_head': 'b390d64abfcdba1a3816b86fc763cbc95d43c12c',
        'authenticated_inputs': pins, 'bit_source_ports_accepted': 111, 'bit_rational_frames_forced_by_fixed_lines': 636,
        'bit_gf2_reduction_before_quotient': mod2_source, 'bit_field_mismatch_witness': {'port': 8, 'source_dot_over_Q': dot, 'source_dot_mod_2': dot % 2},
        'bit_quotients': quotient_rows, 'expansion_repair_screen_only': {'changed_frames': sum(upper[f] != ds[f] for f in ds),
            'paid_mass': V.rank_mass(expanded_profiles[0]), 'surplus': expanded_surplus, 'float_screen': expanded_screen, 'native_lowering_checked': False},
        'complex_source': complex_source, 'complex_quotient': complex_quotient, 'negative_controls': controls,
        'scope': 'Finite endpoint and geometry audit; no new kappa, native realization or outer admission.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    result = run()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'), 'Deterministic audit receipt')
    print(result['status'])
    print('bit_ports_rejected=111 complex_ports_rejected=112 forced_rational_frames=636 controls=5')
