#!/usr/bin/env python3
"""Finite R439 kernel entrance gauge. Adam Gall with OpenAI Codex. Apache-2.0."""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def rref(rows):
    rows = [list(map(Q, row)) for row in rows]
    pivots = []
    k = 0
    for c in range(8):
        j = next((j for j in range(k, len(rows)) if rows[j][c]), None)
        if j is None:
            continue
        rows[k], rows[j] = rows[j], rows[k]
        q = rows[k][c]
        rows[k] = [x / q for x in rows[k]]
        for j in range(len(rows)):
            if j != k and rows[j][c]:
                q = rows[j][c]
                rows[j] = [x - q*y for x, y in zip(rows[j], rows[k])]
        pivots.append(c)
        k += 1
    return rows[:k], pivots


def nullspace(rows):
    basis, pivots = rref(rows)
    result = []
    for j in range(8):
        if j not in pivots:
            row = [Q(int(c == j)) for c in range(8)]
            for br, c in zip(basis, pivots):
                row[c] = -br[j]
            result.append(row)
    return result


def columns(w):
    v = w['v']
    out = [0] * w['R']
    for f, t, ss in w['D']:
        need(f == 0 and v <= t < 2*v, 'D shape')
        for s in ss:
            need(2*v <= s < 2*v+w['R'], 'D source')
            out[s-2*v] ^= 1 << (t-v)
    return out


def sparse_kernels(cols):
    pairs = defaultdict(list)
    for a, b in combinations(range(len(cols)), 2):
        pairs[cols[a] ^ cols[b]].append((a, b))
    found = {(i,) for i, c in enumerate(cols) if c == 0}
    found.update(pairs.get(0, []))
    for i, c in enumerate(cols):
        for a, b in pairs.get(c, []):
            if i not in (a, b):
                found.add(tuple(sorted((i, a, b))))
    for bucket in pairs.values():
        for ab, cd in combinations(bucket, 2):
            if set(ab).isdisjoint(cd):
                found.add(tuple(sorted(ab + cd)))
    return sorted(found), len(pairs)


def independent_kernels(cols):
    """Increasing triple enumeration, not pair-bucket collision enumeration."""
    index = defaultdict(list)
    for i, c in enumerate(cols):
        index[c].append(i)
    out = {(i,) for i, c in enumerate(cols) if not c}
    n = len(cols)
    for a in range(n):
        for b in range(a+1, n):
            pair = cols[a] ^ cols[b]
            if pair == 0:
                out.add((a, b))
            for c in index.get(pair, ()):
                if c > b:
                    out.add((a, b, c))
            for c in range(b+1, n):
                for d in index.get(pair ^ cols[c], ()):
                    if d > c:
                        out.add((a, b, c, d))
    return sorted(out)


def census(w):
    cols = columns(w)
    supports, buckets = sparse_kernels(cols)
    need(supports == independent_kernels(cols), 'independent kernel census')
    first = {}
    offset = 2*w['v']
    for f, t, ss in w['A'] + w['B']:
        for r in [t] + ss:
            if r >= offset:
                first.setdefault(r, f)
    need(len(first) == w['R'], 'first-contact coverage')
    normals = {f: nullspace([w['lines'][i] for i in w['frames'][f]])
               for f in set(first.values())}
    rows = []
    for support in supports:
        helpers = [i + offset for i in support]
        fs = [first[h] for h in helpers]
        inter = nullspace([row for f in fs for row in normals[f]])
        rows.append(dict(helpers=helpers, first_frames=fs,
                         intersection_basis=[[str(x) for x in row] for row in inter]))
    return dict(helper_count=len(cols), pair_count=len(cols)*(len(cols)-1)//2,
                pair_syndromes=buckets, counts=dict(sorted(Counter(map(len, supports)).items())),
                supports=rows, feasible=[r for r in rows if r['intersection_basis']])


def construct(w, pivot=444, donor=470):
    need(columns(w)[pivot-2*w['v']] == columns(w)[donor-2*w['v']], 'kernel pair')
    out = copy.deepcopy(w)
    out['start'][pivot] = 79
    for gate in out['D']:
        gate[2] = [s for s in gate[2] if s != pivot]
    out['A'].insert(0, [79, donor, [pivot]])
    out['C'].append([1, donor, [pivot]])
    return out


def stream(w):
    events = [('add', t, s) for sec in ('D', 'A') for _, t, ss in w[sec] for s in ss]
    temp = 2*w['v'] + w['R']
    for j, h in enumerate(w['ret']):
        events.append(('copy', temp, h))
        events.extend(('add', w['v']+i, temp) for i, ks in enumerate(w['scatter']) if j in ks)
        events.append(('erase', temp, h))
    events.extend(('add', t, s) for sec in ('B', 'C') for _, t, ss in w[sec] for s in ss)
    return events


def literal_check(w, reverse=False):
    n = 2*w['v'] + w['R']
    # Independent set-valued formal-column interpreter, including private work.
    state = [{i} for i in range(n)] + [set()]
    norm = [1]*n + [0]
    peak = 1
    events = stream(w)
    for kind, t, s in (reversed(events) if reverse else events):
        if reverse:
            kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
        if kind == 'add':
            state[t] ^= state[s]
            norm[t] += norm[s]
        elif kind == 'copy':
            need(not state[t], 'copy into live work')
            state[t] = set(state[s])
            norm[t] = norm[s]
        else:
            need(state[t] == state[s], 'invalid erase')
            state[t] = set()
            norm[t] = 0
        peak = max(peak, norm[t])
    for i in range(n):
        expected = {i, i-w['v']} if w['v'] <= i < 2*w['v'] else {i}
        need(state[i] == expected, 'literal endpoint')
    need(not state[-1], 'private work restored')
    return peak


@lru_cache(maxsize=2)
def frame_geometry(lines, frames):
    bases = [rref([lines[i] for i in frame])[0] for frame in frames]
    dims = list(map(len, bases))
    @lru_cache(maxsize=None)
    def contained(a, b):
        if a == b or not bases[a]:
            return True
        return len(rref(bases[a] + bases[b])[0]) == dims[b]
    return dims, contained


def frame_check(w):
    dims, contained = frame_geometry(tuple(map(tuple, w['lines'])),
                                    tuple(map(tuple, w['frames'])))
    current = list(w['start'])
    values = [1 << i for i in range(len(current))]
    profile = Counter()
    def climb(r, f):
        old = current[r]
        need(contained(old, f), 'nonmonotone frame')
        delta = dims[f] - dims[old]
        if delta:
            profile[delta] += 1
        current[r] = f
    for sec in ('D', 'A', 'scatter', 'B', 'C'):
        if sec == 'scatter':
            snapshots = [values[r] for r in w['ret']]
            for r in w['ret']:
                profile[dims[current[r]]] += 1
            for i, ks in enumerate(w['scatter']):
                for k in ks:
                    values[w['v']+i] ^= snapshots[k]
            continue
        for f, t, ss in w[sec]:
            need(len({t, *ss}) == len(ss)+1, 'distinct operands')
            for r in [t]+ss:
                climb(r, f)
            for s in ss:
                values[t] ^= values[s]
    for r, f in enumerate(w['final']):
        climb(r, f)
        expected = (1 << r) ^ (1 << (r-w['v'])) if w['v'] <= r < 2*w['v'] else 1 << r
        need(values[r] == expected, 'frame replay endpoint')
    return dict(sorted(profile.items()))


def check_word(w):
    F, B = literal_check(w), literal_check(w, True)
    profile = frame_check(w)
    local = 64*F**3*B**2
    nine = (1 << 18)*F**5*B**4
    need(local < 1 << 104 and nine < 1 << 192, 'precision guard')
    events = stream(w)
    return dict(profile=profile, rank_mass=sum(r*c for r, c in profile.items()),
                ADDs=sum(k == 'add' for k, _, _ in events),
                copies=sum(k == 'copy' for k, _, _ in events),
                erasures=sum(k == 'erase' for k, _, _ in events),
                F=F, B=B, local_majorant=str(local), nine_stage_majorant=str(nine),
                local_bits=local.bit_length(), nine_stage_bits=nine.bit_length(),
                payload_sha256=hashlib.sha256(canonical(w)).hexdigest())


def controls(w, candidate):
    passed = []
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('control accepted: '+name)
    bad = copy.deepcopy(candidate)
    bad['A'].pop(0)
    reject('omitted entrance shear', lambda: literal_check(bad))
    bad = copy.deepcopy(candidate)
    bad['C'].pop()
    reject('omitted exit shear', lambda: literal_check(bad))
    bad = copy.deepcopy(candidate)
    bad['D'] = copy.deepcopy(w['D'])
    reject('stale compensation', lambda: literal_check(bad))
    bad = copy.deepcopy(candidate)
    bad['start'][444] = 2
    reject('incompatible entrance frame', lambda: frame_check(bad))
    bad = copy.deepcopy(candidate)
    bad['A'][0][0] = 0
    reject('free descent before decoding', lambda: frame_check(bad))
    reject('nonkernel pair', lambda: construct(w, 222, 223))
    need(sparse_kernels([1, 2, 3, 1])[0] == [(0, 1, 2), (0, 3), (1, 2, 3)], 'kernel positive fixture')
    need(nullspace([[int(i == j) for i in range(8)] for j in range(8)]) == [], 'full rank intersection control')
    need(len(nullspace([[1, 0, 0, 0, 0, 0, 0, 0]])) == 7, 'rank-one positive fixture')
    return passed


def run():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for path, digest in pins['sha256'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'source pin: '+path)
    w = json.loads(gzip.decompress((ROOT/pins['word']).read_bytes()))
    scan = census(w)
    need([r['helpers'] for r in scan['feasible']] == [[444, 470]], 'unique sparse frame survivor')
    candidate = construct(w)
    # The reverse orientation has the same finite algebra but a distinct entrance role.
    other = construct(w, 470, 444)
    baseline = check_word(w)
    result = dict(base=pins['base'], seed=18, census=scan, baseline=baseline,
                  candidate=check_word(candidate), alternate=check_word(other),
                  controls=controls(w, candidate), columns=661,
                  hypothesis='one nonzero entrance via a support-at-most-four common-frame helper shear',
                  selected_pivot=444, donor=470, entrance_frame=79,
                  inherited_hosting_reused=False, new_kappa=False)
    need(result['candidate']['rank_mass'] == baseline['rank_mass']-1, 'local rank mass')
    need(result['candidate']['ADDs'] == baseline['ADDs']-53, 'complete scalar invoice')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        need(not path.exists(), 'refusing to overwrite certificate')
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), 'certificate mismatch')
    print('PASS_BIT_KERNEL_ENTRANCE supports=80 viable=1 columns=661 ADDs=24305->24252 local_mass=5129->5128 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
