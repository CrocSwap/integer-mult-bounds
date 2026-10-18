"""Shared invoice-calculus code for the complex (#626-type) and bit (#555-type) moment roots.
root(): b is the root a of  sum_r (r n_r / (m W)) (m / r)^a = 1  (Decimal, Newton from the left: the function is convex and
increasing, so the iteration is monotone).  Inputs are read from ../inputs relative to the package root."""
import gzip, json, os, sys
from collections import Counter, defaultdict
from decimal import Decimal as D, localcontext

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(ROOT, 'inputs')
_failed = []


def check(cid, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + cid + ('  ' + str(detail) if detail != '' else ''), flush=True)
    if not ok:
        _failed.append(cid)
    return ok


def finish():
    sys.exit(1 if _failed else 0)


def load(rel):
    p = os.path.join(INP, rel)
    return json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p))


def root(H, m, W, prec=50, start=None):
    with localcontext() as c:
        c.prec = prec
        terms = [(D(r) * D(n) / D(m * W), (D(m) / D(r)).ln()) for r, n in H.items() if n]
        a = D(0) if start is None else start
        for _ in range(100):
            f = sum(p * (a * l).exp() for p, l in terms) - 1
            df = sum(p * l * (a * l).exp() for p, l in terms)
            na = a - f / df
            if abs(na - a) < D(10) ** (-(prec - 5)):
                return na
            a = na
        raise RuntimeError('no convergence')


def profile(plan):
    return {int(k): v for k, v in plan['profile'].items()}


def hmass(H):
    return sum(r * n for r, n in H.items())


M, W0, CALLS = 73, 7168, {'ck': 8, 'jp8': 64}


class Word626:
    """Per-register climb widths of the ck / jp8 local words of #626 (inputs/derived/k492_registers.json)."""
    def __init__(self):
        d = load('derived/k492_registers.json')
        self.d = d
        self.H = Counter()
        for p, c in CALLS.items():
            for r in d[p]['regs']:
                for w in r:
                    self.H[w] += c
        self.plan = load('pr626/PLAN.json.gz')
        self.prof = profile(self.plan)
        self.idle = Counter(self.prof)
        for w, n in self.H.items():
            self.idle[w] -= n
        self.idle = Counter({w: n for w, n in self.idle.items() if n})
        self.B0 = Counter(self.H) + Counter(self.idle)

    def helpers(self, prov, width):
        d = self.d[prov]; v, R = d['v'], d['R']
        return [d['regs'][r] for r in range(2 * v, 2 * v + R) if r not in d['centers'] and sum(d['regs'][r]) == width]
