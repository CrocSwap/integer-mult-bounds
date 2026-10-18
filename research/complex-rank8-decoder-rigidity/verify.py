#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Gauge rigidity of rank-8 E-graph-exact complex decoders on P112 (and P120).

Standard library only; exact integer / F2 / rational arithmetic throughout.

Model (PR717 B14, D1(a) scope).  The 120 E8 root lines r_i (norm 2); G_ij = <r_i, r_j>; a puncture
removes lines, P112 = 120 lines minus the coordinate frame FRAME0.  A costly-term decoder is a real
matrix K = sum_k x_k y_k^T on the live lines with K_ii = 4 and K_ij = 0 on orthogonal pairs (the
"E-graph"); odd pairs (G_ij = +-1) are free because single-entry terms there cost 0 (label-orthogonal).
This script supports the written proof (PROOF.md) that every such K of rank 8 equals D (2G) D^{-1} for a
diagonal D, by checking every finite fact the proof uses:

  A  model facts and the pivot frame F (a live frame chosen so that the punctured lines form two classes)
  B  the D4-block structure of the lines relative to F: 14 blocks forming the Steiner system S(3,4,8),
     28 classes (4-frames with Hadamard sign matrices), the orthogonality rule, the three matchings of
     every class, and W(E8)-transitivity on the 2025 frames of E8
  C  zero exclusion: the necessary conditions on the zero pattern of K[:,F] and K[F,:] form a CNF whose
     only model is the trivial pattern; the shipped DRUP refutations of "some zero" (for the full CNF and
     for the reduced CNF with only the two-term and diagonal families) are replayed by an independent RUP
     checker (no SAT solver needed)
  D  the within-class and gluing lemmas: the finite inputs they need (live witnesses, class-level
     orthogonality, a complete live class in every block) exist
  E  corollary mechanics in exact rational arithmetic: D (2G) D^{-1} solves the system; for a sampled dual
     basis the factorisation X = D R A, Y = D^{-1} R (2A^{-T}) reproduces K and has supports C(a_k), C(b_k);
     the sampled terms cost >= 8 each (9 in the sample); the coordinate decoder attains 64 / 72
  F  negative controls: relaxed CNFs accept the all-zero pattern, corrupted proofs are rejected, the proof
     needs the "some zero" clause, a zero-free non-Hadamard class matrix satisfies all equations of a lone
     D4 block (cross-block constraints are essential), the Lemma 6 / Section 7 assembly is recomputed
     exactly and fails for class-dependent column scalings, and a rank-9 solution is not of gauge form

Run from the repository root:   python3 -I -B research/complex-rank8-decoder-rigidity/verify.py
Options: --live P120 (replay on the unpunctured unit), --proof FILE (replay another DRUP refutation of the
full CNF; large proofs from other solvers replay slowly in pure Python), --dimacs FILE (dump the
zero-pattern CNF for an external solver), --out FILE (write the full certificate JSON).
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS: list[str] = []
LOG: list[str] = []

# Closed-form clause-family counts and the SHA-256 of the full zero-pattern CNF (with the "some zero"
# clause), per live set.  A change of the builder that alters the CNF is caught here, and the shipped
# proofs are replayed against the CNF built at run time in any case.
EXPECTED = {
    'P112': {'two': 4608, 'four': 312, 'diag': 104, 'trans': 52, 'frames_complete': 26, 'class_pairs': 576,
             'cnf_sha256_reduced': 'f4e38d4cee6fcadb9e371be36a1fa3b7909fd09295dbe1d2baa59640b524cf21',
             'cnf_sha256': 'c1082b339fcbbd3982760142cd0116af747a62a4373d8e3eddc23e33956253ca'},
    # extension units (section G): reduced CNF (two + diag) counts and digests, class profile, witnesses
    'EXT': {
        'generators': 204, 'line_orbits': 1, 'frame_orbits': [28, 336, 896],
        'units': {
            # families: the clause families of the shipped refutation ('two','diag' when those suffice; all four
            # for the type-(4,4) unit, where the two-term and diagonal conditions alone admit a zero pattern)
            'P111':          {'families': ['two', 'diag'], 'vars': 1236, 'clauses': 19387, 'sha256': 'b77a33efd19b8d75b1ee79effeb0426fbf0007891319d362251ab59f82aeee7e',
                              'complete': 25, 'incomplete': 1, 'blocks_with_class': 13, 'transfers': False},
            'P104-44':       {'families': ['two', 'four', 'diag', 'trans'], 'vars': 3456, 'clauses': 25872, 'sha256': 'd984852f74284eb704816b8b584e270947dbe6abef4c30181e4922903f73054c',
                              'complete': 24, 'incomplete': 0, 'blocks_with_class': 12, 'transfers': False},
            'P104-2222':     {'families': ['two', 'diag'], 'vars': 1152, 'clauses': 16864, 'sha256': '8b18530f0ff8980e2ac49c64ffb7b5d34c9ab745e3e20eba0943aa4ddb0c2c6f',
                              'complete': 24, 'incomplete': 0, 'blocks_with_class': 14, 'transfers': True},
            'P104-11111111': {'families': ['two', 'diag'], 'vars': 1152, 'clauses': 16992, 'sha256': '900d21c66ca2656a150b5dc9d5e904df232d56aeeed7926d444e5127b1687d03',
                              'complete': 22, 'incomplete': 4, 'blocks_with_class': 14, 'transfers': False},
        },
    },
    'P120': {'two': 5376, 'four': 336, 'diag': 112, 'trans': 56, 'frames_complete': 28, 'class_pairs': 672,
             'cnf_sha256_reduced': '86e27f4bb6ac6d3650509138558aa1e01130f2a4aa5f21889a6e2e98cfc51893',
             'cnf_sha256': 'f50dd6fa63077a0da68cd86ac2c02a5a771de97ecaa6738d68ac2919cc6af2ed'},
}


def check(tag: str, cond: bool, info: str = '') -> bool:
    line = ('PASS ' if cond else 'FAIL ') + tag + (' | ' + info if info else '')
    print(line, flush=True)
    LOG.append(line)
    if not cond:
        FAILS.append(tag)
    return bool(cond)


# =============================================================================== A. model
def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    return roots


def neg(v):
    return tuple(-a for a in v)


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


ROOTS = e8_roots()
LINES = []
_seen = set()
for _r in ROOTS:
    _key = _r if _r > neg(_r) else neg(_r)
    if _key not in _seen:
        _seen.add(_key)
        LINES.append(_r)
NL = len(LINES)
G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
N = [[(G[i][j] + 1) & 1 for j in range(NL)] for i in range(NL)]          # label pairing over F2
NMASK = [sum(N[i][j] << j for j in range(NL)) for i in range(NL)]

FRAME0 = []
for _a in range(4):
    for _s in (1, -1):
        _v = [0] * 8
        _v[2 * _a], _v[2 * _a + 1] = 2, 2 * _s
        FRAME0.append(LINES.index(tuple(_v)))
P112 = [i for i in range(NL) if i not in FRAME0]
P120 = list(range(NL))


def f2_rank(rows):
    basis = {}
    rank = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                rank += 1
                break
    return rank


def pairing_rank(R, A):
    R, A = list(R), list(A)
    if not R or not A:
        return 0
    amask = 0
    for j in A:
        amask |= 1 << j
    return f2_rank([NMASK[i] & amask for i in R])


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


def blocks_relative(frame, lines):
    """For each line not in `frame`: (T, signs) with T the pivot lines it is odd to, in frame order."""
    info = {}
    for i in lines:
        if i in frame:
            continue
        T = tuple(f for f in frame if G[i][f] != 0)
        signs = tuple(G[i][f] for f in T)
        info[i] = (T, signs)
    return info


def class_parity(signs):
    return sum(1 for s in signs if s == -1) % 2


def choose_pivot(live):
    """Pivot frame F.  For P112: the even class of one FRAME0-block and of its complementary block, so
    that the eight punctured lines are two whole classes relative to F.  For P120: FRAME0 itself."""
    if set(FRAME0) <= set(live):
        return list(FRAME0)
    rel0 = blocks_relative(FRAME0, range(NL))
    blocks = {}
    for i, (T, s) in rel0.items():
        blocks.setdefault(T, []).append(i)
    S0 = sorted(blocks)[0]
    S0c = tuple(f for f in FRAME0 if f not in S0)
    F = [i for i in blocks[S0] if class_parity(rel0[i][1]) == 0] + \
        [i for i in blocks[S0c] if class_parity(rel0[i][1]) == 0]
    return F


# =============================================================================== C. CNF + RUP
class CNF:
    """Deterministic variable numbering shared with make_proof.py (which imports this module)."""

    def __init__(self):
        self.ids = {}
        self.names = []
        self.clauses = []

    def var(self, key):
        v = self.ids.get(key)
        if v is None:
            v = len(self.names) + 1
            self.ids[key] = v
            self.names.append(key)
        return v

    def add(self, clause):
        self.clauses.append(tuple(clause))


ALL_FAMILIES = ('two', 'four', 'diag', 'trans')


def build_zero_cnf(live, F, rel, options=None):
    """Necessary conditions on the zero pattern of a_i = K[i,F] and b_i = K[F,i]^T (a variable is TRUE when the
    entry is zero).  Every clause family must be a necessary condition on real solutions of system (2):
      two   a_i.b_j = a_ik b_jk + a_ik' b_jk' = 0 for orthogonal i, j in blocks meeting in {k,k'}:
            the two products are both zero or both nonzero (both ordered equations);
      four  a_i.b_j = 0 for distinct orthogonal lines of one class: not exactly one nonzero product;
      diag  a_i.b_i = 16: some product nonzero;
      trans Lemma 3: A_C and B_C of a complete class are nonsingular, so their zero patterns admit a transversal.
    options: the families to include (default all)."""
    opts = set(ALL_FAMILIES) if options is None else set(options)
    cnf = CNF()
    nonframe = sorted(rel)
    za = lambda i, f: cnf.var(('a', i, f))
    zb = lambda i, f: cnf.var(('b', i, f))
    for i in nonframe:                      # fix the numbering of the pattern variables first
        for f in rel[i][0]:
            za(i, f)
    for i in nonframe:
        for f in rel[i][0]:
            zb(i, f)
    stats = {k: 0 for k in ALL_FAMILIES}
    for i in nonframe:
        Ti = set(rel[i][0])
        for j in nonframe:
            if j == i or G[i][j] != 0:
                continue
            ov = sorted(Ti & set(rel[j][0]))
            if len(ov) == 2 and 'two' in opts:
                k, kp = ov
                for (p, q), (r, s) in (((za(i, k), zb(j, k)), (za(i, kp), zb(j, kp))),
                                       ((za(i, kp), zb(j, kp)), (za(i, k), zb(j, k)))):
                    cnf.add([-p, r, s])
                    cnf.add([-q, r, s])
                stats['two'] += 1
            elif len(ov) == 4 and 'four' in opts:
                prods = []
                for k in ov:
                    pk = cnf.var(('p', i, j, k))          # pk <-> (a_ik != 0 and b_jk != 0)
                    cnf.add([-pk, -za(i, k)])
                    cnf.add([-pk, -zb(j, k)])
                    cnf.add([pk, za(i, k), zb(j, k)])
                    prods.append(pk)
                for pk in prods:
                    cnf.add([-pk] + [q for q in prods if q != pk])
                stats['four'] += 1
        if 'diag' in opts:
            ds = []
            for k in rel[i][0]:
                dk = cnf.var(('d', i, k))
                cnf.add([-dk, -za(i, k)])
                cnf.add([-dk, -zb(i, k)])
                cnf.add([dk, za(i, k), zb(i, k)])
                ds.append(dk)
            cnf.add(ds)
            stats['diag'] += 1
    classes = {}
    for i in nonframe:
        T, s = rel[i]
        classes.setdefault((T, class_parity(s)), []).append(i)
    if 'trans' in opts:
        for (T, par), lines in sorted(classes.items()):
            if len(lines) != 4:
                continue
            for which, zf in (('A', za), ('B', zb)):
                perms = []
                for perm in itertools.permutations(range(4)):
                    v = cnf.var(('perm', which, T, par, perm))
                    for p, i in enumerate(lines):
                        cnf.add([-v, -zf(i, T[perm[p]])])
                    perms.append(v)
                cnf.add(perms)
                stats['trans'] += 1
    zvars = [cnf.ids[('a', i, f)] for i in nonframe for f in rel[i][0]] + \
            [cnf.ids[('b', i, f)] for i in nonframe for f in rel[i][0]]
    return cnf, zvars, stats


def cnf_digest(clauses):
    return hashlib.sha256('\n'.join(' '.join(map(str, c)) for c in clauses).encode()).hexdigest()


def write_dimacs(path, clauses, nvars):
    with open(path, 'w') as fh:
        fh.write(f'p cnf {nvars} {len(clauses)}\n')
        for c in clauses:
            fh.write(' '.join(map(str, c)) + ' 0\n')


def rup_check(clauses, nvars, proof_lines, limit_lemmas=None):
    """Replay a DRUP refutation: every lemma must follow by unit propagation (RUP) from the original clauses
    plus the earlier lemmas; deletion steps are ignored (sound: the database only grows).  Returns
    (ok, lemmas_checked, reason).  Strict parser: comment lines are skipped, a lemma with a literal 0 or a
    variable above nvars is rejected, duplicate literals are merged."""
    db = [list(c) for c in clauses]
    occ = {}                                 # literal -> clause indices containing it
    units = []                               # top-level unit clauses (original or learned)

    def register(idx):
        for lit in db[idx]:
            occ.setdefault(lit, []).append(idx)
        if len(db[idx]) == 1:
            units.append(db[idx][0])
        if len(db[idx]) == 0:
            units.append(None)
    for idx in range(len(db)):
        register(idx)
    assign = [0] * (nvars + 1)               # 0 unassigned, +1 true, -1 false

    def value(lit):
        return assign[abs(lit)] * (1 if lit > 0 else -1)

    def propagate(seed_lits):
        """Assign the seed literals (negated lemma) and the unit clauses, then unit-propagate.
        Returns True on conflict."""
        trail = []
        queue = []
        for lit in list(seed_lits) + units:
            if lit is None:
                for l in trail:
                    assign[abs(l)] = 0
                return True
            v = value(lit)
            if v == -1:
                for l in trail:
                    assign[abs(l)] = 0
                return True
            if v == 0:
                assign[abs(lit)] = 1 if lit > 0 else -1
                trail.append(lit)
                queue.append(lit)
        conflict = False
        qi = 0
        while qi < len(queue) and not conflict:
            lit = queue[qi]
            qi += 1
            for idx in occ.get(-lit, ()):
                clause = db[idx]
                unassigned = None
                satisfied = False
                for l in clause:
                    v = value(l)
                    if v == 1:
                        satisfied = True
                        break
                    if v == 0:
                        if unassigned is None:
                            unassigned = l
                        else:
                            unassigned = 'many'
                            break
                if satisfied or unassigned == 'many':
                    continue
                if unassigned is None:
                    conflict = True
                    break
                assign[abs(unassigned)] = 1 if unassigned > 0 else -1
                trail.append(unassigned)
                queue.append(unassigned)
        for l in trail:
            assign[abs(l)] = 0
        return conflict

    checked = 0
    for raw in proof_lines:
        raw = raw.strip()
        if not raw or raw.startswith('d') or raw.startswith('c'):
            continue
        try:
            lits = [int(t) for t in raw.split()]
        except ValueError:
            return False, checked, f'unparsable proof line: {raw[:40]}'
        if not lits or lits[-1] != 0:
            return False, checked, f'proof line without terminating 0: {raw[:40]}'
        lits = list(dict.fromkeys(lits[:-1]))
        if any(l == 0 or abs(l) > nvars for l in lits):
            return False, checked, f'lemma {checked + 1} has an out-of-range literal'
        if not propagate([-l for l in lits]):
            return False, checked, f'lemma {checked + 1} is not RUP'
        checked += 1
        if limit_lemmas and checked >= limit_lemmas:
            break
        if not lits:
            return True, checked, 'empty clause derived'
        db.append(lits)
        register(len(db) - 1)
    return False, checked, 'proof ended without the empty clause'


# =============================================================================== E. exact rational helpers
def rank_Q(M):
    M = [[Q(x) for x in row] for row in M]
    rows, cols = len(M), len(M[0]) if M else 0
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def inv_Q(M):
    n = len(M)
    A = [[Q(x) for x in row] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        piv = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        f = A[c][c]
        A[c] = [a / f for a in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                g = A[i][c]
                A[i] = [a - g * b for a, b in zip(A[i], A[c])]
    return [row[n:] for row in A]


def matmul(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


def lcg(seed):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state


def rand_nonzero_Q(rng):
    return Q((next(rng) % 97) + 1, (next(rng) % 13) + 1) * (1 if next(rng) % 2 else -1)


# =============================================================================== G. helpers: stabiliser, frames, units
LINE_INDEX = {}
for _i, _v in enumerate(LINES):
    LINE_INDEX[_v] = _i
    LINE_INDEX[neg(_v)] = _i


def reflection_perm(a):
    """The permutation of the 120 lines induced by the reflection in root a."""
    al = LINES[a]
    return tuple(LINE_INDEX[tuple(x - ip(LINES[i], al) * y for x, y in zip(LINES[i], al))] for i in range(NL))


def frames_inside(live):
    """All frames (8 mutually orthogonal lines) contained in `live`, as sorted tuples."""
    live = set(live)
    orth = [set(j for j in live if j != i and G[i][j] == 0) for i in range(NL)]
    out = set()

    def extend(cl, cands):
        if len(cl) == 8:
            out.add(tuple(sorted(cl)))
            return
        for c in sorted(cands):
            if cl and c < cl[-1]:
                continue
            extend(cl + [c], cands & orth[c])
    extend([], set(live))
    return out


def stabiliser_generators(frame):
    """Line permutations given by single reflections and by products of two reflections that map the frame
    (as a set of lines) to itself.  They generate a subgroup of the stabiliser of the frame in W(E8)."""
    perms = [reflection_perm(a) for a in range(NL)]
    fs = set(frame)
    gens = set()
    for a in range(NL):
        if {perms[a][f] for f in frame} == fs:
            gens.add(perms[a])
        for b in range(a + 1, NL):
            prod = tuple(perms[a][perms[b][i]] for i in range(NL))
            if {prod[f] for f in frame} == fs:
                gens.add(prod)
    return sorted(gens)


def orbits(items, gens, act):
    """Orbits of `items` under the group generated by `gens` (acting through act(g, x)); returns (reps, rep_of)."""
    rep_of = {}
    reps = []
    for s in items:
        if s in rep_of:
            continue
        reps.append(s)
        orb = {s}
        frontier = [s]
        while frontier:
            nxt = []
            for x in frontier:
                for g in gens:
                    y = act(g, x)
                    if y not in orb:
                        orb.add(y)
                        nxt.append(y)
            frontier = nxt
        for x in orb:
            rep_of[x] = s
    return reps, rep_of


def frame_type(frame, rel0):
    """How a frame meets the classes relative to FRAME0: sorted class-hit counts."""
    cls = {}
    for i in frame:
        T, sg = rel0[i]
        key = (T, class_parity(sg))
        cls[key] = cls.get(key, 0) + 1
    return tuple(sorted(cls.values(), reverse=True))


def extension_units():
    """Representative live sets beyond P112 with a deterministic live pivot each:
    P111 (one line removed; all 112 choices are equivalent under the stabiliser) and one P104 unit per
    stabiliser orbit of the 1260 frames inside P112 (types (4,4), (2,2,2,2), (1,...,1)).  For a unit whose
    live classes can all be made complete, the pivot is chosen to do so (then the whole proof transfers)."""
    rel0 = blocks_relative(FRAME0, range(NL))
    gens = stabiliser_generators(FRAME0)
    frames = frames_inside(P112)
    line_reps, line_rep_of = orbits(sorted(P112), gens, lambda g, i: g[i])
    frame_reps, frame_rep_of = orbits(sorted(frames), gens, lambda g, f: tuple(sorted(g[i] for i in f)))
    units = {}
    def best_pivot(live):
        """The first live frame (in sorted order) minimising the number of incomplete live classes."""
        best = None
        for fr in sorted(frames_inside(live)):
            rel = blocks_relative(fr, live)
            sizes = {}
            for i in live:
                if i in fr:
                    continue
                T, sg = rel[i]
                key = (T, class_parity(sg))
                sizes[key] = sizes.get(key, 0) + 1
            incomplete = sum(1 for v in sizes.values() if v != 4)
            if best is None or incomplete < best[0]:
                best = (incomplete, fr)
            if incomplete == 0:
                break
        return best[1]
    live111 = [i for i in P112 if i != line_reps[0]]
    units['P111'] = (live111, best_pivot(live111), f'P112 minus line {line_reps[0]}')
    for rep in frame_reps:
        name = 'P104-' + ''.join(str(c) for c in frame_type(rep, rel0))
        live = [i for i in P112 if i not in rep]
        units[name] = (live, best_pivot(live), f'P112 minus the frame {rep} (type {frame_type(rep, rel0)})')
    return units, gens, line_reps, line_rep_of, frame_reps, frame_rep_of, frames, rel0


# =============================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--live', default='P112', choices=['P112', 'P120'])
    ap.add_argument('--proof', default=None, help='full-CNF DRUP proof (default proof-<live>.drup next to this script)')
    ap.add_argument('--dimacs', default=None, help='write the zero-pattern CNF in DIMACS form and continue')
    ap.add_argument('--out', default=None, help='write the full certificate JSON (file must not exist)')
    args = ap.parse_args()
    live = P112 if args.live == 'P112' else P120
    exp = EXPECTED[args.live]
    cert = {'live': args.live, 'base_commit': '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe'}

    # ---------------------------------------------------------------- A
    print('== A. model and pivot')
    check('A.lines', NL == 120 and len(set(LINES)) == 120, '120 root lines')
    offdiag = set(G[i][j] for i in range(NL) for j in range(NL) if i != j)
    check('A.gram-offdiag', offdiag == {-1, 0, 1}, f'off-diagonal Gram values {sorted(offdiag)}')
    check('A.label-rank', f2_rank(NMASK) == 9 and len(set(NMASK)) == NL, 'N = (G+1) mod 2 has F2 rank 9 and distinct rows')
    check('A.frame0', is_frame(FRAME0) and len(live) == NL - (8 if args.live == 'P112' else 0), f'live={len(live)}')
    F = choose_pivot(live)
    check('A.pivot-frame', is_frame(F) and all(f in live for f in F), f'F={F}')
    rel = blocks_relative(F, live)                 # live non-pivot lines
    rel_all = blocks_relative(F, range(NL))         # all 112 non-pivot lines (punctured ones included)
    nonframe = sorted(rel)
    check('A.pivot-odd-four', all(len(T) == 4 for T, _ in rel_all.values()),
          'every one of the 112 non-pivot lines is odd to exactly 4 pivot lines')
    check('A.pivot-signs', all(all(s in (1, -1) for s in signs) for _, signs in rel_all.values()), 'with inner products +-1')
    cert['pivot'] = F

    # ---------------------------------------------------------------- B
    print('== B. D4-block structure relative to the pivot')
    blocks_all = {}
    for i, (T, s) in rel_all.items():
        blocks_all.setdefault(T, []).append(i)
    B = sorted(blocks_all)
    check('B.blocks-14', len(B) == 14 and all(len(v) == 8 for v in blocks_all.values()), '14 blocks of 8 lines (112 lines)')
    pts = list(F)
    trip_ok = all(sum(1 for T in B if set(t) <= set(T)) == 1 for t in itertools.combinations(pts, 3))
    pair_ok = all(sum(1 for T in B if set(t) <= set(T)) == 3 for t in itertools.combinations(pts, 2))
    meet_ok = all(len(set(S) & set(T)) in (0, 2) for S in B for T in B if S != T)
    comp_ok = all(tuple(f for f in F if f not in S) in blocks_all for S in B)
    check('B.steiner', trip_ok and pair_ok and meet_ok and comp_ok,
          'S(3,4,8): every 3 points in one block, every 2 in three, blocks meet in 0 or 2, complement-closed')
    classes_all = {}
    for i, (T, s) in rel_all.items():
        classes_all.setdefault((T, class_parity(s)), []).append(i)
    check('B.classes-28', len(classes_all) == 28 and all(len(v) == 4 for v in classes_all.values()), '28 classes of 4 lines')
    frame4 = all(all(G[a][b] == 0 for a in L for b in L if a != b) for L in classes_all.values())
    check('B.class-4frames', frame4, 'each class is 4 mutually orthogonal lines')
    had = True
    for (T, par), L in classes_all.items():
        H = [rel_all[i][1] for i in L]
        had &= all(sum(x * y for x, y in zip(H[p], H[q])) == (4 if p == q else 0) for p in range(4) for q in range(4))
        had &= all(sum(H[p][c] * H[p][cc] for p in range(4)) == 0 for c in range(4) for cc in range(4) if c != cc)
    check('B.hadamard', had, 'class sign matrices are 4x4 Hadamard (orthogonal rows and columns)')
    # orthogonality rule between non-pivot lines, including the class criterion for overlap 4
    rule = True
    for i in rel_all:
        Ti, si = rel_all[i]
        for j in rel_all:
            if j == i:
                continue
            Tj, sj = rel_all[j]
            ov = [f for f in Ti if f in Tj]
            if len(ov) == 0:
                predicted = 0
            else:
                tot = sum(si[Ti.index(f)] * sj[Tj.index(f)] for f in ov)   # = 2 <r_i, r_j>
                predicted = tot // 2 if tot % 2 == 0 else None
            rule &= (predicted is not None and predicted == G[i][j]) and len(ov) in (0, 2, 4)
            if len(ov) == 4:
                same_class = class_parity(si) == class_parity(sj)
                rule &= (G[i][j] == 0) == same_class
    check('B.orthogonality-rule', rule,
          '<r_i,r_j> = (1/2) sum over shared pivot lines of sign products; overlaps 0/2/4; overlap-4 pairs are orthogonal iff same class')
    live_classes = {k: [i for i in v if i in live] for k, v in classes_all.items()}
    sizes = sorted(len(v) for v in live_classes.values())
    empty = [k for k, v in live_classes.items() if not v]
    if args.live == 'P112':
        comp_pair = len(empty) == 2 and set(empty[0][0]) == set(F) - set(empty[1][0])
        punct_lines = sorted(i for k in empty for i in classes_all[k])
        check('B.punctured-classes', sizes.count(4) == 26 and sizes.count(0) == 2 and comp_pair and punct_lines == sorted(FRAME0),
              'P112: 26 complete classes; the 2 empty classes are FRAME0 and lie in complementary blocks')
    else:
        check('B.punctured-classes', sizes.count(4) == 28, 'P120: all 28 classes complete')
    cert['class_sizes'] = sizes
    # groups and matchings: for a class and a column pair, the rows split 2+2 by the sign product; the pairing
    # of a column pair equals that of its complement; the three pairings are three distinct perfect matchings
    grp = True
    m3 = True
    for (T, par), L in live_classes.items():
        if len(L) != 4:
            continue
        pairing = {}
        for c, cc in itertools.combinations(range(4), 2):
            prods = [rel_all[i][1][c] * rel_all[i][1][cc] for i in L]
            grp &= prods.count(1) == 2 and prods.count(-1) == 2
            pairing[(c, cc)] = frozenset(frozenset(p for p in range(4) if prods[p] == s) for s in (1, -1))
        m3 &= pairing[(0, 1)] == pairing[(2, 3)] and pairing[(0, 2)] == pairing[(1, 3)] and pairing[(0, 3)] == pairing[(1, 2)]
        m3 &= len({pairing[(0, 1)], pairing[(0, 2)], pairing[(0, 3)]}) == 3
    ncomplete = sum(1 for L in live_classes.values() if len(L) == 4)
    check('B.groups', grp and ncomplete == exp['frames_complete'],
          f'in each of the {ncomplete} complete classes every column pair splits the rows into two groups of two')
    check('B.three-matchings', m3 and ncomplete == exp['frames_complete'],
          'complementary column pairs give the same pairing; the three pairings are distinct matchings of K4')
    # W(E8) acts transitively on frames: every frame is reachable from FRAME0 by root reflections.
    orth_adj = [set(j for j in range(NL) if j != i and G[i][j] == 0) for i in range(NL)]
    frames_all = set()

    def extend(clique, cands):
        if len(clique) == 8:
            frames_all.add(tuple(sorted(clique)))
            return
        for c in sorted(cands):
            if clique and c < clique[-1]:
                continue
            extend(clique + [c], cands & orth_adj[c])
    extend([], set(range(NL)))
    line_index = {}
    for i, v in enumerate(LINES):
        line_index[v] = i
        line_index[neg(v)] = i

    def reflect_line(i, a):
        r, al = LINES[i], LINES[a]
        c = ip(r, al)
        return line_index[tuple(x - c * y for x, y in zip(r, al))]
    seen = {tuple(sorted(FRAME0))}
    frontier = [tuple(sorted(FRAME0))]
    while frontier:
        nxt = []
        for fr in frontier:
            for a in range(NL):
                img = tuple(sorted(reflect_line(i, a) for i in fr))
                if img not in seen:
                    seen.add(img)
                    nxt.append(img)
        frontier = nxt
    check('B.frame-transitivity', len(frames_all) == 2025 and seen == frames_all,
          f'{len(frames_all)} frames in E8, all reachable from FRAME0 by reflections')
    cert['frames'] = len(frames_all)

    # ---------------------------------------------------------------- C
    print('== C. zero exclusion by RUP replay')
    cnf, zvars, stats = build_zero_cnf(live, F, rel)
    nvars = len(cnf.names)
    full_clauses = cnf.clauses + [tuple(zvars)]
    digest = cnf_digest(full_clauses)
    cert['cnf'] = {'vars': nvars, 'clauses': len(cnf.clauses), 'sha256': digest, **stats}
    counts_ok = all(stats[k] == exp[k] for k in ALL_FAMILIES) and len(zvars) == 2 * 4 * len(nonframe)
    check('C.cnf-size', counts_ok, f'{nvars} vars, {len(cnf.clauses)} clauses, families {stats}')
    check('C.cnf-digest', digest == exp['cnf_sha256'], f'sha256 {digest[:16]}...')
    if args.dimacs:
        write_dimacs(args.dimacs, full_clauses, nvars)
        print(f'   wrote DIMACS (with the "some zero" clause) to {args.dimacs}')
    assign = {v: False for v in range(1, nvars + 1)}
    for key, v in cnf.ids.items():
        if key[0] in ('p', 'd') or (key[0] == 'perm' and key[4] == (0, 1, 2, 3)):
            assign[v] = True
    sat_trivial = all(any((assign[abs(l)] if l > 0 else not assign[abs(l)]) for l in c) for c in cnf.clauses)
    check('C.trivial-pattern-satisfies', sat_trivial, 'the all-nonzero pattern satisfies every clause')
    proof_path = Path(args.proof) if args.proof else HERE / f'proof-{args.live}.drup'
    proof_lines = []
    if proof_path.exists():
        proof_lines = proof_path.read_text().splitlines()
        ok, nlem, reason = rup_check(full_clauses, nvars, proof_lines)
        check('C.rup-refutation', ok, f'{proof_path.name}: {nlem} lemmas replayed; {reason}')
        cert['proof'] = {'file': proof_path.name, 'sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest(), 'lemmas': nlem}
    else:
        check('C.rup-refutation', False, f'missing proof file {proof_path}')
    # reduced CNF: only the two-term and diagonal families (Lemma 4 does not need Lemma 3)
    cnf_r, zvars_r, stats_r = build_zero_cnf(live, F, rel, options={'two', 'diag'})
    red_digest = cnf_digest(cnf_r.clauses + [tuple(zvars_r)])
    check('C.cnf-size-reduced', stats_r == {'two': exp['two'], 'four': 0, 'diag': exp['diag'], 'trans': 0}
          and len(cnf_r.names) == 12 * len(nonframe) and red_digest == exp['cnf_sha256_reduced'],
          f'reduced CNF: {len(cnf_r.names)} vars, {len(cnf_r.clauses)} clauses, families {stats_r}, sha256 {red_digest[:16]}...')
    red_path = HERE / f'proof-{args.live}-two-diag.drup'
    if red_path.exists():
        ok_r, nlem_r, reason_r = rup_check(cnf_r.clauses + [tuple(zvars_r)], len(cnf_r.names), red_path.read_text().splitlines())
        check('C.rup-refutation-reduced', ok_r, f'{red_path.name}: two-term + diagonal families only; {nlem_r} lemmas; {reason_r}')
        cert['proof_reduced'] = {'file': red_path.name, 'sha256': hashlib.sha256(red_path.read_bytes()).hexdigest(), 'lemmas': nlem_r,
                                 'vars': len(cnf_r.names), 'clauses': len(cnf_r.clauses)}
    else:
        check('C.rup-refutation-reduced', False, f'missing proof file {red_path}')

    # ---------------------------------------------------------------- D
    print('== D. witnesses for the within-class and gluing lemmas')
    # D1: for every complete live class, column pair {k,k'} and group, a live line j in another block with
    #     T_j ∩ T = {k,k'} orthogonal to both rows of the group (its (k,k') projection of b_j is nonzero by C)
    d1 = True
    ntrip = 0
    for (T, par), L in live_classes.items():
        if len(L) != 4:
            continue
        for c, cc in itertools.combinations(range(4), 2):
            k, kp = T[c], T[cc]
            for sign in (1, -1):
                ntrip += 1
                rows = [i for i in L if rel_all[i][1][c] * rel_all[i][1][cc] == sign]
                d1 &= len(rows) == 2
                wit = [j for j in nonframe if set(rel[j][0]) & set(T) == {k, kp} and all(G[i][j] == 0 for i in rows)]
                d1 &= len(wit) >= 1
    check('D.class-witnesses', d1 and ntrip == 12 * exp['frames_complete'],
          f'each of the {ntrip} (complete class, column pair, group of two rows) triples has a live orthogonal witness in another block')
    # D2: class-level gluing witnesses: for ordered pairs of complete live classes C (block S), C' (block S')
    #     with |S ∩ S'| = 2 = {k,k'}, every j in C' is orthogonal to exactly the two rows i of C with
    #     eps_ik eps_ik' = -eps_jk eps_jk'
    d2 = True
    npairs = 0
    complete = {k: v for k, v in live_classes.items() if len(v) == 4}
    for (T, par), C in complete.items():
        for (Tp, parp), Cp in complete.items():
            ov = sorted(set(T) & set(Tp))
            if T == Tp or len(ov) != 2:
                continue
            npairs += 1
            k, kp = ov
            for j in Cp:
                sj = rel_all[j][1][Tp.index(k)] * rel_all[j][1][Tp.index(kp)]
                orth_rows = [i for i in C if G[i][j] == 0]
                rule_rows = [i for i in C if rel_all[i][1][T.index(k)] * rel_all[i][1][T.index(kp)] == -sj]
                d2 &= len(orth_rows) == 2 and orth_rows == rule_rows
    check('D.gluing-witnesses', d2 and npairs == exp['class_pairs'],
          f'{npairs} ordered pairs of complete classes in blocks meeting in two points: each line of one is orthogonal to exactly the two sign-rule rows of the other')
    # D3: every block has a complete live class; every live non-pivot line lies in one
    d3a = all(any(len(live_classes[(T, par)]) == 4 for par in (0, 1)) for T in B)
    d3b = all(len(live_classes[(rel[i][0], class_parity(rel[i][1]))]) == 4 for i in nonframe)
    check('D.block-live-class', d3a, 'each of the 14 blocks has a complete live class')
    check('D.complete-classes', d3b, 'every live non-pivot line lies in a complete live class')

    # ---------------------------------------------------------------- E
    print('== E. corollary mechanics (exact rational arithmetic)')
    rng = lcg(2024 if args.live == 'P112' else 2025)
    idx = {i: p for p, i in enumerate(live)}
    d = [rand_nonzero_Q(rng) for _ in live]
    K = [[2 * G[i][j] * d[idx[i]] / d[idx[j]] for j in live] for i in live]
    e1 = all(K[idx[i]][idx[i]] == 4 for i in live) and all(K[idx[i]][idx[j]] == 0 for i in live for j in live if i != j and G[i][j] == 0)
    check('E.gauge-solves', e1 and rank_Q(K) == 8, 'D (2G) D^{-1} has rank 8 and solves the E-graph system')
    while True:
        A = [[Q((next(rng) % 7) - 3) for _ in range(8)] for _ in range(8)]
        if rank_Q(A) == 8:
            break
    Bm = [[2 * x for x in row] for row in zip(*inv_Q(A))]           # B = 2 A^{-T}
    R = [[Q(x, 2) for x in LINES[i]] for i in live]                    # true coordinates (norm^2 = 2)
    RA = matmul(R, A)
    RB = matmul(R, Bm)
    X = [[d[p] * x for x in RA[p]] for p in range(len(live))]
    Y = [[RB[p][c] / d[p] for c in range(8)] for p in range(len(live))]
    XY = matmul(X, [list(col) for col in zip(*Y)])
    check('E.factorisation', XY == K, 'X = D R A, Y = D^{-1} R (2A^{-T}) reproduces K exactly (sampled dual basis)')
    supports_ok = True
    costs = []
    for k in range(8):
        a_k = [A[r][k] for r in range(8)]
        b_k = [Bm[r][k] for r in range(8)]
        Rk = [i for p, i in enumerate(live) if X[p][k] != 0]
        Ak = [i for p, i in enumerate(live) if Y[p][k] != 0]
        Ca = [i for i in live if sum(Q(LINES[i][c], 2) * a_k[c] for c in range(8)) != 0]
        Cb = [i for i in live if sum(Q(LINES[i][c], 2) * b_k[c] for c in range(8)) != 0]
        supports_ok &= (Rk == Ca and Ak == Cb)
        costs.append(pairing_rank(Rk, Ak))
    check('E.normal-form-supports', supports_ok, 'sampled term supports are C(a_k), C(b_k) (PR968 normal form)')
    # dimension of the span of the roots orthogonal to each sampled normal: a hyperplane-flat normal has 7,
    # a generic normal fewer (a normal orthogonal to no root has support L)
    def orth_span_dim(vec):
        rows = [[Q(x, 2) for x in LINES[i]] for i in range(NL) if sum(Q(LINES[i][c], 2) * vec[c] for c in range(8)) == 0]
        return rank_Q(rows) if rows else 0
    dims_a = [orth_span_dim([A[r][k] for r in range(8)]) for k in range(8)]
    dims_b = [orth_span_dim([Bm[r][k] for r in range(8)]) for k in range(8)]
    check('E.sample-normals', all(min(da, db) < 7 for da, db in zip(dims_a, dims_b)),
          f'orthogonal-root span dimensions of the sampled normals: a {dims_a}, b {dims_b} (hyperplane-flat normals have 7)')
    floor = 64 if args.live == 'P112' else 72
    check('E.sample-cost', all(c >= 8 for c in costs) and sum(costs) >= floor, f'sampled 8-term costs {costs}, cst {sum(costs)} >= {floor}')
    coord_cost = sum(pairing_rank([i for i in live if G[i][f] != 0], [i for i in live if G[i][f] != 0]) for f in FRAME0)
    check('E.coordinate-decoder', coord_cost == floor, f'coordinate decoder cst = {coord_cost} (attains the floor)')
    cert['sample_costs'] = costs

    # ---------------------------------------------------------------- F
    print('== F. negative controls')
    # F1: the equivalence families alone are satisfied by the all-zero pattern
    cnf2, zv2, _ = build_zero_cnf(live, F, rel, options={'two', 'four'})
    allzero = {v: (cnf2.names[v - 1][0] in ('a', 'b')) for v in range(1, len(cnf2.names) + 1)}
    f1 = all(any((allzero[abs(l)] if l > 0 else not allzero[abs(l)]) for l in c) for c in cnf2.clauses)
    check('F.relaxed-cnf-accepts-all-zero', f1, 'two-term + four-term clauses alone are satisfied by the all-zero pattern')
    if proof_lines:
        lemma_idx = [i for i, l in enumerate(proof_lines) if l.strip() and not l.startswith(('d', 'c'))]
        # F2a: insert, as the first lemma, the unit clause "entry zvars[0] is nonzero".  Its RUP test assigns that
        #      entry zero and propagates over the original clauses only; since unit propagation refutes no single
        #      zero, this lemma is never RUP and the checker must stop at lemma 1 (solver-independent control).
        bad = [' '.join(map(str, [-zvars[0], 0]))] + proof_lines
        ok2, n2, reason2 = rup_check(full_clauses, nvars, bad, limit_lemmas=5)
        # F2b: a proof truncated before its final empty clause must be rejected
        last = lemma_idx[-1]
        ok3, n3, reason3 = rup_check(full_clauses, nvars, proof_lines[:last])
        check('F.corrupted-proof-rejected', not ok2 and n2 == 0 and not ok3 and n3 == len(lemma_idx) - 1,
              f'inserted non-RUP unit lemma: {reason2}; truncated proof: {reason3}')
        # F3: without the "some zero" clause the proof cannot close (the trivial pattern is a model)
        ok4, n4, reason4 = rup_check(cnf.clauses, nvars, proof_lines)
        check('F.proof-needs-some-zero', not ok4, f'without the "some zero" clause: {reason4}')
    else:
        check('F.corrupted-proof-rejected', False, 'no proof file to corrupt')
        check('F.proof-needs-some-zero', False, 'no proof file')
    # F4: a lone D4 block is not rigid: a zero-free, nonsingular class matrix that is not a row/column scaling
    #     of the class Hadamard matrix (so Lemma 4 does not exclude it) satisfies every equation inside its block
    (T0, par0), E0 = next((k, v) for k, v in sorted(live_classes.items()) if len(v) == 4)
    AE = [[Q(1), Q(1), Q(1), Q(1)], [Q(1), Q(2), Q(3), Q(4)], [Q(1), Q(3), Q(6), Q(10)], [Q(1), Q(4), Q(10), Q(20)]]  # Pascal
    assert rank_Q(AE) == 4 and all(x != 0 for row in AE for x in row)
    BE = [[16 * x for x in row] for row in zip(*inv_Q(AE))]
    blockK = matmul(AE, [list(c) for c in zip(*BE)])
    within = all(blockK[p][q] == (16 if p == q else 0) for p in range(4) for q in range(4))
    H = [rel_all[i][1] for i in E0]
    cross_ratio_match = all(
        AE[p][c] * AE[q][cc] * H[p][cc] * H[q][c] == AE[p][cc] * AE[q][c] * H[p][c] * H[q][cc]
        for p in range(4) for q in range(4) for c in range(4) for cc in range(4))
    check('F.single-block-not-rigid', within and not cross_ratio_match,
          'a zero-free non-Hadamard class matrix (Pascal) with B = 16 A^{-T} satisfies all equations of its own block (exactly (E4) and (E0); B.orthogonality-rule shows a block has no others)')
    c, cc = 0, 1
    rows = [p for p in range(4) if H[p][c] * H[p][cc] == 1]
    assert len(rows) == 2
    minor = AE[rows[0]][c] * AE[rows[1]][cc] - AE[rows[0]][cc] * AE[rows[1]][c]
    check('F.minor-obstruction', minor != 0, 'the group minor that a live witness forces to vanish (Lemma 5, eq. (4)) is nonzero for it')
    # F5: Lemma 6 / Section 7 assembly recomputed exactly.  Build a_if = delta_i eps_if gamma^C_f and
    #     b_if = 4 eps_if / (delta_i gamma^C_f) (the Lemma 5 form) and evaluate every equation of system (2).
    #     (i) class-dependent gamma^C: (E0),(E4) hold, some (E2) fail; (ii) gamma^C = c_C g|_T: all hold and
    #     (1/4) K[:,F] K[F,:] = D (2G) D^{-1} with d_i = delta_i c_C / 2, d_f = 1 / g_f.
    rng2 = lcg(777)
    delta = {i: rand_nonzero_Q(rng2) for i in nonframe}
    gvec = {f: rand_nonzero_Q(rng2) for f in F}
    cC = {key: rand_nonzero_Q(rng2) for key in complete}
    gamma_dep = {key: {f: rand_nonzero_Q(rng2) for f in key[0]} for key in complete}
    gamma_glue = {key: {f: cC[key] * gvec[f] for f in key[0]} for key in complete}

    def assemble(gamma):
        a = {}
        b = {}
        for i in nonframe:
            T, s = rel[i]
            key = (T, class_parity(s))
            a[i] = {f: delta[i] * s[T.index(f)] * gamma[key][f] for f in T}
            b[i] = {f: 4 * s[T.index(f)] / (delta[i] * gamma[key][f]) for f in T}
        e0 = all(sum(a[i][f] * b[i][f] for f in rel[i][0]) == 16 for i in nonframe)
        e4 = True
        e2_fail = 0
        e2_total = 0
        for i in nonframe:
            Ti = set(rel[i][0])
            for j in nonframe:
                if j == i or G[i][j] != 0:
                    continue
                ov = Ti & set(rel[j][0])
                val = sum(a[i][f] * b[j][f] for f in ov)
                if len(ov) == 4:
                    e4 &= val == 0
                elif len(ov) == 2:
                    e2_total += 1
                    e2_fail += val != 0
        return a, b, e0, e4, e2_fail, e2_total
    _, _, e0d, e4d, fail_dep, tot_dep = assemble(gamma_dep)
    check('F.assembly-needs-gluing', e0d and e4d and fail_dep > 0,
          f'class-dependent column scalings: (E0),(E4) hold but {fail_dep}/{tot_dep} two-term equations fail')
    a_g, b_g, e0g, e4g, fail_g, tot_g = assemble(gamma_glue)
    KF = {i: {f: (a_g[i].get(f, Q(0)) if i in a_g else Q(0)) for f in F} for i in live}   # K[:,F]
    FK = {j: {f: (b_g[j].get(f, Q(0)) if j in b_g else Q(0)) for f in F} for j in live}   # K[F,:]^T
    for f in F:
        KF[f] = {g: Q(4 if g == f else 0) for g in F}
        FK[f] = {g: Q(4 if g == f else 0) for g in F}
    dd = {}
    for i in nonframe:
        T, s = rel[i]
        dd[i] = delta[i] * cC[(T, class_parity(s))] / 2
    for f in F:
        dd[f] = 1 / gvec[f]
    assembled_ok = e0g and e4g and fail_g == 0
    for i in live:
        for j in live:
            val = sum(KF[i][f] * FK[j][f] for f in F) / 4
            if val != 2 * G[i][j] * dd[i] / dd[j]:
                assembled_ok = False
                break
        if not assembled_ok:
            break
    check('F.assembly-control', assembled_ok and tot_g == exp['two'],
          f'glued scalings: all {tot_g} two-term equations hold and (1/4) K[:,F] K[F,:] = D (2G) D^(-1) with the Section 7 d_i, d_f')
    # F6: the rank hypothesis is essential: 2G + e_i e_j^T on an odd pair solves (E), has rank 9, not gauge form
    i0 = live[0]
    j0 = next(j for j in live if abs(G[i0][j]) == 1)
    K9 = [[Q(2 * G[i][j]) + (1 if (i, j) == (i0, j0) else 0) for j in live] for i in live]
    e9 = all(K9[idx[i]][idx[i]] == 4 for i in live) and all(K9[idx[i]][idx[j]] == 0 for i in live for j in live if i != j and G[i][j] == 0)
    gauge9 = K9[idx[i0]][idx[j0]] * K9[idx[j0]][idx[i0]] == 4 * G[i0][j0] * G[j0][i0]
    check('F.rank9-not-gauge', e9 and rank_Q(K9) == 9 and not gauge9,
          '2G + e_i e_j^T (odd pair) solves the E-graph system with rank 9 and is not D(2G)D^(-1)')

    # ---------------------------------------------------------------- G
    if args.live == 'P112':
        print('== G. beyond one frame: stabiliser orbits, witnesses and zero exclusion on P111 and the P104 units')
        ext = EXPECTED['EXT']
        units, gens, line_reps, line_rep_of, frame_reps, frame_rep_of, frames112, rel0 = extension_units()
        check('G.stabiliser-generators', len(gens) == ext['generators'],
              f'{len(gens)} line permutations from single/double reflections fixing FRAME0 as a set')
        check('G.line-orbits', len(line_reps) == ext['line_orbits'] and len(line_rep_of) == 112,
              'the 112 lines of P112 form one orbit: all P111 units are equivalent')
        fsizes = sorted(sum(1 for v in frame_rep_of.values() if v == r) for r in frame_reps)
        ftypes = {frame_type(r, rel0) for r in frame_reps}
        check('G.frame-orbits', len(frames112) == 1260 and fsizes == ext['frame_orbits'] and
              ftypes == {(4, 4), (2, 2, 2, 2), (1, 1, 1, 1, 1, 1, 1, 1)} and len(ftypes) == 3,
              f'1260 frames in P112 fall into orbits of sizes {fsizes}, one per class-hit type')
        p104_pr717 = tuple(sorted(P112[q] for q in (9, 15, 24, 46, 52, 66, 94, 104)))
        check('G.pr717-p104-orbit', frame_rep_of.get(p104_pr717) is not None and
              frame_type(p104_pr717, rel0) == (1, 1, 1, 1, 1, 1, 1, 1), 'PR717/PR968 P104 clique lies in the 896-orbit (admissible type)')
        cert['extension'] = {}
        for name, (ulive, upivot, desc) in units.items():
            upivot = list(upivot)
            exp_u = ext['units'][name]
            urel = blocks_relative(upivot, ulive)
            unon = sorted(urel)
            ucls = {}
            for i in unon:
                T, sg = urel[i]
                ucls.setdefault((T, class_parity(sg)), []).append(i)
            sizes_u = sorted(len(v) for v in ucls.values())
            ncomp = sizes_u.count(4)
            ninc = sum(1 for v in sizes_u if v != 4)
            # witnesses for the complete classes (Lemma 5 Step 1) and for gluing between complete classes
            w1 = True
            for (T, par), L in ucls.items():
                if len(L) != 4:
                    continue
                for c, cc in itertools.combinations(range(4), 2):
                    for sign in (1, -1):
                        rows = [i for i in L if urel[i][1][c] * urel[i][1][cc] == sign]
                        wit = [j for j in unon if set(urel[j][0]) & set(T) == {T[c], T[cc]} and all(G[i][j] == 0 for i in rows)]
                        w1 &= len(rows) == 2 and len(wit) >= 1
            # blocks (relative to this pivot) that have a complete live class: Lemma 6 needs all 14
            all_blocks = sorted({T for T, _ in blocks_relative(upivot, range(NL)).values()})
            nblk = sum(1 for T in all_blocks if any(len(ucls.get((T, par), [])) == 4 for par in (0, 1)))
            fams = set(exp_u['families'])
            ucnf, uz, ust = build_zero_cnf(ulive, upivot, urel, options=fams)
            udig = cnf_digest(ucnf.clauses + [tuple(uz)])
            pins_ok = (len(ucnf.names) == exp_u['vars'] and len(ucnf.clauses) == exp_u['clauses'] and udig == exp_u['sha256']
                       and ncomp == exp_u['complete'] and ninc == exp_u['incomplete'] and nblk == exp_u['blocks_with_class'])
            check(f'G.{name}.unit', pins_ok and is_frame(upivot) and all(f in ulive for f in upivot) and len(all_blocks) == 14,
                  f'{desc}; live {len(ulive)}; pivot {upivot}; classes: {ncomp} complete, {ninc} incomplete (sizes {sorted(set(sizes_u))}); '
                  f'blocks with a complete live class {nblk}/14; CNF families {sorted(fams)}: {len(ucnf.names)} vars / {len(ucnf.clauses)} clauses, sha256 {udig[:12]}')
            check(f'G.{name}.class-witnesses', w1, 'every complete live class has its live group witnesses in other blocks')
            upath = HERE / f'proof-{name}.drup'
            oku = False
            if upath.exists():
                oku, nlu, reasu = rup_check(ucnf.clauses + [tuple(uz)], len(ucnf.names), upath.read_text().splitlines())
                check(f'G.{name}.zero-exclusion', oku, f'{upath.name}: {nlu} lemmas; {reasu}')
                cert['extension'][name] = {'pivot': upivot, 'classes': sizes_u, 'families': sorted(fams), 'lemmas': nlu, 'cnf_sha256': udig,
                                           'proof_sha256': hashlib.sha256(upath.read_bytes()).hexdigest(), 'blocks_with_class': nblk}
            else:
                check(f'G.{name}.zero-exclusion', False, f'missing proof file {upath}')
            # the written proof transfers verbatim iff every live class is complete, zero exclusion holds, the
            # class witnesses exist and every block has a complete live class
            transfers = (ninc == 0 and oku and w1 and nblk == 14)
            reasons = [] if transfers else ([f'{ninc} incomplete classes'] if ninc else []) + ([] if oku else ['zero exclusion not replayed']) + \
                      ([] if w1 else ['missing class witnesses']) + ([] if nblk == 14 else [f'only {nblk}/14 blocks have a complete live class'])
            check(f'G.{name}.theorem-transfers', transfers == exp_u['transfers'],
                  ('Theorem 1 holds on this unit: all finite inputs of the proof verified' if transfers else 'not established: ' + ', '.join(reasons)))

    # ---------------------------------------------------------------- summary
    summary = (f'PASS_COMPLEX_RANK8_DECODER_RIGIDITY: live {args.live}; pivot {F}; blocks 14; classes {sizes.count(4)} complete; '
               f'frames 2025; zero-pattern CNF {nvars} vars / {len(cnf.clauses)} clauses; proof lemmas '
               f'{cert.get("proof", {}).get("lemmas", 0)} (+{cert.get("proof_reduced", {}).get("lemmas", 0)} reduced); coordinate cst {coord_cost}')
    if FAILS:
        print('FAILED CHECKS:', FAILS)
        print('FAIL_COMPLEX_RANK8_DECODER_RIGIDITY')
    else:
        print(summary)
    cert['log'] = LOG
    cert['fails'] = FAILS
    if args.out:
        outp = Path(args.out)
        if outp.exists():
            print(f'refusing to overwrite {outp}')
            return 2
        outp.write_text(json.dumps(cert, indent=1, default=str))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
