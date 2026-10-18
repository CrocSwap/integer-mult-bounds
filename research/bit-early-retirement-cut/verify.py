#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact common-frame retirement cut. No predecessor executable is imported.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SURVIVORS = ((465, 512), (466, 514), (468, 513), (469, 517), (470, 513), (476, 514))
SEED = 8


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(data):
    return json.dumps(data, sort_keys=True, indent=2) + '\n'


def support(row):
    result = []
    while row:
        bit = row & -row
        result.append(bit.bit_length() - 1)
        row ^= bit
    return result


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def invert(rows):
    a = rows[:]
    right = [1 << i for i in range(len(a))]
    for col in range(len(a)):
        pivot = next((r for r in range(col, len(a)) if a[r] >> col & 1), None)
        need(pivot is not None, 'singular boundary')
        a[col], a[pivot] = a[pivot], a[col]
        right[col], right[pivot] = right[pivot], right[col]
        for r in range(len(a)):
            if r != col and a[r] >> col & 1:
                a[r] ^= a[col]
                right[r] ^= right[col]
    need(a == [1 << i for i in range(len(a))], 'inverse residual')
    return right


def rref(vectors):
    rows = {}
    for vector in vectors:
        a = list(map(Fraction, vector))
        for p, b in sorted(rows.items()):
            if a[p]:
                q = a[p]
                a = [x - q*y for x, y in zip(a, b)]
        pivot = next((i for i, x in enumerate(a) if x), None)
        if pivot is not None:
            q = a[pivot]
            rows[pivot] = [x/q for x in a]
    return rows


class Geometry:
    def __init__(self, word):
        self.word = word
        self.bases = [rref(word['lines'][line] for line in frame)
                      for frame in word['frames']]

    def rank(self, frame):
        return len(self.bases[frame])

    @lru_cache(maxsize=None)
    def contained(self, small, large):
        for vector in self.bases[small].values():
            a = vector[:]
            for p, b in sorted(self.bases[large].items()):
                q = a[p]
                a = [x - q*y for x, y in zip(a, b)]
            if any(a):
                return False
        return True

    def separation(self, small, large):
        """An exact target annihilator detecting a vector in the retirement frame."""
        import math
        basis = self.bases[large]
        for free in range(self.word['h']):
            if free in basis:
                continue
            normal = [Fraction(i == free) for i in range(self.word['h'])]
            for pivot, row in sorted(basis.items(), reverse=True):
                normal[pivot] = -sum(row[j]*normal[j] for j in range(pivot+1, len(row)))
            scale = 1
            for x in normal:
                scale = scale*x.denominator // math.gcd(scale, x.denominator)
            normal = [int(x*scale) for x in normal]
            for line in self.word['frames'][small]:
                dot = sum(a*b for a, b in zip(normal, self.word['lines'][line]))
                if dot:
                    return {'normal': normal, 'line': line, 'dot': dot}
        raise Reject('no separating normal')


def load_word(root):
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    pins = [x for x in sources['files'] if x['usage'] == 'input']
    need(len(pins) == 1 and pins[0]['path'] == WORD, 'input inventory')
    raw = (root / WORD).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pins[0]['sha256'], 'source SHA256')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == pins[0]['git_blob'], 'source Git blob')
    return json.loads(gzip.decompress(raw))


def prefix_and_baseline(word, geometry):
    v, n = word['v'], 2*word['v'] + word['R']
    need((v, n, word['h']) == (111, 661, 8), 'pinned dimensions')
    frames = word['start'][:]
    values = [1 << i for i in range(n)]
    operations = Counter()

    def section(name):
        for f, target, donors in word[name]:
            need(len(set([target, *donors])) == 1+len(donors), 'gate operands')
            for r in [target, *donors]:
                need(geometry.contained(frames[r], f), 'baseline frame descent')
                frames[r] = f
            for donor in donors:
                values[target] ^= values[donor]
                operations[name] += 1

    section('D')
    section('A')
    need(all(frames[r] == 0 for r in range(v, 2*v)), 'pre-scatter target frame')
    # Retained copies use the inherited PR589 scatter interface. This is the
    # exact scalar cut immediately after scatter, not a native COPY compiler.
    need(len(word['scatter']) == v and len(word['ret']) == 9, 'scatter coverage')
    for t, donors in enumerate(word['scatter']):
        for donor in donors:
            values[v+t] ^= values[word['ret'][donor]]
            operations['scatter'] += 1
    boundary_frames, boundary_rows = frames[:], values[:]
    section('B')
    section('C')
    for r in range(n):
        need(geometry.contained(frames[r], word['final'][r]), 'final frame descent')
        expected = (1 << r) ^ (1 << (r-v)) if v <= r < 2*v else 1 << r
        need(values[r] == expected, 'baseline dirty endpoint')
    return boundary_frames, boundary_rows, dict(sorted(operations.items()))


def star(values, inverse, helper):
    restore = support(inverse[helper])
    dirt = [r for r, row in enumerate(values) if row >> helper & 1]
    need(helper in restore and helper in dirt, 'star pivot')
    gates = [[helper, r] for r in restore if r != helper]
    gates += [[r, helper] for r in dirt if r != helper]
    result = values[:]
    for t, s in gates:
        result[t] ^= result[s]
    need(result[helper] == 1 << helper, 'helper restoration')
    need(all(not row >> helper & 1 for r, row in enumerate(result) if r != helper),
         'helper dirt remains')
    return restore, dirt, gates, result


def lost_targets(inverse, participants, terminal, word, geometry):
    mask = sum(1 << r for r in participants)
    result = []
    v = word['v']
    for target in range(v, 2*v):
        if geometry.contained(terminal, word['final'][target]):
            continue
        missing = (inverse[target] ^ inverse[target-v]) & mask
        if missing:
            result.append({'target': target, 'boundary_coordinates': support(missing)})
    return result


def least_restoration(word, geometry, frames, inverse, helper):
    donors = support(inverse[helper])
    dimension = len(rref(vector for r in donors for vector in geometry.bases[frames[r]].values()))
    matches = [f for f in range(len(word['frames'])) if geometry.rank(f) == dimension and
               all(geometry.contained(frames[r], f) for r in donors)]
    need(len(matches) == 1, 'least restoration frame not uniquely catalogued')
    frame = matches[0]
    return {'frame': frame, 'rank': dimension, 'donors': donors,
            'lost_targets': lost_targets(inverse, donors, frame, word, geometry)}


RETIREMENT_GATES = [[186, 470, [77]], [513, 444, [470]], [513, 475, [470]]]


def patched_sections(word, retirement=None):
    cleanup = []
    removed, replaced = [], []
    for i, (f, t, donors) in enumerate(word['C']):
        if t == 470:
            need(donors == [77], 'unexpected cleanup restoration')
            removed.append(i)
            continue
        if 470 in donors:
            need(t == 444 and donors == [470], 'unexpected cleanup use')
            donors = [77]
            replaced.append(i)
        cleanup.append([f, t, donors])
    need(removed == [2343] and replaced == [580], 'cleanup edit coverage')
    return [('D', word['D']), ('A', word['A']), ('scatter', None),
            ('E', RETIREMENT_GATES if retirement is None else retirement),
            ('B', word['B']), ('C', cleanup)]


def replay_complete(word, geometry, sections, final):
    n, v = 2*word['v'] + word['R'], word['v']
    values, positive = [1 << i for i in range(n)], [1]*n
    frames = word['start'][:]
    paths = [[f] for f in frames]
    histogram, adds, moves, peak = Counter(), 0, 0, 1
    scalar_gates, copy_ranks = [], []

    def climb(r, f):
        nonlocal moves
        need(geometry.contained(frames[r], f), 'candidate frame descent')
        if f != frames[r]:
            rank = geometry.rank(f) - geometry.rank(frames[r])
            need(rank > 0, 'candidate redundant frame alias')
            histogram[rank] += 1
            moves += 1
            frames[r] = f
            paths[r].append(f)

    def add(t, s):
        nonlocal peak, adds
        adds += 1
        values[t] ^= values[s]
        positive[t] += positive[s]
        peak = max(peak, positive[t])
        scalar_gates.append((t, s))

    for name, gates in sections:
        if name == 'scatter':
            need(all(frames[r] == 0 for r in range(v, 2*v)), 'candidate scatter boundary')
            for r in word['ret']:
                histogram[geometry.rank(frames[r])] += 1
                copy_ranks.append(geometry.rank(frames[r]))
            for t, donors in enumerate(word['scatter']):
                for donor in donors:
                    add(v+t, word['ret'][donor])
            continue
        for f, t, donors in gates:
            need(len(set([t, *donors])) == len(donors)+1, 'candidate operands')
            for r in [t, *donors]:
                climb(r, f)
            for s in donors:
                add(t, s)
        if name == 'E':
            need(values[470] == 1 << 470 and all(not row >> 470 & 1
                 for r, row in enumerate(values) if r != 470), 'retirement separation')
    expected = [(1 << r) ^ (1 << (r-v)) if v <= r < 2*v else 1 << r for r in range(n)]
    need(values == expected, 'candidate complete dirty endpoint')
    for r, f in enumerate(final):
        climb(r, f)
    reverse = [1 << r for r in range(n)]
    for t, s in reversed(scalar_gates):
        reverse[t] ^= reverse[s]
    need(reverse == expected, 'candidate literal inverse endpoint')
    return {'ADDs': adds, 'MOVEs': moves, 'COPYs': len(word['ret']), 'ERASEs': len(word['ret']),
            'COPY_ranks': copy_ranks, 'records': adds + moves + 2*len(word['ret']),
            'profile': {str(k): x for k, x in sorted(histogram.items())},
            'rank_mass': sum(k*x for k, x in histogram.items()),
            'children': sum(histogram.values()), 'positive_majorant_peak': str(peak),
            'positive_majorant_bits': peak.bit_length(), 'paths': paths}


def ln_interval(q):
    """atanh series after exact power-of-two reduction; explicit geometric tail."""
    q, shift = Fraction(q), 0
    while q >= 2:
        q /= 2
        shift += 1
    need(1 <= q < 2, 'log domain')

    def reduced(x):
        z = (x-1)/(x+1)
        lo = 2*sum(z**(2*j+1)/(2*j+1) for j in range(40))
        return lo, lo + 2*z**81/(81*(1-z*z))

    lo, hi = reduced(q)
    two_lo, two_hi = reduced(Fraction(2))
    return lo+shift*two_lo, hi+shift*two_hi


def rounded_interval(lo, hi, bits=100):
    scale = 1 << bits
    return (Fraction((lo*scale).__floor__(), scale),
            Fraction((hi*scale).__ceil__(), scale))


def weight_interval(rank, a):
    import math
    lo, hi = rounded_interval(*ln_interval(Fraction(64, rank)), bits=160)
    lo, hi = a*lo, a*hi
    need(0 <= lo <= hi < Fraction(1, 100), 'exponential domain')
    lower = sum(lo**j/math.factorial(j) for j in range(13))
    upper = sum(hi**j/math.factorial(j) for j in range(13))
    upper += hi**13/math.factorial(13)/(1-hi/14)
    return rounded_interval(rank*lower, rank*upper)


def invoice_relaxation():
    a = Fraction(1733427039589844234749, 10**24)
    weights = {r: weight_interval(r, a) for r in (1, 2, 4, 5, 6, 7, 10, 12, 14)}
    cases = []
    for remainder in (2, 4, 6):
        delta = Counter({1: 1, 5: 1, 7: -2, remainder+8: 1, remainder: -1})
        need(sum(delta.values()) == sum(r*c for r, c in delta.items()) == 0,
             'two-slot child or mass balance')
        lo = sum(c*weights[r][int(c < 0)] for r, c in delta.items())
        hi = sum(c*weights[r][int(c > 0)] for r, c in delta.items())
        need(hi < 0, 'optimistic two-slot invoice not favorable')
        lo, hi = rounded_interval(lo, hi, bits=80)
        cases.append({'old_remainder': remainder,
                      'profile_delta': {str(r): c for r, c in sorted(delta.items())},
                      'weighted_delta_interval': [str(lo), str(hi)]})
    return {'exponent': str(a), 'weight': 'g(r)=r*(64/r)^a', 'cases': cases,
            'scope': 'Optimistic two-slot relocation only; new owner/window and H4 admission are unresolved.'}


def construction(word, geometry):
    baseline = replay_complete(word, geometry,
        [('D', word['D']), ('A', word['A']), ('scatter', None), ('B', word['B']), ('C', word['C'])],
        word['final'])
    final = word['final'][:]
    final[470] = 513
    candidate = replay_complete(word, geometry, patched_sections(word), final)
    changed_paths = [r for r in range(len(final)) if baseline['paths'][r] != candidate['paths'][r]]
    need(changed_paths == [470], 'unexpected frame itinerary change')
    paths = {'baseline': baseline.pop('paths')[470], 'candidate': candidate.pop('paths')[470]}
    delta = {str(r): candidate['profile'].get(str(r), 0)-baseline['profile'].get(str(r), 0)
             for r in range(1, 9)}
    delta = {r: x for r, x in delta.items() if x}
    need(delta == {'1': 1, '5': 1, '7': -1}, 'paid profile delta')
    need(candidate['ADDs'] == baseline['ADDs']+2 == 24307, 'ADD count')
    return {'retirement_gates': RETIREMENT_GATES,
            'cleanup_replace_source': {'gate': 580, 'old_source': 470, 'new_source': 77},
            'cleanup_omit_gate': 2343, 'final_helper_frame': 513,
            'baseline': baseline, 'candidate': candidate, 'helper470_paths': paths,
            'other_register_paths_unchanged': 660, 'local_profile_delta': delta,
            'optimistic_hosting': invoice_relaxation()}


def analyze(word):
    geometry = Geometry(word)
    frames, values, ops = prefix_and_baseline(word, geometry)
    inverse = invert(values)
    n, v = len(values), word['v']
    # Positive control: the unmodified cut has no inaccessible target donor.
    for target in range(v, 2*v):
        for donor in support(inverse[target] ^ inverse[target-v]):
            need(geometry.contained(frames[donor], word['final'][target]),
                 'baseline target dependency inaccessible')
    rows = []
    for helper, terminal in SURVIVORS[SEED % 6:] + SURVIVORS[:SEED % 6]:
        restore, dirt, gates, isolated = star(values, inverse, helper)
        participants = sorted(set(restore) | set(dirt) | {helper})
        need(all(geometry.contained(frames[r], terminal) for r in participants),
             'retirement input outside terminal')
        union = rref(vector for r in participants for vector in geometry.bases[frames[r]].values())
        need(len(union) == geometry.rank(terminal) == 7, 'unique rank-seven terminal')
        lost = lost_targets(inverse, participants, terminal, word, geometry)
        need(lost, 'no target obstruction')
        # Prefer a source-register witness, so the counterexample is not just
        # the separately listed illegal promotion of a target register.
        witness = next((entry, donor) for entry in lost
                       for donor in entry['boundary_coordinates'] if donor < v)
        entry, donor = witness
        need(donor in restore, 'witness must already be forced by restoration')
        target = entry['target']
        original_delta = [j for j in range(n) if inverse[j] >> donor & 1]
        delta = sum(1 << j for j in original_delta)
        need([sum(1 for j in support(row & delta)) % 2 for row in values] ==
             [int(r == donor) for r in range(n)], 'input pair does not isolate boundary coordinate')
        need(((delta >> target) ^ (delta >> (target-v))) & 1, 'desired target does not distinguish')
        promotions = [{'register': r, 'from_frame': frames[r],
                       'rank_increment': 7-geometry.rank(frames[r])}
                      for r in participants if frames[r] != terminal]
        immediate = [r for r in participants if v <= r < 2*v and
                     not geometry.contained(terminal, word['final'][r])]
        rows.append({'helper': helper, 'terminal_frame': terminal,
                     'restore_row': restore, 'dirty_column': dirt,
                     'forced_participants': participants, 'star_gates': gates,
                     'star_ADDs': len(gates), 'star_isolates_all_661_columns': True,
                     'promotions': promotions,
                     'promotion_rank_sum': sum(x['rank_increment'] for x in promotions),
                     'illegal_target_promotions': immediate, 'lost_targets': lost,
                     'lost_dependency_rank': binary_rank(sum(1 << r for r in x['boundary_coordinates']) for x in lost),
                     'least_frame_restoration': least_restoration(word, geometry, frames, inverse, helper),
                     'witness': {'target': target, 'boundary_coordinate': donor,
                                 'original_input_delta': original_delta,
                                 'separation': geometry.separation(terminal, word['final'][target])}})
    rows.sort(key=lambda x: x['helper'])
    return {'status': 'SCOPED_COMMON_FRAME_EARLY_RETIREMENT_OBSTRUCTION',
            'assignment_seed': SEED, 'dimensions': {'registers': n, 'targets': v},
            'baseline_ADDs': ops, 'baseline_total_ADDs': sum(ops.values()),
            'baseline_target_access_violations': 0, 'retirements': rows,
            'coverage': {'helpers': 6, 'target_contracts': 666,
                         'lost_target_contracts': sum(len(r['lost_targets']) for r in rows),
                         'star_ADD_occurrences': sum(r['star_ADDs'] for r in rows)},
            'construction': construction(word, geometry), 'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=HERE.parents[1])
    parser.add_argument('--emit', type=Path, help='create a new receipt; never overwrite')
    args = parser.parse_args()
    result = analyze(load_word(args.root))
    encoded = canonical(result)
    if args.emit:
        with args.emit.open('x') as stream:
            stream.write(encoded)
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text())
        need(canonical(expected) == encoded, 'certificate mismatch')
    print('PASS_BIT_EARLY_RETIREMENT_CUT helpers=6 lost=59 least_frame_survivor=470 '
          'width=8->7 ADDs=24305->24307 mass=5129->5128 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (Reject, OSError, ValueError, KeyError, IndexError) as error:
        raise SystemExit('REJECT: ' + str(error))
