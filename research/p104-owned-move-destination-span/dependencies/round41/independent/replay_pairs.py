"""Independent exact determinant audit of #7277 two-donor opportunities."""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
import time

WORD = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
CORE = "fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def checked(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"Unexpected SHA-256 for {path.name}")
    return raw


def span(target, first, second):
    dt, z = target
    dx, x = first
    dy, y = second
    assert x and y
    i = min(x)
    xi, yi, zi = x[i], y.get(i, 0), z.get(i, 0)
    donor_support = x.keys() | y.keys()
    pivot = next(((j, d) for j in sorted(donor_support)
                  if (d := xi*y.get(j, 0) - x.get(j, 0)*yi)), None)
    if pivot is None:
        # Since xi is nonzero, all minors involving i vanish iff y is proportional to x.
        if any(xi*z.get(k, 0) != zi*x.get(k, 0) for k in x.keys() | z.keys()):
            return 1, None
        y_over_x = Fraction(yi*dx, xi*dy)
        z_over_x = Fraction(zi*dx, xi*dt)
        b = Fraction(1)
        if z_over_x == y_over_x:
            b = Fraction(2)
        return 1, (z_over_x-b*y_over_x, b)
    j, d = pivot
    zj, yj, xj = z.get(j, 0), y.get(j, 0), x.get(j, 0)
    a_num, b_num = zi*yj-zj*yi, xi*zj-xj*zi
    if any(d*z.get(k, 0) != a_num*x.get(k, 0)+b_num*y.get(k, 0)
           for k in donor_support | z.keys()):
        return 2, None
    return 2, (Fraction(a_num*dx, d*dt), Fraction(b_num*dy, d*dt))


def observer(records):
    def visit(index, role, source, dest, paid_rank, charts, rows, live):
        available = [r for r, chart in enumerate(charts) if r != role and chart == dest]
        donors = [r for r in available if rows[r][1]]
        pairs = dependent = 0
        hits = []
        for a, b in combinations(donors, 2):
            pairs += 1
            rank, coeff = span(rows[role], rows[a], rows[b])
            dependent += rank == 1
            if coeff is not None:
                hits.append({"donors": [a,b], "donor_rank": rank, "coefficients": list(map(str, coeff))})
        records.append({
            "literal_index": index, "role": role, "from": source, "to": dest, "paid_rank": paid_rank,
            "destination_live_roles": len(available), "nonzero_donors": len(donors),
            "zero_donors": len(available)-len(donors), "pairs": pairs,
            "dependent_pairs": dependent, "matches": hits,
        })
    return visit


def controls():
    first = (3, {0:2, 1:-1, 2:1})
    second = (5, {0:1, 1:2, 2:-2})
    target = (15, {0:7, 1:-11, 2:11})
    assert span(target, first, second) == (2, (Fraction(1), Fraction(-1)))
    wrong = (15, {0:7, 1:-11, 2:-11})
    assert span(wrong, first, second) == (2, None)
    dependent = (3, {0:-4, 1:2, 2:-2})
    assert span(target, first, dependent) == (1, None)
    assert span(first, first, dependent) == (1, (Fraction(3), Fraction(1)))
    return {"positive_signed_coefficients": ["1", "-1"],
            "same_support_sign_mutation_rejected": True, "dependent_positive_and_negative": True}


def main():
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--cap", default=26, type=float)
    args = parser.parse_args()
    assert 0 < args.cap <= 26
    core = Path(__file__).resolve().with_name("replay_core.py")
    checked(core, CORE)
    replay = runpy.run_path(str(core))["audit"]
    word = json.loads(gzip.decompress(checked(args.word, WORD)))
    records = []
    result = replay(word, start, args.cap, observer(records))
    assert len(records) == result["paid_owned_moves"]
    payload = {
        **result, "scientific_head": HEAD, "word_sha256": WORD, "replay_core_sha256": CORE,
        "sites_with_pairs": sum(r["pairs"] > 0 for r in records),
        "two_donor_pairs": sum(r["pairs"] for r in records),
        "rank_one_pairs": sum(r["dependent_pairs"] for r in records),
        "matches": sum(len(r["matches"]) for r in records),
        "fallback_sites_with_three_or_more_donors": sum(r["nonzero_donors"] >= 3 for r in records),
        "fallback_whole_rank_upper_before_new_work": 17*sum(
            r["paid_rank"] for r in records if r["nonzero_donors"] >= 3),
        "fallback_bound_complete": result["scope_exhausted"],
        "controls": controls(), "records": records,
    }
    if result["scope_exhausted"]:
        assert (len(records), payload["sites_with_pairs"], payload["two_donor_pairs"]) == (47, 44, 2767)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
