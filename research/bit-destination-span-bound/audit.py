"""Independent per-MOVE GF(2) dual and signed invoice replay."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
INVOICE = "research/paired-query-only-bit/EFREE-RESULT.json"
KAPPA = F(10018846261809, 2500000000000000)
GRID = 10**50


def authenticate(root):
    manifest = HERE / "SOURCES.tsv"
    pins, data = {}, {}
    for line in manifest.read_text().splitlines():
        key, expected, _ = line.split("\t")
        name = Path(key)
        if name.is_absolute() or ".." in name.parts or key in pins:
            raise ValueError(f"ambiguous input path {key}")
        raw = (root / name).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f"changed source {key}")
        pins[key], data[key] = expected, raw
    return pins, json.loads(gzip.decompress(data[WORD])), json.loads(data[INVOICE])


def separating_dual(library, target):
    """Find a linear functional that annihilates the library and hits target."""
    pivots = {}
    for row in library:
        reduced = set(row)
        while reduced:
            key = min(reduced)
            if key not in pivots:
                pivots[key] = reduced
                break
            reduced ^= pivots[key]
    remainder = set(target)
    for p, row in sorted(pivots.items()):
        if p in remainder:
            remainder ^= row
    if not remainder:
        return None, len(pivots)
    free = min(remainder)
    assert free not in pivots
    dual = {free}
    for p, row in sorted(pivots.items(), reverse=True):
        if len(row & dual) & 1:
            dual.add(p)
    assert all(not (len(row & dual) & 1) for row in library)
    assert len(target & dual) & 1
    return sorted(dual), len(pivots)


def control():
    lib = [{0, 1}, {0, 2}]
    assert separating_dual(lib, {1, 2}) == (None, 2)
    assert separating_dual(lib, {0}) == ([0, 1, 2], 2)
    assert separating_dual([], set()) == (None, 0)


def census(word):
    n = word["public"]
    frames = [*word["start"], *([None] * word["owned_fields"])]
    values = [frozenset([j]) if j < n else frozenset() for j in range(len(frames))]
    live = defaultdict(dict)
    for i, (frame, row) in enumerate(zip(frames, values, strict=True)):
        if frame is not None:
            live[frame][i] = row
    rank = {int(f): d["dim"] for f, d in word["frames"].items()}
    library_sizes, library_ranks, paid, removed = (Counter() for _ in range(4))
    duals, members = [], []

    def place(i, frame, value):
        if frames[i] is not None:
            del live[frames[i]][i]
        frames[i], values[i] = frame, value
        if frame is not None:
            live[frame][i] = value

    for t, (op, i, *rest) in enumerate(word["program"]):
        if op == "MOVE":
            src, dst = rest
            assert frames[i] == src and i not in live[dst]
            library = tuple(live[dst].values())
            dual, span_rank = separating_dual(library, values[i])
            library_sizes[len(library)] += 1
            library_ranks[span_rank] += 1
            r = abs(rank[src] - rank[dst])
            paid[r] += 1
            if dual is None:
                members.append(t)
                removed[r] += 1
            else:
                duals.append([t, i, dst, dual])
            place(i, dst, values[i])
        elif op == "ADD":
            j, frame = rest
            assert frames[i] == frames[j] == frame
            place(i, frame, values[i] ^ values[j])
        elif op == "SWAP":
            (j,) = rest
            first, second = (frames[i], values[i]), (frames[j], values[j])
            place(i, *second)
            place(j, *first)
        elif op == "INIT":
            assert frames[i] is None and i >= n
            place(i, rest[0], frozenset())
        else:
            assert op == "CLEAR" and frames[i] == rest[0] and i >= n
            place(i, None, frozenset())
    assert frames == word["final"] + [None]*word["owned_fields"]
    expected = [frozenset([j]) if j < n else frozenset() for j in range(len(frames))]
    for i in range(111):
        expected[i+111] = frozenset([i, i+111])
    assert values == expected
    assert len(duals) + len(members) == sum(paid.values()) == 2871
    return duals, members, library_sizes, library_ranks, paid, removed


def floor(x):
    return F((x*GRID).numerator // (x*GRID).denominator, GRID)


def ceil(x):
    return -floor(-x)


@cache
def natural_log(x):
    z = (x-1)/(x+1)
    term, lower = 2*z, F(0)
    for i in range(55):
        lower += term / (2*i+1)
        term *= z*z
    return floor(lower), ceil(lower + term/(111*(1-z*z)))


def exp_bounds(x):
    term, total = F(1), F(1)
    for j in range(1, 34):
        term *= x/j
        total += term
    tail = (term*x/34)/(1-x/35)
    return total, total+tail


@cache
def power(rank):
    e = rank.bit_length() - 1
    lo, hi = natural_log(F(rank, 2**e))
    log2_lo, log2_hi = natural_log(F(2))
    lo, hi = KAPPA*(lo+e*log2_lo), KAPPA*(hi+e*log2_hi)
    assert 0 <= lo <= hi < 1
    return floor(rank/exp_bounds(hi)[1]), ceil(rank/exp_bounds(lo)[0])


def signed_price(coeffs):
    lo = hi = F(0)
    for rank, n in coeffs.items():
        interval = [n*v for v in power(rank)]
        lo += min(interval)
        hi += max(interval)
    return lo, hi


def audit(root, receipt):
    pins, word, invoice = authenticate(root)
    assert invoice["native_source_sha256"] == pins[WORD]
    duals, members, sizes, ranks, paid, removed = census(word)
    expected_moves = [e["clock"] for e in receipt["all_eligible"]]
    if expected_moves != members or receipt["eligible_paid_moves"] != len(members):
        raise ValueError("forged destination membership")
    assert receipt["status"] == "PASS_GLOBAL_DESTINATION_SPAN_UPPER"
    assert receipt["pins"] == pins
    assert receipt["cases_visited"] == 2871 and receipt["physical_sites"] == 0
    assert receipt["removed_rank_counts"] == {str(r): n for r, n in removed.items()}
    assert receipt["target"] == str(KAPPA)

    assert invoice["native_paid"] == {str(r): n for r, n in paid.items()}
    copies = len(invoice["native_instances"])
    assert copies == invoice["native_calls"] == receipt["native_instances"] == 36
    full_paid = Counter({int(r): n for r, n in invoice["paid"].items()})
    full_targets = Counter({int(r): n for r, n in invoice["targets"].items()})
    assert full_paid - Counter({r: copies*n for r, n in paid.items()}) == {
        1: 444, **{r: 444 for r in range(7, 57, 7)}
    }
    native_helpers = Counter(
        word["frames"][str(end)]["dim"] - word["frames"][str(start)]["dim"]
        for start, end in zip(word["start"][222:], word["final"][222:], strict=True)
    )
    assert native_helpers == Counter({int(r): n for r, n in invoice["native_helpers"].items()})
    derived_targets = Counter({r: copies*n for r, n in native_helpers.items()})
    derived_targets.update({**{r: 444 for r in range(8, 65, 7)}, 127: 222})
    assert full_targets == derived_targets
    assert sum(full_paid.values()) == invoice["paid_jobs"] == 107352
    assert sum(full_targets.values()) == invoice["productive_fields"] == 19950
    signed = full_targets.copy()
    signed.subtract(full_paid)
    assert sum(r*n for r,n in signed.items()) == invoice["rank_surplus"] == 1506
    baseline = signed_price(signed)
    saving = signed_price({r: copies*n for r, n in removed.items()})
    net = tuple(x+y for x,y in zip(baseline, saving, strict=True))
    for key, values in (("raw_comparator_net", baseline), ("saving_interval", saving),
                        ("net_after_free_synthesis", net)):
        lo, hi = map(F, receipt[key])
        assert max(lo, values[0]) <= min(hi, values[1])
    if net[1] < 0:
        assert receipt["decision"] == "PIVOT_NEGATIVE_UPPER"
    witness_bytes = (json.dumps(duals, separators=(",", ":")) + "\n").encode()
    return {
        "status": "PASS_INDEPENDENT_DESTINATION_DUAL_AND_SIGNED_PRICE",
        "pinned_word": pins[WORD], "pinned_invoice": pins[INVOICE],
        "dual_count": len(duals), "member_count": len(members),
        "duals_sha256": sha256(witness_bytes).hexdigest(),
        "destination_library_size_histogram": dict(sizes),
        "destination_library_rank_histogram": dict(ranks),
        "independent_signed_baseline": list(map(str, baseline)),
        "independent_saving": list(map(str, saving)),
        "independent_signed_net": list(map(str, net)),
    }, witness_bytes


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--dual-out", type=Path)
    args = parser.parse_args()
    assert __debug__
    control()
    report, witnesses = audit(args.input_root, json.loads(args.receipt.read_bytes()))
    if args.dual_out is not None:
        with args.dual_out.open("xb") as f:
            f.write(witnesses)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
