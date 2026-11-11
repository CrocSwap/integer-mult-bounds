#!/usr/bin/env python3
"""One-sided COPY recount at the 27-deletion first-failure boundary of PR1609.

Standard library only; exact Fraction arithmetic. Any failed check exits nonzero.
The E8 geometry is rebuilt here (doubled coordinates, norm 8); no predecessor
code is imported. PR1609's CERTIFICATE.json is a live input whose witness fields
are compared with the reconstruction.

Model (PR1609 and its copy diagnostic, restated): live lines L, a decoder
target 2G, with D = R A root-linear and T arbitrary, exact on the mask (orthogonal or
equal pairs, i.e. even root inner product). Term k has top support
S_k = {i in L : D[i,k] != 0} and bottom support T_k = {j in L : T[j,k] != 0};
The checker uses doubled roots q and puts a factor 1/2 in the bottom factor.
Its price is the F2 rank of the pairing matrix N[S_k, T_k] with N[i,j] = 1 iff
the root inner product of lines i and j is even.
"""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as Fr
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = HERE.parent / "masked-e8-puncture-threshold" / "CERTIFICATE.json"

# The PR1609 witness: doubled target root and the vector annihilating its neighbourhood.
TARGET = (2, 2, 0, 0, 0, 0, 0, 0)
NORMAL = (1, -1, 2, 0, 0, 0, 0, 0)
# One-sided frame: first bottom is a TARGET + b NORMAL, the other seven are e_1..e_7.
FRAME_AB = (13, 7)
# Eight root tops (doubled coordinates) of an all-pairs design on the same live lines.
COMPARATOR_TOPS = [
    (0, 0, 2, 0, 0, 0, 0, 2), (0, 0, 2, 0, 0, 0, -2, 0),
    (1, -1, 1, -1, -1, -1, -1, -1), (1, -1, 1, -1, 1, -1, -1, 1),
    (1, -1, 1, 1, 1, 1, -1, 1), (1, -1, 1, -1, 1, 1, -1, -1),
    (1, -1, 1, -1, -1, 1, -1, 1), (1, 1, 1, 1, -1, 1, -1, 1),
]
SAME_FRAME_COPY = 72
ONE_SIDED_COPY = 71
COMPARATOR_COPY = 63


def need(ok, message):
    """Fail the whole run with a readable message."""
    if not ok:
        raise SystemExit("FAIL: " + message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def build_lines():
    """The 120 E8 root lines in doubled coordinates, first nonzero entry positive."""
    roots = []
    for i, j in combinations(range(8), 2):
        for si, sj in product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            roots.append(tuple(v))
    for s in product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(s)
    lines = sorted(r for r in roots if next(x for x in r if x) > 0)
    need(len(roots) == 240 and len(lines) == 120, "E8 root and line counts")
    need(all(dot(r, r) == 8 for r in lines), "root norms")
    return lines


LINES = build_lines()
NL = len(LINES)
IP = [[dot(a, b) // 4 for b in LINES] for a in LINES]
need(all(dot(a, b) % 4 == 0 for a in LINES for b in LINES), "Gram entries divisible by 4")
NR = [sum(1 << j for j in range(NL) if IP[i][j] % 2 == 0) for i in range(NL)]
INDEX = {r: i for i, r in enumerate(LINES)}


def rank2(rows):
    """F2 rank of integer bitmask rows."""
    basis = {}
    for v in rows:
        for _ in range(NL):
            if not v:
                break
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
        else:
            need(v == 0, "F2 elimination exceeded the 120-bit bound")
    return len(basis)


def rank_f2_dense(matrix):
    """Independent F2 rank on explicit 0/1 lists (cross-check of rank2)."""
    m = [row[:] for row in matrix]
    rank = 0
    for c in range(len(m[0]) if m else 0):
        pivot = next((r for r in range(rank, len(m)) if m[r][c]), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for r in range(len(m)):
            if r != rank and m[r][c]:
                m[r] = [x ^ y for x, y in zip(m[r], m[rank])]
        rank += 1
    return rank


def rational_rank(vectors):
    m = [[Fr(x) for x in v] for v in vectors]
    rank = 0
    for c in range(8):
        p = next((r for r in range(rank, len(m)) if m[r][c] != 0), None)
        if p is None:
            continue
        m[rank], m[p] = m[p], m[rank]
        for r in range(len(m)):
            if r != rank and m[r][c] != 0:
                f = m[r][c] / m[rank][c]
                m[r] = [a - f * b for a, b in zip(m[r], m[rank])]
        rank += 1
    return rank


def invert(rows):
    """Inverse of an 8x8 rational matrix given as rows."""
    a = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(8)] for i, row in enumerate(rows)]
    for c in range(8):
        p = next((r for r in range(c, 8) if a[r][c] != 0), None)
        need(p is not None, "singular frame")
        a[c], a[p] = a[p], a[c]
        pv = a[c][c]
        a[c] = [x / pv for x in a[c]]
        for r in range(8):
            if r != c and a[r][c] != 0:
                f = a[r][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return [row[8:] for row in a]


def dual_basis(vectors):
    """Vectors u_k with dot(v_l, u_k) = delta_lk (columns of the inverse)."""
    inv = invert(vectors)
    return [tuple(inv[i][k] for i in range(8)) for k in range(8)]


def boundary(t, normal):
    """Deleted and live line indices for target t and a neighbourhood normal."""
    need(dot(LINES[t], normal) == 0, "normal not orthogonal to target")
    deleted = [i for i in range(NL) if i != t and IP[t][i] == 0 and dot(LINES[i], normal) != 0]
    live = [i for i in range(NL) if i not in deleted]
    need(len(deleted) == 27 and len(live) == 93, "puncture size")
    nbhd = [i for i in live if i == t or IP[t][i] == 0]
    need(all(dot(LINES[i], normal) == 0 for i in nbhd), "neighbourhood not annihilated by normal")
    return deleted, live


def ranks_for(live, source, tops, bottoms):
    """Eight separate-term COPY ranks for a biorthogonal frame (tops, bottoms)."""
    out = []
    for u, w in zip(tops, bottoms):
        left = [i for i in live if dot(LINES[i], u) != 0]
        right_indices = [j for j in live if dot(source[j], w) != 0]
        right = sum(1 << j for j in right_indices)
        rank = rank2([NR[i] & right for i in left])
        dense = [[int(IP[i][j] % 2 == 0) for j in right_indices] for i in left]
        need(rank == rank_f2_dense(dense), "two F2 rank engines disagree")
        out.append(rank)
    return out


def source_rows(live, t, scale):
    """Bottom rows: the lines themselves, with the target row moved to TARGET + scale NORMAL."""
    src = {j: LINES[j] for j in live}
    src[t] = tuple(x + scale * y for x, y in zip(TARGET, NORMAL))
    return src


def exactness(live, source, tops, bottoms):
    """Entries of D T^T - 2G over live pairs: (masked errors, unmasked errors, error map)."""
    d = {i: [dot(LINES[i], u) for u in tops] for i in live}
    tm = {j: [dot(source[j], w) for w in bottoms] for j in live}
    masked = unmasked = 0
    errs = {}
    for i in live:
        for j in live:
            e = (sum(a * b for a, b in zip(d[i], tm[j])) - dot(LINES[i], LINES[j])) / Fr(2)
            if e != 0:
                errs[(i, j)] = e
                if IP[i][j] % 2 == 0:
                    masked += 1
                else:
                    unmasked += 1
    return masked, unmasked, errs


def check_geometry_and_certificate():
    need(rank2(NR) == 9, "F2 rank of the pairing matrix is not 9")
    t = INDEX[TARGET]
    deleted, live = boundary(t, NORMAL)
    nbhd = [LINES[i] for i in live if i == t or IP[t][i] == 0]
    need(len(nbhd) == 37 and rational_rank(nbhd) == 7, "deficient neighbourhood")
    need(rational_rank([LINES[i] for i in live]) == 8, "live rank")
    cert = json.loads(CERT.read_text())["witness"]
    need(tuple(cert["target_doubled_root"]) == TARGET and tuple(cert["normal"]) == NORMAL, "witness vectors")
    need(cert["live_ports"] == 93 and len(cert["deleted_indices"]) == 27, "certificate puncture size")
    need(cert["deleted_indices"] == deleted, "certificate deleted line indices")
    return t, deleted, live


def structured_frame(a, b):
    w1 = tuple(a * x + b * y for x, y in zip(TARGET, NORMAL))
    return [w1] + [tuple(int(i == k) for i in range(8)) for k in range(1, 8)]


def check_one_sided_frame(t, live):
    a, b = FRAME_AB
    bottoms = structured_frame(a, b)
    tops = dual_basis(bottoms)
    need(all(dot(u, w) == int(i == j) for i, u in enumerate(tops) for j, w in enumerate(bottoms)), "biorthogonality")
    star = Fr(-dot(bottoms[0], TARGET), dot(bottoms[0], NORMAL))
    r0 = ranks_for(live, source_rows(live, t, Fr(0)), tops, bottoms)
    rs = ranks_for(live, source_rows(live, t, star), tops, bottoms)
    need(star == Fr(-52, 21), "special scale")
    need(r0 == [9] * 8 and sum(r0) == SAME_FRAME_COPY, "same-frame all-pairs baseline is not 72")
    need(rs == [8] + [9] * 7 and sum(rs) == ONE_SIDED_COPY, "one-sided completion is not 71")
    src0, srcs = source_rows(live, t, Fr(0)), source_rows(live, t, star)
    m0, u0, e0 = exactness(live, src0, tops, bottoms)
    ms, us, es = exactness(live, srcs, tops, bottoms)
    need((m0, u0) == (0, 0), "all-pairs comparator is not exact on every pair")
    need(ms == 0 and us == 56 and all(j == t for (_, j) in es), "one-sided completion is not mask-exact with 56 target-column errors")
    need(all(es[(i, t)] == star * dot(LINES[i], NORMAL) / 2 for (i, _) in es), "error formula")
    return tops, bottoms, star, r0, rs


def check_mechanism(t, live, tops, bottoms, star):
    """Why one rank drops: the target is a coloop of the first bottom's live support."""
    odd = {i for i in range(NL) if IP[t][i] % 2}
    need(len(odd) == 56, "56 lines odd to the target")
    s0 = {j for j in live if dot(source_rows(live, t, Fr(0))[j], bottoms[0]) != 0}
    ss = {j for j in live if dot(source_rows(live, t, star)[j], bottoms[0]) != 0}
    need(s0 == odd | {t} and ss == odd, "bottom support is the root-ray support, minus the target at the special scale")
    need(rank2([NR[i] for i in s0]) == 9 and rank2([NR[i] for i in ss]) == 8, "label span 9 with the target, 8 without")
    top_support = [i for i in live if dot(LINES[i], tops[0]) != 0]
    need(rank2([NR[i] for i in top_support]) == 9, "first top has full label span")
    n = [[(NR[i] >> j) & 1 for j in sorted(ss)] for i in top_support]
    need(rank_f2_dense(n) == 8, "dense cross-check of the rank-8 term")
    need(rank_f2_dense([[(NR[i] >> j) & 1 for j in sorted(s0)] for i in top_support]) == 9, "dense cross-check of the rank-9 term")


def check_comparator(live):
    tops = [tuple(Fr(x) for x in u) for u in COMPARATOR_TOPS]
    need(all(tuple(u) in INDEX or tuple(-x for x in u) in INDEX for u in COMPARATOR_TOPS), "tops are root lines")
    need(len({tuple(u) for u in COMPARATOR_TOPS}) == 8 and rational_rank(COMPARATOR_TOPS) == 8, "tops independent")
    bottoms = dual_basis(tops)
    src = {j: LINES[j] for j in live}
    m, u, _ = exactness(live, src, tops, bottoms)
    need((m, u) == (0, 0), "comparator is exact on all pairs")
    ranks = ranks_for(live, src, tops, bottoms)
    need(ranks == [7, 8, 7, 8, 8, 8, 8, 9] and sum(ranks) == COMPARATOR_COPY, "comparator ranks")
    n_deleted_tops = sum(1 for u in COMPARATOR_TOPS if INDEX.get(u, INDEX.get(tuple(-x for x in u))) not in live)
    need(n_deleted_tops == 7, "seven tops are deleted lines")
    return tops, bottoms, ranks


def check_controls(t, deleted, live, tops, bottoms, star):
    bad = [list(w) for w in bottoms]
    bad[1][0] += 1
    masked, _, _ = exactness(live, source_rows(live, t, star), tops, [tuple(w) for w in bad])
    need(masked > 0, "planted bottom error not detected")
    for x in deleted:
        e = star * dot(LINES[x], NORMAL)
        need(IP[x][t] % 2 == 0 and e != 0, "restoring a deleted line must expose a masked error")
    sensitive = [(3, 1, 2, 0, 0, 0, 0, 0), (3, 1, -1, 0, 0, 0, 0, 0), (2, 0, -1, 0, 0, 0, 0, 0)]
    sensitive += [tuple(int(i == k) for i in range(8)) for k in range(3, 8)]
    r = ranks_for(live, source_rows(live, t, Fr(0)), dual_basis(sensitive), sensitive)
    need(r == [8] + [9] * 7, "recount can return 8 when a top is a deleted-root direction")
    return len(deleted)


def fraction_rows(rows):
    return [[str(x) for x in row] for row in rows]


def result():
    t, deleted, live = check_geometry_and_certificate()
    print("ok   pinned 93-line instance reconstructed; no predecessor census replayed")
    tops, bottoms, star, r0, rs = check_one_sided_frame(t, live)
    print("ok   non-coordinate frame: all-pairs 72, mask-only 71, scale %s" % star)
    check_mechanism(t, live, tops, bottoms, star)
    print("ok   first bottom support loses the target; first pairing rank drops 9 -> 8")
    ctops, cbottoms, cranks = check_comparator(live)
    print("ok   all-pairs comparator ranks %s total %d" % (cranks, sum(cranks)))
    n_ctl = check_controls(t, deleted, live, tops, bottoms, star)
    print("ok   controls: planted masked error, %d restorations, rank sensitivity" % n_ctl)
    return {
        "schema_version": 1,
        "status": "PASS_FIRST_FAILURE_ONE_SIDED_COPY",
        "claim_type": "finite exact constructions",
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(CERT.read_bytes()).hexdigest(),
        "live_ports": len(live),
        "deleted_indices": deleted,
        "one_sided": {
            "tops": fraction_rows(tops), "bottoms": fraction_rows(bottoms),
            "target_scale": str(star), "same_frame_all_pairs_ranks": r0,
            "copy_ranks": rs, "masked_errors": 0, "unmasked_errors": 56,
            "first_bottom_support_sizes": [57, 56],
        },
        "all_pairs": {
            "tops": fraction_rows(ctops), "bottoms": fraction_rows(cbottoms),
            "copy_ranks": cranks, "masked_errors": 0, "unmasked_errors": 0,
        },
        "restoration_controls": n_ctl,
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a generated receipt; refuse overwrite")
    args = parser.parse_args()
    if args.write is not None:
        need(not args.write.exists(), "receipt destination already exists")
    need(CERT.stat().st_size <= 1024 * 1024, "source certificate exceeds 1 MiB")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in sources["files"] if row["path"] == str(CERT.relative_to(HERE.parent.parent)))
    need(hashlib.sha256(CERT.read_bytes()).hexdigest() == pin["sha256"], "source certificate hash")
    receipt = result()
    if args.write is not None:
        with args.write.open("x") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(receipt == json.loads((HERE / "RESULT.json").read_text()), "generated receipt differs")
    print("PASS_FIRST_FAILURE_ONE_SIDED_COPY one_sided=71 same_frame=72 all_pairs=63 no_new_kappa")


if __name__ == "__main__":
    sys.exit(main())
