"""Compensation search for H1+H1->H2 fusions on the #4610 word.

For each consecutive rank-1,rank-1 climb pair (f: E->F->G) whose intervening events are plain adds,
delete the first climb and the intervening events, climb E->G in one job, and ask whether every
"deficit" (the missing add contribution) can be delivered by free same-frame adds somewhere inside
the legal time window, using the exact rows of the fields that stand in that frame at that time.
Rows follow the convention of PR #5377's native.py (origin symbol x free warp word, rational coefficients).

Usage: py -3.12 compsearch.py backward|forward
Writes progress_<orient>.log and result_<orient>.json.
"""
import gzip, json, collections, sys, time
from fractions import Fraction as Q
ORIENT = sys.argv[1] if len(sys.argv) > 1 else 'backward'
import os
W = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'research', 'kappa-round3-warp-20261022', 'ACTUAL-WORD.json.gz')
LOG = open(f'progress_{ORIENT}.log', 'a', buffering=1)
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n')

w = json.load(gzip.open(W, 'rt', encoding='utf-8')); c = w['canonical']; fr = c['frames']
prog = w['programs'][ORIENT]; n = len(prog); backward = (ORIENT == 'backward')
NL = 632

# ---------- index events per role ----------
touch = collections.defaultdict(list)   # role -> [(idx, kind, partner)]
for i, e in enumerate(prog):
    k = e[0]
    if k == 'climb': touch[('L', e[2])].append((i, 'climb', None))
    elif k == 'warp': touch[tuple(e[1])].append((i, 'warp', None))
    elif k == 'center': touch[('C', e[1])].append((i, 'center', None))
    elif k == 'scalar':
        g = e[1]; d = tuple(g[1])
        if g[0] in ('add', 'copy'):
            s = tuple(g[2]); touch[d].append((i, 'dst:' + g[0], s)); touch[s].append((i, 'src:' + g[0], d))
        else: touch[d].append((i, 'dst:' + g[0], None))
def consuming(k):      # event kinds after which a pending deficit on the role can no longer be fixed locally
    return k in ('warp', 'center') or k.startswith('src') or k in ('dst:scale', 'dst:clear', 'dst:copy')

# ---------- candidate pairs and their deficits ----------
climbs = collections.defaultdict(list)
for i, e in enumerate(prog):
    if e[0] == 'climb': climbs[e[2]].append((i, e[3], e[4], e[5]))
cands = []
for f, cl in climbs.items():
    for (i1, E, F, r1), (i2, F2, G, r2) in zip(cl, cl[1:]):
        if r1 != 1 or r2 != 1: continue
        between = [t for t in touch[('L', f)] if i1 < t[0] < i2]
        if any(t[1] not in ('src:add', 'dst:add') for t in between): continue
        prv = max([t[0] for t in touch[('L', f)] if t[0] < i1], default=-1)
        nxt = min([t[0] for t in touch[('L', f)] if t[0] > i2 and consuming(t[1])], default=n)
        defs = []
        for j, k, P in between:
            q = Q(prog[j][1][3], prog[j][1][4])
            if k == 'src:add':   # P += q f deleted -> P lacks q*row_f(j); fix on P in [j, consume_P)
                cP = min([t[0] for t in touch[P] if t[0] > j and consuming(t[1])], default=n)
                defs.append(dict(X=P, Y=('L', f), q=q, j=j, windows=[(j, cP)]))
            else:                # f += q P deleted -> f lacks q*row_P(j); fix on f in (prv,i1) at E or (i2,nxt) at G
                defs.append(dict(X=('L', f), Y=P, q=q, j=j, windows=[(prv + 1, i1), (i1 + 1, nxt)]))
        for d in defs: d.update(f=('L', f), i1=i1, i2=i2, E=E, G=G)
        cands.append(dict(f=f, i1=i1, i2=i2, E=E, F=F, G=G, defs=defs))
log(ORIENT, 'candidate pairs', len(cands), 'deficits', sum(len(x['defs']) for x in cands))

# ---------- exact row engine ----------
def add_into(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv: dst[k] = nv
        else: dst.pop(k, None)
def apply(e, rows, frames):
    """apply one event; return the role touched"""
    k = e[0]
    if k == 'scalar':
        g, frame = e[1], e[2]; d = tuple(g[1])
        if g[0] == 'clear': rows[d] = {}; frames[d] = frame
        elif g[0] == 'copy': rows[d] = dict(rows[tuple(g[2])])
        elif g[0] == 'add': add_into(rows[d], rows[tuple(g[2])], Q(g[3], g[4]))
        elif g[0] == 'scale': rows[d] = {kk: Q(g[2], g[3]) * v for kk, v in rows[d].items()}
        return d
    if k == 'warp':
        d = tuple(e[1]); op = e[2]
        sym = (1 if op > 0 else -1) * (abs(op) + (10**6 if backward else 0))
        rows[d] = {(r, wd[1:] if wd and wd[0] == -sym else (sym,) + wd): q for (r, wd), q in rows[d].items()}
        frames[d] = e[4]; return d
    if k == 'climb': d = ('L', e[2]); frames[d] = e[4]; return d
    if k == 'center': d = ('C', e[1]); frames[d] = e[3]; return d
    return None
def fresh_state():
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(NL)}; rows[('C', 0)] = {(('C', 0), ()): Q(1)}
    frames = {('L', i): c['start'][i] for i in range(NL)}; frames[('C', 0)] = None
    return rows, frames

# ---------- pass 1: deficit vectors v = q*row_Y(j) ----------
need = collections.defaultdict(list)
for ci, cd in enumerate(cands):
    for di, d in enumerate(cd['defs']): need[d['j']].append((ci, di))
rows, frames = fresh_state()
for i, e in enumerate(prog):
    for ci, di in need.get(i, ()):
        d = cands[ci]['defs'][di]; d['v'] = {k: d['q'] * v for k, v in rows[d['Y']].items()}
    apply(e, rows, frames)
log('pass 1 done: deficit vectors stored')

# ---------- span test with memoised elimination per (frame, version) ----------
def reduce_basis(vecs):
    basis = []
    for role, row in vecs:
        r = dict(row); combo = {role: Q(1)}
        for pk, brow, bcombo in basis:
            if pk in r:
                coef = r[pk] / brow[pk]
                add_into(r, brow, -coef); add_into(combo, bcombo, -coef)
        if r:
            pk = min(r, key=repr); basis.append((pk, r, combo))
    return basis
def solve(basis, v):
    r = dict(v); combo = {}
    for pk, brow, bcombo in basis:
        if pk in r:
            coef = r[pk] / brow[pk]
            add_into(r, brow, -coef); add_into(combo, bcombo, coef)
    return (None if r else combo)
def dyadic(q): return (q.denominator & (q.denominator - 1)) == 0

# ---------- pass 2: sweep, test active deficits ----------
members = collections.defaultdict(set); version = collections.Counter()
rows, frames = fresh_state()
for r, fr_ in frames.items():
    if fr_ is not None: members[fr_].add(r)
active_by_start = collections.defaultdict(list)
for ci, cd in enumerate(cands):
    for di, d in enumerate(cd['defs']):
        d['found'] = {'early': None, 'late': None}; d['tests'] = 0
        for wi, (lo, hi) in enumerate(d['windows']):
            if lo < hi: active_by_start[lo].append((ci, di, wi))
active = []
cache = {}
t0 = time.time(); BIG = 80
for t, e in enumerate(prog):
    for (ci, di, wi) in active_by_start.get(t, ()):
        active.append([ci, di, wi, cands[ci]['defs'][di]['windows'][wi][1], None])
    if active:
        keep = []
        for it in active:
            ci, di, wi, hi, last = it
            d = cands[ci]['defs'][di]
            if t >= hi or all(d['found'].values()): continue
            ff, i1_, i2_, E_, G_ = d['f'], d['i1'], d['i2'], d['E'], d['G']
            for variant in ('early', 'late'):
                if d['found'][variant] is not None: continue
                X = d['X']
                # frame of f in the modified program at time t (before applying event t)
                if t < i1_: f_frame = frames[ff]
                elif t < i2_: f_frame = G_ if variant == 'early' else E_
                else: f_frame = G_
                Phi = f_frame if X == ff else frames[X]
                if Phi is None: continue
                mem = set(members[Phi]) - {X}
                if X != ff:
                    mem.discard(ff)
                    if Phi == f_frame: mem.add(ff)
                mkey = (Phi, version[Phi], ff in mem, X)
                lastkey = last if isinstance(last, dict) else {}
                big = len(mem) > BIG
                if mkey != lastkey.get(variant) and (not big or t == hi - 1 or version[Phi] % 40 == 0):
                    lastkey[variant] = mkey; it[4] = lastkey
                    bkey = (Phi, version[Phi], tuple(sorted(mem)))
                    if bkey not in cache:
                        if len(cache) > 64: cache.clear()
                        cache[bkey] = reduce_basis([(r, rows[r]) for r in sorted(mem) if rows[r]])
                    combo = solve(cache[bkey], d['v']); d['tests'] += 1
                    if combo is not None:
                        d['found'][variant] = dict(t=t, frame=Phi, combo={str(k): str(v) for k, v in combo.items()},
                                          dyadic=all(dyadic(v) for v in combo.values()), window=wi, members=len(mem))
                        log('  FOUND fix[%s]: pair f=%s (%d,%d) deficit on %s at t=%d frame %s combo %s dyadic=%s' % (
                            variant, cands[ci]['f'], i1_, i2_, X, t, Phi, d['found'][variant]['combo'], d['found'][variant]['dyadic']))
            keep.append(it)
        active = keep
    # apply event, update membership/version
    oldf = None
    if e[0] == 'scalar': oldf = frames[tuple(e[1][1])]
    elif e[0] in ('warp', 'climb'): oldf = e[3]
    elif e[0] == 'center': oldf = e[2]
    d_role = apply(e, rows, frames)
    if d_role is not None:
        newf = frames[d_role]
        if oldf != newf:
            if oldf is not None: members[oldf].discard(d_role); version[oldf] += 1
            if newf is not None: members[newf].add(d_role)
        if newf is not None: version[newf] += 1
    if t % 2000 == 0:
        log('  t=%d/%d active=%d elapsed=%.0fs' % (t, n, len(active), time.time() - t0))
# ---------- results ----------
res = []
for cd in cands:
    ok = [v for v in ('early', 'late') if all(d['found'][v] is not None for d in cd['defs'])]
    res.append(dict(f=cd['f'], i1=cd['i1'], i2=cd['i2'], E=cd['E'], F=cd['F'], G=cd['G'], all_fixable=ok,
                    defs=[dict(X=str(d['X']), Y=str(d['Y']), j=d['j'], q=str(d['q']), windows=d['windows'],
                               tests=d['tests'], found=d['found']) for d in cd['defs']]))
json.dump(res, open(f'result_{ORIENT}.json', 'w'), indent=1)
nfix = sum(1 for r in res if r['all_fixable']); ndef = sum(len(r['defs']) for r in res)
nfound = sum(1 for r in res for d in r['defs'] if any(d['found'].values()))
log('DONE %s: pairs %d, fully fixable pairs %d; deficits %d, fixable deficits %d' % (ORIENT, len(res), nfix, ndef, nfound))
for r in res:
    if r['all_fixable']: log('  FIXABLE PAIR ' + json.dumps(r)[:600])
