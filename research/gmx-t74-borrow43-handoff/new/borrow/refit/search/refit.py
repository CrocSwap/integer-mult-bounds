"""minimal-change frame refits on a BORROW-WORD (in place on Bounds.Wd.w):
lower(t, X): gate t to F_t & X, backward meet-closure; raise_(t, Y): gate t to F_t + Y, forward join-closure.
Both check every pin (start, end, warp U/E, A/B-boundary equality pins). Return list of changed gate times or a failure string."""
from bounds import Bounds, basis, contained, regs, meet, span


class Refit:
    def __init__(s, b):
        s.b = b; s.Wd = b.Wd; s.ev = b.ev
        s.pos = {}      # (reg, time) -> index in byreg list
        for r, L in b.byreg.items():
            for i, x in enumerate(L):
                s.pos[(r, x[0])] = i

    def F(s, t):
        return basis(s.ev[t][1][-1])

    def setF(s, t, U):
        s.ev[t][1][-1] = list(U)

    def lower(s, t0, X):
        b = s.b; Wd = s.Wd
        C = {t0: basis(X)}
        changed = []
        import heapq
        heap = [-t0]; done = set()
        while heap:
            t = -heapq.heappop(heap)
            if t in done:
                continue
            done.add(t)
            old = s.F(t); new = meet(old, C[t])
            if new == old:
                continue
            if not contained(b.lo[t], new):
                return 'below-lo@%d' % t
            s.setF(t, new); changed.append((t, old, new))
            for q in regs(s.ev[t][1]):
                L = b.byreg[q]; i = s.pos[(q, t)]
                if t >= b.bnd and q in b.pin:
                    pa = [x for x in L[:i] if x[0] >= b.bnd]
                    if not pa and not contained(b.pin[q], new):
                        return 'pin@%d' % q
                if i == 0:
                    if not contained(Wd.start[q], new):
                        return 'start@%d' % q
                    continue
                x = L[i - 1]
                if x[1] == 'warp':
                    if not contained(x[3], new):
                        return 'warpE@%d' % q
                    continue
                k = x[0]
                C[k] = meet(C.get(k, Wd.full), new)
                heapq.heappush(heap, -k)
        return changed

    def raise_(s, t0, Y):
        b = s.b; Wd = s.Wd
        J = {t0: basis(Y)}
        changed = []
        import heapq
        heap = [t0]; done = set()
        while heap:
            t = heapq.heappop(heap)
            if t in done:
                continue
            done.add(t)
            old = s.F(t); new = span(old, J[t])
            if new == old:
                continue
            if not contained(new, b.hi[t]):
                return 'above-hi@%d' % t
            s.setF(t, new); changed.append((t, old, new))
            for q in regs(s.ev[t][1]):
                L = b.byreg[q]; i = s.pos[(q, t)]
                if t < b.bnd and q in b.pin and not [x for x in L[i + 1:] if x[0] < b.bnd]:
                    if new != b.pin[q]:
                        return 'pin@%d' % q
                if i == len(L) - 1:
                    if not contained(new, Wd.end[q]):
                        return 'end@%d' % q
                    continue
                x = L[i + 1]
                if x[1] == 'warp':
                    if new != x[2]:
                        return 'warpU@%d' % q
                    continue
                k = x[0]
                J[k] = span(J.get(k, ()), new)
                heapq.heappush(heap, k)
        return changed
