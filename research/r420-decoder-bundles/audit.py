"""Independent set-valued replay and scalar invoice for an R420 decoder rewrite.

The scalar word, its inverse, every dirty-input column, and all frame paths are
checked here without importing the producer or the upstream checker. Closed
E8 frames and the hosted/cohort realization remain inherited obligations.
PR708 by Sagar Thakrar used set-valued relative replay for pair sharing; this
checker extends that method to bundles and recomputes the scalar paid invoice.
Sagar Thakrar, with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(value):
    if isinstance(value, dict):
        return value
    with (gzip.open(value, "rt") if str(value).endswith(".gz") else open(value)) as stream:
        return json.load(stream)


def rank(rows):
    basis = {}
    for source in rows:
        row = list(map(Fraction, source))
        for pivot, old in sorted(basis.items()):
            factor = row[pivot]
            row = [a - factor * b for a, b in zip(row, old)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [value / scale for value in row]
    return len(basis)


def validate(word):
    require(word["v"] == 120 and word["R"] == 420 and word["h"] == 8,
            "expected the R420 E8 scalar word")
    n = 2 * word["v"] + word["R"]
    frames = word["frames"]
    require(len(word["lines"]) == word["v"] and all(
        len(row) == word["h"] and all(type(x) is int for x in row)
        for row in word["lines"]), "malformed label table")
    for frame in frames:
        require(len(frame) == len(set(frame)) and all(
            type(x) is int and 0 <= x < word["v"] for x in frame), "malformed frame")
    for key in ("start", "final"):
        require(len(word[key]) == n and all(type(x) is int and 0 <= x < len(frames)
                                           for x in word[key]), "malformed " + key)
    for section in "DABC":
        for gate in word[section]:
            require(len(gate) == 3, "malformed gate in " + section)
            frame, destination, sources = gate
            require(type(frame) is int and 0 <= frame < len(frames), "invalid gate frame")
            registers = [destination] + sources
            require(sources and all(type(x) is int and 0 <= x < n for x in registers)
                    and len(registers) == len(set(registers)), "invalid gate operands")
    require(len(word["ret"]) == len(set(word["ret"])) and all(
        type(r) is int and 2 * word["v"] <= r < n for r in word["ret"]),
        "invalid retained helpers")
    require(len(word["scatter"]) == word["v"], "invalid scatter row count")
    for row in word["scatter"]:
        require(len(row) == len(set(row)) and all(
            type(k) is int and 0 <= k < len(word["ret"]) for k in row),
            "invalid scatter operands")
    return n


def events(word, sections):
    for section in sections:
        if section == "scatter":
            for target, row in enumerate(word["scatter"]):
                for index in row:
                    yield None, word["v"] + target, [word["ret"][index]]
        else:
            yield from word[section]


def symbolic(n, gates):
    values = [{r} for r in range(n)]
    for _, destination, sources in gates:
        for source in sources:
            values[destination].symmetric_difference_update(values[source])
    return values


def positive(n, gates):
    """Nonnegative scalar envelope of the forward word and its inverse.

    Replacing every ADD/SUB by addition bounds signed lifts. A scatter COPY is
    read-only, so repeated adds from its unchanged owner give the same envelope.
    With all inputs one, the maximum is the exact maximum positive row sum.
    The reversed event order is the inverse envelope, not a transpose norm.
    """
    result = {}
    for label, ordered in (("forward", gates), ("inverse", reversed(gates))):
        values = [1] * n
        for _, destination, sources in ordered:
            values[destination] += sum(values[source] for source in sources)
        maximum = max(values)
        result[label] = {"maximum": maximum, "bits": maximum.bit_length()}
    return result


def geometry(word, dimensions):
    current = list(word["start"])
    paths = [[frame] for frame in current]
    frames = list(map(set, word["frames"]))
    histogram = Counter()
    moves = 0

    def move(register, frame):
        nonlocal moves
        old = current[register]
        if old == frame:
            return
        require(frames[old] < frames[frame] and dimensions[old] < dimensions[frame],
                f"non-nested frame move on register {register}: {old}->{frame}")
        histogram[dimensions[frame] - dimensions[old]] += 1
        moves += 1
        current[register] = frame
        paths[register].append(frame)

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            require(all(dimensions[f] == 0 for f in current[word["v"]:2 * word["v"]]),
                    "scatter target already left frame zero")
            for helper in word["ret"]:
                histogram[dimensions[current[helper]]] += 1
        else:
            for frame, destination, sources in word[section]:
                for register in [destination] + sources:
                    move(register, frame)
    for register, frame in enumerate(word["final"]):
        move(register, frame)
    return paths, {"paid_histogram": {str(rank): count for rank, count in sorted(histogram.items())},
                   "rank_mass": sum(rank * count for rank, count in histogram.items()),
                   "moves": moves, "copies": len(word["ret"]),
                   "scope": "scalar MOVE and scatter COPY invoice, before cohort hosting"}


def interfaces(word, dimensions):
    v = word["v"]
    target = lambda r: v <= r < 2 * v
    full = [i for i, dimension in enumerate(dimensions) if dimension == word["h"]]
    require(len(full) == 1, "expected a unique full frame")
    reverse = [[full[0], destination, sources] for section in ("A", "B")
               for _, destination, sources in word[section] if not target(destination)]
    return {
        "no_target_feeds_source_or_helper": all(target(d) or all(not target(s) for s in src)
            for section in "DABC" for _, d, src in word[section]),
        "D_targets_from_zero_frame_helpers": all(dimensions[f] == 0 and target(d)
            and all(s >= 2 * v for s in src) for f, d, src in word["D"]),
        "targets_and_helpers_start_at_zero": all(dimensions[f] == 0 for f in word["start"][v:]),
        "A_never_writes_target": all(not target(d) for _, d, _ in word["A"]),
        "C_literal_reverse": word["C"] == reverse[::-1],
        "sources_and_helpers_finish_at_full": all(dimensions[f] == word["h"]
            for r, f in enumerate(word["final"]) if not target(r)),
    }


def compare(baseline, candidate):
    baseline, candidate = load(baseline), load(candidate)
    n = validate(baseline)
    require(validate(candidate) == n, "register count changed")
    immutable = sorted((set(baseline) | set(candidate)) - {"A", "C"})
    changed = [key for key in immutable if baseline.get(key) != candidate.get(key)]
    require(not changed, "changed fields outside A/C: " + ", ".join(changed))
    dimensions = [rank(baseline["lines"][i] for i in frame) for frame in baseline["frames"]]
    expected = [{r, r - baseline["v"]} if baseline["v"] <= r < 2 * baseline["v"] else {r}
                for r in range(n)]
    operators, paths, reports = {}, {}, {}
    for label, word in (("baseline", baseline), ("candidate", candidate)):
        gates = list(events(word, ("D", "A", "scatter", "B", "C")))
        operators[label] = symbolic(n, word["A"])
        paths[label], invoice = geometry(word, dimensions)
        reports[label] = {
            "full_operator_is_target_add": symbolic(n, gates) == expected,
            "inverse_operator_is_target_add": symbolic(n, reversed(gates)) == expected,
            "interface": interfaces(word, dimensions),
            "gates": {section: len(word[section]) for section in "DABC"},
            "adds": {section: sum(len(gate[2]) for gate in word[section]) for section in "DABC"},
            "scatter_adds": sum(map(len, word["scatter"])),
            "positive_scalar_bounds": positive(n, gates),
            "scalar_invoice": invoice,
        }
    differing_a = [r for r in range(n) if operators["baseline"][r] != operators["candidate"][r]]
    differing_paths = [r for r in range(n) if paths["baseline"][r] != paths["candidate"][r]]
    checks = {"all_A_columns_equal": not differing_a, "all_frame_paths_equal": not differing_paths,
              "scalar_invoice_equal": reports["baseline"]["scalar_invoice"] == reports["candidate"]["scalar_invoice"]}
    for label, report in reports.items():
        checks[label + "_full_operator"] = report["full_operator_is_target_add"]
        checks[label + "_inverse_operator"] = report["inverse_operator_is_target_add"]
        checks[label + "_interface"] = all(report["interface"].values())
    return {"status": "PASS" if all(checks.values()) else "FAIL", "columns": n,
            "scope": "relative scalar-word rewrite; closed E8 frames and cohort hosting inherited",
            "checks": checks, "different_A_output_registers": differing_a,
            "different_frame_path_registers": differing_paths, "words": reports,
            "scalar_ADD_saving_including_C": sum(reports["baseline"]["adds"].values())
                - sum(reports["candidate"]["adds"].values())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    args = parser.parse_args()
    result = compare(args.baseline, args.candidate)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
