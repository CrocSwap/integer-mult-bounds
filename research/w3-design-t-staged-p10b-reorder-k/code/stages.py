"""Transcript stages on the Design T word (PR249 snapshots), each bound to a frozen selection:
  kernel  - shared-donor response-kernel entries (our #329 kernel mechanism; #272/#299/#319/#320 lineage), re-derived
            on the post-Design-T helper population;
  retime  - gate-frame retiming (our #329 descent2; #287/#291/#299 lineage);
  reorder - an ADD moves next to a neighbouring incidence of an operand, at that frame (our #329 reorder; #299/#306).
usage: stages.py STAGE IN_DIR OUT_DIR SELECTION.json LABELS.json
Each stage checks that the selection is bound to the exact input records, applies it, and runs stagelib.full_check
(legality, final frames, exact frames and nondegeneracy, formal F2 of every column, source spans); the output records
hash must equal the selection's frozen one.
Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance; Apache-2.0."""
import sys, json
from collections import defaultdict
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import stagelib as L
from stagelib import key_of


def table(fr, keep):
    FR = dict(fr['frames']); dim = L.dims(fr); bykey = {}
    for k, F in FR.items():
        if keep(len(F['B'])): bykey.setdefault(key_of(F['B']), int(k))
    return FR, dim, bykey, [max(int(k) for k in FR) + 1]


def fid(basis, FR, dim, bykey, nxt):
    kk = key_of(basis)
    if kk not in bykey:
        B = [list(map(int, r)) for r in basis]; f = nxt[0]; nxt[0] += 1
        FR[str(f)] = {'B': B, 'A': L.kernel_int(B), 'dim': len(B)}; bykey[kk] = f; dim[f] = len(B)
    return bykey[kk]


def kernel(snap, sel):
    """pivot p starts at E and loses its frame-ZERO completion reads (cat 4); after the last completion read of any
    member, each donor climbs to E (nested along its entries) and pays d += p at E (cat 44); at the end it pays
    d -= p at FULL (cat 45). Requires response(p) = XOR responses(donors) (checked by the F2 replay)."""
    s, fr, rec = snap['s'], snap['fr'], snap['rec']
    n, ZERO, FULL = s['n'], s['ZERO'], s['FULL']
    FR, dim, bykey, nxt = table(fr, lambda d: 1 <= d <= 12)
    ents = [dict(pivot=e['pivot'], donors=list(e['donors']), E=fid(e['basis'], FR, dim, bykey, nxt), rank=len(e['basis'])) for e in sel]
    pivots = {x['pivot'] for x in ents}; donors = {d for x in ents for d in x['donors']}
    assert len(pivots) == len(ents) and not (pivots & donors), 'pivot repeated or used as a donor'
    members = pivots | donors
    for m in members: assert s['initial'][str(m)] == ZERO and s['final'][str(m)] == FULL
    reads = (rec[:, 0] == 1) & (rec[:, 5] == 4) & (rec[:, 4] == ZERO)
    drop = reads & np.isin(rec[:, 2], list(pivots))
    cut = int(np.nonzero(reads & np.isin(rec[:, 2], list(members)))[0].max())
    first = {}
    for k, (o, a, b, c, f, z) in enumerate(rec.tolist()):
        if o == 0 and a in members and a not in first: first[a] = k
        if k <= cut and o == 1 and not reads[k] and (a in members or b in members): raise AssertionError('member touched before the cut')
        if k <= cut and o == 0 and a in members: raise AssertionError('member moved before the cut')
    fs = L.Frames(dict(h=fr['h'], frames=FR))
    for x in ents: assert fs.nondeg(x['E']) and fs.frame_ok(x['E'])
    ents.sort(key=lambda x: (x['rank'], x['pivot']))
    dstate = {}; setup = []
    for x in ents:
        for d in x['donors']:
            cur = dstate.get(d, ZERO)
            if cur != x['E']:
                assert fs.sub(cur, x['E']), ('donor chain not nested', d)
                setup.append([0, d, cur, x['E'], dim[x['E']] - dim[cur], 0]); dstate[d] = x['E']
            setup.append([1, d, x['pivot'], 1, x['E'], 44])
    modify = {}
    for x in ents:
        k = first[x['pivot']]; r = rec[k].tolist(); assert r[2] == ZERO and fs.sub(x['E'], r[3])
        r[2] = x['E']; r[4] = dim[r[3]] - dim[x['E']]; modify[k] = r
    for d, E in dstate.items():
        k = first[d]; r = rec[k].tolist(); assert r[2] == ZERO and fs.sub(E, r[3])
        r[2] = E; r[4] = dim[r[3]] - dim[E]; modify[k] = r
    out = []
    for k, r in enumerate(rec.tolist()):
        if drop[k]: continue
        out.append(modify.get(k, r))
        if k == cut: out.extend(setup)
    for x in ents:
        for d in x['donors']: out.append([1, d, x['pivot'], -1, FULL, 45])
    st = dict(s); ni = dict(s['initial'])
    for x in ents: ni[str(x['pivot'])] = x['E']
    out = np.array(out, dtype=np.int32); st['initial'] = ni; st['record_count'] = len(out)
    print('kernel: %d entries, total entrance rank %d, %d donors, %d completion reads removed, %d setups + %d restores'
          % (len(ents), sum(x['rank'] for x in ents), len(dstate), int(drop.sum()), sum(len(x['donors']) for x in ents), sum(len(x['donors']) for x in ents)))
    return dict(s=st, fr=dict(h=fr['h'], frames=FR), rec=out)


def jit(s, seq, dim):
    """re-emit MOVEs just in time: every operand climbs to the gate frame right before its use; final climbs at the end"""
    n = s['n']; state = {r: s['initial'][str(r)] for r in range(n)}; out = []
    def mv(r, f):
        if state[r] != f: out.append([0, r, state[r], f, dim[f] - dim[state[r]], 0]); state[r] = f
    for o, a, b, c, f, z in seq:
        if o == 1:
            mv(a, f)
            if b != n: mv(b, f)
        elif o == 2: mv(a, c)
        out.append([o, a, b, c, f, z])
    for r in range(n): mv(r, s['final'][str(r)])
    return np.array(out, dtype=np.int32)


def retime(snap, sel):
    s, fr, rec = snap['s'], snap['fr'], snap['rec']
    FR, dim, bykey, nxt = table(fr, lambda d: True)
    gate = {}
    for e in sel:
        k = e['record']; r = rec[k].tolist(); assert r[0] == 1 and [r[1], r[2], r[3], r[5]] == e['scalar'], e
        gate[k] = fid(e['new_basis'], FR, dim, bykey, nxt)
    seq = []
    for k, r in enumerate(rec.tolist()):
        if r[0] == 0: continue
        if k in gate: r[4] = gate[k]
        seq.append(r)
    out = jit(s, seq, dim); st = dict(s); st['record_count'] = len(out)
    print('retime: %d gates moved to new frames' % len(gate))
    return dict(s=st, fr=dict(h=fr['h'], frames=FR), rec=out)


def reorder(snap, sel):
    s, fr, rec = snap['s'], snap['fr'], snap['rec']; n = s['n']
    FR, dim, bykey, nxt = table(fr, lambda d: True)
    moved = set(); before = defaultdict(list); after = defaultdict(list)
    reads = defaultdict(list); writes = defaultdict(list)
    for i, (o, a, b, c, f, z) in enumerate(rec.tolist()):
        if o == 1:
            writes[a].append(i)
            if b != n: reads[b].append(i)
        elif o in (2, 3): reads[a].append(i)
    for e in sel:
        i = e['record']; r = rec[i].tolist(); a, b = r[1], r[2]; assert r[0] == 1 and [a, b, r[3]] == e['incidence']
        T = e['anchor']; lo, hi = (i + 1, T) if e['side'] == 'before' else (T + 1, i)
        assert not any(lo <= t < hi for t in reads[a]) and not any(lo <= t < hi for t in writes[b]), 'crossed gate reads a or writes b'
        r[4] = fid(e['frame_basis'], FR, dim, bykey, nxt); moved.add(i)
        (before if e['side'] == 'before' else after)[T].append(r)
    seq = []
    for k, r in enumerate(rec.tolist()):
        if r[0] == 0 or k in moved: continue
        seq.extend(before.get(k, [])); seq.append(r); seq.extend(after.get(k, []))
    out = jit(s, seq, dim); st = dict(s); st['record_count'] = len(out)
    print('reorder: %d ADDs moved' % len(moved))
    return dict(s=st, fr=dict(h=fr['h'], frames=FR), rec=out)


if __name__ == '__main__':
    stage, src, dst, selp, labp = sys.argv[1:6]
    snap = L.load_snapshot(src); sel = json.load(open(selp))
    assert sel['stage'] == stage and L.rec_sha(snap) == sel['input_records_sha256'], 'selection not bound to this input word'
    out = dict(kernel=kernel, retime=retime, reorder=reorder)[stage](snap, sel['entries'])
    L.full_check(out, L.labels_chi(labp), tag='   ' + stage)
    got = L.rec_sha(out); assert got == sel['output_records_sha256'], ('output hash', got)
    L.save_snapshot(out, dst); print('   %s output records %s... (frozen hash)' % (stage, got[:16]))
