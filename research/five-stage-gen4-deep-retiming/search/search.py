"""Global neighbor-frame local search over ADD gate frames.

Contract (same as descent_transform): each retimed ADD gate gets a nondegenerate frame;
each register's frame chain from initial to final stays nested; the gate frame contains the
exact integer source span of every non-target operand after the gate. Candidate frames are
existing frames of adjacent gates, so nondegeneracy is inherited.
"""
import sys, time, math, json, pickle, random
from collections import Counter, defaultdict
from frames import *

def w(r): return r*math.log(120/r) + 32*120/1e16*0  # per-call fallback weight negligible

def setup():
    d = load(); L = Lattice(d); rec = d['rec']; n = d['n']; v = d['v']
    final = final_frames(d, L); d['final'] = final
    # spans, fixed gates, event lists per register
    columns = [{i: 1} if i < v else {} for i in range(n)]; center = None
    ev = defaultdict(list)    # register -> list of event ids (gate index i or ('c',k))
    frame = {}                # event id -> frame
    ops = {}                  # gate i -> (a,b)
    fixed = set(); need = {}; copy = None
    for k in range(0, len(rec), 6):
        op, a, b, c, f, z = rec[k:k+6]; i = k//6
        if op == 0: continue
        if op == 2:
            center = a; copy = a; ev[a].append(i); frame[i] = c; fixed.add(i); continue
        if op == 3:
            center = None; copy = None; continue
        src = center if b == n else b; ca = columns[a]
        for s, x in columns[src].items():
            y = ca.get(s, 0) + c*x
            if y: ca[s] = y
            else: del ca[s]
        frame[i] = f
        if b == n:
            ev[a].append(i); ops[i] = (a,); fixed.add(i); continue
        ev[a].append(i); ev[b].append(i); ops[i] = (a, b)
        if copy is not None and copy in (a, b): fixed.add(i)
        nd = set()
        if not (v <= a < 2*v): nd.update(ca)
        if not (v <= b < 2*v): nd.update(columns[b])
        need[i] = frozenset(nd)
    return d, L, ev, frame, ops, fixed, need

class State:
    def __init__(self, d, L, ev, frame, ops, fixed, need):
        self.d, self.L, self.ev, self.frame, self.ops, self.fixed, self.need = d, L, ev, frame, ops, fixed, need
        self.pos = {}   # (register, gate) -> index in ev[register]
        for s, lst in ev.items():
            for j, i in enumerate(lst): self.pos[s, i] = j
        self.chi = d['chi']; self.spanc = {}
    def prevf(self, s, i):
        j = self.pos[s, i]
        return self.frame[self.ev[s][j-1]] if j else self.d['initial'][s]
    def nextf(self, s, i):
        j = self.pos[s, i]; lst = self.ev[s]
        return self.frame[lst[j+1]] if j+1 < len(lst) else self.d['final'][s]
    def span_ok(self, i, g):
        nd = self.need[i]
        if not nd: return True
        k = (nd, g); r = self.spanc.get(k)
        if r is None:
            A = self.L.A[g]; r = all(dot(x, self.chi[s]) == 0 for x in A for s in nd); self.spanc[k] = r
        return r
    def local(self, i, g):
        """cost of the chain pieces around gate i if its frame were g (None if infeasible)."""
        L = self.L; dg = L.dimf[g]; tot = 0.0
        for s in self.ops[i]:
            p, q = self.prevf(s, i), self.nextf(s, i)
            if not (L.sub(p, g) and L.sub(g, q)): return None
            a, b = dg - L.dimf[p], L.dimf[q] - dg
            if a: tot += w(a)
            if b: tot += w(b)
        return tot
    def candidates(self, i):
        c = set()
        for s in self.ops[i]:
            c.add(self.prevf(s, i)); c.add(self.nextf(s, i))
        c.discard(self.frame[i]); return c
    def sweep(self, order):
        improved = 0; gain = 0.0
        for i in order:
            if i in self.fixed: continue
            cur = self.local(i, self.frame[i]); best = None; bg = None
            for g in self.candidates(i):
                if not self.L.nondeg(g): continue
                c = self.local(i, g)
                if c is None or c >= cur - 1e-12: continue
                if not self.span_ok(i, g): continue
                if best is None or c < best: best, bg = c, g
            if bg is not None:
                self.frame[i] = bg; improved += 1; gain += cur - best
        return improved, gain

def assignment(st):
    rec = st.d['rec']; out = {}
    for i, g in st.frame.items():
        if rec[6*i] == 1 and g != rec[6*i+4]: out[i] = g
    return out

if __name__ == '__main__':
    t = time.time()
    d, L, ev, frame, ops, fixed, need = setup()
    st = State(d, L, ev, frame, ops, fixed, need)
    base = cost(d, L, {}); print('setup', time.time()-t, 'base calls', sum(base.values()), flush=True)
    desc = Counter({1: -1760, 2: 880, 20: -880, 21: 1760, 22: -880}); cur = Counter(base); cur.update(desc)
    gates = [i for i in ops if i not in fixed]
    for it in range(30):
        order = gates if it % 2 == 0 else gates[::-1]
        k, g = st.sweep(order)
        h = cost(d, L, assignment(st))
        print(it, 'moves', k, 'gain', round(g, 2), 'calls', sum(h.values()), 'saving', saving_from_local(h, cur), round(time.time()-t), flush=True)
        if k == 0: break
    pickle.dump(assignment(st), open('assign_ls.pkl', 'wb'))
    print(sorted(h.items()))
