# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Geometry of the quad skeleton on the 5-pair D4 partition of the 120 E8 lines (Hamming coordinates, #370 order).

Objects
  blocks   10 D4 sub-root-systems (12 lines each) in 5 complementary pairs; comp[b]
  frames4  30 orthogonal 4-frames (3 per block)
  cells    180 pairs inside a 4-frame (cell = tuple(sorted pair)); cell span is 2-dim and holds exactly 2 lines
  D6s      one per cell C' = {t,e}: H = C'^perp (30 lines); 'owner' cell C'
  quads    60 4-dim D4 frames, each = 6 cells from 6 blocks (3 complementary block pairs); each quad is a feeding
           quad of 6 D6s (2 per block pair); each D6 has 2 feeding quads U1, U2 with U1 & U2 = span(d-cell)
The 5-pair partition is data/skeleton/d4part-pairs.json (10 line masks, hex; checked to be a partition into
complementary D4 pairs below)."""
import itertools
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8  # noqa: E402

V = e8.V
GI = e8.GI


def _d4_frames(m):
    ls = e8.bits(m)
    out = [q for q in itertools.combinations(ls, 4) if all(GI[x, y] == 0 for x, y in itertools.combinations(q, 2))]
    assert len(out) == 3
    return out


class Geom:
    def __init__(self, partfile=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "skeleton",
                                           "d4part-pairs.json")):
        D4 = [int(h, 16) for h in json.load(open(partfile))]
        assert sorted(x for m in D4 for x in e8.bits(m)) == list(range(V))
        self.blocks = list(D4)
        self.blk = {x: i for i, m in enumerate(D4) for x in e8.bits(m)}
        self.comp = {i: [j for j, m2 in enumerate(D4) if m2 == e8.perp(m)][0] for i, m in enumerate(D4)}
        self.frames4 = [tuple(sorted(f)) for m in D4 for f in _d4_frames(m)]
        self.phi = {x: f for f in self.frames4 for x in f}
        self.cells = [tuple(sorted(p)) for f in self.frames4 for p in itertools.combinations(f, 2)]
        self.cmask = {c: (1 << c[0]) | (1 << c[1]) for c in self.cells}
        self.cblk = {c: self.blk[c[0]] for c in self.cells}
        self.D6 = {c: e8.perp(self.cmask[c]) for c in self.cells}     # owner cell -> D6 mask
        # E-set and feeding cells
        cells_of = defaultdict(list)
        for c in self.cells:
            for x in c:
                cells_of[x].append(c)
        self.cells_of = cells_of
        fed = defaultdict(set)
        for c in self.cells:
            o = [x for x in self.phi[c[0]] if x not in c]
            E = [s for s in e8.bits(self.D6[c]) if GI[s, o[0]] != 0 and GI[s, o[1]] != 0]
            for s in E:
                for c1 in cells_of[s]:
                    if (self.cmask[c1] & ~self.D6[c]) == 0:
                        fed[c].add(c1)
        # quads
        self.quads = []          # list of masks
        qidx = {}
        self.d6quads = {}        # owner -> (qi1, qi2)
        for c2 in self.cells:
            fs = sorted(fed[c2])
            qs = []
            for q in itertools.combinations(fs, 4):
                m = 0
                for c in q:
                    m |= self.cmask[c]
                if e8.dim(m) == 4:
                    U = e8.closure(m)[0]
                    if U not in qidx:
                        qidx[U] = len(self.quads)
                        self.quads.append(U)
                    qs.append(qidx[U])
            assert len(qs) == 2
            self.d6quads[c2] = tuple(qs)
        self.qcells = [[c for c in self.cells if (self.cmask[c] & ~U) == 0] for U in self.quads]
        self.qowners = defaultdict(list)
        for c2, qs in self.d6quads.items():
            for q in qs:
                self.qowners[q].append(c2)
        for q in range(len(self.quads)):
            assert len(self.qcells[q]) == 6 and len(self.qowners[q]) == 6
        # per (quad, owner): the two pi-cells (d-cell of the owner, Q-cell) and the four E-cells
        self.dcell = {}
        for c2 in self.cells:
            f = self.phi[c2[0]]
            self.dcell[c2] = tuple(sorted(x for x in f if x not in c2))
        self.qcell = {}          # (q, owner) -> Q-cell of quad q w.r.t. owner
        self.ecells = {}
        for q in range(len(self.quads)):
            for c2 in self.qowners[q]:
                b = self.cblk[c2]
                dd = [c for c in self.qcells[q] if self.cblk[c] == b]
                qq = [c for c in self.qcells[q] if self.cblk[c] == self.comp[b]]
                assert len(dd) == 1 and dd[0] == self.dcell[c2] and len(qq) == 1
                self.qcell[(q, c2)] = qq[0]
                self.ecells[(q, c2)] = [c for c in self.qcells[q] if c not in (dd[0], qq[0])]
        # block pairs of a quad: pair -> (owner from lower block id side?, ...)
        self.qpairs = {}
        for q in range(len(self.quads)):
            byp = defaultdict(list)
            for c2 in self.qowners[q]:
                b = self.cblk[c2]
                byp[tuple(sorted((b, self.comp[b])))].append(c2)
            assert all(len(v) == 2 for v in byp.values()) and len(byp) == 3
            self.qpairs[q] = dict(byp)
        # Psi: Q 4-frame for each 4-frame
        self.psi = {}
        for f in self.frames4:
            t = f[0]
            qs = set()
            for e in f[1:]:
                c2 = tuple(sorted((t, e)))
                for q in self.d6quads[c2]:
                    qs.add(self.qcell[(q, c2)])
            lines = tuple(sorted(set(x for c in qs for x in c)))
            assert lines in self.frames4
            self.psi[f] = lines

    def esum(self, c2):
        """mask of the 16 E-lines of D6 owned by c2"""
        m = 0
        for q in self.d6quads[c2]:
            for c in self.ecells[(q, c2)]:
                m |= self.cmask[c]
        return m


if __name__ == "__main__":
    G = Geom()
    print("blocks", len(G.blocks), "frames4", len(G.frames4), "cells", len(G.cells), "quads", len(G.quads))
    # sanity: J_t = E(H1)+E(H2)+E(H3) + d-lines + Q
    for t in range(V):
        f = G.phi[t]
        acc = 0
        for e in f:
            if e != t:
                acc ^= G.esum(tuple(sorted((t, e))))
        for e in f:
            if e != t:
                acc ^= 1 << e
        acc ^= G.blocks[G.comp[G.blk[t]]]
        assert acc == e8.HYP[t], t
    print("J_t = E-sums + d-lines + Q: OK for all 120 targets")
