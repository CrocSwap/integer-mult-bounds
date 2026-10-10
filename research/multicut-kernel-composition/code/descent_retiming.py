#!/usr/bin/env python3
"""Concave-descent frame retiming of selected ADD gates on the cohort-rewritten transcript.

Reads the native six-int transcript written by cohort-transform, the exported
frame tables and the frozen selection, reassigns the selected ADD frames, rebuilds
every MOVE from the actual gate needs, and checks: byte-identical scalar/COPY
projection, nested chains, unchanged initial/final frames and COPY lifetimes,
nondegenerate endpoint bases, exact integer source span of every non-target
operand inside its new frame, and the expected histogram delta at unchanged rank
mass. The downstream native legality, column, bank, price and invoice checkers
re-examine the rewritten transcript independently. Prepared by Rohan Arun with
Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from fractions import Fraction
from math import gcd
from pathlib import Path
import hashlib, json, sys
if not __debug__: raise SystemExit('assertions required')
X, LEAD, SEL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
H = 24

def dot(x, y): return sum(p*q for p, q in zip(x, y))

def rref_key(rows):
    M = [[Fraction(x) for x in r] for r in rows]; r = 0
    for c in range(H):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [x/pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                m = M[i][c]; M[i] = [x-m*y for x, y in zip(M[i], M[r])]
        r += 1
        if r == len(M): break
    return tuple(tuple(x) for x in M[:r])

def prim(v):
    g = 0
    for x in v: g = gcd(g, abs(x))
    if g > 1: v = [x//g for x in v]
    f = next((x for x in v if x), 0)
    return tuple(-x for x in v) if f < 0 else tuple(v)

def rank(rows):
    M = [[Fraction(x) for x in r] for r in rows]; r = 0
    for c in range(len(M[0]) if M else 0):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [x/pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                m = M[i][c]; M[i] = [x-m*y for x, y in zip(M[i], M[r])]
        r += 1
        if r == len(M): break
    return r

frames = {}
for name in (X/'frames.json', LEAD/'COHORT249-FRAMES.json'):
    j = json.loads(name.read_text()); j = j.get('frames', j)
    for k, rec in j.items():
        frames[int(k)] = dict(B=[list(map(int, r)) for r in rec['B']], A=[list(map(int, r)) for r in rec['A']], d=int(rec['dim']))
for f, fr in frames.items():
    assert len(fr['B']) == fr['d'] and len(fr['A']) + fr['d'] == H and all(dot(a, b) == 0 for a in fr['A'] for b in fr['B'])
by_key = {}
for f in sorted(frames): by_key.setdefault(rref_key(frames[f]['B']) if frames[f]['B'] else (), f)
canon = {f: by_key[rref_key(frames[f]['B']) if frames[f]['B'] else ()] for f in frames}
subcache = {}
def sub(f, g):
    if f == g: return True
    k = (f, g)
    if k not in subcache: subcache[k] = frames[f]['d'] <= frames[g]['d'] and all(dot(a, b) == 0 for a in frames[g]['A'] for b in frames[f]['B'])
    return subcache[k]
def nondeg(f):
    B, A = frames[f]['B'], frames[f]['A']
    if not B or len(B) == H: return True
    if len(B) <= len(A):
        s = [sum(b) for b in B]; return rank([[9*dot(B[i], B[j]) - s[i]*s[j] for j in range(len(B))] for i in range(len(B))]) == len(B)
    s = [sum(a) for a in A]; return rank([[(9-H)*dot(A[i], A[j]) + s[i]*s[j] for j in range(len(A))] for i in range(len(A))]) == len(A)

st = json.loads((X/'249-states.json').read_text()); n, v = st['n'], st['v']; ZERO, FULL = st['ZERO'], st['FULL']
initial = {int(k): f for k, f in json.loads((LEAD/'COHORT249-INITIAL.json').read_text()).items()}
sel = json.loads(SEL.read_text())
old = array('i'); old.frombytes((LEAD/'COHORT249-RECORDS.bin').read_bytes()); assert old.itemsize == 4 and len(old) % 6 == 0
assert hashlib.sha256(old.tobytes()).hexdigest() == sel['input_record_sha256'] and len(old)//6 == sel['input_record_count']
final = dict(initial)
for k in range(0, len(old), 6):
    if old[k] == 0: final[old[k+1]] = old[k+3]
assert all(final[i] == FULL for i in initial if i < v or i >= 2*v)
cov = [list(map(int, c)) for c in st['source_covectors']]
chi = {s: frames[initial[s]]['B'][0] for s in range(v)}
for s in range(v): assert frames[initial[s]]['d'] == 1
# selected gates: bound by ADD ordinal among non-MOVE records and by scalar content
nonmove = [k//6 for k in range(0, len(old), 6) if old[k]]
chosen = {}; changed = []
for r in sel['entries']:
    i = nonmove[r['gate']]; assert i not in chosen
    op, a, b, c, f, z = old[6*i:6*i+6]
    assert op == 1 and b != n and [a, b, c, z] == r['scalar'] and frames[f]['d'] == r['old_dimension']
    assert rref_key(frames[f]['B']) == rref_key([list(map(int, x)) for x in r['old_basis']]), 'old frame basis mismatch'
    g = by_key.get(rref_key([list(map(int, x)) for x in r['new_basis']])); assert g is not None, 'new frame absent from exported tables'
    assert frames[g]['d'] == r['new_dimension'] and nondeg(g) and canon[g] != canon[f]
    chosen[i] = g; changed.append(dict(record=i, gate=r['gate'], old_frame=f, new_frame=g, old_dimension=frames[f]['d'], new_dimension=frames[g]['d']))
assert len(chosen) == sel['selected_gate_count'] > 0
# exact integer source spans after each selected gate
columns = [{i: 1} if i < v else {} for i in range(n)]; center = None; spans = {}
for k in range(0, len(old), 6):
    op, a, b, c, f, z = old[k:k+6]
    if op == 0: continue
    if op == 2: assert center is None; center = a; continue
    if op == 3: assert center == a; center = None; continue
    source = center if b == n else b; ca = columns[a]
    for s, x in columns[source].items():
        y = ca.get(s, 0) + c*x
        if y: ca[s] = y
        else: del ca[s]
    if k//6 in chosen:
        need = set()
        if not (v <= a < 2*v): need.update(ca)
        if not (v <= b < 2*v) and b != n: need.update(columns[b])
        spans[k//6] = sorted(need)
assert center is None
for i, g in chosen.items():
    for s in spans[i]: assert all(dot(x, chi[s]) == 0 for x in frames[g]['A']), ('retimed frame omits operand source span', i, s)
# rebuild MOVEs from the retimed needs
state = dict(initial); out = array('i'); copy = None
def move(s, f):
    before = state[s]
    if before == f: return
    assert sub(before, f), ('descent frame nesting', s, before, f)
    gap = frames[f]['d'] - frames[before]['d']; assert gap >= 0
    out.extend((0, s, before, f, gap, 0)); state[s] = f
for k in range(0, len(old), 6):
    op, a, b, c, f, z = old[k:k+6]
    if op == 0: continue
    if op == 1:
        g = chosen.get(k//6, f)
        if copy is not None and k//6 in chosen: assert a != copy[0] and b != copy[0]
        move(a, g)
        if b == n: assert g == f == ZERO and copy is not None
        else: move(b, g)
        out.extend((op, a, b, c, g, z))
    elif op == 2:
        assert copy is None and b == n; move(a, c); state[b] = f; copy = (a, b, c); out.extend((op, a, b, c, f, z))
    else:
        assert op == 3 and copy == (a, b, c) and state[a] == c and state[b] == f
        out.extend((op, a, b, c, f, z)); del state[b]; copy = None
assert copy is None
for s in sorted(final): move(s, final[s])
assert state == final
def projection(a):
    return hashlib.sha256(b''.join(a[k:k+4].tobytes() + a[k+5:k+6].tobytes() for k in range(0, len(a), 6) if a[k])).hexdigest()
assert projection(old) == projection(out)
# independent census from needs and endpoints; ranks are exact dimension gaps
needs = {i: [] for i in initial}; copies = Counter(); copy = None
for k in range(0, len(out), 6):
    op, a, b, c, f, z = out[k:k+6]
    if op == 1:
        assert c % 2; needs[a].append(f)
        if b != n: needs[b].append(f)
        else: assert copy is not None and f == ZERO
    elif op == 2: assert copy is None; copy = (a, b, c); needs[a].append(c); copies[frames[c]['d']] += 1
    elif op == 3: assert copy == (a, b, c); copy = None
assert copy is None and copies == {22: 24}
census = Counter(copies); pairs = set()
for s, before in initial.items():
    for f in needs[s] + [final[s]]:
        assert sub(before, f); r = frames[f]['d'] - frames[before]['d']
        if r: census[r] += 1
        pairs.add((before, f)); before = f
for f in {f for pair in pairs for f in pair}: assert nondeg(f)
for a, b in pairs: assert len(frames[b]['A']) <= len(frames[a]['A']) and all(dot(x, y) == 0 for x in frames[b]['A'] for y in frames[a]['B'])
for t in range(v):
    f = final[v+t]; assert frames[f]['d'] == 23 and all(dot(cov[t], b) == 0 for b in frames[f]['B'])
hist = Counter(); state = dict(initial); copy = None; count = 0
for k in range(0, len(out), 6):
    op, a, b, c, f, z = out[k:k+6]
    if op == 0:
        assert state[a] == b and sub(b, c) and frames[c]['d'] - frames[b]['d'] == f; state[a] = c
        if f: hist[f] += 1
    elif op == 1: assert state[a] == state[b] == f and a != b; count += 1
    elif op == 2: assert copy is None and state[a] == c and f == ZERO and z == 22; state[b] = f; hist[z] += 1; copy = (a, b, c)
    else: assert copy == (a, b, c) and state[a] == c and state[b] == f == ZERO; del state[b]; copy = None
assert state == final and hist == census and copy is None
replay = json.loads((LEAD/'COHORT249-REPLAY.json').read_text())
oldH = Counter({int(r): c for r, c in replay['histogram'].items()})
delta = Counter(hist); delta.subtract(oldH); delta = {r: c for r, c in delta.items() if c}
assert delta == {int(r): c for r, c in sel['expected_local_histogram_delta'].items()}, ('histogram delta', delta)
assert sum(r*c for r, c in hist.items()) == sum(r*c for r, c in oldH.items()) == replay['new_rank_mass'] == sel['expected_rank_mass']
assert sum(hist.values()) == sum(oldH.values()) - sel['expected_removed_calls'] and count == sel['expected_scalar_additions']
(LEAD/'COHORT249-PRE-DESCENT-RECORDS.bin').write_bytes(old.tobytes())
(LEAD/'COHORT249-RECORDS.bin').write_bytes(out.tobytes())
# 'delta' stays the total change against the pinned PR249 baseline, which the price checker rebuilds from it.
combined = Counter({int(r): c for r, c in replay['delta'].items()}); combined.update(delta); combined = {r: c for r, c in combined.items() if c}
replay.update(status='PASS_FULL_CURRENT249_COHORT_REWRITE_AND_CONCAVE_DESCENT_RETIMING', cohort_rewrite_records=len(old)//6, new_records=len(out)//6,
              cohort_rewrite_histogram=replay['histogram'], cohort_rewrite_delta=replay['delta'], histogram={str(r): c for r, c in sorted(hist.items())},
              delta={str(r): c for r, c in sorted(combined.items())}, descent_delta={str(r): c for r, c in sorted(delta.items())},
              descent_retimed_gates=len(changed), descent_removed_calls=sel['expected_removed_calls'])
(LEAD/'COHORT249-REPLAY.json').write_text(json.dumps(replay, indent=2) + '\n')
receipt = dict(status='PASS_CONCAVE_DESCENT_RETIMING_AND_BOTH_REFLECTED_LEDGERS', selected_gate_count=len(changed), changed_gates=changed,
               removed_calls=sel['expected_removed_calls'], local_histogram_delta={str(r): c for r, c in sorted(delta.items())},
               rank_mass=sum(r*c for r, c in hist.items()), paid_calls=sum(hist.values()), scalar_additions=count,
               identical_scalar_and_copy_projection=True, both_reflected_ledgers=True, unchanged_all_input_output_frames=True,
               unchanged_copy_lifetimes=True, operand_source_spans_contained=True, checked_operand_spans=sum(len(s) for s in spans.values()),
               unique_required_frame_pairs=len(pairs), input_record_sha256=sel['input_record_sha256'], output_record_sha256=hashlib.sha256(out.tobytes()).hexdigest(),
               selection_sha256=hashlib.sha256(SEL.read_bytes()).hexdigest())
(LEAD/'DESCENT-RETIMING.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS concave descent retiming', len(changed), 'gates', sum(hist.values()), 'paid calls', len(out)//6, 'records', flush=True)
