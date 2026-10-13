"""Word builder for punctured bit words (live port subset of the 120 E8 lines).
Internal ids follow wordkit.Word (x_s = s, y_t = V+t, helpers 2V+k, geometry line indices); build() renumbers to the
compact v = |live| layout of the bitE8/1 format.  Frames are LIVE line sets (closed 120-line mask & live mask); their
rank is that of the live lines (checkers recompute it from the word's `lines`)."""
import os, sys
PARENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "e8-bit-carrier-skeleton")   # PR #493's package
sys.path.insert(0, os.path.join(PARENT, "code", "skeleton"))
import e8  # noqa
from wordkit import solve_transform_lu, inverse_ops_nopivot, save  # noqa

V = e8.V


class PWord:
    def __init__(self, live):
        self.live = live
        self.ports = e8.bits(live)
        self.nh = 0
        self.cur, self.content, self.role = {}, {}, {}
        for s in self.ports:
            self.cur[s] = 1 << s
            self.content[s] = 1 << s
        for t in self.ports:
            self.cur[V + t] = 0
            self.content[V + t] = 1 << (V + t)
        self.A, self.B = [], []
        self.ret = []
        self.phase = "A"
        self.cleanup = "literal"

    def helper(self, role=""):
        r = 2 * V + self.nh
        self.nh += 1
        self.cur[r] = 0
        self.content[r] = 1 << r
        self.role[r] = role
        return r

    def fr(self, F):
        return (e8.closure(F)[0] if F else 0) & self.live

    def climb(self, r, F):
        a = self.cur[r]
        if a == F:
            return
        assert (a & ~F) == 0, ("frame not nested", r, e8.bits(a), e8.bits(F))
        self.cur[r] = F

    def gate(self, F, dst, srcs):
        F = self.fr(F)
        regs = [dst] + list(srcs)
        assert len(set(regs)) == len(regs), regs
        assert not (V <= dst < 2 * V and self.phase == "A"), "y written before the scatter"
        for r in regs:
            assert r in self.cur, ("absent register", r)
            if V <= r < 2 * V:
                assert self.phase == "B", "y used before the scatter"
            self.climb(r, F)
        for s in srcs:
            self.content[dst] ^= self.content[s]
        (self.A if self.phase == "A" else self.B).append((F, dst, list(srcs)))

    def xpart(self, r):
        return self.content[r] & ((1 << V) - 1)

    def build(self, scatter_rows):
        nh = self.nh
        ports = self.ports
        v = len(ports)
        pidx = {s: i for i, s in enumerate(ports)}

        def rid(r):           # internal -> compact id
            if r < V:
                return pidx[r]
            if r < 2 * V:
                return v + pidx[r - V]
            return 2 * v + (r - 2 * V)
        frames = {}

        def fid(mask):
            if mask not in frames:
                frames[mask] = len(frames)
            return frames[mask]
        FULL = self.live
        fid(0)
        fid(FULL)
        A = [[fid(F), d, list(s)] for F, d, s in self.A]     # internal ids
        B = [[fid(F), d, list(s)] for F, d, s in self.B]
        dv = {}
        for h in range(nh):
            dv[2 * V + h] = 1 << h
        for s in ports:
            dv[s] = 0
            dv[V + s] = 0
        for f, d, srcs in A:
            for s in srcs:
                dv[d] ^= dv[s]
        cdirt = [dv[q] for q in self.ret]
        for t in ports:
            for k in scatter_rows[t]:
                dv[V + t] ^= cdirt[k]
        for f, d, srcs in B:
            for s in srcs:
                dv[d] ^= dv[s]
        D = []
        for t in ports:
            m = dv[V + t]
            srcs = []
            while m:
                b = m & -m
                srcs.append(2 * V + b.bit_length() - 1)
                m ^= b
            if srcs:
                D.append([fid(0), V + t, srcs])
        Cl = []
        for f, d, srcs in reversed(A + B):
            if d < V or d >= 2 * V:
                Cl.append([fid(FULL), d, srcs])
        fr = [None] * len(frames)
        for mk, i in frames.items():
            fr[i] = [pidx[b] for b in e8.bits(mk)]
        z = fid(0)
        start = [fid(1 << s) for s in ports] + [z] * (v + nh)
        final = [fid(FULL)] * v + [fid(e8.HYP[t] & self.live) for t in ports] + [fid(FULL)] * nh
        # frames dict may have grown (fid for start/final): rebuild fr
        fr = [None] * len(frames)
        for mk, i in frames.items():
            fr[i] = [pidx[b] for b in e8.bits(mk)]

        def rg(gs):
            return [[f, rid(d), [rid(s) for s in srcs]] for f, d, srcs in gs]
        return dict(format="bitE8/1+mut", coords="ham", h=8, v=v, R=nh, lines=[list(e8.LINES[s]) for s in ports],
                    form="<x,y>/2", frames=fr, start=start, final=final, ret=[rid(q) for q in self.ret],
                    scatter=[list(scatter_rows[t]) for t in ports], D=rg(D), A=rg(A), B=rg(B), C=rg(Cl),
                    punctured=[s for s in range(V) if not (self.live >> s) & 1],
                    ports_geom=ports)
