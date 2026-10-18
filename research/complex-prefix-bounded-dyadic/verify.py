"""Exact finite replay of prefix-bounded dyadic circuits; Python 3.11+.

Chris Pagolu, with substantial OpenAI Codex assistance. Apache-2.0.
This checks scalar substitution, not the full multiplication theorem.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import heapq
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from lower import binary_lower, bounded_digits, lower

WORK = ("W", 0)
T, S = ("T", 0), ("S", 0)
PROVIDERS = "research/community-k492-audit/pr626/replay/mixed-global/base/providers"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def check_pins():
    pins = read(HERE / "SOURCES.json")
    for name, pin in pins["files"].items():
        data = (ROOT / name).read_bytes()
        if pin["representation"] == "decompressed":
            data = gzip.decompress(data)
        else:
            need(pin["representation"] == "bytes", "unknown pin representation")
        need(sha(data) == pin["sha256"], "source pin mismatch: " + name)
    reference = pins["vendored_reference"]
    need(sha((HERE / reference["path"]).read_bytes()) == reference["sha256"],
         "vendored PR696 source mismatch")
    selected = read(ROOT / "certificates/selected-result.json")
    assembly = read(ROOT / selected["certificate"])
    need(sha((ROOT / selected["certificate"]).read_bytes()) == selected["certificate_sha256"],
         "selected certificate hash")
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")
    need(selected["kappa"] == assembly["kappa"] == spec["expected"]["kappa"],
         "selected kappa binding")
    return spec


def baseline_cost(op):
    """Literal original emitter formula, counted per real component."""
    if op[0] in ("clear", "copy"):
        return 1
    q = Q(*op[3:5]) if op[0] == "add" else Q(*op[2:4])
    n, d = abs(q.numerator), q.denominator
    if op[0] == "scale":
        return abs(n.bit_length() - d.bit_length()) + int(q < 0)
    return 3 + (n.bit_length() - 1) + n.bit_count() + (d.bit_length() - 1)


def dense_step(matrix, primitive):
    """Three formal inputs; deliberately separate from the sparse full replay."""
    tag, target = primitive[:2]
    i = {T: 0, S: 1, WORK: 2}[target]
    if tag == "clear":
        matrix[i] = [Q(0)] * 3
    elif tag == "copy":
        matrix[i] = matrix[{T: 0, S: 1, WORK: 2}[primitive[2]]].copy()
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        matrix[i] = [factor * x for x in matrix[i]]
    elif tag in ("add", "subtract"):
        j = {T: 0, S: 1, WORK: 2}[primitive[2]]
        factor = 1 if tag == "add" else -1
        matrix[i] = [a + factor * b for a, b in zip(matrix[i], matrix[j])]
    else:
        raise ValueError("unknown primitive")


def check_add(q, word, budget):
    """Weighted prefix domination for arbitrary target, source and dirty work."""
    matrix = [[Q(i == j) for j in range(3)] for i in range(3)]
    n = abs(q.numerator)
    peak = Q(0)
    overwritten = False
    for primitive in word:
        dense_step(matrix, primitive)
        target, source, work = matrix
        need(source == [0, 1, 0], "source was changed")
        need(target[0] == 1 and abs(target[1]) <= abs(q) and target[2] == 0,
             "target prefix envelope")
        if work == [0, 0, 1] and not overwritten:
            # The reference also has this arbitrary entry state. Unit circuits
            # erase it after accumulating; it never enters a public register.
            continue
        overwritten = True
        need(work[0] == work[2] == 0 and 0 <= work[1] <= n,
             "work prefix envelope")
        peak = max(peak, work[1])
    need(matrix == [[1, q, 0], [0, 1, 0], [0, 0, 0]], "macro endpoint / work clearing")
    need(len(word) <= budget, "primitive budget exceeded")
    return peak


def graph_crosscheck(limit=128):
    """Dijkstra over forward digit transitions, independent of backward DP.

    Each edge c -> 2c+d costs 1+|d|, with the intermediate 2c <= B.
    For every bound 1..limit, compare every reachable positive target <= B.
    """
    checked = 0
    for bound in range(1, limit + 1):
        distance = {1: 0}
        queue = [(0, 1)]
        while queue:
            cost, c = heapq.heappop(queue)
            if cost != distance[c] or 2 * c > bound:
                continue
            for digit in (-1, 0, 1):
                target = 2 * c + digit
                if not 1 <= target <= bound:
                    continue
                value = cost + 1 + abs(digit)
                if value < distance.get(target, value + 1):
                    distance[target] = value
                    heapq.heappush(queue, (value, target))
        need(len(distance) == bound, "digit graph coverage")
        for n, cost in distance.items():
            digits = bounded_digits(n, bound)
            need(sum(1 + abs(d) for d in digits) == cost, "DP / graph cost disagreement")
            c = 1
            for d in digits:
                need(1 <= 2 * c <= bound, "digit intermediate exceeds bound")
                c = 2 * c + d
                need(1 <= c <= bound, "digit endpoint exceeds bound")
            need(c == n, "digit value disagreement")
            checked += 1
    return {"bounds": [1, limit], "target_bound_pairs": checked, "status": "PASS"}


def sparse_step(rows, primitive):
    tag, target = primitive[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = rows[primitive[2]].copy()
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: x * factor for j, x in rows[target].items()}
    elif tag in ("add", "subtract"):
        factor = 1 if tag == "add" else -1
        dest = rows[target]
        for j, x in list(rows[primitive[2]].items()):
            value = dest.get(j, Q(0)) + factor * x
            if value:
                dest[j] = value
            else:
                dest.pop(j, None)
    else:
        raise ValueError("unknown primitive")


def replay(events, checks, receipt, orientation, coefficients):
    n, v = 716, 112
    rows = {("L", r): {r: Q(1)} for r in range(n)}
    # Private columns are arbitrary on entry, then explicitly erased.
    rows[WORK] = {n: Q(1)}
    rows.update({("C", k): {n + 1 + k: Q(1)} for k in range(8)})
    envelope = {("L", r): Q(1) for r in range(n)}
    peak = Q(1)
    paid, tags, used = Counter(), Counter(), Counter()
    before = reference = macros = changed = 0
    stream_hash = hashlib.sha256()
    extra_source_reads = 0
    for event in events:
        if event[0] != "scalar":
            need(event[0] in ("climb", "center", "phase", "adapter", "residual_adapter"),
                 "unknown non-scalar event")
            if event[0] == "climb":
                paid[event[5]] += 1
            if event[0] == "center":
                paid[event[4]] += 1
            # Preserve each recursive call, frame transition and adapter.
            stream_hash.update(canonical(event) + b"\n")
            continue
        op, frame = event[1:]
        target, tag = tuple(op[1]), op[0]
        word = lower(op)
        comparison = binary_lower(op)
        need(len(word) <= len(comparison), "local cost regression")
        before += 2 * baseline_cost(op)
        reference += 2 * len(comparison)
        macros += 1
        changed += len(word) < len(comparison)
        if tag == "add":
            q, source = Q(*op[3:5]), tuple(op[2])
            used[q] += 1
            peak = max(peak, abs(q.numerator) * envelope[source])
            envelope[target] = envelope.get(target, Q(0)) + abs(q) * envelope[source]
            # Count ALL source accesses, including coefficient synthesis.
            new_reads = sum(len(p) == 3 and p[2] == source for p in word)
            old_reads = sum(len(p) == 3 and p[2] == source for p in comparison)
            extra_source_reads += new_reads - old_reads
        elif tag == "clear":
            envelope[target] = Q(0)
        elif tag == "copy":
            envelope[target] = envelope[tuple(op[2])]
        elif tag == "scale":
            envelope[target] *= abs(Q(*op[2:4]))
        peak = max(peak, envelope[target])
        for primitive in word:
            sparse_step(rows, primitive)
            tags[primitive[0]] += 2
            stream_hash.update(canonical(["primitive", primitive, frame]) + b"\n")
        if tag == "add":
            need(not rows[WORK], "work survives macro")
    for r in range(n):
        want = {r: Q(1)}
        if orientation == "forward" and v <= r < 2 * v:
            want[r - v] = Q(1)
        if orientation == "backward" and r < v:
            want[r + v] = Q(-1)
        need(rows[("L", r)] == want, "complete scalar endpoint at register " + str(r))
    need(all(not row for reg, row in rows.items() if reg[0] != "L"), "private columns survive")
    need(before == checks["real_component_primitive_bound"], "original primitive receipt")
    need(macros == checks["scalar_macros"], "scalar count receipt")
    need(dict(paid) == {int(k): v for k, v in checks["paid_profile"].items()}, "paid profile receipt")
    need(peak == Q(receipt["prefix_l1_upper"]), "retained prefix bound")
    need(peak < 2 ** receipt["charged_payload_bits"], "payload bound")
    need(extra_source_reads <= 0, "additional source accesses")
    coefficients.update(used)
    after = sum(tags.values())
    return {
        "native_input_columns": n, "arbitrary_private_input_columns": 9,
        "scalar_macros": macros, "improved_macros_vs_pr696": changed,
        "original_real_primitives": before, "pr696_real_primitives": reference,
        "new_real_primitives": after, "saved_vs_original": before - after,
        "saved_vs_pr696": reference - after,
        "source_reads_delta_vs_pr696_per_real_component": extra_source_reads,
        "real_primitive_counts": dict(sorted(tags.items())),
        "expanded_stream_sha256": stream_hash.hexdigest(),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "retained_prefix_l1_bound": str(peak),
        "retained_payload_bits": receipt["charged_payload_bits"],
    }


def negative_controls():
    op = ["add", list(T), list(S), 31, 2]
    good = lower(op)
    tests = {
        "missing_clear": (Q(31, 2), good[:-1], len(good)),
        "missing_source_copy": (Q(31, 2), good[1:], len(good)),
        "wrong_signed_digit": (Q(31, 2), [("add", *p[1:]) if p[0] == "subtract" else p for p in good], len(good)),
        "missing_halving": (Q(31, 2), [p for p in good if p[0] != "halve"], len(good)),
        "cost_inflation": (Q(31, 2), good + [("clear", WORK)], len(good)),
        # Endpoint-correct and cheaper: 32-1 violates the required bound 31.
        "unbounded_naf_overshoot": (Q(31, 2), [("copy", WORK, S)] + [("double", WORK)] * 5 +
                                   [("subtract", WORK, S), ("halve", WORK), ("add", T, WORK), ("clear", WORK)], 100),
        "source_growth_then_restore": (Q(31, 2), [("double", S), ("halve", S)] + good, 100),
        "unit_dirty_work": (Q(1), [("add", T, S)], 2),
    }
    rejected = {}
    for name, (q, word, budget) in tests.items():
        try:
            check_add(q, word, budget)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError("accepted negative control: " + name)
    need(rejected["unbounded_naf_overshoot"] == "work prefix envelope", "overshoot control reason")
    need(rejected["cost_inflation"] == "primitive budget exceeded", "cost control reason")
    for name, invalid in {
        "non_dyadic": ["add", list(T), list(S), 1, 3],
        "source_target_alias": ["add", list(T), list(T), 1, 1],
        "work_alias": ["add", list(T), list(WORK), 1, 1],
        "zero_addition": ["add", list(T), list(S), 0, 1],
    }.items():
        try:
            lower(invalid)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError("accepted invalid macro: " + name)
    return rejected


def collect():
    spec = check_pins()
    coefficients = Counter()
    programs = {}
    graph = graph_crosscheck()
    controls = negative_controls()
    # The seed-selected JP8 backward screen was followed by complete coverage.
    for provider in ("ck", "jp8"):
        folder = ROOT / PROVIDERS / provider
        events, checks, inherited = [read(folder / name) for name in
                                    ("LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json", "INDEPENDENT-LOCAL-REPLAY.json")]
        need(set(events) == {"forward", "backward"}, "program orientation coverage")
        need(sha(canonical(events)) == spec["providers"][provider]["artifact_semantic_sha256"]["LOCAL-PROGRAMS.json.gz"],
             "selected SPEC program binding")
        for orientation in ("forward", "backward"):
            need(sha(canonical(events[orientation])) == checks[orientation]["sha256"] ==
                 spec["providers"][provider]["program_hashes"][orientation], "orientation binding")
            programs[provider + "/" + orientation] = replay(events[orientation], checks[orientation],
                inherited["local"][orientation], orientation, coefficients)
    census = []
    for q, occurrences in sorted(coefficients.items()):
        op = ["add", list(T), list(S), q.numerator, q.denominator]
        candidate, comparison = lower(op), binary_lower(op)
        peak = check_add(q, candidate, len(candidate))
        check_add(q, comparison, len(comparison))
        n = abs(q.numerator)
        digits = bounded_digits(n, n)
        need(len(candidate) <= len(comparison) <= baseline_cost(op), "coefficient cost ordering")
        census.append({"coefficient": str(q), "occurrences": occurrences,
                       "digits_after_leading_one": list(digits),
                       "signed_real_cost": len(candidate), "pr696_real_cost": len(comparison),
                       "work_peak_multiple": str(peak)})
    return {"status": "PASS_PREFIX_BOUNDED_DYADIC", "programs": programs,
            "distinct_coefficients": len(census), "coefficient_census": census,
            "independent_digit_graph": graph, "negative_controls": controls,
            "new_recursive_children": 0, "additional_private_registers": 0,
            "kappa_claim": None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the checked deterministic certificate")
    args = parser.parse_args()
    result = collect()
    need(result == read(HERE / "EXPECTED.json"), "expected certificate mismatch")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        savings = ",".join(str(p["saved_vs_pr696"]) for p in result["programs"].values())
        print(f"PASS_PREFIX_BOUNDED_DYADIC programs=4 columns=716+9 coefficients={result['distinct_coefficients']} "
              f"extra_savings={savings} controls={len(result['negative_controls'])}")
