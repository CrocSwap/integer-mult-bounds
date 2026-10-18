# SPDX-License-Identifier: Apache-2.0
"""Screen single-helper dirty entry on a BORROW-WORD supplier word.

A compensated helper q0 can enter dirty (start at a nonzero frame, losing width and its first climb) only if
its whole target-dirt response is cancelled inside the program. This screen asks whether that response lies in
the exact span of responses reachable by inserted gates `r += u*q0`:

* insertion at any program position outside the prelude and the cut, up to q0's purity horizon (first scale
  of q0 or first warp pin after its first use);
* before q0's first use, q0 = z0 exactly; afterwards q0 = z0 + sum c_j s_j and every read partner s_j must be
  unchanged, with cancellation gates `r += -u c_j s_j` at the same frame;
* receivers: every live non-target register except q0, initial-correction sources, entering helpers and
  (mode `direct`) q0's own partners; mode `pre-only` allows only insertions before q0's first use;
* frame feasibility over the full program timeline: one gate frame U with join(current frames) <= U <=
  meet(next required frames) for the receiver, q0 and every cancelled partner; exact pins are respected;
* `--chains`: one-hop relays through an intermediate helper m (inject into m at t1, then `r += k*m` at t2 with
  m's partner cancellation). Chain gates move m's whole content, so a plan is valid only if the injection
  coefficient into m is nonzero: target in span(V + R_m) and (R_m in span(V) or target not in span(V)),
  where V = direct options not touching m plus the chain vectors from that injection;
* `--relax-frames`: drop every frame constraint and cost (an optimistic control, not a construction).

The reported cost is a pruned greedy upper bound on the extra climb cost (H_r = r^p at the #2863 root).
A positive answer is a screening lead only; it is not an audited word, allocation or kappa.

Prepared for digitalis-p with Claude (Anthropic) assistance. Apache-2.0.
"""
import argparse
import bisect
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wordlib as W  # noqa: E402

ALPHA = 0.001720100805416886
P = 1 - ALPHA


def H(d):
    return d ** P if d > 0 else 0.0


def split_cost(u, f, n):
    if u == f or u == n:
        return 0.0
    return H(len(u) - len(f)) + H(len(n) - len(u)) - H(len(n) - len(f))


class Span:
    def __init__(self, vectors=()):
        self.piv = {}
        for v in vectors:
            self.add(v)

    def reduce(self, v):
        v = dict(v)
        while v:
            k = min(v)
            if k not in self.piv:
                return v, k
            pv = self.piv[k]
            f = v[k] / pv[k]
            for kk, val in pv.items():
                nv = v.get(kk, F(0)) - f * val
                if nv:
                    v[kk] = nv
                else:
                    v.pop(kk, None)
        return v, None

    def add(self, v):
        r, k = self.reduce(v)
        if k is not None:
            self.piv[k] = r
            return True
        return False

    def contains(self, v):
        return not self.reduce(v)[0]


def in_span(vectors, target):
    return Span(vectors).contains(target)


class Screen:
    def __init__(self, x, mode='direct', relax=False):
        self.x, self.mode, self.relax = x, mode, relax
        self.npre = x.get('prelude_events', 0)
        self.live = set(range(W.NREG)) - set(x['removed'])
        self.nontarget = [r for r in sorted(self.live) if not (W.V <= r < 2 * W.V)]
        self.R0, self.taint0, self.snaps, self.prog = W.adjoint(x, record=set(self.nontarget))
        self.nA = len(x['A'])
        self.corr = {c['source'] for c in x['initial_corrections']}
        self.entering = set(map(int, x['start_extra']))
        self.start = W.start_frames(x)
        self.tl = W.timeline(x, self.prog)
        self.writes = {}
        for k, (_, _, e) in enumerate(self.prog):
            if e[0] in ('add', 'scale'):
                self.writes.setdefault(e[1], []).append(k)
        self.tpos = {r: [i for (i, _, _, _) in ev] for r, ev in self.tl.items()}
        self.spos = {r: [k for (k, _, _) in sn] for r, sn in self.snaps.items()}

    def cur(self, r, k):
        j = bisect.bisect_left(self.tpos[r], k) - 1
        return self.tl[r][j][3] if j >= 0 else self.start[r]

    def nxt(self, r, k):
        j = bisect.bisect_left(self.tpos[r], k)
        if j >= len(self.tl[r]):
            raise AssertionError('timeline has an end event')
        return self.tl[r][j][2]

    def unchanged(self, s, a, b):
        w = self.writes.get(s, [])
        j = bisect.bisect_right(w, a)
        return not (j < len(w) and w[j] < b)

    def resp(self, r, k):
        pos = self.spos.get(r)
        if not pos:
            return {}, False
        j = bisect.bisect_left(pos, k)
        if j >= len(pos):
            return {}, False
        _, R, tn = self.snaps[r][j]
        return R, tn

    def insertable(self, k):
        return k >= self.npre and (k >= len(self.prog) or self.prog[k][0] != 'cut')

    def events(self, q):
        return [(k, e) for k, (_, _, e) in enumerate(self.prog)
                if e[0] in ('add', 'scale') and q in W.regs_of(e)]

    def eligible(self, q):
        return (q in self.live and q not in self.entering and q not in self.corr
                and not self.taint0[q] and bool(self.R0[q]) and bool(self.events(q)))

    def horizon(self, q, evs, t0):
        h = len(self.prog)
        for k, e in evs:
            if e[0] == 'scale':
                h = min(h, k)
                break
        for (i, kind, req, aft) in self.tl[q]:
            if kind == 'pin' and i > t0:
                h = min(h, i)
                break
        return h

    def gate_option(self, r, tau, fq, nq, act, extra_lo=(), base_cost=0.0):
        """Feasible frame and extra cost for a gate on receiver r at tau (None if infeasible)."""
        fr, nr = self.cur(r, tau), self.nxt(r, tau)
        if self.relax:
            return fr, 0.0
        lo = W.join(fr, fq, extra_lo, *[self.cur(s, tau) for s, _, _ in act])
        hi = W.meet(nr, nq)
        for s, _, _ in act:
            hi = W.meet(hi, self.nxt(s, tau))
        if len(hi) == 0 or not W.contained(lo, hi):
            return None
        best = None
        for u in ({lo, hi} if len(lo) else {hi}):
            c = split_cost(u, fr, nr)
            c += sum(split_cost(u, self.cur(s, tau), self.nxt(s, tau)) for s, _, _ in act)
            c += base_cost
            if best is None or c < best[1]:
                best = (u, c)
        return best

    def direct_options(self, q0, t0, F1, partners, horizon, pset):
        opts = []
        qtimes = {k for k, _ in self.events(q0)}
        for r in self.nontarget:
            if r == q0 or r in self.corr or r in self.entering:
                continue
            if self.mode == 'direct' and r in pset:
                continue
            times = sorted({i for (i, _, _, _) in self.tl[r] if i < len(self.prog)} | qtimes)
            for tau in times:
                if tau > horizon or not self.insertable(tau):
                    continue
                if self.mode == 'pre-only' and tau > t0:
                    continue
                R, tn = self.resp(r, tau)
                if tn or not R:
                    continue
                if tau <= t0:
                    fq, nq, act = (), F1, []
                else:
                    fq, nq = self.cur(q0, tau), self.nxt(q0, tau)
                    act = [(s, c, ri) for (s, c, ri) in partners if ri < tau]
                    if not all(self.unchanged(s, ri, tau) for s, _, ri in act):
                        continue
                opt = self.gate_option(r, tau, fq, nq, act)
                if opt is None:
                    continue
                u, c = opt
                if not self.relax and tau > t0:
                    c += split_cost(u, fq, nq)
                opts.append(dict(r=r, tau=tau, U=u, cost=c, R=R, pre=tau <= t0))
        return opts

    def chain_check(self, q0, target, direct, pset):
        """Exact bilinear validity of one-hop relays. Returns list of (m, tau1, valid) for usable relays."""
        out = []
        for o1 in direct:
            m = o1['r']
            if m < 2 * W.V or m in pset:
                continue
            mev = self.events(m)
            mpart = [(e[2], F(e[3], e[4]), k) for k, e in mev if e[0] == 'add' and e[1] == m]
            mscale = [k for k, e in mev if e[0] == 'scale']
            mp = {s for s, _, _ in mpart}
            chains = []
            for r in self.nontarget:
                if r in (m, q0) or r in self.corr or r in self.entering or r in pset or r in mp:
                    continue
                for (tau2, kind, req, aft) in self.tl[r]:
                    if tau2 <= o1['tau'] or tau2 >= len(self.prog) or not self.insertable(tau2):
                        continue
                    if any(o1['tau'] <= j < tau2 for j in mscale):
                        continue
                    R, tn = self.resp(r, tau2)
                    if tn or not R:
                        continue
                    act = [(s, c, ri) for (s, c, ri) in mpart if ri < tau2]
                    if not all(self.unchanged(s, ri, tau2) for s, _, ri in act):
                        continue
                    fm, nm = W.join(self.cur(m, tau2), o1['U']), self.nxt(m, tau2)
                    if self.gate_option(r, tau2, fm, nm, act) is None:
                        continue
                    chains.append(R)
            if not chains:
                continue
            others = [o['R'] for o in direct if o['r'] != m and o['r'] not in mp]
            V = Span(others + chains)
            with_m = Span(others + chains + [o1['R']])
            if not with_m.contains(target):
                continue
            valid = V.contains(o1['R']) or not V.contains(target)
            out.append(dict(m=m, tau1=o1['tau'], valid=valid))
        return out

    def run(self, q0, chains=False):
        evs = self.events(q0)
        t0, first = evs[0]
        F1 = W.basis(first[-1])
        rec: dict = dict(q0=q0, first_pos=t0, first_frame_dim=len(F1))
        if len(F1) == 0 and not self.relax:
            rec.update(in_span=False, reason='first gate at the zero frame')
            return rec
        partners, horizon = [], None
        for k, e in evs:
            if e[0] == 'add' and e[1] == q0:
                partners.append((e[2], F(e[3], e[4]), k))
        horizon = self.horizon(q0, evs, t0)
        pset = {s for s, _, _ in partners}
        target = {t: -v for t, v in self.R0[q0].items()}
        opts = self.direct_options(q0, t0, F1, partners, horizon, pset)
        rec.update(options=len(opts), options_after_A=sum(o['tau'] >= self.nA for o in opts))
        span = Span()
        used = []
        for o in sorted(opts, key=lambda o: o['cost']):
            if span.contains(target):
                break
            if span.add(o['R']):
                used.append(o)
        ok = span.contains(target)
        rec['in_span'] = ok
        if ok:
            pool = [o for o in opts if o['cost'] == 0] + [o for o in used if o['cost'] > 0]
            for o in sorted([o for o in pool if o['cost'] > 0], key=lambda o: -o['cost']):
                rest = [p for p in pool if p is not o]
                if in_span([p['R'] for p in rest], target):
                    pool = rest
            costly = [o for o in pool if o['cost'] > 0]
            rec.update(pruned_cost=round(sum(o['cost'] for o in costly), 6),
                       costly=[(o['r'], o['tau'], len(o['U']), round(o['cost'], 6)) for o in costly])
        elif chains:
            ch = self.chain_check(q0, target, opts, pset)
            rec['chain_relays'] = ch
            rec['chain_valid'] = any(c['valid'] for c in ch)
        return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--word', required=True, type=Path)
    ap.add_argument('--mode', choices=['direct', 'pre-only'], default='direct')
    ap.add_argument('--chains', action='store_true')
    ap.add_argument('--relax-frames', action='store_true')
    ap.add_argument('--zero-first-only', action='store_true')
    ap.add_argument('--helpers', default='')
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    x, digest = W.load(a.word)
    sc = Screen(x, a.mode, a.relax_frames)
    helpers = [int(h) for h in a.helpers.split(',') if h] or [h for h in range(2 * W.V, W.NREG) if sc.eligible(h)]
    rows = []
    for q in helpers:
        if not sc.eligible(q):
            rows.append(dict(q0=q, eligible=False))
            continue
        if a.zero_first_only and len(W.basis(sc.events(q)[0][1][-1])) > 0:
            continue
        rows.append(sc.run(q, chains=a.chains))
    res = dict(word_sha256=digest, mode=a.mode, chains=a.chains, relax_frames=a.relax_frames,
               zero_first_only=a.zero_first_only, screened=sum(1 for r in rows if r.get('eligible', True)),
               in_span=sorted(r['q0'] for r in rows if r.get('in_span')),
               zero_frame_first=sorted(r['q0'] for r in rows if r.get('reason')),
               chain_apparent=sorted(r['q0'] for r in rows if r.get('chain_relays')),
               chain_valid=sorted(r['q0'] for r in rows if r.get('chain_valid')), rows=rows)
    text = json.dumps(res, indent=1, default=list) + '\n'
    if a.out:
        a.out.write_text(text, encoding='utf-8')
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
