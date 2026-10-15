"""Large-neighbourhood search with CP-SAT on a T16 owner map (fifth version): lns.py plus two neighbourhood modes.
The helpers of the neighbourhood's bins are re-assigned by (time, width) class to those bins (windows and the active
pair via Model.allowed, capacity, at most one helper per family per call), maximising sum over bins of
round(SC * g(free)), g(f) = f ln f; a result is accepted only if the exact kappa rises (compared as Decimal).
argv: LIBDIR START OUT_PREFIX ITERS SEED [TL] [MODE] [...]
Modes as in lns.py (fam, set:<calls>, time, early<k>, queue, tgt:..., f3, evac) and:
  guide: neighbourhood from a stage-1 class target (env GUIDE = a winlp.py ip JSON): for a random fraction GFRAC of
         the classes whose target differs, up to GMUL x (excess + 1) bins holding helpers whose class (call, width)
         count must drop, and up to GMUL x (excess + 1) bins whose pattern count must drop. The CP-SAT model then
         maximises the surrogate exactly over that neighbourhood (used by sloop.sh, fifth version).
  rc:    lossy small bins plus 1-3 partly filled cap-48 bins sharing their calls (tried in the session; no shipped
         checkpoint came from it).
env: NW = CP-SAT workers per solve (default 2), DIV=1 plateau step, TL2 = time limit of the DIV re-solve,
     NB = neighbourhood size for evac/rc, RESTRICT=1 limits each bin's free value to a few values (not used in sloop.sh).
kappa values are compared as Decimal, never as strings (the pinned assembler can drop trailing zeros)."""
import sys, math, json, gzip, random, time
from decimal import Decimal
sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter, defaultdict
from ortools.sat.python import cp_model
start, outp, ITERS, SEED = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
TL = float(sys.argv[6]) if len(sys.argv) > 6 else 30.0
import os; NW = int(os.environ.get('NW', 2)); DIV = os.environ.get('DIV') == '1'; TL2 = float(os.environ.get('TL2', 60))
rng = random.Random(SEED)
SC = 10000
def gi(f): return round(SC * lib.g(f))

roles = lib.read(start)
def kappa_of(roles):
    au = lib.audit(roles); return lib.price(au['profile'])['kappa_decimal'], au['idle']
best_k, best_idle = kappa_of(roles)
print('start', best_k, best_idle, flush=True)

def setup(roles):
    m = lib.Model(roles)
    fambins = defaultdict(list)
    for k in m.cap: fambins[m.fam[k]].append(k)
    return m, fambins

m, fambins = setup(roles)
grp = defaultdict(list)   # (owner, pair-side id) -> families
for f, bins in fambins.items():
    o, c, p = bins[0]; pair, side = lib.geo['place'][c]; grp[o, 2*pair+side].append(f)
famtimes = {f: set().union(*(m.allowed[k] for k in bins)) for f, bins in fambins.items()}

def frag(f): return sum(1 for k in fambins[f] if 0 < m.free(k) < m.cap[k])

def pick():
    """Choose families: seed groups with fragments, then groups whose windows overlap."""
    fr = [f for f in fambins if frag(f)]
    f0 = rng.choice(fr); o0, c0, _ = fambins[f0][0]
    T0 = famtimes[f0]
    gkeys = list(grp)
    # score groups by overlap of times with T0
    ov = sorted(gkeys, key=lambda g: -len(famtimes[grp[g][0]] & T0) + rng.random() * 3)
    ng = rng.choice([2, 3, 4, 5, 6])
    chosen = [g for g in ov[:12] if len(famtimes[grp[g][0]] & T0)]
    rng.shuffle(chosen); chosen = chosen[:ng]
    g0 = [g for g in grp if f0 in grp[g]][0]
    if g0 not in chosen: chosen.append(g0)
    budget = rng.choice([60, 90, 120, 160])
    per = max(4, budget // len(chosen))
    fams = {f0}
    for g in chosen:
        fs = grp[g][:]
        rng.shuffle(fs)
        fs.sort(key=lambda f: -(frag(f) > 0) * rng.random())
        # mix fragment and full / empty families
        fams.update(fs[:per])
    return sorted(fams)

DELTA = None
RESTRICT = os.environ.get('RESTRICT') == '1'
def solve(bins, H):
    Hs = set(H)
    D = Counter((m.roles[i]['time'], m.roles[i]['width']) for i in H)
    byt = defaultdict(list)
    for (t, w) in D: byt[t].append(w)
    resid = {k: m.cap[k] - sum(m.roles[i]['width'] for i in m.members[k] if i not in Hs) for k in bins}
    fixocc = defaultdict(set)
    for t in byt:
        fixocc[t] = set(m.occ[t]) - {m.fam[m.bin(i)] for i in H if m.roles[i]['time'] == t}
    mdl = cp_model.CpModel(); y = {}
    for k in bins:
        for t in m.allowed[k]:
            if t not in byt or m.fam[k] in fixocc[t]: continue
            for w in byt[t]:
                if w <= resid[k]: y[k, t, w] = mdl.NewBoolVar('')
    cur = Counter(); obj0 = 0
    for i in H: z = m.roles[i]; cur[m.bin(i), z['time'], z['width']] += 1
    for k in bins: obj0 += gi(m.free(k))
    byk = defaultdict(list); bytw = defaultdict(list); byft = defaultdict(list)
    for (k, t, w), v in y.items():
        byk[k].append((w, v)); bytw[t, w].append(v); byft[m.fam[k], t].append(v)
        mdl.AddHint(v, cur[k, t, w])
    for (k, t, w), c in cur.items(): assert (k, t, w) in y, (k, t, w)
    for tw, d in D.items(): mdl.Add(sum(bytw[tw]) == d)
    for vs in byft.values():
        if len(vs) > 1: mdl.AddAtMostOne(vs)
    obj = []; ohf = defaultdict(list); N0 = Counter()
    for k in bins:
        cap = resid[k]; f0 = m.free(k)
        okf = set(range(cap + 1)) if not RESTRICT else ({0, cap, f0, resid[k]} | ({1} if m.cap[k] == 32 else set()) | ({3} if m.cap[k] == 16 else set()))
        okf = {f for f in okf if 0 <= f <= cap}
        oh = [mdl.NewBoolVar('') if f in okf else mdl.NewConstant(0) for f in range(cap + 1)]
        mdl.AddExactlyOne(oh)
        mdl.Add(sum(f * b for f, b in enumerate(oh)) == cap - sum(w * v for w, v in byk[k]))
        for f, b in enumerate(oh):
            if f in okf: mdl.AddHint(b, f == f0)
        obj += [gi(f) * b for f, b in enumerate(oh) if gi(f) and f in okf]
        for f, b in enumerate(oh): ohf[f].append(b)
        N0[f0] += 1
    if DELTA:
        for f in ohf:
            mdl.Add(sum(ohf[f]) == N0[f] + DELTA.get(f, 0))
    mdl.Maximize(sum(obj))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = TL; sv.parameters.num_workers = NW; sv.parameters.repair_hint = True
    sv.parameters.random_seed = rng.randrange(1 << 30)
    st = sv.Solve(mdl)
    info = dict(bins=len(bins), helpers=len(H), vars=len(y), status=sv.StatusName(st), obj0=obj0)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None, info
    info['obj'] = sv.ObjectiveValue(); info['bound'] = sv.BestObjectiveBound()
    if sv.ObjectiveValue() <= obj0 and not DIV: return None, info
    # phase 2: keep the objective, minimise relocations (or, with DIV on a plateau, randomly maximise them)
    best = int(sv.ObjectiveValue()); vals = {key: sv.Value(v) for key, v in y.items()}
    mdl.ClearHints()
    for key, v in y.items(): mdl.AddHint(v, vals[key])
    mdl.Add(sum(obj) >= best)
    if best <= obj0: mdl.Maximize(sum(rng.randrange(1, 4) * v for key, v in y.items() if not cur[key]))
    else: mdl.Maximize(sum(v for key, v in y.items() if cur[key]))
    sv2 = cp_model.CpSolver(); sv2.parameters.max_time_in_seconds = TL2; sv2.parameters.num_workers = NW
    st2 = sv2.Solve(mdl)
    if st2 in (cp_model.OPTIMAL, cp_model.FEASIBLE): sv = sv2; info['kept'] = sv2.ObjectiveValue()
    # reconstruct
    pool = defaultdict(list)
    for i in H: z = m.roles[i]; pool[z['time'], z['width']].append(i)
    want = defaultdict(list)
    for (k, t, w), v in y.items():
        if sv.Value(v): want[t, w].append(k)
    new = [dict(z) for z in m.roles]
    for tw, ks in want.items():
        hs = pool[tw]; rem = list(ks); free_h = []
        for i in hs:
            if m.bin(i) in rem: rem.remove(m.bin(i))
            else: free_h.append(i)
        assert len(free_h) == len(rem)
        for i, k in zip(free_h, rem):
            new[i] = lib.relocate(new[i], *k); new[i]['offset'] = 10**6
    return lib.compact(new), info

MODE = sys.argv[7] if len(sys.argv) > 7 else 'fam'
EMPTYOK = {16: 17}
QUEUE = []
def pick_times():
    if MODE.startswith('early'):
        hi = int(MODE[5:] or 15); n = rng.choice([4, 5, 5, 6, 6, 7])
        return set(rng.sample(range(hi + 1), n))
    if MODE == 'queue':
        if not QUEUE:
            sets = sorted({tuple(sorted(m.allowed[k])) for k in m.cap if 0 < m.free(k) < m.cap[k]}, key=len)
            for a in sets:
                if len(a) <= 6: QUEUE.append(set(a))
                else:
                    for j in range(0, len(a), 4): QUEUE.append(set(a[j:j+5]))
            rng.shuffle(QUEUE); print('queue', len(QUEUE), flush=True)
        return QUEUE.pop()
    if MODE == 'f3': fr = [k for k in m.cap if m.free(k) in (2, 3, 6, 7, 9, 10)]
    else: fr = [k for k in m.cap if 0 < m.free(k) < m.cap[k]]
    k0 = rng.choice(fr); al = sorted(m.allowed[k0])
    n = rng.choice([1, 2, 2, 3, 3, 4]) if MODE != 'f3' else rng.choice([2, 3, 4, 5, 6])
    return set(rng.sample(al, min(n, len(al))))
def nbhd_times(Ts):
    H = [i for i, z in enumerate(m.roles) if z['time'] in Ts]
    hb = {m.bin(i) for i in H}
    bins = [k for k in m.cap if k in hb or (4 <= m.free(k) < EMPTYOK.get(m.cap[k], m.cap[k]) and m.allowed[k] & Ts)]
    return bins, H
DLIST = []
NB = int(os.environ.get('NB', 200))
def pick_evac():
    """Stranded bins (cap 48, 0 < used <= 20) + bins with spare that share times with them + full bins of the same classes."""
    st = [k for k in m.cap if m.cap[k] == 48 and 0 < m.cap[k] - m.free(k) <= 20]
    if not st: st = [k for k in m.cap if 0 < m.free(k) < m.cap[k] and m.free(k) >= 4]
    k0s = rng.sample(st, min(len(st), rng.choice([1, 1, 2, 3])))
    T0 = {m.roles[i]["time"] for k in k0s for i in m.members[k]}
    nb = rng.choice([NB // 2, NB, NB, int(NB * 1.5)])
    cand = [k for k in m.cap if k not in k0s and m.allowed[k] & T0 and m.free(k) < m.cap[k]]
    spare = [k for k in cand if m.free(k) > 0]; full = [k for k in cand if m.free(k) == 0]
    rng.shuffle(spare); rng.shuffle(full)
    # bias toward bins with larger spare
    spare.sort(key=lambda k: -m.free(k) * rng.random())
    a = spare[:int(nb * rng.choice([0.3, 0.5, 0.7]))]
    sel = set(k0s) | set(a)
    # full bins: prefer those whose allowed set overlaps chosen spare bins' classes
    rest = nb - len(sel); sel |= set(full[:max(0, rest)])
    # also some empty cap-48 bins allowing T0 (lets a 2-for-1 consolidation happen)
    emp = [k for k in m.cap if m.free(k) == m.cap[k] and m.allowed[k] & T0]; rng.shuffle(emp); sel |= set(emp[:rng.choice([0, 2, 5])])
    return sorted(sel)
def pick_rc():
    """Seeds: many lossy bins (cap16 free 3/16/7 etc.), plus 1-3 full cap-48 targets sharing times, plus full bins of overlapping classes."""
    lossy = [k for k in m.cap if m.cap[k] < 48 and m.free(k) >= 2]
    nA = rng.choice([8, 16, 24, 40])
    k0 = rng.choice(lossy); T0 = set(m.allowed[k0])
    close = sorted(lossy, key=lambda k: -len(m.allowed[k] & T0) / len(m.allowed[k] | T0) - 0.3 * rng.random())
    A = close[:nA]; T0 = set().union(*(m.allowed[k] for k in A))
    tg = [k for k in m.cap if m.cap[k] == 48 and m.free(k) < 48 and m.allowed[k] & T0]
    tg = rng.sample(tg, min(len(tg), rng.choice([1, 2, 3])))
    Th = {m.roles[i]['time'] for k in A + tg for i in m.members[k]}
    nb = rng.choice([NB // 2, NB, int(NB * 1.5), 2 * NB])
    cand = [k for k in m.cap if k not in A and k not in tg and m.free(k) < m.cap[k] and m.allowed[k] & Th]
    rng.shuffle(cand)
    # prefer bins holding 7s/8s/4s/5s at the hot times (the exchange currency)
    cand.sort(key=lambda k: -sum(1 for i in m.members[k] if m.roles[i]['time'] in Th and m.roles[i]['width'] != 9) * rng.random())
    sel = set(A) | set(tg) | set(cand[:nb])
    emp = [k for k in m.cap if m.free(k) == m.cap[k] and m.allowed[k] & Th]; rng.shuffle(emp); sel |= set(emp[:rng.choice([0, 2, 4])])
    return sorted(sel)
def pick_guide():
    """Neighbourhood from a stage-1 class target (env GUIDE): bins holding helpers whose class (t,w) count must drop, bins whose pattern count must drop."""
    W = [4, 5, 7, 8, 9]; d = json.load(open(os.environ['GUIDE']))
    cls = defaultdict(list)
    for k in m.cap: cls[m.cap[k], frozenset(m.allowed[k])].append(k)
    CL = list(cls); cid = {k: i for i, c in enumerate(CL) for k in cls[c]}
    pat = {k: tuple(Counter(m.roles[i]['width'] for i in m.members[k])[w] for w in W) for k in m.cap}
    cx = Counter((cid[k], pat[k]) for k in m.cap); cy = Counter((cid[m.bin(i)], z['time'], z['width']) for i, z in enumerate(m.roles))
    nx = Counter({(ci, tuple(p)): v for ci, p, v in d['x']}); ny = Counter({(ci, t, w): v for ci, t, w, v in d['y']})
    FR = float(os.environ.get('GFRAC', 1.0)); MUL = float(os.environ.get('GMUL', 2.0))
    keys = [kk for kk in set(cx) | set(nx) if nx[kk] < cx[kk]]
    ykeys = [kk for kk in set(cy) | set(ny) if ny[kk] < cy[kk]]
    sel = set()
    chosen_cls = set(rng.sample(sorted({kk[0] for kk in keys} | {kk[0] for kk in ykeys}), max(1, int(FR * len({kk[0] for kk in keys} | {kk[0] for kk in ykeys})))))
    for (ci, p) in keys:
        if ci not in chosen_cls: continue
        bs = [k for k in cls[CL[ci]] if pat[k] == p]; rng.shuffle(bs); sel |= set(bs[:int(MUL * (cx[ci, p] - nx[ci, p])) + 1])
    for (ci, t, w) in ykeys:
        if ci not in chosen_cls: continue
        bs = [k for k in cls[CL[ci]] if any(m.roles[i]['time'] == t and m.roles[i]['width'] == w for i in m.members[k])]
        rng.shuffle(bs); sel |= set(bs[:int(MUL * (cy[ci, t, w] - ny[ci, t, w])) + 1])
    print('guide classes', len(chosen_cls), 'bins', len(sel), flush=True)
    return sorted(sel)
if MODE.startswith('tgt:'):
    for x in sys.argv[8].split(';'):
        a, b = x.split('>'); d = Counter(map(int, b.split('+'))); d.subtract(Counter(map(int, a.split('+'))))
        d[0] += len(a.split('+')) - len(b.split('+')); DLIST.append({f: v for f, v in d.items() if v})
    ITERS = len(DLIST)
for it in range(ITERS):
    t0 = time.time()
    if DLIST: DELTA = DLIST[it]; print('delta', DELTA, flush=True)
    if MODE == 'guide':
        bins = pick_guide(); H = [i for k in bins for i in m.members[k]]; tag = ('guide', len(bins))
    elif MODE == 'rc':
        bins = pick_rc(); H = [i for k in bins for i in m.members[k]]; tag = ('rc', len(bins))
    elif MODE.startswith('evac'):
        bins = pick_evac(); H = [i for k in bins for i in m.members[k]]; tag = ('evac', len(bins))
    elif MODE == 'fam':
        fams = pick(); bins = [k for f in fams for k in fambins[f]]; H = [i for k in bins for i in m.members[k]]; tag = len(fams)
    else:
        Ts = set(map(int, MODE[4:].split(','))) if MODE[:4] in ('set:', 'tgt:') else pick_times(); bins, H = nbhd_times(Ts); tag = sorted(Ts)
    res, info = solve(bins, H)
    msg = f"it {it} {tag} {info} {time.time()-t0:.1f}s"
    if res is not None:
        try:
            k, idle = kappa_of(res)
        except Exception as e:
            print(msg, 'AUDIT REJECT', e, flush=True); continue
        msg += f" kappa {k} idle {idle}"
        if Decimal(k) > Decimal(best_k) or (DIV and Decimal(k) == Decimal(best_k)):   # never compare kappa strings
            best_k, best_idle, roles = k, idle, res
            m, fambins = setup(roles)
            open(outp + '.OWNERS.json.gz', 'wb').write(gzip.compress(json.dumps(roles).encode(), mtime=0))
            msg += ' ** NEW BEST'
    print(msg, flush=True)
print('final', best_k, best_idle)
