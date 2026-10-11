"""Raise-and-propagate and lower-and-propagate large-neighbourhood moves on gate frames."""
import sys, time, math, pickle, random
from collections import Counter
from search import setup
from bcd import BCD, save, restore, assignment, w
from frames import cost, saving_from_local

def make(start=None):
    d, L, ev, frame, ops, fixed, need = setup()
    def join(f, g):
        if L.sub(f, g): return g
        if L.sub(g, f): return f
        return L.register(list(L.B[f]) + list(L.B[g]))
    st = BCD(d, L, ev, frame, ops, fixed, need, join=join, use_joins=True)
    if start:
        obj = pickle.load(open(start, 'rb'))
        if obj and isinstance(next(iter(obj.values())), int): st.frame.update(obj)
        else: restore(st, start)
    return st

def nxt(st, s, i):
    j = st.pos[s, i]; lst = st.ev[s]
    return lst[j+1] if j+1 < len(lst) else None
def prv(st, s, i):
    j = st.pos[s, i]
    return st.ev[s][j-1] if j else None

def raise_move(st, i, X, limit=400):
    """Propose frame changes raising gate i to contain X, closing forward. Returns dict or None."""
    L = st.L; new = {}; q = [(i, X)]
    while q:
        j, Y = q.pop()
        cur = new.get(j, st.frame[j]); g = st.join(cur, Y)
        if g == cur: continue
        if j in st.fixed: return None
        if not L.nondeg(g): return None
        new[j] = g
        if len(new) > limit: return None
        for s in st.ops[j]:
            k = nxt(st, s, j)
            if k is None:
                if not L.sub(g, st.d['final'][s]): return None
            else:
                fk = new.get(k, st.frame[k])
                if not L.sub(g, fk): q.append((k, g))
    return new

def lower_move(st, i, X, limit=400):
    """Lower gate i into X (must still contain spans), closing backward with meets."""
    L = st.L; new = {}; q = [(i, X)]
    while q:
        j, Y = q.pop()
        cur = new.get(j, st.frame[j]); g = L.meet(cur, Y)
        if g == cur: continue
        if j in st.fixed: return None
        if not (L.nondeg(g) and st.span_ok(j, g)): return None
        new[j] = g
        if len(new) > limit: return None
        for s in st.ops[j]:
            k = prv(st, s, j)
            if k is None:
                if not L.sub(st.d['initial'][s], g): return None
            else:
                fk = new.get(k, st.frame[k])
                if not L.sub(fk, g): q.append((k, g))
    return new

def try_apply(st, new):
    affected = set()
    for j in new: affected.update(st.ops[j])
    before = sum(st.chain_cost(r) for r in affected)
    old = {j: st.frame[j] for j in new}
    st.frame.update(new)
    after = [st.chain_cost(r) for r in affected]
    if any(a is None for a in after) or sum(after) > before - 1e-9:
        st.frame.update(old); return 0.0
    return before - sum(after)

K = 3
def sweep(st, gates, rnd):
    tot = 0.0; k = 0
    for i in gates:
        if i in st.fixed: continue
        best = None
        cands = []
        for s in st.ops[i]:
            j = st.pos[s, i]; lst = st.ev[s]; seen = {st.frame[i]}
            for k in lst[j+1:]:
                f = st.frame[k]
                if f not in seen:
                    seen.add(f); cands.append(('r', f))
                    if len(seen) > K: break
            cands.append(('r', st.d['final'][s]))
            seen = {st.frame[i]}
            for k in reversed(lst[:j]):
                f = st.frame[k]
                if f not in seen:
                    seen.add(f); cands.append(('l', f))
                    if len(seen) > K: break
        dedup = []
        for c in cands:
            if c not in dedup: dedup.append(c)
        cands = dedup
        for kind, X in cands:
            if X == st.frame[i]: continue
            new = raise_move(st, i, X) if kind == 'r' else lower_move(st, i, X)
            if not new: continue
            g = try_apply(st, new)
            if g > 0: tot += g; k += 1; break
    return k, tot

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--start'); ap.add_argument('--tag', default='casc'); ap.add_argument('--passes', type=int, default=10)
    a = ap.parse_args(); t = time.time()
    st = make(a.start); d, L = st.d, st.L
    base = cost(d, L, {}); desc = Counter({1: -1760, 2: 880, 20: -880, 21: 1760, 22: -880}); cur = Counter(base); cur.update(desc)
    h = cost(d, L, assignment(st)); print('start calls', sum(h.values()), 'saving', saving_from_local(h, cur), flush=True)
    gates = [i for i in st.ops if i not in st.fixed]; rnd = random.Random(7)
    for it in range(a.passes):
        order = list(gates); rnd.shuffle(order)
        k, g = sweep(st, order, rnd)
        h = cost(d, L, assignment(st))
        print(it, 'moves', k, 'gain', round(g, 2), 'calls', sum(h.values()), 'saving', saving_from_local(h, cur), round(time.time()-t), flush=True)
        save(st, f'assign_{a.tag}.pkl')
        if k == 0: break
