"""Annealing over commuting gate orders, priced by least-frame lifting, then exact frame re-solve.

Moves a gate of A or B within its commutation window (two additions commute unless one writes the other's
source; scales commute only with disjoint gates -- the rule of build_gate_moves.py). Each order is priced by its
least feasible frame assignment (each gate at the span of its registers' current frames, forced to the cut anchor
when it is a register's last A gate); infeasible orders (least value above a cap/anchor/final) are rejected.

usage: order_search.py WORD.json.gz OUT-ORDER.json [--steps N --seed S --temp T]
"""
import argparse, gzip, json, math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_lift as L

SUMS = {}


def ssum(a, b):
    if a & ~b == 0: return b
    if b & ~a == 0: return a
    k = (a, b) if a < b else (b, a)
    s = SUMS.get(k)
    if s is None:
        s = L.span_mask([x for x in range(512) if (a | b) >> x & 1]); SUMS[k] = s
    return s


def regs(e):
    return (e[1], e[2]) if e[0] == 'add' else (e[1],)


def commute(x, y):
    if x[0] == 'add' and y[0] == 'add':
        return x[1] != y[2] and y[1] != x[2]
    return not set(regs(x)) & set(regs(y))


class Pricer:
    def __init__(self, word):
        self.w = word
        v = word['report']['v']; R = word['report']['R']; self.n = n = 2 * v + R
        self.start = [1] * n
        for t in range(v): self.start[t] = L.span_mask([word['ports'][t]])
        for r, f in word.get('start_extra', {}).items(): self.start[int(r)] = L.span_mask(f)
        lev = {int(t): L.span_mask(f) for t, f in word.get('target_levels', {}).items()}
        self.anchor = {r: L.span_mask(cf) for r, cf in zip(word['centers'], word['center_frames'])}
        for t in range(v): self.anchor[v + t] = lev.get(t, 1)
        self.final = L.final_frames(word)
        tail = [(int(i), f) for i, f in word.get('early_cleanup', [])]
        self.tail = [(word['cleanup'][i][:-1], L.span_mask(f)) for i, f in tail]
        self.Wt = [L.W(d) for d in range(10)]

    def price(self, A, B, frames_out=None):
        """A, B: gate lists. returns cost or None if infeasible."""
        cur = list(self.start); cost = 0.0; W = self.Wt; dim = L.dim
        lastA = {}
        for i, e in enumerate(A):
            for r in regs(e): lastA[r] = i
        fr = []
        for i, e in enumerate(A):
            rs = regs(e)
            f = cur[rs[0]] if len(rs) == 1 else ssum(cur[rs[0]], cur[rs[1]])
            for r in rs:
                if lastA.get(r) == i and r in self.anchor:
                    an = self.anchor[r]
                    if f & ~an: return None
                    f = an
            for r in rs:
                if f & ~self.final[r]: return None
            for r in rs:
                if cur[r] != f: cost += W[dim(f) - dim(cur[r])]; cur[r] = f
            fr.append(f)
        for r, an in self.anchor.items():
            if cur[r] != an: return None    # register without A gates must start at its anchor (unchanged input)
        for part, seq in (('B', B), ('T', None)):
            items = [(e, None) for e in seq] if seq is not None else self.tail
            for e, fixed in items:
                rs = regs(e)
                f = cur[rs[0]] if len(rs) == 1 else ssum(cur[rs[0]], cur[rs[1]])
                if fixed is not None:
                    if f & ~fixed: return None
                    f = fixed
                for r in rs:
                    if f & ~self.final[r]: return None
                for r in rs:
                    if cur[r] != f: cost += W[dim(f) - dim(cur[r])]; cur[r] = f
                if part == 'B': fr.append(f)
        for r in range(self.n):
            f = self.final[r]
            if cur[r] & ~f: return None
            if cur[r] != f: cost += W[dim(f) - dim(cur[r])]
        if frames_out is not None: frames_out.extend(fr)
        return cost


def window(seq, i):
    lo = i
    while lo > 0 and commute(seq[i], seq[lo - 1]): lo -= 1
    hi = i
    while hi < len(seq) - 1 and commute(seq[i], seq[hi + 1]): hi += 1
    return lo, hi


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--steps', type=int, default=100000); ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--temp', type=float, default=0.5)
    a = ap.parse_args()
    word = json.load(gzip.open(a.src)); P = Pricer(word); rng = random.Random(a.seed)
    A = [list(e) for e in word['A']]; B = [list(e) for e in word['B']]
    c0 = P.price(A, B); print('least-frame price of input order %.4f' % c0, flush=True)
    cur = best = c0; bestAB = (list(A), list(B))
    acc = 0
    for step in range(a.steps):
        T = a.temp * (1 - step / a.steps)
        seq = A if rng.random() < len(A) / (len(A) + len(B)) else B
        i = rng.randrange(len(seq)); lo, hi = window(seq, i)
        if lo == hi: continue
        j = rng.randint(lo, hi)
        if j == i: continue
        g = seq.pop(i); seq.insert(j, g)
        c = P.price(A, B)
        if c is not None and (c < cur - 1e-12 or (T > 0 and rng.random() < math.exp(-(c - cur) / T))):
            cur = c; acc += 1
            if c < best - 1e-9:
                best = c; bestAB = (list(A), list(B))
        else:
            seq.pop(j); seq.insert(i, g)
        if step % 20000 == 0:
            print('step', step, 'cur %.4f best %.4f acc %d' % (cur, best, acc), flush=True)
    print('best least-frame price %.4f (input %.4f, gain %.4f)' % (best, c0, c0 - best))
    A, B = bestAB
    # order as permutation of original indices (gates are unique as lists? use positions)
    Path(a.out).write_text(json.dumps({'A': A, 'B': B}))


if __name__ == '__main__':
    main()
