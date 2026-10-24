#!/usr/bin/env python3
"""Part 2: no further owned cold-helper relation pays on the complex #4610 backward word after #5383's eight.

Standard library only; a few seconds.  Reads Cao Yifan's #4610 word
(research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz) and the eight owned relations of PR #5383 / #5387
(research/eight-owned-relations/RELATIONS.json), both pinned by SHA256 in SOURCES.json.  This is the local word of
the #5383 -> #5392 -> #5398 chain; the selected #5413 caller adds 144 paid and 144 target rank-8 jobs that cancel
rank by rank, so its relation question is this one.

Model (the #5377/#5383 owned-relation model, extended from single relations to subspaces):
  * replay the backward program exactly over Q with warp words (free group ring); cold helpers (start frame 0,
    final frame 1, 326 of them, rank-9 targets) are free inputs and a relation subspace V lies in their span;
  * a paid climb is free iff its row is a pure cold-helper combination lying in V; a centre job (rank 8) is free
    iff row(centre) - row(Z) lies in V for some earlier snapshot Z of a field standing in its destination frame;
  * each dimension of V costs one rank-9 target; per local call the raw moment changes by
    sum_{removed} r^t - 9^t dim V.
Checks:
  1. pinned inputs; the backward paid profile {1:2201,2:412,3:510,4:127,5:40,8:8};
  2. the eight #5383 relations V0 make all eight centres and exactly eight rank-1 zero-site climbs free;
  3. modulo V0 every remaining pure-cold climb row (155 rows, rank mass <= 3 each) is linearly independent over Q,
     and no centre remains; hence any further subspace V removes at most 3 dim V of paid mass and the moment
     change is <= (3 - 9^t) dim V < 0;
  4. the stored RESULT-COMPLEX.json equals the rebuild.
Usage: python3 -I -B complex.py [--write]
"""
import argparse, collections, gzip, hashlib, json
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / 'research' / 'kappa-round3-warp-20261022' / 'ACTUAL-WORD.json.gz'
RELATIONS = ROOT / 'research' / 'eight-owned-relations' / 'RELATIONS.json'
BACKWARD_PAID = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
C_SELECTED = D('0.003027288235')
NL = 632
getcontext().prec = 50


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def add_into(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv:
            dst[k] = nv
        else:
            dst.pop(k, None)


def candidates(word):
    """Pure cold-helper climb rows (A) and centre-minus-snapshot rows (B), as {cold index: Fraction}."""
    c = word['canonical']; fr = c['frames']; prog = word['programs']['backward']
    cold = {i for i in range(224, NL) if c['start'][i] == 0 and c['final'][i] == 1}
    require(len(cold) == 326 and all(len(fr[c['final'][i]]) - len(fr[c['start'][i]]) == 9 for i in cold),
            '326 cold helpers with rank-9 targets')
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(NL)}; rows[('C', 0)] = {(('C', 0), ()): Q(1)}
    frames = {('L', i): c['start'][i] for i in range(NL)}; frames[('C', 0)] = None
    centre_frames = {e[3] for e in prog if e[0] == 'center'}
    snapshots = collections.defaultdict(list)
    paid = collections.Counter(); A, B = [], []

    def pure(row):
        return bool(row) and all(wd == () and r[0] == 'L' and r[1] in cold for (r, wd) in row)

    def vec(row):
        return {r[1]: q for (r, wd), q in row.items()}

    def snap(role):
        if frames[role] in centre_frames and rows[role]:
            snapshots[frames[role]].append(dict(rows[role]))
    for t, e in enumerate(prog):
        k = e[0]
        if k == 'climb':
            X = ('L', e[2]); paid[e[5]] += 1
            if pure(rows[X]):
                A.append((t, e[5], vec(rows[X])))
            frames[X] = e[4]; snap(X)
        elif k == 'center':
            X = ('C', e[1]); paid[e[4]] += 1
            for rz in snapshots[e[3]]:
                d = dict(rows[X]); add_into(d, rz, Q(-1))
                require(bool(d), 'no centre equals an earlier snapshot exactly')
                if pure(d):
                    B.append((t, e[4], vec(d)))
            frames[X] = e[3]
        elif k == 'warp':
            X = tuple(e[1]); op = e[2]
            sym = (1 if op > 0 else -1) * (abs(op) + 10 ** 6)
            rows[X] = {(r_, wd[1:] if wd and wd[0] == -sym else (sym,) + wd): q for (r_, wd), q in rows[X].items()}
            frames[X] = e[4]; snap(X)
        elif k == 'scalar':
            g, frame = e[1], e[2]; d_ = tuple(g[1])
            if g[0] == 'clear':
                rows[d_] = {}; frames[d_] = frame
            elif g[0] == 'copy':
                rows[d_] = dict(rows[tuple(g[2])])
            elif g[0] == 'add':
                add_into(rows[d_], rows[tuple(g[2])], Q(g[3], g[4]))
            elif g[0] == 'scale':
                rows[d_] = {kk: Q(g[2], g[3]) * v for kk, v in rows[d_].items()}
            snap(d_)
    require(dict(paid) == BACKWARD_PAID, 'backward paid profile of the #4610 word')
    return A, B


class Echelon:
    """Exact rational row echelon on sparse rows {column: Fraction}."""

    def __init__(self):
        self.rows = {}

    def reduce(self, v):
        v = dict(v)
        while v:
            col = min(v)
            if col not in self.rows:
                return v
            f = v[col]
            add_into(v, self.rows[col], -f)
        return v

    def add(self, v):
        v = self.reduce(v)
        if not v:
            return False
        col = min(v); f = v[col]
        self.rows[col] = {k: x / f for k, x in v.items()}
        return True


def build():
    pinned_inputs()
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    A, B = candidates(word)
    rel = json.loads(RELATIONS.read_text(encoding='utf-8'))
    V0 = Echelon()
    for row in rel['rows']:
        require(V0.add({int(k): Q(s) for k, s in row.items()}), 'eight independent #5383 relations')
    require(len(V0.rows) == 8, 'V0 has dimension eight')
    centres = sorted({t for t, _, v in B if not V0.reduce(v)})
    require(len(centres) == 8 and len({t for t, _, _ in B}) == 8, 'V0 frees all eight centre jobs')
    zero_sites = sorted((t, r) for t, r, v in A if not V0.reduce(v))
    require(len(zero_sites) == 8 and all(r == 1 for _, r in zero_sites), 'V0 frees exactly eight rank-1 zero-site climbs')
    rest = [(t, r, V0.reduce(v)) for t, r, v in A if V0.reduce(v)]
    E = Echelon()
    independent = all(E.add(v) for _, _, v in rest)
    require(independent, 'remaining pure-cold climb rows are linearly independent modulo V0')
    max_rank = max(r for _, r, _ in rest)
    require(max_rank == 3, 'remaining rows have rank mass at most 3')
    t_ = 1 - C_SELECTED
    nine_t = (t_ * D(9).ln()).exp()
    require(D(max_rank) < nine_t, 'density 3 is below 9^t')
    return dict(cold_helpers=326, backward_paid=dict(sorted(BACKWARD_PAID.items())),
                pure_cold_climbs=len(A), centre_snapshot_options=len(B),
                V0_frees=dict(centres=centres, zero_site_climbs=[t for t, _ in zero_sites]),
                remaining_rows=len(rest), remaining_rank=len(E.rows), remaining_profile=dict(sorted(collections.Counter(r for _, r, _ in rest).items())),
                bound='every further relation subspace V frees paid mass <= 3 dim V',
                moment=dict(C=str(C_SELECTED), nine_to_t=str(nine_t.quantize(D('1e-12'))),
                            loss_per_dimension_at_least=str((nine_t - 3).quantize(D('1e-12')))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT-COMPLEX.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT-COMPLEX.json equals the rebuild')
    print('PASS_COMPLEX_RELATION_SUBSPACES_NO_FURTHER_GAIN_AFTER_5383')


if __name__ == '__main__':
    main()
