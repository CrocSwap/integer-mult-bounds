#!/usr/bin/env python3
"""Deterministic CNF generator for the TIGHT55 certificate (standard library only, no pickles).

Statement encoded: no tight B-linear half-integer P104 decoder (rows z in Z16, U_z a subspace of F2^9, W arbitrary)
has price <= 55.  Variables: used[z,i] (dim U_z^perp > i, order encoded), RREF basis bits f/L, membership m[z,t],
nin[z] = [n_z in U_z]; covering clauses (data/zclauses.json, re-derived from the Z4 definition by check.py);
totalizer sum(used)+sum(nin) >= 89 (<=> cost <= 55); lex-leader over the 384 symmetries (data/perms.json).

Usage:  python3 gen.py base OUT.cnf
        python3 gen.py cube ID OUT.cnf      (ID from cubes.txt)
        python3 gen.py sha ID               (print sha256 of the cube CNF)
"""
import hashlib
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
BUD = 55
K = 144 - BUD


def load_geometry():
    E = json.loads((DATA / "e8base.json").read_text())
    CR = E["C"]
    Z = CR[104:]
    H = [[1] + [x % 2 for x in c] for c in CR[:104]]
    Nz = [[1] + [x % 2 for x in z] for z in Z]
    CL = json.loads((DATA / "zclauses.json").read_text())
    PERMS = json.loads((DATA / "perms.json").read_text())
    return H, Nz, CL, PERMS


class Base:
    def __init__(self):
        H, Nz, CL, PERMS = load_geometry()
        self.nv = 0
        cls = self.cls = []
        new = self.new

        f = {}; used = self.used = {}; L = {}
        for z in range(16):
            for i in range(9):
                used[z, i] = new()
                for c in range(9):
                    f[z, i, c] = new(); L[z, i, c] = new()
        for z in range(16):
            for i in range(9):
                u = used[z, i]
                if i > 0: cls.append((-u, used[z, i - 1]))
                for c in range(9): cls.append((u, -f[z, i, c])); cls.append((u, -L[z, i, c]))
                cls.append(tuple([-u] + [L[z, i, c] for c in range(9)]))
                for c in range(9):
                    for c2 in range(c + 1, 9): cls.append((-L[z, i, c], -L[z, i, c2]))
                    cls.append((-L[z, i, c], f[z, i, c]))
                    for c2 in range(c): cls.append((-L[z, i, c], -f[z, i, c2]))
                    for i2 in range(9):
                        if i2 != i: cls.append((-L[z, i, c], -f[z, i2, c]))
                    if i < 8:
                        for c2 in range(c + 1): cls.append((-L[z, i, c], -L[z, i + 1, c2]))

        self.xdef = xdef = {}
        self.tnodes = []

        def xorvar(lits):
            if len(lits) == 1: return lits[0]
            a = lits[0]
            for b in lits[1:]:
                p = new(); xdef[p] = (a, b)
                cls.extend([(-p, a, b), (-p, -a, -b), (p, -a, b), (p, a, -b)]); a = p
            return a
        m = {}; nin = self.nin = {}
        for z in range(16):
            for t in range(104):
                m[z, t] = new()
                sup = [c for c in range(9) if H[t][c]]
                for i in range(9):
                    p = xorvar([f[z, i, c] for c in sup]); cls.append((-m[z, t], -p))
        for z in range(16):
            sup = [c for c in range(9) if Nz[z][c]]
            nin[z] = new()
            for i in range(9):
                p = xorvar([f[z, i, c] for c in sup]); cls.append((-nin[z], -p))
        self.n_cov0 = len(cls)
        for t in range(104):
            for r in CL[t]: cls.append(tuple(m[z, t] for z in range(16) if r >> z & 1))
        lits = [used[z, i] for z in range(16) for i in range(9)] + [nin[z] for z in range(16)]

        def tot(ls):
            if len(ls) == 1: return [ls[0]]
            h = len(ls) // 2; a = tot(ls[:h]); b = tot(ls[h:]); o = [new() for _ in range(len(ls))]
            p = len(a); q = len(b)
            for i in range(p + 1):
                for j in range(q + 1):
                    k = i + j + 1
                    if k > p + q: continue
                    c = [-o[k - 1]]
                    if i < p: c.append(a[i])
                    if j < q: c.append(b[j])
                    cls.append(tuple(c))
            self.tnodes.append((o, a, b))
            return o
        self.n_tot0 = len(cls)
        self.lits = lits
        o = tot(lits); cls.append((o[K - 1],))
        self.n_tot1 = len(cls)
        self.lex = []
        for p in PERMS:
            if all(p[j] == j for j in range(16)): continue
            prev = None
            for j in range(16):
                if p[j] == j: continue
                e = new(); pre = [] if prev is None else [-prev]
                for v in range(9): cls.append(tuple(pre + [-used[p[j], v], used[j, v]]))
                ss = []
                for v in range(9):
                    sv = new(); ss.append(sv); cls.append((-sv, used[j, v])); cls.append((-sv, -used[p[j], v]))
                cls.append(tuple(pre + [e] + ss)); prev = e
                self.lex.append((p, j, e, ss))
        self.m = m; self.f = f; self.L = L

    def new(self):
        self.nv += 1
        return self.nv

    def text(self, extra=()):
        out = ["p cnf %d %d\n" % (self.nv, len(self.cls) + len(extra))]
        out.extend(" ".join(map(str, c)) + " 0\n" for c in self.cls)
        out.extend(" ".join(map(str, c)) + " 0\n" for c in extra)
        return "".join(out)


# split recipes: cube id -> (inactive mask, order, extra clauses as [(sign, kind, z, i)]) ; u = used[z,i]
U = lambda z, i: (1, "u", z, i)
NU = lambda z, i: (-1, "u", z, i)
SPLITS = {  # (mask, units-before-norm?, split literals as clauses)
    "i1_d1le5": (1, True, [[NU(1, 5)]]),
    "i1_d1_6": (1, True, [[U(1, 5)], [NU(1, 6)]]),
    "i1_d1_7": (1, True, [[U(1, 6)], [NU(1, 7)]]),
    "i1_d1_8": (1, True, [[U(1, 7)]]),
    "i0_d0_le6": (0, False, [[NU(0, 6)]]),
    "i0_d0_7": (0, False, [[U(0, 6)], [NU(0, 7)]]),
    "j8_le5": (0, False, [[U(0, 7)], [NU(1, 5)]]),
    "j8_6": (0, False, [[U(0, 7)], [U(1, 5)], [NU(1, 6)]]),
    "j8_7": (0, False, [[U(0, 7)], [U(1, 6)], [NU(1, 7)]]),
    "j8_8": (0, False, [[U(0, 7)], [U(1, 7)]]),
}


def cube_extra(b, cid):
    """extra clauses (after the base body) of cube cid: 'i<mask>' / 'f<mask>' or a split cube name."""
    def units(mask): return [[b.used[z, 8] if mask >> z & 1 else -b.used[z, 8]] for z in range(16)]
    norm = [[-b.used[z, 7], b.used[z, 8], -b.nin[z]] for z in range(16)]
    if cid in SPLITS:
        mask, ufirst, sp = SPLITS[cid]
        sp = [[s * b.used[z, i] for (s, _, z, i) in cl] for cl in sp]
        return (units(mask) + norm if ufirst else norm + units(mask)) + sp
    return units(int(cid[1:])) + norm


def cube_text(cid, b=None):
    b = b or Base()
    return b.text(cube_extra(b, cid))


def main(argv):
    if len(argv) >= 3 and argv[1] == "base":
        Path(argv[2]).write_text(Base().text())
    elif len(argv) >= 4 and argv[1] == "cube":
        Path(argv[3]).write_text(cube_text(argv[2]))
    elif len(argv) >= 3 and argv[1] == "sha":
        print(hashlib.sha256(cube_text(argv[2]).encode()).hexdigest())
    else:
        print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
