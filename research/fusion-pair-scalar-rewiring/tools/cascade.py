"""Cascade compensation search for H1+H1->H2 fusions on the #4610 word.

Generalises compsearch.py: a deficit (missing contribution) is allowed to propagate downstream through
reads, warps and scalings, and may be repaid on ANY deficient field at ANY time by free same-frame adds
whose exact rows span the deficit.  Greedy: repay as soon as the span test passes.  A pair succeeds if
every deficit is repaid before the end of the program (then final rows are the original ones).

One sweep of the original program serves all pairs: the original rows are shared; each pair keeps a
small dict {field: deficit}.  Usage: py -3.12 cascade.py backward|forward [MAXDEF]
"""
import gzip, json, collections, sys, time
from fractions import Fraction as Q
ORIENT = sys.argv[1] if len(sys.argv) > 1 else 'backward'
MAXDEF = int(sys.argv[2]) if len(sys.argv) > 2 else 24      # give up on a pair with more deficient fields
import os
W = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'research', 'kappa-round3-warp-20261022', 'ACTUAL-WORD.json.gz')
LOG = open(f'cascade_{ORIENT}.log', 'a', buffering=1)
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n')

w = json.load(gzip.open(W, 'rt', encoding='utf-8')); c = w['canonical']; fr = c['frames']
prog = w['programs'][ORIENT]; n = len(prog); backward = (ORIENT == 'backward'); NL = 632

touch = collections.defaultdict(list)
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
climbs = collections.defaultdict(list)
for i, e in enumerate(prog):
    if e[0] == 'climb': climbs[e[2]].append((i, e[3], e[4], e[5]))
pairs = []
for f, cl in climbs.items():
    for (i1, E, F, r1), (i2, F2, G, r2) in zip(cl, cl[1:]):
        if r1 != 1 or r2 != 1: continue
        between = [t for t in touch[('L', f)] if i1 < t[0] < i2]
        if any(t[1] not in ('src:add', 'dst:add') for t in between): continue
        for variant in ('late', 'early'):
            pairs.append(dict(f=('L', f), i1=i1, i2=i2, E=E, F=F, G=G, variant=variant, deleted={j for j, k, P in between},
                              D={}, dead=None, fixes=[], last={}))
log(ORIENT, 'pair-variants', len(pairs))
by_start = collections.defaultdict(list)
for p in pairs: by_start[p['i1']].append(p)

def add_into(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv: dst[k] = nv
        else: dst.pop(k, None)
def warp_row(row, op):
    sym = (1 if op > 0 else -1) * (abs(op) + (10**6 if backward else 0))
    return {(r, wd[1:] if wd and wd[0] == -sym else (sym,) + wd): q for (r, wd), q in row.items()}
def reduce_basis(vecs):
    basis = []
    for role, row in vecs:
        r = dict(row); combo = {role: Q(1)}
        for pk, brow, bcombo in basis:
            if pk in r:
                coef = r[pk] / brow[pk]; add_into(r, brow, -coef); add_into(combo, bcombo, -coef)
        if r: basis.append((min(r, key=repr), r, combo))
    return basis
def solve(basis, v):
    r = dict(v); combo = {}
    for pk, brow, bcombo in basis:
        if pk in r:
            coef = r[pk] / brow[pk]; add_into(r, brow, -coef); add_into(combo, bcombo, coef)
    return None if r else combo
def dyadic(q): return (q.denominator & (q.denominator - 1)) == 0

rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(NL)}; rows[('C', 0)] = {(('C', 0), ()): Q(1)}
frames = {('L', i): c['start'][i] for i in range(NL)}; frames[('C', 0)] = None
members = collections.defaultdict(set); version = collections.Counter()
for r, fr_ in frames.items():
    if fr_ is not None: members[fr_].add(r)
active = []; cache = {}; BIG = 80; t0 = time.time()

def f_frame(p, t):
    if t < p['i1']: return frames[p['f']]
    if t < p['i2']: return p['G'] if p['variant'] == 'early' else p['E']
    return p['G']
def frame_of(p, X, t): return f_frame(p, t) if X == p['f'] else frames[X]
def mod_row(p, X): return rows[X] if X not in p['D'] else {k: v for k, v in ((k, rows[X].get(k, 0) - p['D'][X].get(k, 0)) for k in set(rows[X]) | set(p['D'][X])) if v}

def try_fix(p, t):
    """repay any deficient field whose frame members span the deficit (shared basis per frame version)"""
    ff = p['f']
    for X in list(p['D']):
        v = p['D'][X]
        if not v: p['D'].pop(X); continue
        Phi = frame_of(p, X, t)
        if Phi is None: continue
        key = (Phi, version[Phi], len(p['D']))
        if p['last'].get(X) == key: continue
        nmem = len(members[Phi])
        if nmem > BIG and version[Phi] % 100: continue
        p['last'][X] = key
        ukey = ('U', Phi, version[Phi])
        if ukey not in cache:
            if len(cache) > 48: cache.clear()
            u = set()
            for r in members[Phi]: u.update(rows[r].keys())
            if f_frame(p, t) == Phi: u.update(rows[ff].keys())
            cache[ukey] = u
        if not set(v.keys()) <= cache[ukey]: continue
        bkey = ('B', Phi, version[Phi])
        if bkey not in cache:
            if len(cache) > 48: cache.clear()
            cache[bkey] = reduce_basis([(r, rows[r]) for r in sorted(members[Phi]) if rows[r]])
        combo = solve(cache[bkey], v)
        if combo is None and f_frame(p, t) == Phi and ff not in members[Phi]:
            # f is present in this frame only in the modified program: extend basis by f
            combo = solve(reduce_basis([(r, rows[r]) for r in sorted(members[Phi]) if rows[r]] + [(ff, rows[ff])]), v)
        if combo is None: continue
        bad = any(r in p['D'] or r == X or (r == ff and f_frame(p, t) != Phi) for r in combo)
        if bad: continue
        p['fixes'].append(dict(t=t, X=X, frame=Phi, combo={str(k): str(q) for k, q in combo.items()}, dyadic=all(dyadic(q) for q in combo.values())))
        p['D'].pop(X); p['last'].pop(X, None)

for t, e in enumerate(prog):
    for p in by_start.get(t, ()): active.append(p)
    k = e[0]
    if active:
        keep = []
        for p in active:
            if p['dead']: continue
            # 1. propagate / create deficits through this event (modified program semantics)
            if t in p['deleted']:
                g = e[1]; d = tuple(g[1]); s = tuple(g[2]); q = Q(g[3], g[4])
                # deleted  d += q s  -> d lacks q * (modified row of s)
                add_into(p['D'].setdefault(d, {}), mod_row(p, s), q)
                if not p['D'][d]: p['D'].pop(d)
            elif k == 'scalar':
                g = e[1]; d = tuple(g[1])
                if g[0] == 'clear': p['D'].pop(d, None)
                elif g[0] == 'copy':
                    s = tuple(g[2]); p['D'].pop(d, None)
                    if s in p['D']: p['D'][d] = dict(p['D'][s])
                elif g[0] == 'add':
                    s = tuple(g[2])
                    if s in p['D']:
                        add_into(p['D'].setdefault(d, {}), p['D'][s], Q(g[3], g[4]))
                        if not p['D'][d]: p['D'].pop(d)
                elif g[0] == 'scale':
                    if d in p['D']: p['D'][d] = {kk: Q(g[2], g[3]) * v for kk, v in p['D'][d].items()}
            elif k == 'warp':
                d = tuple(e[1])
                if d in p['D']: p['D'][d] = warp_row(p['D'][d], e[2])
            # 2. try to repay (after the event's effect on rows below, so test before applying rows? rows change
            #    only for the touched field; we test with the state BEFORE applying, which is also a legal time)
            if len(p['D']) > MAXDEF: p['dead'] = ('too many deficient fields', t); continue
            if p['D']: try_fix(p, t)
            if p['D'] or t < p['i2']: keep.append(p)
            else: p['dead'] = None  # finished clean: no deficits and past i2 -> success (stays success)
            if not p['D'] and t >= p['i2']: p['done'] = t
        active = keep
    # apply event to the shared original state
    oldf = None
    if k == 'scalar':
        g, frame = e[1], e[2]; d = tuple(g[1]); oldf = frames[d]
        if g[0] == 'clear': rows[d] = {}; frames[d] = frame
        elif g[0] == 'copy': rows[d] = dict(rows[tuple(g[2])])
        elif g[0] == 'add': add_into(rows[d], rows[tuple(g[2])], Q(g[3], g[4]))
        elif g[0] == 'scale': rows[d] = {kk: Q(g[2], g[3]) * v for kk, v in rows[d].items()}
    elif k == 'warp':
        d = tuple(e[1]); oldf = e[3]; rows[d] = warp_row(rows[d], e[2]); frames[d] = e[4]
    elif k == 'climb': d = ('L', e[2]); oldf = e[3]; frames[d] = e[4]
    elif k == 'center': d = ('C', e[1]); oldf = e[2]; frames[d] = e[3]
    else: d = None
    if d is not None:
        newf = frames[d]
        if oldf != newf:
            if oldf is not None: members[oldf].discard(d); version[oldf] += 1
            if newf is not None: members[newf].add(d)
        if newf is not None: version[newf] += 1
    if t % 500 == 0:
        log('  t=%d/%d active=%d dead=%d elapsed=%.0fs' % (t, n, len(active), sum(1 for p in pairs if p['dead']), time.time() - t0))

ok = [p for p in pairs if not p['dead'] and not p['D'] and p.get('done') is not None]
unfinished = [p for p in pairs if not p['dead'] and p['D']]
log('DONE %s: pair-variants %d, SUCCESS %d, dead %d, deficits left at end %d' % (ORIENT, len(pairs), len(ok), sum(1 for p in pairs if p['dead']), len(unfinished)))
deadreasons = collections.Counter(p['dead'][0] for p in pairs if p['dead'])
log('dead reasons', dict(deadreasons))
out = [dict(f=p['f'], i1=p['i1'], i2=p['i2'], E=p['E'], F=p['F'], G=p['G'], variant=p['variant'], deleted=sorted(p['deleted']),
            fixes=p['fixes'], dead=p['dead'], left={str(k): len(v) for k, v in p['D'].items()}) for p in pairs]
json.dump(out, open(f'cascade_{ORIENT}.json', 'w'), indent=1, default=str)
for p in ok: log('  SUCCESS', p['f'], p['i1'], p['i2'], p['variant'], 'fixes', json.dumps(p['fixes'])[:500])
# statistics on how far pairs got
left = collections.Counter(len(p['D']) for p in unfinished)
log('deficient-field count at end among unfinished:', dict(sorted(left.items())))
