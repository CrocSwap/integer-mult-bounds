"""Shared model of a #2474 BORROW-WORD: time-ordered forward program, per-register touches,
frame replay (literal copy of audit_local.run_borrow section 4), per-register climbs.

Time order (audit_local): precondition, compensation, A (prelude first), cut, B with warps inserted
before B[p], restore, then final climbs to end frames. Cleanup is the inverse-reverse of the recorded
forward program at FULL, so it mirrors the forward intervals and is not modelled separately.
"""
import gzip, json
from collections import Counter, defaultdict


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv:
                a ^= piv[bit]
            else:
                piv[bit] = a
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b):
    return basis(list(a) + list(b)) == b


def regs(e):
    return e[1:3] if e[0] == 'add' else e[1:2]


class Word:
    def __init__(self, path):
        w = json.load(gzip.open(path))
        self.w = w
        v, h, R = w['report']['v'], w['report']['h'], w['report']['R']
        self.v, self.h, self.R = v, h, R
        n = 2 * v + R
        self.n = n
        self.removed = set(w['removed'])
        self.live = [r for r in range(n) if r not in self.removed]
        self.helpers = [r for r in self.live if r >= 2 * v]
        full = basis([1 << i for i in range(h)])
        self.full = full
        end = [full] * v + [basis([x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0]) for p in w['ports']] + [full] * R
        for q, U in w.get('helper_final', {}).items():
            end[int(q)] = basis(U)
        start = [(p,) for p in w['ports']] + [()] * (v + R)
        for q, U in w.get('start_extra', {}).items():
            start[int(q)] = basis(U)
        self.start, self.end = start, end
        # ---- time-ordered event list: (time, section, item)
        ev = []
        for sec in ('precondition', 'compensation'):
            for e in w[sec]:
                ev.append((sec, e))
        for e in w['A']:
            ev.append(('A', e))
        for e in w['cut']:
            ev.append(('cut', e))
        byp = defaultdict(list)
        for op, rec in enumerate(w['warps'], 1):
            byp[rec[0]].append(op)
        B = w['B']
        for p in range(len(B) + 1):
            for op in byp.get(p, []):
                ev.append(('Bwarp', ['warp', w['warps'][op - 1][1], op]))
            if p < len(B):
                ev.append(('B', B[p]))
        for e in w['restore']:
            ev.append(('restore', e))
        self.events = ev
        self.T_END = len(ev)
        # ---- frame replay with climbs (literal copy of audit logic)
        cur = list(start)
        paid = Counter()
        climbs = defaultdict(list)       # reg -> [(time, rank, from, to)]
        gateframe = {}                   # time -> frame of the gate (basis) or None

        def climb(q, U, t):
            U = basis(U)
            assert contained(cur[q], U), ('frame not monotone', q, cur[q], U)
            d = len(U) - len(cur[q])
            if d:
                paid[d] += 1
                climbs[q].append((t, d, cur[q], U))
            cur[q] = U

        npre = w.get('prelude_events', 0)
        warps = w['warps']
        A0 = len(w['precondition']) + len(w['compensation'])
        self.frames_at = {}
        for t, (sec, e) in enumerate(ev):
            if sec in ('precondition', 'compensation', 'cut'):
                continue
            if e[0] == 'warp':
                if sec == 'A':
                    _, r_, op_, fr_, to_ = e
                    assert cur[r_] == basis(fr_)
                    cur[r_] = basis(to_)
                else:
                    _, lender, op = e
                    _, _, cols, U, E = warps[op - 1]
                    assert cur[lender] == basis(U)
                    cur[lender] = basis(E)
                continue
            gateframe[t] = basis(e[-1])
            for q in regs(e):
                climb(q, e[-1], t)
            if sec == 'A' and t == A0 + len(w['A']) - 1:
                pass
        # centre path (between A and B; charged to centres, as in audit)
        lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
        # (centre frames were reached during A; the centre path is extra paid children)
        self.centre_paid = Counter()
        for q, U in zip(w['centers'], w['center_frames']):
            U = basis(U)
            served = {lev.get(e[1] - v, ()) for e in w['cut'] if e[2] == q}
            for T in sorted(served, key=lambda x: -len(x)):
                if T != U:
                    paid[len(U) - len(T)] += 1
                    self.centre_paid[len(U) - len(T)] += 1
                U = T
        for q in self.live:
            climb(q, end[q], self.T_END)
        self.paid = paid
        self.climbs = climbs
        self.gateframe = gateframe
        assert dict(paid) == {int(k): a for k, a in w['report']['local_profile'].items()}, (dict(paid), w['report']['local_profile'])
        inv = Counter(len(end[q]) - len(start[q]) for q in self.helpers)
        assert dict(inv) == {int(k): a for k, a in w['report']['width_inventory'].items()}
        # ---- touches
        touches = defaultdict(list)     # reg -> [(time, section)]
        for t, (sec, e) in enumerate(ev):
            if e[0] == 'warp':
                touches[e[1]].append((t, sec + ':warp'))
            else:
                for q in regs(e):
                    touches[q].append((t, sec))
        self.touches = touches

    def istarget(self, r):
        return self.v <= r < 2 * self.v
