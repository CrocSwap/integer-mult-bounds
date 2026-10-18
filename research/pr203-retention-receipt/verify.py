#!/usr/bin/env python3
"""Offline PR203 source-retention proof and saved-certificate reconciliation.

steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
This checks Git object identity and recorded/recomputed exact screens, not C++ or solver replay.
"""
import argparse
import base64
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "534de584c7c9b7abd621a0d8cec959d021e5b510"
MERGE_BASE = "3b6b66891c0ac888521cf591fe306c6286601d4f"
PR203 = "d2873e20750d0949d2ad75cbc4cd82b5b1a74e84"
PR187 = "201737a1ec4f936e166e2481fb9e88104cb2ccc7"
PR193 = "187e1010ac8b259af8e9b5166f68b64bc27b4b47"
PR204 = "525ed356ec4928f4c31c7668ecb547f575278f4e"
PR288 = "475a088b5862f75f0b10596cfd6842d19531a5ec"
ARCHIVE_92 = "b91de239a64d24d8aee409a0f4ac3e00710ae5c1"
ARCHIVE_NEXT100 = "bd1b279e5e5449f81ca262c1647961e81dd69e50"

PKG_DIR = "research/percent-exponent-architecture"
PKG_WORKFLOW = ".github/workflows/percent-exponent-architecture.yml"
PKG_TREE = "1f3d82dd561239625548eba0b3f01728c5aacd38"
PKG_WORKFLOW_BLOB = "b22fdbd4e01db1c284bf028d4f8f2da716327340"
NOTICE_BLOB = "617d9e0ac5ca10d23741382e96ca8bb524ca4013"

PR187_PHYSICAL_PATH = "research/source-assisted-bit-bootstrap/emitted-physical.json"
PR187_PHYSICAL_BLOB = "035552f14bf74ae7c951aa0a0cc5382b6e51e4ea"
PR187_PHYSICAL_SHA256 = "5f1f1d978937b816a14b07fee5ac8fc31f3a9aaf05046a477e8be57bb6d07ce6"

PR193_CERT_PATH = "research/source-assisted-v4/certificate.json"
PR193_CERT_BLOB = "1bf00cdb8472c0992a9846af38778ed86eb909e0"
PR193_CERT_SHA256 = "d84406d2fcc6990deba2b135509e6d86600e57123d88f9b21f7b7240e1aeb513"

PR193_BALANCED_FANO_PATH = "scripts/experiments/balanced_fano.py"
PR193_BALANCED_FANO_BLOB = "136446fa017ae8370c3f069d98ba278f4c5f96ce"
PR193_BALANCED_FANO_SHA256 = "1586fb1db4f40e79e97bae59f47192675663403bbcacbf5f4e0b702edfd22b0a"

FANO_COMPLETION_PATH = "scripts/experiments/fano_completion.py"
FANO_COMPLETION_BLOB = "86a0ec6e62fc9a371f03d0e87457a085c9e494f3"
FANO_COMPLETION_SHA256 = "6cade2a36b910bf7e68a872dc4fd3560837935cffe80f9526cd012a28b247738"

INPUTS = (
    "research/community-reconciliation-next100-audit/ARCHIVE.json",
    "research/community-reconciliation-next100-audit/REVIEW.json",
    "research/community-reconciliation92-audit/ARCHIVE.json",
    "research/community-reconciliation92-audit/REVIEW.json",
    "research/community-round9-audit/pr203-replay.log.txt",
    "research/community-round9-audit/review-ledger.json",
    "scripts/experiments/fano_completion.py",
)

GRID = 10 ** 24
TARGET = Q(1, 100)

FANO_EDGES = (
    ("a", "u1"), ("a", "tc"), ("b", "u1"), ("b", "u2"), ("c", "u2"),
    ("c", "u6"), ("u1", "u3"), ("u2", "u4"), ("u3", "u5"), ("u3", "u6"),
    ("u4", "u5"), ("u4", "ta"), ("u5", "u7"), ("u6", "u8"), ("u7", "u9"),
    ("u7", "tc"), ("u8", "u9"), ("u8", "ta"), ("u9", "u10"), ("u10", "tb"),
)
GL2 = ((1, 2), (2, 1), (1, 3), (3, 2), (2, 3), (3, 1))
OBSTRUCTION_CASE_IDS = (0, 3, 4, 13, 16, 34, 36, 37, 41, 43, 47, 50, 60, 62, 67, 70)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def loads(raw):
    return json.loads(raw, object_pairs_hook=no_duplicate_keys)


def git_id(kind, raw):
    return hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class Proof:
    def __init__(self, document):
        require(document["schema_version"] == 1, "unsupported proof schema")
        self.objects = document["objects"]
        self.used = set()

    def raw(self, oid, kind):
        require(re.fullmatch(r"[0-9a-f]{40}", oid) is not None, "invalid Git id")
        require(oid in self.objects, "missing Git object: " + oid)
        obj = self.objects[oid]
        require(obj["type"] == kind, "Git object type mismatch")
        raw = base64.b64decode(obj["base64"], validate=True)
        require(git_id(kind, raw) == oid, "Git object digest mismatch: " + oid)
        self.used.add(oid)
        return raw

    def commit(self, oid):
        header = self.raw(oid, "commit").split(b"\n\n", 1)[0].decode("utf-8").splitlines()
        trees = [line[5:] for line in header if line.startswith("tree ")]
        require(len(trees) == 1, "commit needs one tree")
        return trees[0], [line[7:] for line in header if line.startswith("parent ")]

    def tree(self, oid):
        raw, offset, entries = self.raw(oid, "tree"), 0, {}
        while offset < len(raw):
            space = raw.find(b" ", offset)
            zero = raw.find(b"\0", space + 1)
            require(space > offset and zero > space + 1 and zero + 21 <= len(raw),
                    "malformed Git tree")
            mode = raw[offset:space].decode("ascii")
            name = raw[space + 1:zero].decode("utf-8")
            require(mode in ("40000", "100644", "100755", "120000"), "unsupported tree mode")
            require(name not in (".", "..") and "/" not in name and name not in entries,
                    "invalid or duplicate tree path")
            entries[name] = (mode, raw[zero + 1:zero + 21].hex())
            offset = zero + 21
        return entries

    def resolve(self, commit, path, expected_mode=None):
        parts = path.split("/")
        require(all(p and p not in (".", "..") for p in parts), "invalid requested path")
        oid, _ = self.commit(commit)
        mode = "40000"
        for part in parts:
            require(mode == "40000", "path traverses a non-directory")
            entries = self.tree(oid)
            require(part in entries, "missing path component: " + part)
            mode, oid = entries[part]
        if expected_mode is not None:
            require(mode == expected_mode, "path mode mismatch: " + path)
        return mode, oid

    def inventory(self, tree, prefix=""):
        result = {}
        for name, (mode, oid) in self.tree(tree).items():
            path = prefix + name
            if mode == "40000":
                result.update(self.inventory(oid, path + "/"))
            else:
                result[path] = {"mode": mode, "blob": oid}
        return result

    def difference(self, before, after, prefix=""):
        """Walk every changed subtree; equal Git trees are skipped exactly."""
        if before == after:
            return {}
        left, right = self.tree(before), self.tree(after)
        changed = {}
        for name in sorted(set(left) | set(right)):
            a, b = left.get(name), right.get(name)
            path = prefix + name
            if a == b:
                continue
            if a is None and b[0] == "40000":
                changed.update({p: {"before": None, "after": row}
                                for p, row in self.inventory(b[1], path + "/").items()})
            elif a is not None and b is not None and a[0] == b[0] == "40000":
                changed.update(self.difference(a[1], b[1], path + "/"))
            else:
                changed[path] = {
                    "before": None if a is None else {"mode": a[0], "blob": a[1]},
                    "after": None if b is None else {"mode": b[0], "blob": b[1]},
                }
        return changed


def down(x):
    return Q(x.numerator * GRID // x.denominator, GRID)


def atanh_log(x, terms=40):
    require(Q(1) <= x <= Q(2), "log series outside range")
    z = (x - 1) / (x + 1)
    power = z
    total = Q(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return total, total + tail


@lru_cache(None)
def log_interval(x):
    x = Q(x)
    require(x >= 1, "only ratios >= 1 supported")
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    lo2, hi2 = atanh_log(Q(2))
    lo, hi = atanh_log(x)
    lo += power * lo2
    hi += power * hi2
    return down(lo), Q(-((-hi.numerator * GRID) // hi.denominator), GRID)


def cost_floor(m, histogram):
    require(all(0 < int(r) < m and int(n) > 0 for r, n in histogram.items()),
            "invalid data child histogram")
    return sum((Q(int(n) * int(r)) * log_interval(Q(m, int(r)))[0]
                for r, n in histogram.items()), Q(0))


def uplift_floor(m, histogram, saving):
    result = Q(0)
    for r, n in histogram.items():
        x = saving * log_interval(Q(m, int(r)))[0]
        term = Q(1)
        uplift = Q(0)
        for j in range(1, 13):
            term = term * x / j
            uplift += term
        result += int(n) * int(r) * uplift
    return down(result)


def data_histogram(source, target, v):
    result = Counter()
    for hist in (source, target):
        for r, n in hist.items():
            if int(r) and int(n):
                result[int(r)] += 3 * int(n)
    result[2] += 2 * v
    return result


def binary_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def recompute_checkpoint(name, x):
    p = x["profile"]
    m, h, v = p["m"], p["h"], p["v"]
    delta, loss = p["deficit"], p["loss"]
    children = {int(r): n for r, n in p["child_histogram"].items() if int(r)}
    require(m == 3 * h, "pinned three-block architecture mismatch: " + name)
    require(delta == 2 * v - 3 * loss, "pinned deficit identity mismatch: " + name)
    require(sum(r * n for r, n in children.items()) == p["rank"], "full rank recount mismatch: " + name)
    require(m * p["W"] - p["rank"] == delta, "full stock/deficit recount mismatch: " + name)
    for key in ("source_data_histogram", "target_data_histogram"):
        require(sum(int(r) * n for r, n in p[key].items()) == v * (h - 1),
                "complete local data itinerary mismatch: " + name)
    data = data_histogram(p["source_data_histogram"], p["target_data_histogram"], v)
    require(all(children.get(r, 0) >= n for r, n in data.items()),
            "data is not an actual submultiset of child_histogram: " + name)
    lower = cost_floor(m, data)
    full_cost = cost_floor(m, children)
    paid_at_target = uplift_floor(m, data, TARGET)
    assembly_required_saving = TARGET / (1 - TARGET)
    paid_at_assembly_target = uplift_floor(m, data, assembly_required_saving)
    require(Q(2 * v) / lower < Q(9, 1000), "free-center ceiling exceeds 0.009: " + name)
    require(paid_at_target > 2 * v, "fixed data fails to reject a=0.01: " + name)
    return {
        "name": name, "provenance": x["provenance"], "h": h, "m": m, "v": v,
        "retained_loss": loss, "retained_deficit": delta,
        "data_histogram": {str(k): v_count for k, v_count in sorted(data.items())},
        "data_entropy_floor": str(lower), "data_entropy_floor_per_port": str(lower / v),
        "full_entropy_floor": str(full_cost),
        "retained_loss_a_ceiling": str(Q(delta) / lower),
        "free_center_a_ceiling": str(Q(2 * v) / lower),
        "fixed_data_required_deficit_at_a_001_lower": str(paid_at_target),
        "fixed_data_required_deficit_per_port_at_a_001_lower": str(paid_at_target / v),
        "assembly_required_saving": str(assembly_required_saving),
        "fixed_data_required_deficit_at_assembly_target_lower": str(paid_at_assembly_target),
        "available_deficit_even_with_free_centers": 2 * v,
        "scope": "The pinned data itinerary and deficit identity; all auxiliary entropy is discarded. Free-center relaxation assumes only D<=2v.",
    }


def odd_cube_ledger(p, degree):
    require(degree >= 3 and degree % 2 == 1 and p >= degree + 1, "invalid odd-cube domain")
    t = (degree - 1) // 2
    h, m = 2 * p, 6 * p
    v = (2 ** degree) * comb(p, degree)
    loss = (2 ** t) * comb(p, t) * (h - 2 * t)
    delta = 2 * v - 3 * loss
    source = Counter([degree - 1, h - degree - 1, 1])
    target = Counter([h - degree - 1] + [1] * degree)
    data = data_histogram(source, target, 1)
    require(sum(r * n for r, n in data.items()) == 6 * (h - 1) + 4, "odd-cube data rank identity mismatch")
    require(max(data) < h, "odd-cube data child width reaches h")
    lower = cost_floor(m, data)
    relaxed = cost_floor(m, {h - 1: 6, 2: 2})
    return {
        "p": p, "degree": degree, "h": h, "m": m, "v": v,
        "loss": loss, "deficit": delta,
        "data_histogram_per_port": dict(sorted(data.items())),
        "data_entropy_floor_per_port": str(lower),
        "a_ceiling": str(Q(delta, v) / lower) if delta > 0 else None,
        "arbitrary_local_chains_entropy_floor_per_port": str(relaxed),
        "arbitrary_local_chains_a_ceiling": str(Q(delta, v) / relaxed) if delta > 0 else None,
    }


def b_value(intersection, degree):
    result = Q(1)
    for j in range(1, (degree - 1) // 2 + 1):
        result *= Q(intersection - (2 * j - 1), degree - (2 * j - 1))
    return result


def local_identity(degree):
    size = 1 << degree
    denominator = size // 2
    first = []
    for mask in range(size):
        value = b_value(degree - mask.bit_count(), degree) * denominator
        require(value.denominator == 1, "local kernel is not dyadic")
        first.append(int(value))
    eigenvalues = []
    for character in range(size):
        eig = sum((-1 if (character & x).bit_count() % 2 else 1) * first[x]
                  for x in range(size))
        expected = 2 * denominator if character.bit_count() <= (degree - 1) // 2 else 0
        require(eig == expected, "Walsh projector identity mismatch")
        eigenvalues.append(eig)
    k = [-b for b in first]
    k[0] += denominator
    for shift in range(size):
        conv = sum(k[x] * k[x ^ shift] for x in range(size))
        require(conv == (denominator ** 2 if shift == 0 else 0), "K^2 involution mismatch")
        require(not k[shift] or shift.bit_count() % 2 == 1, "K only joins opposite parities")
    addresses = [sum(1 << (2 * j + ((mask >> j) & 1)) for j in range(degree))
                 for mask in range(size)]
    parity_classes = [[addresses[x] for x in range(size) if x.bit_count() % 2 == p]
                      for p in (0, 1)]
    require(all(binary_rank(xs) == degree for xs in parity_classes), "parity source frame rank mismatch")
    require(all((a & b).bit_count() % 2 == 0 for a in parity_classes[0] for b in parity_classes[1]),
            "source/target orthogonality mismatch")
    return {
        "degree": degree, "ports_per_cube": size, "B_rank": size // 2,
        "K_squared_identity": True, "opposite_parity_source_rank": degree,
        "denominator": denominator, "kernel_numerators": first,
    }


def star_check(p, degree):
    t = (degree - 1) // 2
    fixed = tuple(2 * i for i in range(t))
    vectors = []
    for pairs in combinations(range(t, p), degree - t):
        for bits in product((0, 1), repeat=degree - t):
            vectors.append(sum(1 << i for i in fixed)
                           + sum(1 << (2 * i + b) for i, b in zip(pairs, bits)))
    observed = binary_rank(vectors)
    require(observed == 2 * p - 2 * t, "copied t-star span mismatch")
    return {"p": p, "degree": degree, "fixed_coordinates": list(fixed),
            "source_count": len(vectors), "rank": observed}


def recompute_ceiling_certificate(in_193, in_187):
    rows = [odd_cube_ledger(p, d) for p in range(4, 30) for d in range(3, p, 2)]
    positive = [r for r in rows if r["a_ceiling"] is not None]
    best = max(positive, key=lambda r: Q(r["a_ceiling"]))
    best_relaxed = max(positive, key=lambda r: Q(r["arbitrary_local_chains_a_ceiling"]))
    claimed_ceiling = Q(5164, 10 ** 6)
    relaxed_ceiling = Q(8094, 10 ** 6)
    require(Q(best["a_ceiling"]) < claimed_ceiling, "finite family ceiling exceeded")
    require(Q(best_relaxed["arbitrary_local_chains_a_ceiling"]) < relaxed_ceiling,
            "arbitrary local data chain ceiling exceeded")
    tail = Q(2) / ((12 * 30 - 2) * log_interval(Q(3))[0])
    require(tail < Q(best["a_ceiling"]), "infinite tail not below finite maximum")
    scan_sha256 = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()

    def stringify_hist(row):
        out = dict(row)
        out["data_histogram_per_port"] = {str(k): v for k, v in row["data_histogram_per_port"].items()}
        return out

    odd_cube = {
        "finite_cases": len(rows),
        "positive_deficit_cases": len(positive),
        "finite_scan_sha256": scan_sha256,
        "best_optimistic_case": stringify_hist(best),
        "best_arbitrary_local_chains_case": stringify_hist(best_relaxed),
        "tail_from_p": 30,
        "all_degrees_tail_a_ceiling": str(tail),
        "strict_global_a_ceiling": str(claimed_ceiling),
        "strict_arbitrary_local_chains_a_ceiling": str(relaxed_ceiling),
        "scope": "Odd d>=3, p>=d+1; copied t-star centers and m=6p. The 0.005164 bound keeps the destructive-parity source/target flag. The 0.008094 bound permits any local source/target chains of endpoint distance h-1 with each jump at most h. Both discard all auxiliary entropy. No global side circuit is claimed.",
        "local_identity_checks": [local_identity(d) for d in (3, 5, 7)],
        "star_span_checks": [star_check(p, d) for p, d in ((4, 3), (7, 3), (6, 5), (9, 5), (8, 7))],
    }

    log3_lo, log3_hi = log_interval(Q(3))
    small_cases = []
    for stock in (30, 31):
        lo, hi = log_interval(Q(3 * stock, 3 * stock - 1))
        lower, upper = lo / log3_hi, hi / log3_lo
        if stock == 30:
            require(lower > Q(1, 99), "30-role one-deficit budget below 1/99")
        else:
            require(upper < Q(1, 99), "31-role adverse budget control not below 1/99")
        small_cases.append({
            "m": 3, "W": stock, "rank_deficit": 1,
            "uniform_bit_saving_lower": str(lower),
            "uniform_bit_saving_upper": str(upper),
            "exceeds_assembly_requirement": stock == 30,
        })

    return {
        "status": "SCOPED ARCHITECTURE CEILINGS; NO NEW KAPPA",
        "target_kappa": str(TARGET),
        "checkpoints": [
            recompute_checkpoint("complex-pr193", in_193),
            recompute_checkpoint("bit-pr187", in_187),
        ],
        "odd_cube_extension": odd_cube,
        "small_network_target": {
            "necessary_ordinary_saving_for_kappa_001": "1/99",
            "cases": small_cases,
            "scope": "Conditional search budget for the raw uniform bit recurrence, assuming a complete all-role rational-frame certificate exists. No such circuit or complex companion is supplied.",
        },
    }


def matrix(a):
    n = len(a)
    require(n > 0 and all(len(row) == n for row in a), "square nonempty matrices required")
    require(not any(isinstance(v, float) for row in a for v in row), "use exact entries")
    return tuple(tuple(Q(v) for v in row) for row in a)


def multiply(a, b):
    require(len(a) == len(b), "matrix dimensions differ")
    n = len(a)
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(n)), Q(0))
                       for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    rows = [list(a[i]) + [Q(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [v / scale for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def rejection(frames, basis=None):
    frames = tuple(dict.fromkeys(matrix(a) for a in frames))
    require(bool(frames) and all(len(a) == len(frames[0]) for a in frames),
            "nonempty common-dimensional frame family required")
    n = len(frames[0])
    if basis is not None:
        basis = matrix(basis)
        require(len(basis) == n, "wrong common basis dimension")
        inv = inverse(basis)
        changed = [multiply(multiply(inv, a), basis) for a in frames]
        require(not any(a[i][j] for a in changed for i in range(n) for j in range(i)),
                "supplied common basis does not triangularize every frame")
        return {"rejected": True, "reason": "Exact common triangularizing basis",
                "unique_frames": len(frames), "rank_lower_bound": "W*m"}
    commuting = all(multiply(a, b) == multiply(b, a) for a, b in combinations(frames, 2))
    return {"rejected": commuting,
            "reason": "Pairwise commuting frames" if commuting else "This sufficient screen is inconclusive",
            "unique_frames": len(frames), "rank_lower_bound": "W*m" if commuting else None}


def ports(p):
    labels = [tuple(2 * i + b for i, b in zip(coarse, bits))
              for coarse in combinations(range(p), 3)
              for bits in product((0, 1), repeat=3)]
    return labels, [sum(1 << j for j in label) for label in labels]


def support_rank(p, coefficients):
    labels, vectors = ports(p)
    return binary_rank(q for label, q in zip(labels, vectors)
                       if sum(coefficients[j] for j in label))


@lru_cache(None)
def ternary_sweep_p5():
    p = 5
    labels, vectors = ports(p)
    threshold = 2 * p - 2
    checked = 0
    for coefficients in product((-1, 0, 1), repeat=2 * p):
        if not any(coefficients):
            continue
        pivots = {}
        for (a, b, c), q in zip(labels, vectors):
            if not (coefficients[a] + coefficients[b] + coefficients[c]):
                continue
            while q:
                top = q.bit_length() - 1
                if top in pivots:
                    q ^= pivots[top]
                else:
                    pivots[top] = q
                    break
            if len(pivots) >= threshold:
                break
        require(len(pivots) >= threshold, "finite source-support counterexample")
        checked += 1
    return {
        "p": p,
        "coefficient_alphabet": [-1, 0, 1],
        "nonzero_vectors_checked": checked,
        "certified_support_rank_floor": threshold,
        "scope": "Finite control only; the written lemma handles every characteristic-zero coefficient vector.",
    }


def recompute_center_basis_certificate():
    sharp = []
    for p in (5, 6, 11, 13, 16):
        h = 2 * p
        gram = matrix([[4 * comb(p - 1, 2) if i == j else 0 if i // 2 == j // 2
                        else 2 * (p - 2) for j in range(h)] for i in range(h)])
        inverse(gram)
        center_rank = support_rank(p, [1] + [0] * (h - 1))
        omitted_pair = support_rank(p, [-2, -2] + [1] * (h - 2))
        require(center_rank == omitted_pair == h - 2, "sharp center-support example mismatch")
        sharp.append({
            "p": p, "h": h, "incidence_rank_Q": h,
            "star_support_rank_F2": center_rank,
            "omitted_pair_support_rank_F2": omitted_pair,
            "rank_minimal_center_loss_floor": h * (h - 2),
        })
    small = support_rank(4, [-2, -2] + [1] * 6)
    require(small == 4 and small < 8 - 2, "p>=5 domain control mismatch")
    return {
        "status": "SHARP LOWER BOUND FOR RANK-MINIMAL COPIED CENTERS",
        "theorem": "For p>=5 and h=2p, every nonzero characteristic-zero linear combination of coordinate stars has binary source-support span at least h-2. Therefore any factorization of B=(AA^T-J)/2 through exactly h copied scalar centers has loss at least h(h-2).",
        "sharp_examples": sharp,
        "finite_sweep": ternary_sweep_p5(),
        "excluded_domain_control": {"p": 4, "support_rank": small, "putative_floor": 6},
        "scope": "Exactly h linearly independent copied centers. Overcomplete factors, a different center mechanism, changed port families and global stage fusion remain outside this result.",
    }


def check_triangular_obstruction_controls():
    upper = [matrix([[1, 1], [0, 0]]), matrix([[0, 2], [0, 1]])]
    basis = matrix([[1, 1], [1, 2]])
    inv = inverse(basis)
    frames = [multiply(multiply(basis, a), inv) for a in upper]
    require(not rejection(frames)["rejected"], "noncommuting upper-triangularizable pair should not commute")
    require(rejection(frames, basis)["rejected"], "explicit common basis should reject")
    rotation = [[0, -1], [1, 0]]
    translated = [[1, -1], [1, 1]]
    require(rejection([rotation, translated])["rejected"], "commuting frames without Q-eigenbasis should reject")
    non_tri = [[[1, 0], [0, 0]], [[Q(1, 2), Q(1, 2)], [Q(1, 2), Q(1, 2)]]]
    require(not rejection(non_tri)["rejected"], "nontriangular pair must remain inconclusive")
    return 3


def balanced_fano_model():
    order = ("a", "b", "c", "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "ta", "tb", "tc")
    source = {"a": 0, "b": 1, "c": 2}
    edge_roles = {}
    next_role = 3
    pairs = []
    gates_at = []
    auxiliary_inputs = []
    auxiliary_outputs = []
    targets = {}
    for vertex in order:
        incoming = [i for i, (_, v) in enumerate(FANO_EDGES) if v == vertex]
        outgoing = [i for i, (u, _) in enumerate(FANO_EDGES) if u == vertex]
        roles = [edge_roles[i] for i in incoming]
        if vertex in source:
            roles.append(source[vertex])
        output_count = len(outgoing) + int(vertex in ("ta", "tb", "tc"))
        width = max(len(roles), output_count)
        require(width in (1, 2), "unexpected local width in balanced Fano DAG")
        while len(roles) < width:
            auxiliary_inputs.append((vertex, next_role))
            roles.append(next_role)
            next_role += 1
        if width == 2:
            pairs.append(tuple(roles))
            gates_at.append(vertex)
        for edge, role in zip(outgoing, roles):
            edge_roles[edge] = role
        occupied = len(outgoing)
        if vertex in ("ta", "tb", "tc"):
            targets[vertex] = roles[occupied]
            occupied += 1
        auxiliary_outputs.extend((vertex, r) for r in roles[occupied:])
    require(next_role == 10 and len(pairs) == 14, "wrong balanced Fano model size")
    return {
        "W": next_role,
        "pairs": pairs,
        "gate_vertices": gates_at,
        "prescribed": {0: targets["ta"], 1: targets["tb"], 2: targets["tc"]},
        "auxiliary_inputs": auxiliary_inputs,
        "auxiliary_outputs": auxiliary_outputs,
    }


def execute_gl2(width, pairs, choices):
    rows = [1 << i for i in range(width)]
    for (a, b), k in zip(pairs, choices):
        u, v = rows[a], rows[b]
        c0, c1 = GL2[k]
        rows[a] = (u if (c0 & 1) else 0) ^ (v if (c0 & 2) else 0)
        rows[b] = (u if (c1 & 1) else 0) ^ (v if (c1 & 2) else 0)
    return rows


@lru_cache(None)
def enumerate_fano_topologies():
    base = balanced_fano_model()
    time = {name: i for i, name in enumerate(base["gate_vertices"])}
    donors = [(name, role) for name, role in base["auxiliary_outputs"]
              if any(time[name] < time[rec] for rec, _ in base["auxiliary_inputs"])]
    recipients = [(name, role) for name, role in base["auxiliary_inputs"]
                  if any(time[don] < time[name] for don, _ in donors)]
    options = [[None] + [(don, role) for don, role in donors if time[don] < time[rec]]
               for rec, _ in recipients]
    out = []
    for choice in product(*options):
        chosen = [p for p in choice if p is not None]
        if len(chosen) != len(set(chosen)):
            continue
        parent = list(range(base["W"]))

        def find(i):
            while parent[i] != i:
                i = parent[i]
            return i

        reused = []
        removed_inputs = set()
        for (receiver, r), donor in zip(recipients, choice):
            if donor is None:
                continue
            vertex, d = donor
            require(time[vertex] < time[receiver] and find(r) != find(d), "invalid stub reuse")
            parent[find(r)] = find(d)
            reused.append({"from_vertex": vertex, "from_role": d,
                           "to_vertex": receiver, "to_role": r})
            removed_inputs.add(r)
        independent = [i for i in range(base["W"]) if i not in removed_inputs]
        index = {find(i): k for k, i in enumerate(independent)}
        renumber = [index[find(i)] for i in range(base["W"])]
        pairs = [[renumber[a], renumber[b]] for a, b in base["pairs"]]
        require(all(a != b for a, b in pairs), "self-loop in reused topology")
        prescribed = {str(renumber[i]): renumber[j] for i, j in base["prescribed"].items()}
        width = len(independent)
        inputs_sorted = tuple(sorted(int(k) for k in prescribed))
        states = {inputs_sorted}
        for a, b in pairs:
            states |= {tuple(b if p == a else a if p == b else p for p in s)
                       for s in states}
        destination = tuple(prescribed[str(p)] for p in inputs_sorted)
        routing = {
            "routable": destination in states,
            "reachable_token_placements": len(states),
            "prescribed_destination": list(destination),
        }
        out.append({
            "id": len(out),
            "W": width,
            "pairs": pairs,
            "prescribed": prescribed,
            "reuse": reused,
            "independent_original_roles": independent,
            "old_to_new_roles": renumber,
            "routing": routing,
        })
    return tuple(out)


@lru_cache(None)
def recompute_direct_full_word_controls():
    specs = (
        (3, ()),
        (3, ((0, 1),)),
        (4, ((0, 1), (2, 3))),
        (4, ((0, 1), (1, 2), (2, 3))),
        (4, ((0, 1), (1, 2), (0, 2), (2, 3))),
        (4, ((0, 1), (1, 2), (2, 3), (0, 3), (1, 3))),
        (5, ((0, 1), (2, 3), (1, 4), (0, 2), (3, 4))),
        (5, ((0, 4), (1, 4), (2, 4), (3, 4), (0, 4))),
    )
    for width, pairs in specs:
        routes = {tuple(range(width))}
        for a, b in pairs:
            next_routes = set(routes)
            for perm in routes:
                new = list(perm)
                new[a], new[b] = new[b], new[a]
                next_routes.add(tuple(new))
            routes = next_routes
        actual = set()
        for choices in product(range(6), repeat=len(pairs)):
            rows = execute_gl2(width, pairs, choices)
            if sorted(rows) != [1 << j for j in range(width)]:
                continue
            actual.add(tuple(row.bit_length() - 1 for row in rows))
        require(actual == routes, "direct full-word control found non-routable or missing scalar permutation")
    return len(specs)


def parse_round9_log(raw_text):
    lines = raw_text.splitlines()
    require(len(lines) == 24, "unexpected Round-9 PR203 replay log line count")
    require(lines[0] == "PASS exact data/family ceilings and the sharp rank-minimal center controls",
            "Round-9 replay log header mismatch")
    require(lines[1] == "......." and lines[3].startswith("Ran 7 tests in ") and lines[5] == "OK",
            "Round-9 unit-test summary mismatch")
    require(lines[6] == "PASS all 87 topologies and all scalar permutations; independent full-word controls",
            "Round-9 87-topology line mismatch")
    require(lines[23] == "PASS conditional architecture audit; no new multiplication exponent",
            "Round-9 final status line mismatch")
    cases = []
    for idx, line in enumerate(lines[7:23], start=1):
        m = re.fullmatch(r"PASS (\d+)/16: case (\d+), W=(\d+), all 6\^14 assignments excluded", line)
        require(m is not None and int(m.group(1)) == idx, "malformed Round-9 Fano case line: " + line)
        cases.append((int(m.group(2)), int(m.group(3))))
    return cases


def check_upstream_provenance(in_187, in_193, ref_source, raw_187, raw_193, raw_bf193, raw_fc193, live_fc):
    require(hashlib.sha256(raw_187).hexdigest() == PR187_PHYSICAL_SHA256, "PR187 emitted-physical SHA256 mismatch")
    require(hashlib.sha256(raw_193).hexdigest() == PR193_CERT_SHA256, "PR193 certificate SHA256 mismatch")
    require(hashlib.sha256(raw_bf193).hexdigest() == PR193_BALANCED_FANO_SHA256,
            "PR193 balanced_fano.py SHA256 mismatch")
    require(raw_fc193 == live_fc and hashlib.sha256(raw_fc193).hexdigest() == FANO_COMPLETION_SHA256,
            "fano_completion.py SHA256 or live retention mismatch")

    require(in_187["provenance"] == {
        "commit": PR187,
        "path": PR187_PHYSICAL_PATH,
        "pr": 187,
        "source_file_sha256": PR187_PHYSICAL_SHA256,
    }, "inputs/bit-pr187.json provenance mismatch")
    p187_up = loads(raw_187)
    p187 = in_187["profile"]
    require((p187["W"], p187["m"], p187["rank"], p187["deficit"])
            == (p187_up["W_per_vertex"], p187_up["m"], p187_up["rank_per_vertex"], p187_up["deficit_per_vertex"])
            == (21108, 72, 1517840, 1936), "bit-pr187 profile scalar mismatch")
    require(p187["h"] == 24 and p187["v"] == 1760 and p187["loss"] == 528 == 24 * 22,
            "bit-pr187 paired-cube loss mismatch")
    for key in ("child_histogram", "source_data_histogram", "target_data_histogram"):
        require(p187[key] == p187_up[key], "bit-pr187 histogram mismatch: " + key)

    require(in_193["provenance"] == {
        "commit": PR193,
        "path": PR193_CERT_PATH,
        "pr": 193,
        "source_file_sha256": PR193_CERT_SHA256,
    }, "inputs/complex-pr193.json provenance mismatch")
    c193_up = loads(raw_193)["complex_profile"]
    p193 = in_193["profile"]
    require((p193["W"], p193["m"], p193["h"], p193["v"], p193["deficit"], p193["loss"], p193["rank"])
            == (c193_up["W_per_vertex"], c193_up["m"], c193_up["h"], c193_up["v"],
                c193_up["deficit_per_vertex"], c193_up["loss"], c193_up["rank_per_vertex"])
            == (12052, 66, 22, 1320, 1320, 440, 794112), "complex-pr193 profile scalar mismatch")
    for key in ("child_histogram", "source_data_histogram", "target_data_histogram"):
        require(p193[key] == c193_up[key], "complex-pr193 histogram mismatch: " + key)

    require(ref_source["commit"] == PR193 and ref_source["files"] == {
        PR193_BALANCED_FANO_PATH: PR193_BALANCED_FANO_SHA256,
        FANO_COMPLETION_PATH: FANO_COMPLETION_SHA256,
    }, "references/SOURCE.json provenance mismatch")


def check_fano_certificates(enum_ctrl, fano_all, fano_reuse, vector_receipts, r9_cases):
    direct_count = recompute_direct_full_word_controls()
    require(enum_ctrl == {"all_passed": True, "direct_full_word_controls": direct_count},
            "enumeration-controls.json mismatch")

    topos = list(enumerate_fano_topologies())
    require(len(topos) == 87, "recomputed balanced-Fano topology count mismatch")
    topo_for_hash = []
    for t in topos:
        d = dict(t)
        d["prescribed"] = {int(k): v for k, v in t["prescribed"].items()}
        topo_for_hash.append(d)
    topo_sha = hashlib.sha256(json.dumps(topo_for_hash, sort_keys=True).encode()).hexdigest()
    require(fano_all["topologies"] == 87 and fano_all["topology_specification_sha256"] == topo_sha,
            "fano-all-permutations.json topology specification hash mismatch")
    width_counts_all = {str(k): v for k, v in sorted(Counter(t["W"] for t in topos).items())}
    require(fano_all["width_counts"] == width_counts_all == {"6": 4, "7": 32, "8": 38, "9": 12, "10": 1},
            "fano-all-permutations.json width_counts mismatch")
    require(len(fano_all["results"]) == 87, "fano-all-permutations.json results length mismatch")
    for topo, row in zip(topos, fano_all["results"]):
        require(row["id"] == topo["id"] and row["W"] == topo["W"], "fano-all-permutations topology id/W mismatch")
        require(row["nonroutable_scalar_permutation"] is False, "nonroutable scalar permutation reported")
        if not row.get("all_permutations_routable"):
            require(row["prefix_assignments"] == row["suffix_assignments"] == 6 ** 7 == 279936,
                    "incomplete meet-in-the-middle half in fano-all-permutations")
            require(row["scalar_permutations"] == row["routing_permutations"],
                    "scalar_permutations != routing_permutations in fano-all-permutations")

    non_routable = [t for t in topos if not t["routing"]["routable"]]
    require(tuple(t["id"] for t in non_routable) == OBSTRUCTION_CASE_IDS,
            "obstruction-preserving topology ID list mismatch")
    require(fano_reuse["topologies_enumerated"] == 87
            and fano_reuse["obstruction_preserving_topologies"] == 16
            and fano_reuse["other_topologies"] == 71,
            "fano-reuse-certificate.json summary counts mismatch")
    width_counts_16 = {str(k): v for k, v in sorted(Counter(t["W"] for t in non_routable).items())}
    require(fano_reuse["width_counts"] == width_counts_16 == {"7": 2, "8": 7, "9": 6, "10": 1},
            "fano-reuse-certificate.json width_counts mismatch")
    require(len(fano_reuse["cases"]) == 16, "fano-reuse-certificate.json case count mismatch")

    observed_r9 = []
    for expected_topo, cert_case in zip(non_routable, fano_reuse["cases"]):
        require(cert_case["topology"] == expected_topo, "fano-reuse-certificate topology mismatch")
        se = cert_case["scalar_exhaustion"]
        require(se["W"] == expected_topo["W"] and se["prescribed"] == expected_topo["prescribed"],
                "scalar_exhaustion W/prescribed mismatch")
        require(se["exists"] is False and se["exhaustive_negative"] is True and se["witness"] is None,
                "scalar_exhaustion negative status mismatch")
        require(se["gates"] == 14 and se["split"] == 7
                and se["prefix_assignments"] == 279936 and se["suffix_assignments"] == 279936
                and se["full_assignment_count"] == 6 ** 14 == 78364164096,
                "scalar_exhaustion assignment count mismatch")
        require(re.fullmatch(r"[0-9a-f]{64}", se["prefix_sha256"]) is not None
                and re.fullmatch(r"[0-9a-f]{64}", se["suffix_sha256"]) is not None,
                "invalid prefix/suffix sha256 in scalar_exhaustion")
        observed_r9.append((expected_topo["id"], expected_topo["W"]))
    require(observed_r9 == r9_cases, "Round-9 replay log 16 Fano cases do not match fano-reuse-certificate.json")

    expected_w_by_id = {t["id"]: t["W"] for t in non_routable}
    vector_summary = {}
    for name, k, canonical, expected_unsat, expected_unknown in (
        ("vector-k2.json", 2, False, 16, 0),
        ("vector-k3.json", 3, False, 13, 3),
        ("vector-k3-canonical.json", 3, True, 16, 0),
        ("vector-k4.json", 4, False, 5, 11),
        ("vector-k4-canonical.json", 4, True, 16, 0),
    ):
        rows = vector_receipts[name]
        require(isinstance(rows, list) and len(rows) == 16, "vector receipt length mismatch: " + name)
        require(tuple(r["case_id"] for r in rows) == OBSTRUCTION_CASE_IDS,
                "vector receipt case_id order mismatch: " + name)
        unsat_count = 0
        unknown_count = 0
        for r in rows:
            require(r["block"] == k and r["W"] == k * expected_w_by_id[r["case_id"]],
                    "vector receipt block/W mismatch: " + name)
            require(r["status"] in ("unsat", "unknown"), "unexpected vector receipt status: " + name)
            if r["status"] == "unsat":
                unsat_count += 1
            else:
                require(r.get("reason") == "timeout", "unknown vector receipt missing timeout reason: " + name)
                unknown_count += 1
            if canonical:
                require(r.get("canonical_internal_edge_bases") is True,
                        "missing canonical_internal_edge_bases flag: " + name)
        require((unsat_count, unknown_count) == (expected_unsat, expected_unknown),
                "vector receipt unsat/unknown counts mismatch: " + name)
        vector_summary[name] = {"unsat": unsat_count, "unknown": unknown_count}

    return {
        "direct_full_word_controls": direct_count,
        "topologies_enumerated": 87,
        "topology_specification_sha256": topo_sha,
        "all_permutations_width_counts": width_counts_all,
        "obstruction_preserving_topologies": 16,
        "obstruction_case_ids": list(OBSTRUCTION_CASE_IDS),
        "obstruction_width_counts": width_counts_16,
        "vector_receipts": vector_summary,
    }


def check_accounting(payloads, raw_187, raw_193, raw_bf193, raw_fc193, live_fc, r9_cases):
    source_manifest = loads(payloads[PKG_DIR + "/SOURCE.json"])
    expected_manifest_files = {
        path[len(PKG_DIR) + 1:]: hashlib.sha256(raw).hexdigest()
        for path, raw in sorted(payloads.items())
        if path.startswith(PKG_DIR + "/") and path != PKG_DIR + "/SOURCE.json"
    }
    require(len(expected_manifest_files) == 27 and source_manifest["files"] == expected_manifest_files,
            "PR203 SOURCE.json 27-file SHA256 manifest mismatch")

    in_187 = loads(payloads[PKG_DIR + "/inputs/bit-pr187.json"])
    in_193 = loads(payloads[PKG_DIR + "/inputs/complex-pr193.json"])
    ref_source = loads(payloads[PKG_DIR + "/references/SOURCE.json"])
    check_upstream_provenance(in_187, in_193, ref_source, raw_187, raw_193, raw_bf193, raw_fc193, live_fc)

    saved_ceiling = loads(payloads[PKG_DIR + "/ceiling-certificate.json"])
    recomputed_ceiling = recompute_ceiling_certificate(in_193, in_187)
    require(saved_ceiling == recomputed_ceiling, "recomputed ceiling-certificate.json differs from saved certificate")

    saved_center = loads(payloads[PKG_DIR + "/center-basis-certificate.json"])
    recomputed_center = recompute_center_basis_certificate()
    require(saved_center == recomputed_center,
            "recomputed center-basis-certificate.json differs from saved certificate")

    triangular_controls = check_triangular_obstruction_controls()

    enum_ctrl = loads(payloads[PKG_DIR + "/enumeration-controls.json"])
    fano_all = loads(payloads[PKG_DIR + "/fano-all-permutations.json"])
    fano_reuse = loads(payloads[PKG_DIR + "/fano-reuse-certificate.json"])
    vector_receipts = {
        name: loads(payloads[PKG_DIR + "/discovery/receipts/" + name])
        for name in (
            "vector-k2.json",
            "vector-k3.json",
            "vector-k3-canonical.json",
            "vector-k4.json",
            "vector-k4-canonical.json",
        )
    }
    fano_summary = check_fano_certificates(enum_ctrl, fano_all, fano_reuse, vector_receipts, r9_cases)

    cp193, bp187 = saved_ceiling["checkpoints"]
    odd_ext = saved_ceiling["odd_cube_extension"]
    return {
        "package_manifest_files_verified": len(expected_manifest_files),
        "checkpoints": {
            "complex_pr193_retained_loss_a_ceiling": cp193["retained_loss_a_ceiling"],
            "complex_pr193_free_center_a_ceiling": cp193["free_center_a_ceiling"],
            "bit_pr187_retained_loss_a_ceiling": bp187["retained_loss_a_ceiling"],
            "bit_pr187_free_center_a_ceiling": bp187["free_center_a_ceiling"],
        },
        "odd_cube_family": {
            "finite_cases": odd_ext["finite_cases"],
            "positive_deficit_cases": odd_ext["positive_deficit_cases"],
            "finite_scan_sha256": odd_ext["finite_scan_sha256"],
            "best_optimistic_p_d": [
                odd_ext["best_optimistic_case"]["p"],
                odd_ext["best_optimistic_case"]["degree"],
            ],
            "best_optimistic_a_ceiling": odd_ext["best_optimistic_case"]["a_ceiling"],
            "strict_global_a_ceiling": odd_ext["strict_global_a_ceiling"],
            "best_arbitrary_local_chains_p_d": [
                odd_ext["best_arbitrary_local_chains_case"]["p"],
                odd_ext["best_arbitrary_local_chains_case"]["degree"],
            ],
            "best_arbitrary_local_chains_a_ceiling": (
                odd_ext["best_arbitrary_local_chains_case"]["arbitrary_local_chains_a_ceiling"]
            ),
            "strict_arbitrary_local_chains_a_ceiling": odd_ext["strict_arbitrary_local_chains_a_ceiling"],
            "all_degrees_tail_a_ceiling": odd_ext["all_degrees_tail_a_ceiling"],
            "local_identity_degrees": [row["degree"] for row in odd_ext["local_identity_checks"]],
            "star_span_cases": len(odd_ext["star_span_checks"]),
        },
        "center_basis": {
            "sharp_example_ps": [row["p"] for row in saved_center["sharp_examples"]],
            "p5_nonzero_ternary_vectors_checked": saved_center["finite_sweep"]["nonzero_vectors_checked"],
            "p5_support_rank_floor": saved_center["finite_sweep"]["certified_support_rank_floor"],
            "p4_excluded_domain_support_rank": saved_center["excluded_domain_control"]["support_rank"],
        },
        "triangular_flag_controls_verified": triangular_controls,
        "fano_screen": fano_summary,
    }


def external_inputs():
    pins = loads((HERE / "SOURCES.json").read_bytes())
    require(pins["base_commit"] == BASE, "wrong research base")
    rows = {row["path"]: row for row in pins["files"] if row["usage"] == "input"}
    require(set(rows) == set(INPUTS), "external input coverage changed")
    loaded = {}
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == rows[path]["sha256"], "external source drift: " + path)
        require(git_id("blob", raw) == rows[path]["git_blob"], "external blob drift: " + path)
        loaded[path] = raw
    archive_next100 = loads(loaded["research/community-reconciliation-next100-audit/ARCHIVE.json"])
    reviews_next100 = loads(loaded["research/community-reconciliation-next100-audit/REVIEW.json"])
    archive_92 = loads(loaded["research/community-reconciliation92-audit/ARCHIVE.json"])
    reviews_92 = loads(loaded["research/community-reconciliation92-audit/REVIEW.json"])
    r9_cases = parse_round9_log(loaded["research/community-round9-audit/pr203-replay.log.txt"].decode("utf-8"))
    r9_ledger = loads(loaded["research/community-round9-audit/review-ledger.json"])
    live_fc = loaded["scripts/experiments/fano_completion.py"]
    contributors = (
        (ROOT / "CONTRIBUTORS.md").read_text(encoding="utf-8")
        if (ROOT / "CONTRIBUTORS.md").is_file()
        else None
    )
    return archive_92, reviews_92, archive_next100, reviews_next100, r9_ledger, r9_cases, live_fc, contributors


def verify(document, archive_92, reviews_92, archive_next100, reviews_next100,
           r9_ledger, r9_cases, live_fc, contributors=None):
    proof = Proof(document)
    mb_tree, _ = proof.commit(MERGE_BASE)
    pr203_tree, pr203_parents = proof.commit(PR203)
    require(pr203_parents == [MERGE_BASE], "PR203 comparison parent changed")

    _, pkg_203 = proof.resolve(PR203, PKG_DIR, "40000")
    require(pkg_203 == PKG_TREE, "PR203 percent-exponent-architecture tree mismatch")
    _, wf_203 = proof.resolve(PR203, PKG_WORKFLOW, "100644")
    require(wf_203 == PKG_WORKFLOW_BLOB, "PR203 workflow blob mismatch")

    direct_files = {PKG_WORKFLOW: {"mode": "100644", "blob": wf_203}}
    for path, row in proof.inventory(pkg_203).items():
        direct_files[PKG_DIR + "/" + path] = row
    require(len(direct_files) == 29 and direct_files == document["files"],
            "incomplete or changed PR203 29-file inventory")

    diff_full = proof.difference(mb_tree, pr203_tree)
    expected_full = {path: {"before": None, "after": row} for path, row in direct_files.items()}
    require(len(diff_full) == 29 and diff_full == expected_full,
            "PR203 merge-base diff differs from the 29 package and workflow files")

    a92_tree, a92_parents = proof.commit(ARCHIVE_92)
    require(archive_92["commit"] == ARCHIVE_92 and archive_92["tree"] == a92_tree
            and archive_92["parents"] == a92_parents,
            "reconciliation92 archive receipt does not match its Git commit")
    require(PR187 in a92_parents, "PR187 absent from reconciliation92 archive parents")
    require(reviews_92["187"]["head"] == PR187 and reviews_92["187"]["contributor"]["login"] == "rohanarun",
            "reconciliation92 review #187 head or contributor mismatch")

    anext_tree, anext_parents = proof.commit(ARCHIVE_NEXT100)
    require(archive_next100["commit"] == ARCHIVE_NEXT100 and archive_next100["tree"] == anext_tree
            and archive_next100["parents"] == anext_parents,
            "next100 archive receipt does not match its Git commit")
    for parent in (PR193, PR204, PR288):
        require(parent in anext_parents, "expected parent absent from next100 archive: " + parent)
    for pr_num, (head, login) in (
        ("193", (PR193, "ikeboy")),
        ("204", (PR204, "maxime-fleury")),
        ("288", (PR288, "eumemic")),
    ):
        require(reviews_next100[pr_num]["head"] == head, f"next100 review #{pr_num} refers to a different head")
        require(reviews_next100[pr_num]["contributor"]["login"] == login,
                f"next100 review #{pr_num} contributor mismatch")

    r9_prs = r9_ledger["prs"]
    r9_rows = [row for row in (r9_prs.values() if isinstance(r9_prs, dict) else r9_prs) if row.get("number") == 203]
    require(len(r9_rows) == 1, "missing PR203 entry in Round-9 review ledger")
    r9_203 = r9_rows[0]
    require(r9_203["head"] == PR203 and r9_203["author"] == "huxint",
            "Round-9 ledger PR203 head or author mismatch")
    require(r9_203["disposition"] == "scoped-replay-passed"
            and r9_203["evidence"] == ["pr203-replay.log.txt"],
            "Round-9 ledger PR203 disposition or evidence mismatch")
    require(sorted(r9_203["source_files"]) == sorted(diff_full),
            "Round-9 ledger PR203 source_files mismatch")

    _, notice_203 = proof.resolve(PR203, PKG_DIR + "/NOTICE", "100644")
    require(notice_203 == NOTICE_BLOB, "PR203 NOTICE blob mismatch")
    require(proof.raw(notice_203, "blob") == (HERE / "UPSTREAM-NOTICE").read_bytes(),
            "original notice was not retained exactly in UPSTREAM-NOTICE")

    _, b187 = proof.resolve(PR187, PR187_PHYSICAL_PATH, "100644")
    require(b187 == PR187_PHYSICAL_BLOB, "PR187 emitted-physical.json blob mismatch")
    raw_187 = proof.raw(b187, "blob")

    _, b193 = proof.resolve(PR193, PR193_CERT_PATH, "100644")
    require(b193 == PR193_CERT_BLOB, "PR193 certificate.json blob mismatch")
    raw_193 = proof.raw(b193, "blob")

    _, bf193 = proof.resolve(PR193, PR193_BALANCED_FANO_PATH, "100644")
    require(bf193 == PR193_BALANCED_FANO_BLOB, "PR193 balanced_fano.py blob mismatch")
    raw_bf193 = proof.raw(bf193, "blob")

    _, fc193 = proof.resolve(PR193, FANO_COMPLETION_PATH, "100644")
    require(fc193 == FANO_COMPLETION_BLOB, "PR193 fano_completion.py blob mismatch")
    raw_fc193 = proof.raw(fc193, "blob")

    payloads = {path: proof.raw(row["blob"], "blob") for path, row in direct_files.items()}
    total_bytes = sum(len(raw) for raw in payloads.values())
    require(total_bytes == 195812, "PR203 total payload byte size mismatch")

    accounting = check_accounting(payloads, raw_187, raw_193, raw_bf193, raw_fc193, live_fc, r9_cases)
    if contributors is not None:
        require("https://github.com/CrocSwap/integer-mult-bounds/pull/203" in contributors
                and "research/pr203-retention-receipt/README.md" in contributors,
                "CONTRIBUTORS.md missing PR203 attribution or receipt link")
    require(proof.used == set(proof.objects), "unused evidence objects")

    return {
        "status": "PASS_PR203_RETENTION_AND_CERTIFICATE_RECONCILIATION",
        "base_commit": BASE,
        "merge_base": MERGE_BASE,
        "original_pr203_head": PR203,
        "upstream_pr187_head": PR187,
        "upstream_pr193_head": PR193,
        "archive_reconciliation92_commit": ARCHIVE_92,
        "archive_next100_commit": ARCHIVE_NEXT100,
        "package_tree": PKG_TREE,
        "workflow_blob": PKG_WORKFLOW_BLOB,
        "total_changed_paths": len(diff_full),
        "total_payload_bytes": total_bytes,
        "authenticated_git_objects": len(proof.used),
        "accounting": accounting,
        "fresh_cpp_or_solver_replay": False,
        "new_kappa_claim": False,
        "scope": "Complete PR203 29-file source retention, upstream PR187/PR193 input authentication, and exact ceiling/center-basis/Fano certificate reconciliation; no new construction acceptance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=HERE / "SOURCE-PROOF.json")
    parser.add_argument("--write-result", type=Path,
                        help="write a newly recomputed receipt instead of comparing RESULT.json")
    args = parser.parse_args()
    result = verify(loads(args.proof.read_bytes()), *external_inputs())
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        require(result == loads((HERE / "RESULT.json").read_bytes()), "saved result differs from recomputation")
    acc = result["accounting"]
    print(f"{result['status']} paths={result['total_changed_paths']} bytes={result['total_payload_bytes']} "
          f"odd_cube={acc['odd_cube_family']['finite_cases']} "
          f"center_sweep={acc['center_basis']['p5_nonzero_ternary_vectors_checked']} "
          f"fano_topos={acc['fano_screen']['topologies_enumerated']}")


if __name__ == "__main__":
    main()
