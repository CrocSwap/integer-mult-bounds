"""Register-level block coordinate descent on ADD gate frames (exact concave objective)."""
import sys, time, math, pickle, random
from collections import Counter, defaultdict
from search import setup, State
from frames import cost, saving_from_local, saving, BASEH

def w(r): return r*math.log(120/r) if r > 0 else 0.0

class BCD(State):
    def __init__(self, *a, join=None, use_joins=False):
        super().__init__(*a); self.join = join; self.use_joins = use_joins
        self.partner = {}
        for i, o in self.ops.items():
            if len(o) == 2: self.partner[o[0], i] = o[1]; self.partner[o[1], i] = o[0]
    def chain_cost(self, s):
        L = self.L; prev = self.d['initial'][s]; c = 0.0
        for i in self.ev[s]:
            f = self.frame[i]
            if not L.sub(prev, f): return None
            c += w(L.dimf[f] - L.dimf[prev]); prev = f
        f = self.d['final'][s]
        if not L.sub(prev, f): return None
        return c + w(L.dimf[f] - L.dimf[prev])
    def optimize(self, s):
        L = self.L; lst = self.ev[s]; init = self.d['initial'][s]; fin = self.d['final'][s]
        # DP states: frame -> (cost, backpointer list)
        states = {init: (0.0, None)}; trace = []
        for i in lst:
            if i in self.fixed:
                cands = {self.frame[i]}; p = None
            else:
                p = self.partner.get((s, i))
                pp, pn = self.prevf(p, i), self.nextf(p, i)
                cands = set(states) | {self.frame[i], pp, pn, self.prevf(s, i), self.nextf(s, i)}
                if self.use_joins:
                    for X in list(states):
                        j = self.join(X, pp)
                        if L.sub(j, pn): cands.add(j)
            new = {}
            for X in cands:
                if p is not None:
                    if not (L.sub(pp, X) and L.sub(X, pn) and L.sub(X, fin)): continue
                    if X != self.frame[i] and not (L.nondeg(X) and self.span_ok(i, X)): continue
                    pc = w(L.dimf[X] - L.dimf[pp]) + w(L.dimf[pn] - L.dimf[X])
                else: pc = 0.0
                best = None
                for Y, (cy, _) in states.items():
                    if L.sub(Y, X):
                        c = cy + w(L.dimf[X] - L.dimf[Y])
                        if best is None or c < best[0]: best = (c, Y)
                if best is not None: new[X] = (best[0] + pc, best[1])
            if not new: return 0.0
            trace.append(new); states = new
        best = None
        for Y, (cy, _) in states.items():
            if L.sub(Y, fin):
                c = cy + w(L.dimf[fin] - L.dimf[Y])
                if best is None or c < best[0]: best = (c, Y)
        if best is None: return 0.0
        # backtrack
        choice = [None]*len(lst); X = best[1]
        for t in range(len(lst)-1, -1, -1):
            choice[t] = X; X = trace[t][X][1]
        changes = [(i, X) for i, X in zip(lst, choice) if X != self.frame[i]]
        if not changes: return 0.0
        affected = {s} | {self.partner[s, i] for i, _ in changes if (s, i) in self.partner}
        before = sum(self.chain_cost(r) for r in affected)
        old = {i: self.frame[i] for i, _ in changes}
        for i, X in changes: self.frame[i] = X
        after = [self.chain_cost(r) for r in affected]
        if any(a is None for a in after) or sum(after) > before - 1e-9:
            for i, f in old.items(): self.frame[i] = f
            return 0.0
        return before - sum(after)

def assignment(st):
    rec = st.d['rec']; out = {}
    for i, g in st.frame.items():
        if rec[6*i] == 1 and g != rec[6*i+4]: out[i] = g
    return out

def save(st, path):
    a = assignment(st)
    pickle.dump({i: [list(r) for r in st.L.B[g]] for i, g in a.items()}, open(path, 'wb'))

def restore(st, path):
    for i, B in pickle.load(open(path, 'rb')).items():
        st.frame[i] = st.L.register(B) if B else st.d['ZERO']

def run(passes=20, use_joins=False, start=None, tag="bcd", seed=1):
    t = time.time()
    d, L, ev, frame, ops, fixed, need = setup()
    def join(f, g):
        if L.sub(f, g): return g
        if L.sub(g, f): return f
        return L.register(list(L.B[f]) + list(L.B[g]))
    st = BCD(d, L, ev, frame, ops, fixed, need, join=join, use_joins=use_joins)
    if start:
        obj = pickle.load(open(start, 'rb'))
        if obj and isinstance(next(iter(obj.values())), int):
            for i, g in obj.items(): st.frame[i] = g
        else: restore(st, start)
    base = cost(d, L, {}); desc = Counter({1: -1760, 2: 880, 20: -880, 21: 1760, 22: -880}); cur = Counter(base); cur.update(desc)
    regs = sorted(ev); rnd = random.Random(seed)
    for it in range(passes):
        rnd.shuffle(regs); tot = 0.0; k = 0
        for s in regs:
            g = st.optimize(s)
            if g > 0: tot += g; k += 1
        a = assignment(st); h = cost(d, L, a)
        print(it, 'improved regs', k, 'gain', round(tot, 2), 'calls', sum(h.values()), 'saving', saving_from_local(h, cur), 'gates', len(a), round(time.time()-t), flush=True)
        save(st, f'assign_{tag}.pkl')
        if k == 0: break
    return st

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--joins', action='store_true'); ap.add_argument('--start'); ap.add_argument('--tag', default='bcd'); ap.add_argument('--passes', type=int, default=20); ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args(); run(a.passes, a.joins, a.start, a.tag, a.seed)
