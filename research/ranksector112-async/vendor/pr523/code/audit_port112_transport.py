"""Independently match the restricted Hamming and canonical scalar words.
Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy, gzip, hashlib, json, sys

out = Path(sys.argv[1])
w = json.load(gzip.open(out / 'FULL-WORD.json.gz'))
c = json.load(gzip.open(out / 'CANONICAL-WORD.json.gz'))
v, R = c['v'], c['R']
assert v == len(w['ports']) == 112 and R == w['report']['R']
n = 2 * v + R


def basis(vs):
    b = {}
    for x in vs:
        for k in sorted(b, reverse=True):
            if x >> k & 1:
                x ^= b[k]
        if x:
            k = x.bit_length() - 1
            for j in b:
                if b[j] >> k & 1:
                    b[j] ^= x
            b[k] = x
    return tuple(b[k] for k in sorted(b, reverse=True))


def tau(x):
    return x ^ (43 if (x & 43).bit_count() % 2 else 0)


assert 43 .bit_count() % 2 == 0
assert set(map(tau, w['ports'])) == set(c['ports'])
mp = {i: c['ports'].index(tau(p)) for i, p in enumerate(w['ports'])}
mp.update({v + i: v + mp[i] for i in range(v)})
mp.update({2 * v + h: 2 * v + h for h in range(R)})
fi = {basis(f): i for i, f in enumerate(c['frames'])}


def frame(F):
    return fi[basis(tau(x) for x in F)]


def event(e):
    e = copy.deepcopy(e)
    e[1] = mp[e[1]]
    if e[0] == 'add':
        e[2] = mp[e[2]]
    if e[-1] is not None:
        e[-1] = frame(e[-1])
    return e


for seq in ['A', 'B', 'cut', 'cleanup', 'precondition']:
    assert [event(e) for e in w[seq]] == c[seq], seq
assert [mp[r] for r in w['centers']] == c['centers']
assert [frame(F) for F in w['center_frames']] == c['center_frames']
assert {str(mp[v + int(t)] - v): frame(F) for t, F in w['target_levels'].items()} == c['target_levels']
for r in range(n):
    expected = frame([w['ports'][r]]) if r < v else frame(w.get('start_extra', {}).get(str(r), []))
    assert c['start'][mp[r]] == expected


def apply(e, rows):
    if e[0] == 'scale':
        _, t, a, b, *_ = e
        rows[t] = {j: Q(a, b) * x for j, x in rows[t].items()}
        return
    _, t, s, a, b, *_ = e
    q = Q(a, b)
    for j, x in list(rows[s].items()):
        z = rows[t].get(j, Q(0)) + q * x
        if z:
            rows[t][j] = z
        else:
            rows[t].pop(j, None)


mx = [{i: Q(1)} for i in range(n)]
for e in w['A'] + w['cut'] + w['B']:
    apply(e, mx)
dirty = [{} for _ in range(n)]
for t in range(v, 2 * v):
    dirty[t] = {r: x for r, x in mx[t].items() if r >= 2 * v}
for e in w['precondition']:
    apply(e, dirty)
comp = []
for t in range(v, 2 * v):
    for r, x in sorted(dirty[t].items()):
        assert str(r) not in w['start_extra'], ('illegal frame-zero compensation of entering helper', r)
        comp.append(['add', t, r, -x.numerator, x.denominator, []])
assert [event(e) for e in comp] == c['compensation']

report = {
    'status': 'PASS_EXACT_112_PORT_WORD_TRANSPORT',
    'word_sha256': hashlib.sha256((out / 'FULL-WORD.json.gz').read_bytes()).hexdigest(),
    'canonical_sha256': hashlib.sha256((out / 'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),
    'hamming_to_canonical_source_map': {i: mp[i] for i in range(v)},
    'all_main_cleanup_precondition_center_and_entrance_frames_match': True,
    'independently_recomputed_helper_compensations_match': len(comp),
    'columns_in_recomputed_raw_main': n,
    'scope': 'Exact transport of the whole raw word to the canonical word, including recomputed arbitrary-dirt compensation. Canonical emitted replay supplies both orientation identities.',
}
(out / 'TRANSPORT.json').write_text(json.dumps(report, indent=2) + '\n')
print(report['status'], len(comp), 'compensations', flush=True)
