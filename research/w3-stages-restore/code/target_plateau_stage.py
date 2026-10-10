#!/usr/bin/env python3
"""Exact target-prefix compression (PR268/PR273 mechanism) ported to the w3 (#310) bit word.

usage: target_prefix_w3.py CAND_DIR SELECTION.json OUT_DIR [PLATEAU.json]

Optional PLATEAU.json: plateau ascent retiming - listed ADD gates (original record index) move from old_frame
to new_frame (new frames supplied with exact integer B/A, appended to COHORT249-FRAMES.json); operands of
retimed gates are re-MOVEd lazily like group members.

A group is a dependent target register t, retained target registers p_1..p_k with signs e_j in {+1,-1},
a close record c and a close frame F.  At the global cut (all targets in ZERO, all ZERO-frame target reads
done) the transform emits t += (-e_j) p_j at ZERO; the dependent's own ADDs in (cut, c] are deleted; right
after record c it emits t += e_j p_j at F.  Legal iff the integer window response R_t(cut,c] equals
sum_j e_j R_pj(cut,c].  The script re-derives every response from the actual word (exact F2 columns and an
integer fingerprint mod 2^61-1 with 4 independent pseudo-random dirty inputs), then re-emits MOVEs for the
group members only (lazy: each member is moved just before each use; all other registers keep their
original MOVE records), and checks: nested chains, common-frame ADDs, COPY lifecycle, final frames,
forward/inverse F2 all-column replays, an integer replay mod 2^61-1 equal on every register to the
original word, and the source-span rule (every non-target ADD operand's exact source content lies in the
gate frame), on both the input and the output.
"""
import hashlib, json, random, shutil, struct, sys, math
from array import array
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
if not __debug__: raise SystemExit('assertions required')
CAND, SELP, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
PLAT = json.loads(Path(sys.argv[4]).read_text()) if len(sys.argv) > 4 else dict(gates=[], new_frames={})
H = 24; Q = (1 << 61) - 1; M = 120
def phi(r): return r * math.log(M / r) if r > 0 else 0.0

st = json.loads((CAND / '249-states.json').read_text()); n, v = st['n'], st['v']; ZERO, FULL = st['ZERO'], st['FULL']
cov = np.array(st['source_covectors'], dtype=np.int64)
frj = json.loads((CAND / 'frames.json').read_text())['frames']
dim = {int(k): int(f['dim']) for k, f in frj.items()}
Bm = {int(k): np.array(f['B'], dtype=np.int64).reshape(-1, H) for k, f in frj.items()}
Am = {int(k): np.array(f['A'], dtype=np.int64).reshape(-1, H) for k, f in frj.items()}
del frj
newframes = json.loads((CAND / 'COHORT249-FRAMES.json').read_text())
added = {int(k): fr for k, fr in PLAT['new_frames'].items()}
for k, fr in added.items():
    assert k not in dim and len(fr['B']) == fr['dim'] and len(fr['A']) + fr['dim'] == H
    B_, A_ = np.array(fr['B'], dtype=np.int64), np.array(fr['A'], dtype=np.int64)
    assert not np.any(B_ @ A_.T) and np.linalg.matrix_rank(B_.astype(float)) == fr['dim'] and np.linalg.matrix_rank(A_.astype(float)) == H - fr['dim']
    dim[k] = fr['dim']; Bm[k] = B_; Am[k] = A_
for k in newframes: assert int(k) in dim
initial = {int(k): f for k, f in json.loads((CAND / 'COHORT249-INITIAL.json').read_text()).items()}
final = {int(k): f for k, f in st['final'].items()}
raw = (CAND / 'COHORT249-RECORDS.bin').read_bytes()
old = list(struct.iter_unpack('<6i', raw))
sel = json.loads(SELP.read_text()); CUT = sel['cut_record']
assert hashlib.sha256(raw).hexdigest() == sel['input_record_sha256'] == st['record_sha256'] and len(old) == sel['input_record_count']
subc = {}
def sub(a, b):
    if a == b: return True
    k = (a, b)
    if k not in subc:
        subc[k] = dim[a] <= dim[b] and (Bm[a].shape[0] == 0 or Am[b].shape[0] == 0 or not np.any(Bm[a] @ Am[b].T))
    return subc[k]
istarget = lambda r: v <= r < 2 * v

# ---------- groups ----------
groups = sel['groups']; dep_of = {}; atclose = defaultdict(list); members = set(); retained = set()
for j, g in enumerate(groups):
    t, ps, sg, c, F = g['dependent'], g['retained'], g['signs'], g['close_after_record'], g['frame']
    assert istarget(t) and all(istarget(p) for p in ps) and t not in ps and len(set(ps)) == len(ps) and len(sg) == len(ps)
    assert all(s in (1, -1) for s in sg) and c > CUT and dim[F] == g['close_rank']
    assert t not in dep_of; dep_of[t] = j; atclose[c].append(j); members.update([t] + ps); retained.update(ps)
    assert all(not np.any(Bm[F] @ cov[m - v]) for m in [t] + ps), 'close frame outside a member cap'
assert not (set(dep_of) & retained), 'a dependent is also retained'

# ---------- literal responses (F2 columns + integer fingerprints) on the original word ----------
K = 4; rng = random.Random(0x5EED310)
val = [[rng.randrange(Q) for _ in range(K)] for _ in range(n + 1)]
cols = [1 << i for i in range(n)] + [0]
resF = {m: 0 for m in members}; resI = {m: [0] * K for m in members}
state = dict(initial); center = None; cpos = None; deleted = 0
for i, (op, a, b, c, f, z) in enumerate(old):
    if op == 0: state[a] = c
    elif op == 1:
        if i > CUT:
            if b in dep_of: assert i > groups[dep_of[b]]['close_after_record'], 'active dependent used as a source'
            if a in members and (a not in dep_of or i <= groups[dep_of[a]]['close_after_record']):
                if a in dep_of: assert not istarget(b), 'target source inside a dependent prefix'; deleted += 1
                resF[a] ^= cols[b]; resI[a] = [(x + c * y) % Q for x, y in zip(resI[a], val[b])]
        cols[a] ^= cols[b] if c % 2 else 0
        val[a] = [(x + c * y) % Q for x, y in zip(val[a], val[b])]
    elif op == 2: assert center is None; center = a; cols[n] = cols[a]; val[n] = list(val[a]); state[n] = f
    elif op == 3: center = None; cols[n] = 0; del state[n]
    if i == CUT:
        assert center is None and all(state[m] == ZERO for m in members), 'cut not at ZERO'
        resF = {m: 0 for m in members}; resI = {m: [0] * K for m in members}
    for j in atclose.get(i, []):
        g = groups[j]; t = g['dependent']; RF = resF[t]; RI = list(resI[t])
        for p, s in zip(g['retained'], g['signs']):
            RF ^= resF[p]; RI = [(x - s * y) % Q for x, y in zip(RI, resI[p])]
        assert RF == 0 and RI == [0] * K, ('window dependency fails', j)
        assert center is None
print('dependencies checked', len(groups), 'groups; deleted dependent reads', deleted, flush=True)
assert deleted > 0

retime = {}
for gte in PLAT['gates']:
    i = gte['record']; assert old[i][0] == 1 and old[i][4] == gte['old_frame'] and i not in retime and old[i][2] != n
    retime[i] = gte['new_frame']
    members.update([old[i][1], old[i][2]])
# ---------- emit ----------
zmax = max(e[5] for e in old if e[0] == 1); SETUP, RESTORE = zmax + 1, zmax + 2
out = []; state = dict(initial); inserted = 0
def move(r, f):
    if state[r] == f: return
    assert sub(state[r], f), ('nonnested use', r, state[r], f)
    out.append((0, r, state[r], f, dim[f] - dim[state[r]], 0)); state[r] = f
def need(r, f):
    if r in members: move(r, f)
for i, e in enumerate(old):
    op, a, b, c, f, z = e
    if op == 0:
        if a in members: continue
        assert state[a] == b; out.append(e); state[a] = c
    elif op == 1:
        if a in dep_of and CUT < i <= groups[dep_of[a]]['close_after_record']: pass
        else:
            if i in retime: f = retime[i]; e = (op, a, b, c, f, z)
            need(a, f); need(b, f); out.append(e)
    elif op == 2:
        need(a, c); out.append(e); state[n] = f
    elif op == 3:
        out.append(e); del state[n]
    if i == CUT:
        for g in groups:
            for p, s in zip(g['retained'], g['signs']):
                move(g['dependent'], ZERO); move(p, ZERO); out.append((1, g['dependent'], p, -s, ZERO, SETUP)); inserted += 1
    for j in atclose.get(i, []):
        g = groups[j]
        for p, s in zip(g['retained'], g['signs']):
            move(g['dependent'], g['frame']); move(p, g['frame']); out.append((1, g['dependent'], p, s, g['frame'], RESTORE)); inserted += 1
for r in sorted(members): move(r, final[r])
assert state == final

# ---------- independent checks ----------
def legality(recs):
    state = dict(initial); hist = Counter(); copied = False; cs = None
    for (op, a, b, c, f, z) in recs:
        if op == 0:
            assert state[a] == b and sub(b, c) and dim[c] - dim[b] == f; state[a] = c
            if f: hist[f] += 1
        elif op == 1:
            assert state[a] == f and state[b] == f and a != b and c % 2
            if copied: assert a != cs and a != n
        elif op == 2: assert not copied and b == n and state[a] == c and z == dim[c]; copied = True; cs = a; state[n] = f; hist[z] += 1
        else: assert copied and a == cs and state[a] == c and state[n] == f; copied = False; del state[n]
    assert not copied and all(state[s] == final[s] for s in range(n))
    return hist
def f2_replay(recs, reverse=False):
    columns = [1 << i for i in range(n)] + [0]; wanted = [1 << i for i in range(n)]
    for t in range(v): wanted[v + t] ^= 1 << t
    rng_ = range(len(recs) - 1, -1, -1) if reverse else range(len(recs)); center = None
    for k in rng_:
        op, a, b, c, f, z = recs[k]
        if op == 1:
            if c % 2: columns[a] ^= columns[b]
        elif op == (3 if reverse else 2): assert center is None; center = a; columns[n] = columns[a]
        elif op == (2 if reverse else 3): center = None; columns[n] = 0
    assert columns[:n] == wanted, 'F2 all-column endpoint failure'
def int_replay(recs, seed):
    r = random.Random(seed); val = [r.randrange(Q) for _ in range(n)] + [0]
    for (op, a, b, c, f, z) in recs:
        if op == 1: val[a] = (val[a] + c * val[b]) % Q
        elif op == 2: val[n] = val[a]
        elif op == 3: val[n] = 0
    return val[:n]
def source_span(recs):
    """every non-target ADD operand's exact integer source content lies in the gate frame"""
    # exact source content: x-source i holds the basis vector of its (rank-1) initial frame; helpers/targets 0.
    # The COPY temporary (role n, copied-center scatter in the ZERO frame) is the COPY mechanism's own
    # projection and is exempt, exactly as in the input word.
    content = np.zeros((n + 1, H), dtype=np.int64); checked = 0; maxabs = 0
    for i in range(v):
        assert dim[initial[i]] == 1; content[i] = Bm[initial[i]][0]
    Abad = 0
    for (op, a, b, c, f, z) in recs:
        if op == 1:
            for r in (a, b):
                if istarget(r) or r == n: continue
                if Am[f].shape[0] and np.any(Am[f] @ content[r]): Abad += 1
                checked += 1
            content[a] += c * content[b]
            if abs(content[a]).max() > 1 << 40: raise OverflowError
        elif op == 2: content[n] = content[a]
        elif op == 3: content[n] = 0
    maxabs = int(abs(content).max())
    return checked, Abad, maxabs

hist_old = legality(old); hist_new = legality(out)
print('legality ok', flush=True)
for recs in (old, out): f2_replay(recs); f2_replay(recs, True)
print('F2 forward/inverse ok', flush=True)
for seed in (1, 2, 3):
    assert int_replay(old, seed) == int_replay(out, seed), 'integer final values differ'
print('integer replays equal (3 seeds, mod 2^61-1)', flush=True)
sp_old = source_span(old); sp_new = source_span(out)
print('source span old (checked, violations, maxabs)', sp_old, 'new', sp_new, flush=True)
assert sp_new[1] <= sp_old[1], 'new source-span violations'
delta = Counter(hist_new); delta.subtract(hist_old); delta = {r: c for r, c in sorted(delta.items()) if c}
dphi = sum(c * phi(r) for r, c in hist_new.items()) - sum(c * phi(r) for r, c in hist_old.items())

# ---------- write candidate ----------
OUT.mkdir(parents=True, exist_ok=True)
outb = b''.join(struct.pack('<6i', *e) for e in out)
(OUT / 'COHORT249-RECORDS.bin').write_bytes(outb)
(OUT / '249-records.bin').write_bytes(outb)
nf = dict(newframes); nf.update({str(k): fr for k, fr in added.items()})
(OUT / 'COHORT249-FRAMES.json').write_text(json.dumps(nf))
if added:
    fj = json.loads((CAND / 'frames.json').read_text()); fj['frames'].update({str(k): fr for k, fr in added.items()})
    (OUT / 'frames.json').write_text(json.dumps(fj)); del fj
else:
    shutil.copyfile(CAND / 'frames.json', OUT / 'frames.json')
for name in ('COHORT249-INITIAL.json', 'COHORT249-FINAL.json', 'SOURCE-BINDING.json', 'base-frames.json'):
    if (CAND / name).exists(): shutil.copyfile(CAND / name, OUT / name)
shutil.copyfile(CAND / 'COHORT249-SELECTION.json', OUT / 'COHORT249-SELECTION.json')
st['record_sha256'] = hashlib.sha256(outb).hexdigest(); st['record_count'] = len(out)
(OUT / '249-states.json').write_text(json.dumps(st))
rec = dict(status='PASS_W3_TARGET_PREFIX_COMPRESSION', plateau_retimed_gates=len(retime), plateau_new_frames=len(added), groups=len(groups), members=len(members), dependents=len(dep_of),
           retained_distinct=len(retained), cut_record=CUT, deleted_dependent_reads=deleted, inserted_setup_restore_adds=inserted,
           records_in=len(old), records_out=len(out), local_histogram_delta={str(r): c for r, c in delta.items()},
           local_phi_old=sum(c * phi(r) for r, c in hist_old.items()), local_phi_new=sum(c * phi(r) for r, c in hist_new.items()),
           delta_phi=dphi, predicted_delta_kappa=-6.45e-10 * dphi,
           source_span_checked_operands=sp_new[0], source_span_violations=sp_new[1], source_span_violations_input=sp_old[1],
           integer_replay='equal on all registers, 3 seeds mod 2^61-1', f2_all_columns='forward and inverse',
           input_record_sha256=sel['input_record_sha256'], output_record_sha256=st['record_sha256'],
           selection_sha256=hashlib.sha256(SELP.read_bytes()).hexdigest())
(OUT / 'TARGET-PREFIX-W3.json').write_text(json.dumps(rec, indent=2) + '\n')
print(json.dumps(rec, indent=1))
