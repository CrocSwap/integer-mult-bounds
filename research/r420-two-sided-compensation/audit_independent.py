#!/usr/bin/env python3
"""Independent set-valued audit of a frozen two-sided frame-zero D recipe.

Uses only the standard library and imports neither the producer nor its verifier.
All 660 formal input coordinates are replayed simultaneously as Python sets.
Recipe coordinates: each [destination, source] pair and every transformed_rows
entry uses global register numbers. Helper pairs have disjoint endpoints. Target
receivers are unique and disjoint from all target donors; donors may repeat.
The only candidate word change permitted is D.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

BASELINE_SEMANTIC_SHA256 = "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class Reject(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fresh(n):
    return [{i} for i in range(n)]


def apply_gates(values, gates, n):
    for index, gate in enumerate(gates):
        require(isinstance(gate, list) and len(gate) == 3,
                f"gate {index}: expected [frame,destination,sources]")
        frame, destination, sources = gate
        require(type(frame) is int and type(destination) is int,
                f"gate {index}: noninteger coordinate")
        require(isinstance(sources, list) and sources, f"gate {index}: empty/malformed sources")
        operands = [destination] + sources
        require(all(type(r) is int and 0 <= r < n for r in operands),
                f"gate {index}: operand out of range")
        require(len(set(operands)) == len(operands), f"gate {index}: duplicate/self source")
        for source in sources:
            values[destination].symmetric_difference_update(values[source])
    return values


def rational_basis(rows):
    """Independent exact row-echelon basis, indexed by leading column."""
    basis = {}
    for row in rows:
        residual = list(map(Fraction, row))
        for pivot, vector in sorted(basis.items()):
            coefficient = residual[pivot]
            if coefficient:
                residual = [x - coefficient * y for x, y in zip(residual, vector)]
        pivot = next((j for j, x in enumerate(residual) if x), None)
        if pivot is not None:
            coefficient = residual[pivot]
            basis[pivot] = [x / coefficient for x in residual]
    return basis


class NativeReplay:
    def __init__(self, word):
        self.word = word
        self.v = word["v"]
        self.n = 2 * self.v + word["R"]
        require((word["h"], self.v, word["R"], self.n) == (8, 120, 420, 660),
                "unexpected R420 header")
        require(word["frames"][0] == [], "frame zero must be empty")
        self.frames = [set(frame) for frame in word["frames"]]
        self.dimensions = [len(rational_basis(word["lines"][r] for r in frame))
                           for frame in word["frames"]]
        require(len(word["start"]) == self.n == len(word["final"]), "frame array size mismatch")
        for r in range(self.n):
            f = word["start"][r]
            require(0 <= f < len(self.frames), "invalid start frame")
            require(self.frames[f] == ({r} if r < self.v else set()), "invalid register start frame")

    def replay(self, d_override=None, check_frames=True):
        word, n, v = self.word, self.n, self.v
        values = fresh(n)
        current = word["start"][:]
        climbs = 0

        def climb(register, frame):
            nonlocal climbs
            require(type(frame) is int and 0 <= frame < len(self.frames), "invalid gate frame")
            old = current[register]
            if old != frame:
                require(self.frames[old] <= self.frames[frame]
                        and self.dimensions[old] < self.dimensions[frame],
                        f"illegal climb: register {register}, frame {old} -> {frame}")
                current[register] = frame
                climbs += 1

        for phase in ("D", "A", "scatter", "B", "C"):
            if phase == "scatter":
                require(len(word[phase]) == v, "scatter target count mismatch")
                require(all(2 * v <= register < n for register in word["ret"]),
                        "retained total not in helper range")
                if check_frames:
                    require(all(self.dimensions[current[t]] == 0 for t in range(v, 2 * v)),
                            "target left zero frame before scatter")
                retained = [set(values[r]) for r in word["ret"]]
                for target, row in enumerate(word[phase], v):
                    require(len(set(row)) == len(row), "duplicate retained scatter source")
                    for slot in row:
                        require(type(slot) is int and 0 <= slot < len(retained), "bad scatter slot")
                        values[target].symmetric_difference_update(retained[slot])
                continue
            gates = d_override if phase == "D" and d_override is not None else word[phase]
            for gate in gates:
                # Operand validation occurs before frame-index access.
                apply_gates(values, [gate], n)
                if check_frames:
                    frame, destination, sources = gate
                    for register in [destination] + sources:
                        climb(register, frame)
        if check_frames:
            for register, frame in enumerate(word["final"]):
                climb(register, frame)
                if register < v or register >= 2 * v:
                    require(self.dimensions[frame] == 8, "source/helper final frame not full")
                else:
                    target = register - v
                    expected = {r for r, line in enumerate(word["lines"])
                                if sum(a * b for a, b in zip(line, word["lines"][target])) == 0}
                    require(self.frames[frame] == expected, "target final frame not target perpendicular")
        return values, climbs


def mismatches(actual, expected):
    bad = [i for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
    first = bad[0] if bad else None
    return {"count": len(bad), "first_register": first,
            "first_symmetric_difference": sorted(actual[first] ^ expected[first]) if bad else []}


def check_pairs(pairs, low, high, label):
    require(isinstance(pairs, list) and pairs, f"{label} pairs must be nonempty")
    used = set()
    for pair in pairs:
        require(isinstance(pair, list) and len(pair) == 2, f"malformed {label} pair")
        destination, source = pair
        require(type(destination) is int and type(source) is int
                and low <= destination < high and low <= source < high and destination != source,
                f"{label} pair has invalid global register coordinates")
        require(not ({destination, source} & used), f"{label} pairs are not disjoint")
        used.update(pair)


def check_target_pairs(pairs, low, high):
    require(isinstance(pairs, list) and pairs, "target pairs must be nonempty")
    receivers, donors = set(), set()
    for pair in pairs:
        require(isinstance(pair, list) and len(pair) == 2, "malformed target pair")
        receiver, donor = pair
        require(type(receiver) is int and type(donor) is int
                and low <= receiver < high and low <= donor < high and receiver != donor,
                "target pair has invalid global register coordinates")
        require(receiver not in receivers, "target receiver repeated")
        receivers.add(receiver)
        donors.add(donor)
    require(not receivers & donors, "modified target receiver used as donor")


def fixed_donor_audit(rows, recipe, v):
    """Optimal receiver assignment in the explicitly frozen donor-set class."""
    donors = recipe["target_search"]["donors"]
    require(isinstance(donors, list) and donors == sorted(set(donors)) and donors,
            "frozen donors must be a sorted, unique nonempty list")
    require(all(type(d) is int and v <= d < 2*v for d in donors), "frozen donor out of range")
    assigned = dict(recipe["target_pairs"])
    require(not set(assigned) & set(donors), "a nominated donor is also a receiver")
    require(all(source in donors for source in assigned.values()), "assigned donor not nominated")
    positive = {}
    for target in range(v, 2*v):
        if target in donors:
            continue
        gains = {donor: len(rows[target-v]) - len(rows[target-v] ^ rows[donor-v]) - 2
                 for donor in donors}
        best_gain = max(gains.values())
        if best_gain > 0:
            require(target in assigned, "profitable receiver omitted from fixed-donor assignment")
            require(gains[assigned[target]] == best_gain, "receiver assigned a suboptimal frozen donor")
            positive[target] = best_gain
        else:
            require(target not in assigned, "unprofitable target pair included")
    require(set(positive) == set(assigned), "fixed-donor receiver mismatch")
    saved = sum(positive.values())
    require(saved == recipe["target_search"]["saved_over_helper_only"], "target saving metadata mismatch")
    return {"status": "PASS_OPTIMAL_RECEIVER_ASSIGNMENT_FOR_FROZEN_DONOR_SET",
            "nominated_donors": len(donors), "used_donors": len(set(assigned.values())),
            "receivers": len(positive), "paid_gain_sum": saved,
            "minimum_pair_paid_gain": min(positive.values()),
            "maximum_pair_paid_gain": max(positive.values()),
            "scope": "One donor per receiver, at most one update per nondonor; no global donor-set optimality claim"}


def audit(baseline_path, recipe_path, candidate_path):
    baseline, recipe, candidate = map(load, (baseline_path, recipe_path, candidate_path))
    require(semantic_digest(baseline) == BASELINE_SEMANTIC_SHA256, "baseline semantic SHA256 changed")
    require(set(candidate) == set(baseline), "candidate header keys changed")
    changed = [key for key in baseline if baseline[key] != candidate[key]]
    require(changed == ["D"], f"non-D changes or no change: {changed}")
    v, n = baseline["v"], 2 * baseline["v"] + baseline["R"]
    helper_pairs = recipe["helper_pairs"]
    target_pairs = recipe["target_pairs"]
    check_pairs(helper_pairs, 2 * v, n, "helper")
    check_target_pairs(target_pairs, v, 2 * v)

    rows = [set() for _ in range(v)]
    for frame, target, sources in baseline["D"]:
        require(frame == 0 and v <= target < 2 * v
                and all(2 * v <= source < n for source in sources), "invalid baseline D gate")
        for source in sources:
            rows[target - v].symmetric_difference_update({source})
    baseline_rows = [set(row) for row in rows]
    columns = {source: {target for target, row in enumerate(rows) if source in row}
               for source in range(2*v, n)}
    helper_gains = [len(columns[source]) - len(columns[source] ^ columns[destination]) - 2
                    for destination, source in helper_pairs]
    require(all(gain > 0 for gain in helper_gains), "nonpositive paid helper pair gain")
    # Compute K H^{-1}: a helper destination-to-source column update.
    for destination, source in reversed(helper_pairs):
        for row in rows:
            if destination in row:
                row.symmetric_difference_update({source})
    helper_only_terms = sum(map(len, rows)) + 2 * len(helper_pairs)
    require(helper_only_terms == recipe["helper_only_adds"], "helper-only cost metadata mismatch")
    require(sum(map(len, baseline_rows)) - helper_only_terms == sum(helper_gains),
            "helper pair gains do not add to helper-only saving")
    target_assignment = fixed_donor_audit(rows, recipe, v)
    # Compute P K H^{-1}: target destination row XOR source row.
    for destination, source in target_pairs:
        rows[destination - v].symmetric_difference_update(rows[source - v])
    frozen_rows = recipe["transformed_rows"]
    require(len(frozen_rows) == v, "transformed row count mismatch")
    require(all(row == sorted(set(row)) for row in frozen_rows), "transformed rows not sorted/unique")
    require([sorted(row) for row in rows] == frozen_rows, "frozen feed matrix is not P K H^{-1}")

    segments = {
        "helper_prepare": [[0, dst, [src]] for dst, src in helper_pairs],
        "target_prepare": [[0, dst, [src]] for dst, src in target_pairs],
        "feed": [[0, v + target, sorted(row)] for target, row in enumerate(rows) if row],
        "target_restore": [[0, dst, [src]] for dst, src in reversed(target_pairs)],
        "helper_restore": [[0, dst, [src]] for dst, src in reversed(helper_pairs)],
    }
    reconstructed = [gate for gates in segments.values() for gate in gates]
    require(candidate["D"] == reconstructed, "candidate D differs from independent recipe expansion")
    require(all(gate[0] == 0 for gate in reconstructed), "D includes nonzero frame")
    d_expected = apply_gates(fresh(n), baseline["D"], n)
    d_actual = apply_gates(fresh(n), reconstructed, n)
    require(d_actual == d_expected, f"D endpoint mismatch: {mismatches(d_actual, d_expected)}")
    require(all(d_actual[r] == {r} for r in list(range(v)) + list(range(2*v, n))),
            "D failed to restore source/helper")

    native = NativeReplay(baseline)
    expected_full = [{r, r - v} if v <= r < 2*v else {r} for r in range(n)]
    baseline_full, baseline_climbs = native.replay()
    require(baseline_full == expected_full, "baseline full native sequence fails")
    candidate_full, candidate_climbs = native.replay(d_override=reconstructed)
    require(candidate_full == expected_full, "candidate full native sequence fails")
    require(candidate_climbs == baseline_climbs, "candidate changed native climb count")

    controls = {}
    chained_pairs = [pair[:] for pair in target_pairs]
    require(len(chained_pairs) >= 2, "need two target pairs for receiver-as-donor control")
    chained_pairs[1][1] = chained_pairs[0][0]
    try:
        check_target_pairs(chained_pairs, v, 2*v)
    except Reject as error:
        require(str(error) == "modified target receiver used as donor", "wrong shared-donor control rejection")
        controls["modified_receiver_as_donor"] = {"rejected": True, "reason": str(error)}
    else:
        raise Reject("modified receiver as donor was accepted")
    for omitted in ("helper_restore", "target_prepare"):
        mutant = [gate for name, gates in segments.items() if name != omitted for gate in gates]
        dirty_endpoint = apply_gates(fresh(n), mutant, n)
        dirty_full, _ = native.replay(d_override=mutant)
        endpoint_difference = mismatches(dirty_endpoint, d_expected)
        full_difference = mismatches(dirty_full, expected_full)
        require(endpoint_difference["count"] and full_difference["count"],
                f"negative control {omitted} was not rejected by both replays")
        controls["drop_" + omitted] = {"rejected": True, "D_endpoint": endpoint_difference,
                                    "native_full": full_difference}

    baseline_terms = sum(len(gate[2]) for gate in baseline["D"])
    candidate_terms = sum(len(gate[2]) for gate in reconstructed)
    require(baseline_terms - candidate_terms == sum(helper_gains) + target_assignment["paid_gain_sum"],
            "combined saving does not equal the independently recomputed pair gains")
    return {
        "status": "PASS", "auditor": "independent standard-library set-valued replay",
        "inputs": {"baseline_semantic_sha256": semantic_digest(baseline), "recipe_sha256": digest(recipe_path),
                   "candidate_sha256": digest(candidate_path)},
        "formal_columns": n, "dirty_helper_columns": baseline["R"],
        "changed_word_fields": changed,
        "helper_pairs": len(helper_pairs), "target_pairs": len(target_pairs),
        "helper_pair_paid_gains": {"sum": sum(helper_gains), "minimum": min(helper_gains),
                                   "maximum": max(helper_gains)},
        "target_fixed_donor_assignment": target_assignment,
        "target_basis_verified": "P = I + N with N^2 = 0; repeated donors allowed",
        "feed_matrix_verified": "L = P K H^-1",
        "D_endpoint_verified": "(x,s,y) -> (x,s,y+K s)",
        "native_full_verified": "(x,s,y) -> (x,s,y+x)",
        "native_frame_climbs": candidate_climbs,
        "frame_audit": "exact rational dimensions and nested inherited frame line sets; unchanged labels",
        "segments": {name: {"gates": len(gates), "terms": sum(len(g[2]) for g in gates)}
                     for name, gates in segments.items()},
        "baseline_D_terms": baseline_terms, "candidate_D_terms": candidate_terms,
        "D_term_saving": baseline_terms - candidate_terms,
        "negative_controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path,
                        default=ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz")
    parser.add_argument("--recipe", type=Path, default=HERE / "recipe.json")
    parser.add_argument("--candidate", type=Path, default=HERE / "output/candidate.json")
    parser.add_argument("--output", type=Path, default=HERE / "independent-audit.json")
    args = parser.parse_args()
    try:
        report = audit(args.baseline, args.recipe, args.candidate)
    except (Reject, KeyError, TypeError, ValueError, IndexError) as exc:
        print(json.dumps({"status": "REJECT", "reason": str(exc)}, sort_keys=True))
        return 1
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
