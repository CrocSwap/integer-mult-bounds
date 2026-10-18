"""Independent exact proof of the PR525 packing ceiling without fallback charges."""

import hashlib
import itertools
import json
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

SOURCE_COMMIT = "71acd0c35ee81de848316b3f2b4c3bd15b219c51"
M, LIVE, CALLS = 73, 7680, 72
B = Q(6981767, 5000000000)
GRID = 1 << 128
PROFILE = {1: 2537, 2: 192, 3: 506, 4: 88, 5: 298, 6: 68, 7: 1, 8: 17}
WIDTHS = {7: 18, 8: 164, 9: 378}
STOCK = {8: 5760, 16: 3840, 32: 3840, 48: 3840}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def floor_grid(value):
    return Q(value.numerator * GRID // value.denominator, GRID)


def log_series(value):
    """Twenty positive terms of 2*atanh((value-1)/(value+1))."""
    require(Q(1) <= value <= Q(2), "log series domain")
    z = (value - 1) / (value + 1)
    term, total = z, Q(0)
    for k in range(20):
        total += term / (2 * k + 1)
        term *= z * z
    return 2 * total


@lru_cache(None)
def log_lower(value):
    require(value >= 1, "log domain")
    powers = 0
    while value >= 2:
        value /= 2
        powers += 1
    return floor_grid(powers * log_series(Q(2)) + log_series(value))


def exp_lower(value):
    require(value >= 0, "exp domain")
    term, total = Q(1), Q(1)
    for k in range(1, 9):
        term *= value / k
        total += term
    return floor_grid(total)


@lru_cache(None)
def rank_cost_lower(rank, rate=B):
    """Lower bound on r*((73/r)**rate - 1); no fallback term."""
    require(isinstance(rank, int) and 0 <= rank < M, "rank domain")
    require(rate >= 0, "rate domain")
    if rank == 0:
        return Q(0)
    return rank * (exp_lower(rate * log_lower(Q(M, rank))) - 1)


def patterns():
    # Complete enumeration; includes empty bins and zero-remainder bins.
    return [
        (rank, counts, rank - sum(w * n for w, n in zip(WIDTHS, counts)))
        for rank in STOCK
        for counts in itertools.product(*(range(rank // w + 1) for w in WIDTHS))
        if sum(w * n for w, n in zip(WIDTHS, counts)) <= rank
    ]


def check_dual(eta, lam, rate=B):
    require(set(eta) == set(STOCK), "dual rank keys")
    require(set(lam) == set(WIDTHS), "dual width keys")
    rows = patterns()
    require(len(rows) == 112, "pattern count")
    slacks = [
        rank_cost_lower(left, rate) - eta[rank]
        - sum(lam[w] * n for w, n in zip(WIDTHS, counts))
        for rank, counts, left in rows
    ]
    require(min(slacks) >= 0, "dual inequality fails")
    residual_mass = sum(r * n for r, n in STOCK.items()) - CALLS * sum(
        w * n for w, n in WIDTHS.items()
    )
    fixed_mass = CALLS * sum(r * n for r, n in PROFILE.items())
    require(residual_mass == 66240, "remainder mass")
    require(fixed_mass + residual_mass == M * LIVE - 2496, "rank conservation")
    fixed_extra = CALLS * sum(n * rank_cost_lower(r, rate) for r, n in PROFILE.items())
    dual_extra = sum(n * eta[r] for r, n in STOCK.items()) + CALLS * sum(
        n * lam[w] for w, n in WIDTHS.items()
    )
    margin = (fixed_mass + residual_mass + fixed_extra + dual_extra) / (M * LIVE) - 1
    require(margin > 0, "ideal moment does not reject")
    return min(slacks), margin


def audit(profile, certificate):
    require({int(k): v for k, v in profile["profile"].items()} == PROFILE, "local profile")
    require({int(k): v for k, v in profile["widths"].items()} == WIDTHS, "profile widths")
    require({int(k): v for k, v in certificate["helper_widths"].items()} == WIDTHS, "helper widths")
    require({int(k): v for k, v in certificate["rank_stock"].items()} == STOCK, "rank stock")
    require(certificate["calls"] == CALLS, "call count")
    require(certificate["patterns"] == 112, "certificate pattern count")
    require(certificate["remainder_mass"] == 66240, "certificate remainder mass")
    require(Q(certificate["rejected_b"]) == B, "rejected rate")
    require(Q(certificate["kappa_upper"]) == B / (1 + B), "kappa transform")
    # Lower the published multipliers to allow removal of its positive fallback.
    eta = {int(k): Q((Q(v) * 10**9).__floor__(), 10**9)
           for k, v in certificate["dual_rank"].items()}
    lam = {int(k): Q(v) for k, v in certificate["dual_width"].items()}
    minimum_slack, margin = check_dual(eta, lam)
    return {
        "status": "PASS_IDEAL_FIXED_WORD_CEILING",
        "source_commit": SOURCE_COMMIT,
        "rejected_b": str(B),
        "kappa_upper": str(B / (1 + B)),
        "patterns": 112,
        "helper_uses": CALLS * sum(WIDTHS.values()),
        "remainder_mass": 66240,
        "dual_rank": {str(k): str(v) for k, v in sorted(eta.items())},
        "dual_width": {str(k): str(v) for k, v in sorted(lam.items())},
        "minimum_dual_slack": str(minimum_slack),
        "ideal_moment_rejection_margin_lower": str(margin),
        "fallback_charges": "all omitted",
        "construction_scope": "Conditional on the frozen local profile and inventories; no scalar reconstruction.",
    }


def load_inputs(root):
    manifest = json.loads((root / "SOURCES.json").read_bytes())
    require(manifest["commit"] == SOURCE_COMMIT, "source commit")
    files = manifest["files"]
    require(len(files) == 2 and {f["path"] for f in files} == {
        "inputs/profile.json", "inputs/ceiling.json"
    }, "source file set")
    for item in files:
        raw = (root / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source sha256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == item["git_blob"], "source git blob")
    raw_profile = (root / "inputs/profile.json").read_bytes()
    profile = json.loads(raw_profile)
    certificate = json.loads((root / "inputs/ceiling.json").read_bytes())
    require(hashlib.sha256(raw_profile).hexdigest() == certificate["nomination_sha256"], "nomination binding")
    return profile, certificate


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    result = audit(*load_inputs(root))
    require(result == json.loads((root / "EXPECTED.json").read_bytes()), "expected report")
    print(json.dumps(result, indent=2))
