#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact integer spectral evidence; see README for the quantified proof.

Arham Tahir with substantial OpenAI Codex assistance. No solver or floats.
"""
import argparse
import hashlib
import json
from math import comb
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
# Runtime native oracle for dense.py; demoted from live SOURCES/VERIFY pins after
# research/clifford-state-production/ rewrote the working multicold evaluator.
KERNEL = 'research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'
INPUTS = {'research/selector-batching/README.md'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def check_sources(root=ROOT, package=PKG):
    sources = read_json(package / 'SOURCES.json')
    live = [r for r in sources['files'] if r['usage'] == 'input']
    require(len(live) == len(INPUTS) and {r['path'] for r in live} == INPUTS,
            'incomplete or duplicate live input inventory')
    for row in live:
        path = root / row['path']
        require(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), 'external source')
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 mismatch: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == row['git_blob'], 'source blob mismatch: ' + row['path'])
    return {r['path']: r['sha256'] for r in live}


def spectrum(f, direction=1):
    require(type(f) is int and f >= 1 and type(direction) is int and direction in (-1, 1), 'tensor domain')
    out = [0] * 4
    for j in range(f + 1):
        out[(direction * j) % 4] += comb(f, j)
    return out


def cyclic_spectrum(f, direction=1):
    """Separate recurrence multiplying eigenvalue polynomials modulo x^4-1."""
    out = [1, 0, 0, 0]
    for _ in range(f):
        out = [out[j] + out[(j - direction) % 4] for j in range(4)]
    return out


def phase_shift(counts, phase):
    return [counts[(j - phase) % 4] for j in range(4)]


def target(f, q, dirty=0, direction=1):
    require(type(q) is int and q > 0 and type(dirty) is int and dirty >= 0, 'lane/padding domain')
    out = [q * b for b in spectrum(f, direction)]
    out[0] += dirty
    return out


def child(h, spectators, phase=0, direction=1):
    require(type(spectators) is int and spectators > 0, 'spectator domain')
    return phase_shift([spectators * b for b in spectrum(h, direction)], phase)


def trace(counts, power=1):
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    return tuple(sum(n * roots[(j * power) % 4][k] for j, n in enumerate(counts)) for k in (0, 1))


def norm(z):
    return z[0] ** 2 + z[1] ** 2


def correction_floor(a, b):
    require(sum(a) == sum(b), 'correction comparison needs equal dimensions')
    # Rank perturbation of A-mu I changes nullity by at most rank(A-B).
    return max(abs(x - y) for x, y in zip(a, b))


def make_certificate():
    pins = check_sources()
    digest = hashlib.sha256()
    uniform_cases = uniform_matches = 0
    for f in range(1, 65):
        plus = spectrum(f)
        minus = spectrum(f, -1)
        require(plus == cyclic_spectrum(f) and minus == cyclic_spectrum(f, -1), 'independent spectrum disagreement')
        require(sum(plus) == 2 ** f and trace(plus, 2) == (0, 0), 'tensor square-trace identity')
        require(trace(plus, 3) == (trace(plus)[0], -trace(plus)[1]), 'third trace is conjugate')
        require(norm(trace(plus)) == 2 ** f and norm(trace(minus)) == 2 ** f, 'tensor trace-norm identity')
        for q in (1, 2, 3, 4, 8, 16):
            for h in range(1, f + 5):
                payload = q * 2 ** f
                t0 = (payload + 2 ** h - 1) // 2 ** h
                for t in (t0, t0 + 1):
                    d = t * 2 ** h - payload
                    a = target(f, q, d)
                    matches = [p for p in range(4) if a == child(h, t, p)]
                    inverse_matches = [p for p in range(4) if a == child(h, t, p, -1)]
                    require(bool(matches) == (d == 0 and h == f), 'uniform forward classification')
                    require(bool(inverse_matches) == (d == 0 and h == f), 'uniform inverse classification')
                    require(trace(a, 2) == (d, 0), 'dirty identity square trace')
                    if d == 0:
                        require(norm(trace(a)) == q * q * 2 ** f, 'uniform lane trace norm')
                    digest.update(canonical([f, q, h, t, d, matches, inverse_matches]).encode() + b'\n')
                    uniform_cases += 1
                    uniform_matches += bool(matches)
    mixed = []
    for f in range(1, 65):
        a = [x + y for x, y in zip(spectrum(f), spectrum(f, -1))]
        phases = [p for p in range(4) if a == child(f + 1, 1, p)]
        expected = [3 if f % 4 == 1 else 0] if f % 2 else []
        require(phases == expected, 'opposite-direction parity classification')
        all_ranks = []
        for h in range(1, f + 2):
            size = 2 ** (f + 1)
            if size % (2 ** h):
                continue
            t = size // (2 ** h)
            for p in range(4):
                if a == child(h, t, p):
                    all_ranks.append([h, t, p])
        expected_all = [[f+1, 1, expected[0]]] if f % 2 else ([[f, 2, 0]] if f % 4 == 0 else [])
        require(all_ranks == expected_all, 'complete opposite-direction tensor classification')
        mixed.append({'f': f, 'next_rank_matching_phases': phases,
                      'all_matching_rank_spectator_phase_triples': all_ranks,
                      'target_multiplicities': a})
    rank1_16 = target(1, 16)
    floors = [correction_floor(rank1_16, child(5, 1, p)) for p in range(4)]
    require(min(floors) == 6, 'six-dimensional correction floor')
    controls = {
        'same_direction_two_lanes_reject_rank_two': not any(target(1, 2) == child(2, 1, p) for p in range(4)),
        'restored_dirty_padding_has_nonzero_square_trace': trace(target(1, 1, 2), 2) == (2, 0) and trace(child(2, 1), 2) == (0, 0),
        'wrong_phase_rejects_mixed_rank_one_fixture': [2, 1, 0, 1] != child(2, 1, 0),
        'mixed_odd_width_is_a_real_scope_countercontrol': [2, 1, 0, 1] == child(2, 1, 3),
        'mixed_even_width_rejects_every_phase': not any([x+y for x,y in zip(spectrum(2), spectrum(2,-1))] == child(3,1,p) for p in range(4)),
        'unchanged_rank_is_positive_control': target(3, 3) == child(3, 3),
    }
    require(all(controls.values()), 'spectral control failed')
    return {
        'schema_version': 1,
        'scope': 'Written all-size characteristic-zero proof; finite evidence is not a kernel theorem or physical supplier.',
        'source_sha256': pins,
        'uniform': {'f_range': [1, 64], 'q_values': [1, 2, 3, 4, 8, 16], 'h_range': '1..f+4',
                    'spectator_values': 'ceil(q*2^f/2^h), and that value plus one',
                    'phase_domain': [0, 1, 2, 3], 'child_directions': [-1, 1],
                    'cases': uniform_cases, 'matching_cases': uniform_matches, 'digest': digest.hexdigest(),
                    'classification': 'some phase matches iff dirty=0 and h=f'},
        'opposite_two_lanes': mixed,
        'correction_rank_example': {'f': 1, 'q': 16, 'h': 5, 'spectators': 1,
                                    'uniform_target': rank1_16, 'child': child(5, 1),
                                    'floors_by_phase': floors, 'minimum_floor': 6,
                                    'meaning': 'For every reciprocal basis, a subsequent correction F needs rank(F-I)>=6. This is not a recursive-cost lower bound.'},
        'controls': controls,
        'volume_obstruction': 'For h>f and sigma>0, q*A*V*h^sigma > q*A*V*f^sigma, even with encoding/decoding free. Available upper-bound expressions, not optimal runtimes.'
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='regenerate this package certificate')
    args = ap.parse_args()
    cert = make_certificate()
    path = PKG / 'CERTIFICATE.json'
    if args.write:
        path.write_text(json.dumps(cert, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        require(canonical(read_json(path)) == canonical(cert), 'certificate mismatch')
    print('PASS_CLIFFORD_RECIPROCAL_BASIS cases=' + str(cert['uniform']['cases'])
          + ' mixed_widths=64 correction_floor=6 controls=6 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('FAIL: ' + str(error))
