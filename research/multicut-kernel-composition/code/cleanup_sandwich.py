#!/usr/bin/env python3
"""Cleanup-sandwich cancellation (PR271's mechanism, evmckinney9) as a stage on the native six-int transcript.

For each frozen helper a, the suffix of the word after the first kernel cut contains exactly three gates on a,
    t += a,   a += b,   t += a          (F2, in this order; the last is the family's Q^-1 pass)
and t is not a control strictly between the first and the last. Over F2 these equal a += b; t += b. The rewrite
emits a += b at the cut at the joint frame of a and b there (four-dimensional, nondegenerate for 9I - J), replaces
the middle gate by t += b at its frame and drops the first and last gates. The helper then has no gate after the
cut and ends at the joint frame instead of climbing to the full frame. Every MOVE is rebuilt from the actual
needs, every new connector is checked for exact rational inclusion, and the emitted word is replayed over F2 on
every formal source, target and dirty column with both omission controls. The stage writes the rewritten lead
directory, an export directory whose 249-states.json carries the new final frames (for the native legality
checker), and folds its histogram delta into the replay receipt.
usage: cleanup_sandwich.py EXPORT LEAD SELECTION OUTPUT
Adapted from research/cleanup-sandwich-263/sandwich263.py (Apache-2.0); Anthropic Claude assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import json, shutil, struct, sys
if not __debug__: raise SystemExit('assertions required')
H = 24; PRIME = 1000003
X, L, SEL, O = map(Path, sys.argv[1:5])
def load(p): return json.loads(Path(p).read_text())
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
def annihilator(B):
    pivots = [next(i for i, x in enumerate(row) if x) for row in B]; out = []
    for free in sorted(set(range(H)) - set(pivots)):
        vec = [Q(i == free) for i in range(H)]
        for p, row in reversed(list(zip(pivots, B))): vec[p] = -sum(Q(row[j])*vec[j] for j in range(p+1, H)) / row[p]
        d = lcm(*(x.denominator for x in vec)); out.append([int(x*d) for x in vec])
    return out
def histogram(records):
    h = Counter()
    for op, a, b, c, f, z in records:
        if op == 0 and f: h[f] += 1
        elif op == 2: h[z] += 1
    return h
sel = load(SEL); helpers = sel['helpers']
frames = load(X/'frames.json')['frames']; lead_frames = load(L/'COHORT249-FRAMES.json'); frames.update(lead_frames)
states = load(X/'249-states.json'); n, v = states['n'], states['v']
initial = {int(a): f for a, f in load(L/'COHORT249-INITIAL.json').items()}
blob = (L/'COHORT249-RECORDS.bin').read_bytes(); assert sha256(blob).hexdigest() == sel['input_record_sha256']
old = list(struct.iter_unpack('<6i', blob))
cut = next(i for i, r in enumerate(old) if r[0] == 1 and r[5] == 3)
zmax = max(r[5] for r in old if r[0] == 1); EARLY, SANDWICH = zmax + 1, zmax + 2
at_cut = dict(initial)
for op, a, b, c, f, z in old[:cut]:
    if op == 1: at_cut[a] = at_cut[b] = f
    elif op == 2: at_cut[a], at_cut[b] = c, f
    elif op == 3: del at_cut[b]
edits, skip, replace, new_frames = [], set(), {}, {}
next_id = max(int(k) for k in frames) + 1
for a in helpers:
    assert 2*v <= a < n and frames[str(initial[a])]['dim'] == 1
    gates = [(i, r) for i, r in enumerate(old) if i >= cut and r[0] == 1 and a in r[1:3]]
    assert len(gates) == 3, ('helper must have exactly three gates after the cut', a)
    (first, x), (middle, y), (last, w) = gates
    t, b = x[1], y[2]
    assert x[2] == a and y[1] == a and w[1:3] == (t, a), ('not a sandwich t+=a, a+=b, t+=a', a)
    assert all(r[0] != 1 or r[2] != t for r in old[first+1:last]), ('t is a control inside the sandwich', a)
    assert b not in helpers and t not in helpers, ('overlapping sandwiches', a)
    B = rational_basis(frames[str(at_cut[a])]['B'] + frames[str(at_cut[b])]['B'])
    assert len(B) == 4, ('the joint frame of a and b at the cut is not four-dimensional', a)
    sums = [sum(u) for u in B]
    gram = [[9*sum(p*q for p, q in zip(u, w2)) - su*sw for w2, sw in zip(B, sums)] for u, su in zip(B, sums)]
    assert rank_mod_prime(gram) == 4, ('new frame is degenerate for 9I - J', a)
    frame = next_id; next_id += 1; assert str(frame) not in frames
    frames[str(frame)] = new_frames[str(frame)] = {'dim': 4, 'B': B, 'A': annihilator(B)}
    skip.update((first, last)); replace[middle] = (1, t, b, y[3], y[4], SANDWICH)
    edits.append({'helper': a, 'source': b, 'target': t, 'frame': frame, 'old_indices': [first, middle, last], 'entrance_frame': initial[a], 'cut_frames': [at_cut[a], at_cut[b]]})
state, new, checked = dict(initial), [], set()
inherited = {(b, c) for op, a, b, c, f, z in old if op == 0}
def move(a, f):
    before = state[a]
    if before == f: return
    if (before, f) not in inherited and (before, f) not in checked:
        B, A = frames[str(before)]['B'], frames[str(f)]['A']
        assert all(sum(Q(p)*Q(q) for p, q in zip(u, w2)) == 0 for u in B for w2 in A), ('not nested', before, f)
        checked.add((before, f))
    rank = frames[str(f)]['dim'] - frames[str(before)]['dim']; assert rank >= 0, ('frame retreats', a, before, f)
    new.append((0, a, before, f, rank, 0)); state[a] = f
def emit(r):
    op, a, b, c, f, z = r
    if op == 1: move(a, f); move(b, f)
    elif op == 2: move(a, c); state[b] = f
    elif op == 3: assert state[a] == c and state[b] == f; del state[b]
    new.append(r)
for i, r in enumerate(old):
    if i == cut:
        for e in edits: emit((1, e['helper'], e['source'], 1, e['frame'], EARLY))
    if r[0] != 0 and i not in skip: emit(replace.get(i, r))
final = {int(a): f for a, f in states['final'].items()}; final.update({e['helper']: e['frame'] for e in edits})
for a in range(n): move(a, final[a])
assert state == final
def wrong_rows(records, omit=None):
    rows = [1 << a for a in range(n)] + [0]
    for op, a, b, c, f, z in records:
        if op == 1 and c % 2 and z != omit: rows[a] ^= rows[b]
        elif op == 2: rows[b] = rows[a]
        elif op == 3: assert rows[a] == rows[b]; rows[b] = 0
    return sum(rows[a] != ((1 << a) ^ ((1 << (a - v)) if v <= a < 2*v else 0)) for a in range(n))
assert wrong_rows(new) == 0, 'rewritten word fails the formal replay'
controls = {'omit early a += b': wrong_rows(new, EARLY), 'omit sandwich t += b': wrong_rows(new, SANDWICH)}
assert all(controls.values()), 'an omission control was accepted'
# chronological frame legality of the emitted word against the new final frames
st = dict(initial); copy = None; hist = Counter(); count = 0
for op, a, b, c, f, z in new:
    if op == 0:
        assert st[a] == b and frames[str(c)]['dim'] - frames[str(b)]['dim'] == f; st[a] = c
        if f: hist[f] += 1
    elif op == 1: assert st[a] == st[b] == f and a != b; count += 1
    elif op == 2: assert copy is None and st[a] == c; st[b] = f; hist[z] += 1; copy = (a, b, c)
    else: assert copy == (a, b, c) and st[a] == c and st[b] == f; del st[b]; copy = None
assert st == final and copy is None
delta = Counter(hist); delta.subtract(histogram(old)); delta = {r: c for r, c in delta.items() if c}
assert sum(r*c for r, c in delta.items()) == -20*len(edits), 'endpoint rank mass must drop by 20 per helper'
assert delta == {int(k): c for k, c in sel['expected_local_histogram_delta'].items()}, ('histogram delta', delta)
data = b''.join(struct.pack('<6i', *r) for r in new)
# outputs: rewritten lead, export with the new final frames, folded replay receipt
O.mkdir(); (O/'export').mkdir()
for name in ('COHORT249-INITIAL.json', 'COHORT249-SELECTION.json', 'descent-selection.json', 'DESCENT-RETIMING.json', 'DESCENT-REBIND-EVIDENCE.json', 'PLATEAU-RETIMING.json', 'PLATEAU-SOURCE-SPANS.json', 'FRAME-TABLE-AUDIT.json', 'target-selection.json', 'TARGET-PREFIX.json'):
    if (L/name).exists(): shutil.copy2(L/name, O/name)
(O/'COHORT249-RECORDS.bin').write_bytes(data); (O/'COHORT249-PRE-SANDWICH-RECORDS.bin').write_bytes(blob)
lead_frames.update(new_frames); (O/'COHORT249-FRAMES.json').write_text(json.dumps(lead_frames) + '\n')
for name in ('frames.json', '249-records.bin', '249-DONOR-OWNERSHIP.json'): shutil.copyfile(X/name, O/'export'/name)
states['final'].update({str(e['helper']): e['frame'] for e in edits}); (O/'export/249-states.json').write_text(json.dumps(states) + '\n')
replay = load(L/'COHORT249-REPLAY.json'); oldH = Counter({int(k): c for k, c in replay['histogram'].items()}); assert oldH == histogram(old)
total = Counter({int(k): c for k, c in replay['delta'].items()}); total.update(delta)
replay.update(status='CLEANUP_SANDWICH_CANCELLATION_NATIVE_BANK_REVIEW_NOT_APPLICABLE', pre_sandwich_records=len(old), new_records=len(new), pre_sandwich_histogram=replay['histogram'],
              histogram={str(r): c for r, c in sorted(hist.items())}, delta={str(r): c for r, c in sorted(total.items()) if c}, sandwich_histogram_delta={str(r): c for r, c in sorted(delta.items())},
              sandwich_helpers_retired=len(edits), new_rank_mass=sum(r*c for r, c in hist.items()))
(O/'COHORT249-REPLAY.json').write_text(json.dumps(replay, indent=2) + '\n')
receipt = {'status': 'PASS_CLEANUP_SANDWICH_REWRITE_FORMAL_F2_COLUMNS_AND_FRAMES', 'helpers_retired': len(edits), 'cut_record': cut, 'input_sha256': sha256(blob).hexdigest(), 'output_sha256': sha256(data).hexdigest(),
           'formal_columns': n, 'omission_controls_wrong_rows': controls, 'new_connectors_checked': len(checked), 'new_frames': len(new_frames), 'histogram_delta': {str(r): c for r, c in sorted(delta.items()) if c},
           'endpoint_rank_mass_drop': 20*len(edits), 'rank_mass': sum(r*c for r, c in hist.items()), 'paid_calls': sum(hist.values()), 'scalar_additions': count, 'early_category': EARLY, 'sandwich_category': SANDWICH,
           'selection_sha256': sha256(SEL.read_bytes()).hexdigest(), 'edits': edits}
(O/'CLEANUP-SANDWICH.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS cleanup sandwich', len(edits), 'helpers', 'controls', controls, 'delta', receipt['histogram_delta'], 'records', len(new), flush=True)
