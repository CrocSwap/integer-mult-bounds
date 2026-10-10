"""Scan a six-int word for cleanup-sandwich helpers (PR271 pattern) and check the frame conditions. usage: scan_sandwich.py X LEAD OUT.json"""
import json, struct, sys
from fractions import Fraction as Q
from math import lcm
from collections import Counter
from pathlib import Path
X, LEAD, OUT = map(Path, sys.argv[1:4]); H = 24; PRIME = 1000003
frames = json.loads((X/'frames.json').read_text())['frames']; frames.update(json.loads((LEAD/'COHORT249-FRAMES.json').read_text()))
st = json.loads((X/'249-states.json').read_text()); n, v = st['n'], st['v']
initial = {int(a): f for a, f in json.loads((LEAD/'COHORT249-INITIAL.json').read_text()).items()}
old = list(struct.iter_unpack('<6i', (LEAD/'COHORT249-RECORDS.bin').read_bytes()))
cut = next(i for i, r in enumerate(old) if r[0] == 1 and r[5] == 3)
at_cut = dict(initial)
for op, a, b, c, f, z in old[:cut]:
    if op == 1: at_cut[a] = at_cut[b] = f
    elif op == 2: at_cut[a], at_cut[b] = c, f
    elif op == 3: del at_cut[b]
def rational_basis(rows):
    basis = {}
    for values in rows:
        row = list(map(Q, values))
        for p, b in sorted(basis.items()):
            if row[p]: row = [x - row[p]*y for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None: basis[p] = [x/row[p] for x in row]
    out = []
    for _, row in sorted(basis.items()):
        d = lcm(*(x.denominator for x in row)); out.append([int(x*d) for x in row])
    return out
def rank_mod_prime(rows):
    basis = {}
    for row in rows:
        row = [x % PRIME for x in row]
        for p, b in sorted(basis.items()):
            if row[p]: c = row[p]; row = [(x - c*y) % PRIME for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None: inv = pow(row[p], -1, PRIME); basis[p] = [x*inv % PRIME for x in row]
    return len(basis)
gates = {a: [] for a in range(2*v, n)}
for i in range(cut, len(old)):
    r = old[i]
    if r[0] == 1:
        for x in (r[1], r[2]):
            if 2*v <= x < n: gates[x].append((i, r))
census = Counter(len(g) for g in gates.values()); print('cut', cut, 'helpers by post-cut gate count', sorted(census.items())[:12], flush=True)
cands = []; reasons = Counter()
for a, g in gates.items():
    if len(g) != 3: continue
    (first, x), (middle, y), (last, w) = g
    if not (x[2] == a and y[1] == a and w[1:3] == x[1:3] and x[1] == w[1]): reasons['not sandwich shape'] += 1; continue
    t, b = x[1], y[2]
    if any(r[0] == 1 and r[2] == t for r in old[first+1:last]): reasons['t control inside'] += 1; continue
    B = rational_basis(frames[str(at_cut[a])]['B'] + frames[str(at_cut[b])]['B'])
    if len(B) != 4: reasons['joint dim %d' % len(B)] += 1; continue
    sums = [sum(u) for u in B]
    gram = [[9*sum(p*q for p, q in zip(u, w2)) - su*sw for w2, sw in zip(B, sums)] for u, su in zip(B, sums)]
    if rank_mod_prime(gram) != 4: reasons['degenerate'] += 1; continue
    cands.append(dict(helper=a, source=b, target=t, indices=[first, middle, last], frames=[x[4], y[4], w[4]], cats=[x[5], y[5], w[5]], a_cut=at_cut[a], b_cut=at_cut[b], dims=[frames[str(at_cut[a])]['dim'], frames[str(at_cut[b])]['dim']], entrance_dim=frames[str(initial[a])]['dim']))
print('rejections', dict(reasons), 'candidates', len(cands), flush=True)
# non-overlap: b and t of one may not be a selected helper; greedy in helper order
chosen, used = [], set()
for c in sorted(cands, key=lambda c: c['helper']):
    if c['helper'] in used or c['source'] in {d['helper'] for d in chosen} or c['target'] in {d['helper'] for d in chosen}: continue
    if any(c['helper'] in (d['source'], d['target']) for d in chosen): continue
    chosen.append(c); used.add(c['helper'])
print('chosen', len(chosen), 'entrance dims', Counter(c['entrance_dim'] for c in chosen), 'cut dims', Counter(tuple(c['dims']) for c in chosen), 'frames', Counter(tuple(c['frames']) for c in chosen).most_common(3), 'cats', Counter(tuple(c['cats']) for c in chosen))
print('sample', chosen[:2])
OUT.write_text(json.dumps(dict(cut=cut, candidates=cands, chosen=chosen), indent=1) + '\n')
