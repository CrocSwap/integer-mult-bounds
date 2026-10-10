#!/usr/bin/env python3
"""Exact F2 target-prefix compression (PR268's mechanism) on the cohort-rewritten native transcript.

A group is one dependent target t with retained targets p_1..p_k, a cut and a close record, and a common close
frame F inside every member's cap.  The dependent's reads in (cut, close] are omitted; at the cut it receives
t -= p_j at the zero frame, and at the close t += p_j at F, after moving every member to F.  The transform
recomputes each member's literal prefix response from the actual transcript and requires the F2 dependency
R_t = sum_j R_pj before emitting anything; it then rebuilds every MOVE from the actual needs and checks nested
chains, fixed endpoints, COPY lifetimes, nondegenerate endpoint bases and forward/inverse all-column replays.
Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import hashlib, json, sys
if not __debug__: raise SystemExit('assertions required')
X, LEAD, SEL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
H = 24
def dot(x, y): return sum(p*q for p, q in zip(x, y))
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
def _introw(r):
    from fractions import Fraction as _F
    from math import lcm as _lcm
    q = [_F(str(x)) for x in r]; d = 1
    for x in q: d = _lcm(d, x.denominator)
    return [int(x*d) for x in q]
frames = {}
for name in (X/'frames.json', LEAD/'COHORT249-FRAMES.json'):
    j = json.loads(name.read_text()); j = j.get('frames', j)
    for k, rec_ in j.items(): frames[int(k)] = dict(B=[_introw(r) for r in rec_['B']], A=[_introw(r) for r in rec_['A']], d=int(rec_['dim']))
for f, fr in frames.items(): assert len(fr['B']) == fr['d'] and len(fr['A']) + fr['d'] == H and all(dot(a, b) == 0 for a in fr['A'] for b in fr['B'])
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
cov = [list(map(int, c)) for c in st['source_covectors']]
initial = {int(k): f for k, f in json.loads((LEAD/'COHORT249-INITIAL.json').read_text()).items()}
sel = json.loads(SEL.read_text()); cut = sel['cut_record']
old = array('i'); old.frombytes((LEAD/'COHORT249-RECORDS.bin').read_bytes()); assert old.itemsize == 4 and len(old) % 6 == 0
assert hashlib.sha256(old.tobytes()).hexdigest() == sel['input_record_sha256'] and len(old)//6 == sel['input_record_count']
final = dict(initial)
for k in range(0, len(old), 6):
    if old[k] == 0: final[old[k+1]] = old[k+3]
groups = []; owner = {}; atclose = defaultdict(list); dep_of = {}
for j, g in enumerate(sel['groups']):
    t, ps, close, F = g['dependent'], list(g['retained']), g['close_after_record'], g['frame']
    assert close > cut and len(ps) >= 1 and t not in ps and len(set(ps)) == len(ps)
    assert frames[F]['d'] == g['close_rank'] and nondeg(F)
    for m in [t] + ps:
        assert m not in owner; owner[m] = j
        assert initial[v+m] == ZERO and all(dot(cov[m], b) == 0 for b in frames[F]['B']), 'close frame outside a member cap'
    dep_of[t] = j; atclose[close].append(j); groups.append(dict(dependent=t, retained=ps, close=close, frame=F))
assert len(groups) == sel['selected_groups'] > 0
# literal prefix responses and member states from the actual transcript
cols = [1 << i for i in range(n)]; center = None; responses = {m: 0 for m in owner}; state = dict(initial); state_at_close = {}
for k in range(0, len(old), 6):
    op, a, b, c, f, z = old[k:k+6]; i = k//6
    if op == 0: state[a] = c
    elif op == 1:
        src = center if b == n else b; assert src is not None
        if i > cut:
            if src - v in owner: assert i > groups[owner[src-v]]['close'], 'active group target used as a source'
            if a - v in owner and i <= groups[owner[a-v]]['close']:
                assert not (v <= src < 2*v), 'target source inside an active prefix'; responses[a-v] ^= cols[src]
        assert c % 2; cols[a] ^= cols[src]
    elif op == 2: assert center is None; center = a; state[b] = f
    elif op == 3: assert center == a; center = None; del state[b]
    for j in atclose.get(i, []):
        g = groups[j]; R = responses[g['dependent']]
        for p in g['retained']: R ^= responses[p]
        assert R == 0, ('literal prefix dependency fails', j)
        for m in [g['dependent']] + g['retained']: assert sub(state[v+m], g['frame']), ('member frame not inside close frame', j, m)
assert center is None
# emit
zmax = max(old[k+5] for k in range(0, len(old), 6) if old[k] == 1); SETUP, RESTORE = zmax + 1, zmax + 2
state = dict(initial); out = array('i'); center = None; deleted = []; inserted = 0
def move(s, f):
    before = state[s]
    if before == f: return
    assert sub(before, f), ('nonnested actual use', s, before, f)
    gap = frames[f]['d'] - frames[before]['d']; assert gap >= 0; out.extend((0, s, before, f, gap, 0)); state[s] = f
def add(a, b, c, f, z): move(a, f); move(b, f); out.extend((1, a, b, c, f, z))
for k in range(0, len(old), 6):
    op, a, b, c, f, z = old[k:k+6]; i = k//6
    if op == 1:
        j = dep_of.get(a - v)
        if j is not None and cut < i <= groups[j]['close']: assert not (v <= b < 2*v); deleted.append(i)
        else: add(a, b, c, f, z)
    elif op == 2: assert center is None; move(a, c); out.extend((op, a, b, c, f, z)); state[b] = f; center = (a, b, c)
    elif op == 3: assert center == (a, b, c) and state[a] == c and state[b] == f; out.extend((op, a, b, c, f, z)); del state[b]; center = None
    if i == cut:
        assert center is None and all(state[v+m] == ZERO for m in owner)
        for g in groups:
            for p in g['retained']: add(v+g['dependent'], v+p, -1, ZERO, SETUP); inserted += 1
    for j in atclose.get(i, []):
        g = groups[j]
        for m in [g['dependent']] + g['retained']: move(v+m, g['frame'])
        for p in g['retained']: add(v+g['dependent'], v+p, 1, g['frame'], RESTORE); inserted += 1
for s in sorted(final): move(s, final[s])
assert center is None and state == final
# census from needs, independent of emitted MOVEs
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
# forward and inverse all-column replays with arbitrary dirty contents
def replay(records, reverse=False, omit=None):
    columns = [1 << i for i in range(n)]; wanted = columns[:]; center = None; cnt = 0
    for t in range(v): wanted[v+t] ^= 1 << t
    for k in (range(len(records)-6, -1, -6) if reverse else range(0, len(records), 6)):
        op, a, b, c, f, z = records[k:k+6]
        if op == 1:
            if b == n: assert center is not None; b = center
            if k//6 == omit: continue
            assert c % 2 and a != b; columns[a] ^= columns[b]; cnt += 1
        elif op == (3 if reverse else 2): assert center is None; center = a
        elif op == (2 if reverse else 3): assert center == a; center = None
    assert center is None and columns == wanted, 'all-column endpoint failure'
    return cnt
assert replay(out) == replay(out, True) == count
first_setup = next(k//6 for k in range(0, len(out), 6) if out[k] == 1 and out[k+5] == SETUP)
try: replay(out, omit=first_setup)
except AssertionError: negative = 'omitted target-prefix setup rejected'
else: raise AssertionError('missing setup admitted')
replay_path = LEAD/'COHORT249-REPLAY.json'
if replay_path.exists():
    replay_json = json.loads(replay_path.read_text()); oldH = Counter({int(r): c for r, c in replay_json['histogram'].items()})
else:
    replay_json = None; oldH = Counter({22: 24})
    for k in range(0, len(old), 6):
        if old[k] == 0 and old[k+4]: oldH[old[k+4]] += 1
delta = Counter(hist); delta.subtract(oldH); delta = {r: c for r, c in delta.items() if c}
assert delta == {int(r): c for r, c in sel['expected_local_histogram_delta'].items()}, ('histogram delta', delta)
assert sum(r*c for r, c in hist.items()) == sum(r*c for r, c in oldH.items()) and (replay_json is None or sum(r*c for r, c in hist.items()) == replay_json['new_rank_mass'])
assert (len(deleted), inserted, count) == (sel["expected_deleted_reads"], sel["expected_inserted_additions"], sel["expected_scalar_additions"]), ("counts", len(deleted), inserted, count)
(LEAD/'COHORT249-PRE-TARGET-RECORDS.bin').write_bytes(old.tobytes())
(LEAD/'COHORT249-RECORDS.bin').write_bytes(out.tobytes())
if replay_json is not None:
    combined = Counter({int(r): c for r, c in replay_json['delta'].items()}); combined.update(delta); combined = {r: c for r, c in combined.items() if c}
    replay_json.update(status='PASS_FULL_CURRENT249_COHORT_REWRITE_AND_TARGET_PREFIX_COMPRESSION', pre_target_records=len(old)//6, new_records=len(out)//6,
                       pre_target_histogram=replay_json['histogram'], pre_target_delta=replay_json['delta'], histogram={str(r): c for r, c in sorted(hist.items())},
                       delta={str(r): c for r, c in sorted(combined.items())}, target_prefix_delta={str(r): c for r, c in sorted(delta.items())},
                       target_prefix_groups=len(groups), target_prefix_deleted_reads=len(deleted), target_prefix_setup_restore_additions=inserted)
    (LEAD/'COHORT249-REPLAY.json').write_text(json.dumps(replay_json, indent=2) + '\n')
receipt = dict(status='PASS_EXACT_F2_TARGET_PREFIX_COMPRESSION', selected_groups=len(groups), targets=len(owner), cut_record=cut, deleted_prefix_adds=len(deleted),
               inserted_setup_restore_adds=inserted, literal_prefix_dependencies_checked=True, remaining_payload_additions=count,
               local_histogram_delta={str(r): c for r, c in sorted(delta.items())}, rank_mass=sum(r*c for r, c in hist.items()), paid_calls=sum(hist.values()),
               both_reflected_ledgers=True, unchanged_all_input_output_frames=True, unchanged_copy_lifetimes=True, forward_and_inverse_all_columns=True,
               negative_control=negative, unique_required_frame_pairs=len(pairs), setup_category=SETUP, restore_category=RESTORE,
               input_record_sha256=sel['input_record_sha256'], output_record_sha256=hashlib.sha256(out.tobytes()).hexdigest(), selection_sha256=hashlib.sha256(SEL.read_bytes()).hexdigest())
(LEAD/'TARGET-PREFIX.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS target prefix', len(groups), 'groups', count, 'ADDs', sum(hist.values()), 'paid calls', len(out)//6, 'records', flush=True)
