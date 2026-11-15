"""BIG-RELAY pin.py: per transfer j->i at a relay frame F (ADD i += c j), the shear window (t_lo, t_hi) bounded by the
nearest blocking ops (write into j from a non-i source, read of i by a non-j target; F-ops excluded; SCALEs absorbable).
pinned  = i and j co-reside in the window ONLY at F.  courier = some third register D meets j (after t_lo) and then i (before t_hi)
at frames != F, in time order, with no new stop."""
import collections, pickle, bisect, math
from lib import *
W = load(); NP, mains, fixed, dim = setup(W); P = W['program']
X = pickle.load(open('explore.pkl', 'rb'))
NO = W['owned_fields']
byreg = collections.defaultdict(list)
for t, e in enumerate(P):
    if e[0] in ('ADD', 'COPY'): byreg[e[1]].append(t); byreg[e[2]].append(t)
    elif e[0] != 'MOVE': byreg[e[1]].append(t)
# stays: register -> list of (t_from, t_to, frame)
cur = list(W['initial']) + [None] * NO; start = [0] * (NP + NO); ST = collections.defaultdict(list)
for t, e in enumerate(P):
    if e[0] == 'MOVE': ST[e[1]].append((start[e[1]], t, cur[e[1]])); cur[e[1]] = e[3]; start[e[1]] = t
    elif e[0] == 'INIT': cur[e[1]] = e[2]; start[e[1]] = t
    elif e[0] == 'CLEAR': ST[e[1]].append((start[e[1]], t, cur[e[1]])); cur[e[1]] = None
for r in range(NP): ST[r].append((start[r], len(P), cur[r]))
byframe = collections.defaultdict(list)       # frame -> stays (r, a, b)
for r, L in ST.items():
    for a, b, G in L:
        if G is not None: byframe[G].append((r, a, b))
def meets(r, lo, hi, F):
    """{(other, frame, a, b)} co-residence intervals of r with others inside (lo,hi), frame != F."""
    out = []
    for a, b, G in ST[r]:
        if G == F or b <= lo or a >= hi: continue
        a2, b2 = max(a, lo), min(b, hi)
        for (o, c, d) in byframe[G]:
            if o != r and c < b2 and d > a2: out.append((o, G, max(a2, c), min(b2, d)))
    return out
HALF = {}; NP_ = {}; rows = []; pinned_frames = 0; stat = collections.Counter(); blk = collections.Counter()
for F in X['relay']:
    hs = {s[0] for s in X['stops'][F]}; Fpin = False; Fcour = True; Fmh = []; Fblk = []
    for t, e in enumerate(P):
        pass
    for t in sorted({t for h in hs for t in byreg[h] if evframe(P[t]) == F}):
        e = P[t]
        if e[0] != 'ADD': continue
        i, j = e[1], e[2]
        def isblk(u):
            o = P[u]
            if evframe(o) == F or o[0] != 'ADD': return False
            return (o[1] == j and o[2] != i) or (o[2] == i and o[1] != j)
        before = [u for u in byreg[i] + byreg[j] if u < t and isblk(u)]; after = [u for u in byreg[i] + byreg[j] if u > t and isblk(u)]
        lo = max(before) if before else -1; hi = min(after) if after else len(P)
        for u in (max(before) if before else None, min(after) if after else None):
            if u is None: continue
            o = P[u]; who = o[2] if o[1] in (i, j) else o[1]
            blk[('write-into-j' if o[1] == j else 'read-of-i', 'fixed' if fixed(who) else 'helper', dim[o[4]])] += 1
        co = [m for m in meets(i, lo, hi, F) if m[0] == j]
        if co: stat['transfer not pinned'] += 1; continue
        stat['pinned'] += 1; Fpin = True
        # courier: D meets j in (lo, t) then i in (that time, hi)
        mj = {}
        for (o, G, a, b) in meets(j, lo, hi, F):
            if o not in hs or True: mj.setdefault(o, []).append(a)
        ok = False
        for (o, G, a, b) in meets(i, lo, hi, F):
            if o in mj and min(mj[o]) < b and not fixed(o): ok = True; break
        stat['pinned, courier exists' if ok else 'pinned, no courier'] += 1
        # multi-hop: earliest-arrival flood from j (time lo) through helpers, reach i before hi
        import heapq
        arr = {j: lo}; pq = [(lo, j)]; reach = False; nst = 0
        while pq and nst < 4000:
            a0, r = heapq.heappop(pq); nst += 1
            if a0 > arr.get(r, 1e18): continue
            for (o, G, a, b) in meets(r, a0, hi, F):
                if fixed(o): continue
                ta = max(a, a0)
                if o == i: reach = True; break
                if ta < arr.get(o, 1e18): arr[o] = ta; heapq.heappush(pq, (ta, o))
            if reach: break
        stat['pinned, multi-hop path' if reach else 'pinned, no multi-hop path'] += 1
        Fmh.append(reach)
        if not reach:
            A = {o for (o, G, a, b) in meets(j, lo, hi, F) if not fixed(o)}; B = {o for (o, G, a, b) in meets(i, lo, hi, F) if not fixed(o)}
            HALF.setdefault(F, {})[(i, j)] = bool(A or B)
        if not reach: NP_.setdefault(F, set()).add((i, j))
        bl = [P[u] for u in ((max(before),) if before else ()) + ((min(after),) if after else ())]
        Fblk.append(all(fixed(o[2] if o[1] in (i, j) else o[1]) for o in bl))
        if not ok: Fcour = False
    rows.append((F, Fpin, Fcour, all(Fmh), any(Fblk)))
print(stat); print('frames with >=1 pinned transfer', sum(1 for r in rows if r[1]), 'of', len(rows), '; all pinned transfers courier-able', sum(1 for r in rows if r[1] and r[2]))
print('frames whose pinned transfers all have a multi-hop helper path', sum(1 for r in rows if r[3]), '; frames with a pinned transfer blocked on both sides by FIXED-register ops', sum(1 for r in rows if r[4]))
print('blockers (kind, partner, dim):', blk.most_common(12))
pickle.dump(dict(rows=rows, nopath=NP_, half=HALF), open('pin.pkl', 'wb'))
gain = {r[0]: r[6] for r in X['rows']}
L = 2 * math.log(2)
c1 = sum(max(0, gain[F] - L) for F in NP_); 
mt = {F: max(len({p[0] for p in v}), len({p[1] for p in v})) for F, v in NP_.items()}
c2 = sum(max(0, gain[F] - L * mt[F]) for F in NP_)
print('gain all relay frames %.1f; ceiling m_F=1 %.1f; ceiling m_F=max(#targets,#sources) %.1f' % (sum(gain.values()), c1, c2))
print('m_F dist', collections.Counter(mt.values()), 'frames with gain_F > L*m_F', sum(1 for F in NP_ if gain[F] > L * mt[F] + 1e-9))
import collections as C2; print('no-path pairs per frame', C2.Counter(len(v) for v in NP_.values()))
