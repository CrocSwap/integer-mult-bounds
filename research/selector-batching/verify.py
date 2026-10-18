#!/usr/bin/env python3
"""Exact, volume-aware selector batching experiment. Apache-2.0.

Prepared by Greer Guthrie with substantial OpenAI Codex assistance.
This checks finite identities and a bound comparison, not a multiplication theorem.
No implementation from the supplier's Clifford checker is imported.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
SEED = 22
SUPPLIER = "research/complex-k492-owner-repair/data/SPEC.json"
PROGRAM = ("research/community-k492-audit/pr626/replay/mixed-global/base/"
           "providers/jp8/LOCAL-PROGRAMS.json.gz")
STATUS = "PASS_SELECTOR_BATCHING_IDENTITIES_AND_VOLUME_OBSTRUCTION"


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def source_bytes(root, relative, pin):
    data = (root / relative).read_bytes()
    if pin["representation"] == "gzip-payload":
        data = gzip.decompress(data)
    else:
        require(pin["representation"] == "file-bytes", "unknown source representation")
    require(hashlib.sha256(data).hexdigest() == pin["sha256"],
            "source pin mismatch: " + relative)
    return data


def check_sources(root):
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    require(pins["base_commit"] == BASE, "wrong base commit")
    return {name: source_bytes(root, name, pin) for name, pin in pins["files"].items()}


def supplier_reference(sources):
    spec = json.loads(sources[SUPPLIER])
    programs = json.loads(sources[PROGRAM])
    profiles = {}
    for orientation, events in sorted(programs.items()):
        # These are the two paid event forms emitted by hpe_emit_local.py.
        profile = Counter()
        for event in events:
            if event[0] == "climb":
                require(len(event) == 6, "malformed climb")
                profile[event[5]] += 1
            elif event[0] == "center":
                require(len(event) == 5, "malformed center")
                profile[event[4]] += 1
        profile = dict(sorted(profile.items()))
        require(profile == {int(r): count for r, count in
                            spec["providers"]["jp8"]["expected_profile"].items()},
                "native paid profile does not match the supplier")
        profiles[orientation] = {str(r): count for r, count in profile.items()}
    require(set(profiles) == {"backward", "forward"}, "missing orientation")
    ranks = sorted(map(int, profiles["forward"]))
    rank = ranks[SEED % len(ranks)]
    events = programs["forward"]
    pairs = []
    for i, event in enumerate(events[:-2]):
        following = events[i + 1]
        if (event[0] == following[0] == "climb" and
                event[-1] == following[-1] == rank and event[4] == following[4]):
            scalar = events[i + 2]
            if (scalar[0] == "scalar" and scalar[1][0] == "add" and
                    {tuple(scalar[1][1]), tuple(scalar[1][2])} ==
                    {("L", event[2]), ("L", following[2])}):
                pairs.append([[i, event], [i + 1, following]])
    require(rank == 2 and len(pairs) == 32, "seed-selected scope drifted")
    pair = pairs[SEED % len(pairs)]
    require([item[0] for item in pair] == [14512, 14513], "selected pair drifted")
    saving = Q(spec["expected"]["complex_lower"])
    require(0 < saving < 1, "invalid saving")
    return {
        "supplier_pr": 626,
        "provider": "jp8",
        "program_payload_sha256": hashlib.sha256(sources[PROGRAM]).hexdigest(),
        "paid_profiles": profiles,
        "eligible_consecutive_pairs": len(pairs),
        "seed_selected_rank": rank,
        "seed_selected_pair": pair,
        "complex_saving": str(saving),
        "sigma": str(1 - saving),
        "accepted_kappa_at_base": spec["expected"]["kappa"],
        "scope": "Reads pinned native receipts; does not rerun the full supplier or assert legal co-scheduling.",
    }


def gaussian_mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


@lru_cache(maxsize=None)
def tensor_entry(n, distance, direction):
    """Independent closed-form Kronecker entry, numerator over 2**n."""
    value = (1, 0)
    for _ in range(n - distance):
        value = gaussian_mul(value, (1, direction))
    for _ in range(distance):
        value = gaussian_mul(value, (1, -direction))
    return value


def coordinate_layer(vector, axis, direction, n, only_padding_from=None):
    """Integer Gaussian butterfly; each step adds one power of two to denominator."""
    out = [(0, 0)] * len(vector)
    bit = 1 << axis
    for i in range(len(vector)):
        if i & bit:
            continue
        j = i | bit
        if only_padding_from is not None and i >> n < only_padding_from:
            out[i] = tuple(2 * a for a in vector[i])
            out[j] = tuple(2 * a for a in vector[j])
            continue
        a, b = vector[i]
        c, d = vector[j]
        # (u+v +/- i(u-v))/2; inverse changes direction from +1 to -1.
        out[i] = (a + c - direction * (b - d), b + d + direction * (a - c))
        out[j] = (a + c + direction * (b - d), b + d - direction * (a - c))
    return out


def run_column(n, s, k, column, direction=1, mutant=None):
    q = 1 << s
    require(n >= 1 and s >= 1 and 1 <= k <= q, "invalid circuit dimensions")
    vector = [(0, 0)] * (1 << (n + s))
    vector[column] = (1, 0)
    denominator = 0
    # C_(n+s) on the joined q-lane array.
    for axis in range(n + s):
        vector = coordinate_layer(vector, axis, direction, n)
        denominator += 1
    # The inverse selector is a paid C_s with sign/phase wrappers.
    if mutant != "omit_selector":
        axes = list(range(n, n + s))
        if mutant == "wrong_selector_axis":
            axes[0] = 0
        for axis in axes:
            sign = direction if mutant == "forward_selector" else -direction
            vector = coordinate_layer(vector, axis, sign, n)
            denominator += 1
    # Padded lanes contain arbitrary dirt, so undo their unwanted C_n.
    if k < q and mutant != "omit_padding_restoration":
        for axis in range(n):
            vector = coordinate_layer(vector, axis, -direction, n, k)
            denominator += 1
    if mutant == "wrong_global_phase":
        vector = [(-b, a) for a, b in vector]
    if mutant == "wrong_normalization":
        vector = [(2 * a, 2 * b) for a, b in vector]
    return vector, denominator


def reference_entry(n, k, row, column, direction):
    row_lane, col_lane = row >> n, column >> n
    if col_lane >= k:
        return ((1 << n, 0) if row == column else (0, 0))
    if row_lane != col_lane:
        return (0, 0)
    return tensor_entry(n, (row ^ column).bit_count(), direction)


def first_mismatch(n, s, k, direction=1, mutant=None):
    for column in range(1 << (n + s)):
        vector, denominator = run_column(n, s, k, column, direction, mutant)
        for row, actual in enumerate(vector):
            expected = reference_entry(n, k, row, column, direction)
            if tuple(a << n for a in actual) != tuple(a << denominator for a in expected):
                return {"column": column, "row": row,
                        "actual_numerator": list(actual), "actual_denominator_power": denominator,
                        "expected_numerator": list(expected), "expected_denominator_power": n}
    return None


def operator_replays():
    # Exhaust every basis column of every case, rather than sample input vectors.
    cases = [(n, s, 1 << s) for n in range(1, 7) for s in (1, 2)]
    cases += [(n, 2, 3) for n in range(1, 5)] + [(8, 1, 2)]
    receipts = []
    for n, s, k in cases:
        size = 1 << (n + s)
        for direction in (1, -1):
            digest = hashlib.sha256()
            for column in range(size):
                vector, denominator = run_column(n, s, k, column, direction)
                for row, actual in enumerate(vector):
                    expected = reference_entry(n, k, row, column, direction)
                    require(tuple(a << n for a in actual) ==
                            tuple(a << denominator for a in expected),
                            f"operator mismatch at {(n, s, k, direction, row, column)}")
                    digest.update(canonical([row, column, list(expected)]))
            # Support is invariant under invertible monomial pre/post maps.
            # C_(n+s) is dense; each desired active row has only 2**n nonzeros.
            require(all(tensor_entry(n + s, d, direction) != (0, 0)
                        for d in range(n + s + 1)), "unexpected zero in tensor kernel")
            receipts.append({"data_axes": n, "selector_axes": s, "active_lanes": k,
                             "direction": direction, "all_columns": size,
                             "dirty_padding_columns": ((1 << s) - k) * (1 << n),
                             "raw_row_support": size, "target_active_row_support": 1 << n,
                             "reference_matrix_sha256": digest.hexdigest()})
    return receipts


def operator_controls():
    controls = []
    for name, n, s, k in [
        ("omit_selector", 2, 1, 2),
        ("forward_selector", 2, 1, 2),
        ("wrong_selector_axis", 2, 1, 2),
        ("wrong_global_phase", 2, 1, 2),
        ("wrong_normalization", 2, 1, 2),
        ("omit_padding_restoration", 2, 2, 3),
    ]:
        witness = first_mismatch(n, s, k, mutant=name)
        require(witness is not None, "invalid operator accepted: " + name)
        if name == "omit_padding_restoration":
            require(witness["column"] >= k * (1 << n), "dirty control missed dirty input")
        controls.append({"name": name, "rejected_by": "full operator identity", "witness": witness})
    return controls


@lru_cache(maxsize=None)
def log_bounds(x):
    """Exact atanh-series bounds, reduced to [1,2]; no floating point."""
    require(x > 0, "log domain")
    if x < 1:
        lo, hi = log_bounds(1 / x)
        return -hi, -lo
    shifts = 0
    while x > 2:
        x /= 2
        shifts += 1
    t = (x - 1) / (x + 1)
    count = 40
    lo = 2 * sum((t ** (2 * j + 1) / (2 * j + 1) for j in range(count)), Q(0))
    hi = lo + 2 * t ** (2 * count + 1) / ((2 * count + 1) * (1 - t * t))
    if shifts:
        a, b = log_bounds(Q(2))
        lo += shifts * a
        hi += shifts * b
    return lo, hi


def exp_bounds(x):
    if x < 0:
        lo, hi = exp_bounds(-x)
        return 1 / hi, 1 / lo
    count = 60
    require(x < count + 2, "exp tail bound outside its domain")
    term = total = Q(1)
    for j in range(1, count + 1):
        term = term * x / j
        total += term
    next_term = term * x / (count + 1)
    return total, total + next_term / (1 - x / (count + 2))


@lru_cache(maxsize=None)
def power_bounds(base, exponent):
    require(base > 0 and 0 <= exponent <= 1, "power domain")
    if exponent == 0:
        return Q(1), Q(1)
    if exponent == 1:
        return base, base
    lo, hi = log_bounds(base)
    return exp_bounds(exponent * lo)[0], exp_bounds(exponent * hi)[1]


def compact_interval(bounds):
    lo, hi = bounds
    grid = 10 ** 24
    lower = (lo.numerator * grid) // lo.denominator
    upper = -((-hi.numerator * grid) // hi.denominator)
    require(lower <= upper, "reversed interval")
    return {"lower": str(Q(lower, grid)), "upper": str(Q(upper, grid))}


def bill(n, s, k):
    q = 1 << s
    # Weights are volumes in units of ONE original lane's volume V.
    return {"data_axes": n, "selector_axes": s, "active_lanes": k,
            "joined_volume_over_V": q,
            "calls": [[q, n + s, "joined transform"], [q, s, "inverse selector"]] +
                     ([[q - k, n, "dirty padding restoration"]] if q > k else [])}


def check_bill(invoice):
    n, s, k = (invoice[name] for name in ("data_axes", "selector_axes", "active_lanes"))
    require(n >= 1 and s >= 1 and 1 <= k <= 1 << s, "bad bill dimensions")
    # Independently check each operation's domain cardinality against the input
    # lanes. In particular the joined operator acts on every selector value.
    lanes = len(range(1 << s))
    require(invoice["joined_volume_over_V"] == lanes, "joined array volume omitted")
    calls = {why: (volume, width) for volume, width, why in invoice["calls"]}
    require(len(calls) == len(invoice["calls"]), "duplicate call type")
    required = {"joined transform", "inverse selector"}
    if k < lanes:
        required.add("dirty padding restoration")
    require(set(calls) == required, "required operator omitted from bill")
    require(calls["joined transform"] == (lanes, n + s), "wrong joined transform domain")
    require(calls["inverse selector"] == (lanes, s), "wrong inverse selector domain")
    if k < lanes:
        require(calls["dirty padding restoration"] == (lanes - k, n),
                "wrong dirty restoration domain")


def ratio_bounds(n, s, k, sigma):
    invoice = bill(n, s, k)
    check_bill(invoice)
    lo = hi = Q(0)
    for volume, width, _ in invoice["calls"]:
        a, b = power_bounds(Q(width, n), sigma)
        lo += Q(volume, k) * a
        hi += Q(volume, k) * b
    return lo, hi


def budget_certificate(sigma):
    # At sigma=1/2, square the endpoints to independently validate the engine.
    for base in (Q(1, 2), Q(3, 2), Q(2), Q(5)):
        lo, hi = power_bounds(base, Q(1, 2))
        require(0 < lo <= hi and lo * lo <= base <= hi * hi, "sqrt enclosure failed")
    correct = ratio_bounds(2, 1, 2, sigma)
    naive = (correct[0] / 2, correct[1] / 2)
    require(naive[1] < 1 < correct[0], "false-saving control did not separate")
    fixed = []
    for f in (1, 2, 4, 8, 16, 32, 128, 1024):
        ratio = ratio_bounds(2 * f, 1, 2, sigma)
        require(ratio[0] > 1, "fixed-lane budget unexpectedly improves")
        fixed.append({"f": f, "bill": bill(2 * f, 1, 2), "ratio_to_original": compact_interval(ratio)})
    scaled = []
    for f in range(1, 9):
        ratio = ratio_bounds(2 * f, f, 2, sigma)
        require(ratio[0] > 1, "slot-scaled selector budget unexpectedly improves")
        scaled.append({"f": f, "bill": bill(2 * f, f, 2), "ratio_to_original": compact_interval(ratio)})
    mutations = []
    for name in ("omit_volume_factor", "omit_selector_cost", "omit_dirty_restoration"):
        invoice = bill(2, 2, 3) if name == "omit_dirty_restoration" else bill(2, 1, 2)
        if name == "omit_volume_factor":
            invoice["joined_volume_over_V"] = 1
            invoice["calls"] = [[1, width, why] for _, width, why in invoice["calls"]]
        else:
            omitted = "inverse selector" if name == "omit_selector_cost" else "dirty padding restoration"
            invoice["calls"] = [call for call in invoice["calls"] if call[2] != omitted]
        try:
            check_bill(invoice)
        except VerificationError:
            mutations.append(name)
        else:
            raise VerificationError("invalid bill accepted: " + name)
    return {"sigma": str(sigma), "f1_original_profile": {"2": 2},
            "f1_incorrect_unweighted_profile": {"1": 1, "3": 1},
            "f1_volume_weighted_profile": {"1": 2, "3": 2},
            "f1_naive_ratio": compact_interval(naive), "f1_complete_ratio": compact_interval(correct),
            "f1_even_if_selector_is_free": compact_interval(power_bounds(Q(3, 2), sigma)),
            "fixed_two_lanes": fixed, "two_lanes_with_slot_scaled_selector": scaled,
            "bill_mutations_rejected": mutations,
            "interpretation": "Comparison of inherited cost bounds, not a lower bound on actual algorithms."}


def make_certificate(root):
    sources = check_sources(root)
    reference = supplier_reference(sources)
    replays = operator_replays()
    controls = operator_controls()
    budget = budget_certificate(Q(reference["sigma"]))
    return {"schema": "selector-batching/1", "status": STATUS, "base_commit": BASE,
            "assignment_seed": SEED, "supplier_reference": reference,
            "operator_replays": replays,
            "total_exact_columns": sum(r["all_columns"] for r in replays),
            "total_exact_matrix_entries": sum(r["all_columns"] ** 2 for r in replays),
            "total_dirty_padding_columns": sum(r["dirty_padding_columns"] for r in replays),
            "operator_mutations_rejected": controls, "budget": budget,
            "scope": "Finite exact evidence plus the written all-size bound comparison in README.md; no new kappa or full theorem verification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--output", type=Path, help="write an identical receipt to a new file after verification")
    args = parser.parse_args()
    certificate = make_certificate(args.repo_root.resolve())
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(certificate == expected, "recomputed certificate differs from CERTIFICATE.json")
    if args.output:
        with args.output.open("x") as handle:
            json.dump(certificate, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(STATUS)
    print(f"{len(certificate['operator_replays'])} full operator cases; "
          f"{certificate['total_exact_columns']} exact columns; "
          f"{certificate['total_dirty_padding_columns']} dirty padding columns; "
          "6 operator and 3 invoice mutations rejected")


if __name__ == "__main__":
    main()
