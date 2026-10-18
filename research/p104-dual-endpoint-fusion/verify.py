"""Read-only exact replay of the scoped P104 physical-dual endpoint fusion."""

from collections import Counter
from pathlib import Path
import argparse
import copy
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def rank_bits(vectors):
    # Independent rank computation, separate from frame canonicalization.
    rows = list(vectors)
    count = 0
    for bit in range(9):
        pivot = next((i for i in range(count, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[pivot], rows[count] = rows[count], rows[pivot]
        for i in range(count + 1, len(rows)):
            if (rows[i] >> bit) & 1:
                rows[i] ^= rows[count]
        count += 1
    return count


def check_native(native, pairs, interpreter):
    expected = M.native_edges(pairs)
    records = native["transports"]
    indexed = {M.edge_key(r["old"], r["new"]): r for r in records}
    M.require(len(indexed) == len(records) and set(indexed) == set(expected), "native edge coverage")
    ranks = Counter()
    for key, events in expected.items():
        old, new = key
        record = indexed[key]
        M.require(record["events"] == events, "native occurrence coverage")
        gates = M.conjugate(interpreter.adjoint(interpreter.frame(old, 9))
                            + interpreter.frame(new, 9))
        recipe = record["recipe"]
        tableau = interpreter.tableau(gates)
        intrinsic_rank = rank_bits(x for x, _, _ in tableau[9:])
        M.require(type(recipe["rank"]) is int and recipe["rank"] == intrinsic_rank
                  == len(new) - len(old), "native intrinsic rank")
        interpreter.equal(interpreter.recipe(recipe), gates, "new child recipe")
        ranks[intrinsic_rank] += len(events)
    # Check telescoping against both literal predecessor transports, including phase.
    for pair in pairs:
        old, middle, new = (tuple(pair[k]) for k in ("old", "middle", "new"))
        first = interpreter.adjoint(interpreter.frame(old, 9)) + interpreter.frame(middle, 9)
        second = interpreter.adjoint(interpreter.frame(middle, 9)) + interpreter.frame(new, 9)
        actual = interpreter.recipe(indexed[(old, new)]["recipe"])
        interpreter.equal(actual, M.conjugate(first + second), "two-edge physical composition")
    return dict(distinct_recipes=len(records), occurrences=sum(ranks.values()),
                new_rank_counts={str(k): v for k, v in sorted(ranks.items())},
                complete_operator_phase_checks=len(records) + len(pairs))


def independent_run_census(word):
    """One forward dependency scan; does not call touches() or endpoint_runs()."""
    sequences = {g + str(n): [] for g in "XY" for n in range(104)}
    for index, event in enumerate(word["program"]):
        operands = event[1:3] if event[0] == "add" else event[1:2]
        for role in operands:
            if role in sequences and event[0] != "sign":
                sequences[role].append((index, event[0]))
    found = []
    summary = Counter()
    for role, sequence in sequences.items():
        for side, ordered in (("entry", sequence), ("exit", list(reversed(sequence)))):
            indices = []
            for index, tag in ordered:
                if tag != "transport":
                    break
                indices.append(index)
            summary[side + "_" + role[0] + "_" + str(len(indices))] += 1
            if len(indices) > 1:
                found.append(sorted(indices))
    return sorted(found), dict(sorted(summary.items()))


def expect_reject(label, action, message):
    try:
        action()
    except ValueError as error:
        M.require(message in str(error), label + " rejected for wrong reason: " + str(error))
        return label
    raise ValueError("fault accepted: " + label)


def controls(source, candidate, native, pairs, interpreter):
    accepted = []
    wrong = copy.deepcopy(native)
    wrong["transports"][0]["recipe"]["left"]["phase"] ^= 2
    accepted.append(expect_reject("global phase", lambda: check_native(wrong, pairs, interpreter),
                                  "exact global phase"))
    wrong = copy.deepcopy(native)
    wrong["transports"][0]["recipe"]["rank"] -= 1
    accepted.append(expect_reject("child rank", lambda: check_native(wrong, pairs, interpreter),
                                  "native intrinsic rank"))
    wrong = copy.deepcopy(native)
    wrong["transports"].pop()
    accepted.append(expect_reject("missing recipe", lambda: check_native(wrong, pairs, interpreter),
                                  "native edge coverage"))
    wrong = copy.deepcopy(native)
    wrong["transports"][0]["events"][0] += 1
    accepted.append(expect_reject("wrong occurrence", lambda: check_native(wrong, pairs, interpreter),
                                  "native occurrence coverage"))

    # Ignoring source reads would incorrectly fuse Y0's entry over real ADDs.
    wrong = copy.deepcopy(source)
    indices = [i for i, e in enumerate(wrong["program"])
               if e[0] == "transport" and e[1] == "Y0"]
    i, j = indices[:2]
    left, right = wrong["program"][i], wrong["program"][j]
    wrong["program"][j] = ["transport", "Y0", left[2], right[3], len(right[3])]
    del wrong["program"][i]
    accepted.append(expect_reject("cross source-read ADD barrier", lambda: M.replay(wrong),
                                  "ADD common frame"))

    # Every successful X-exit fusion moves across one scalar sign. Its chart
    # annotation must move too; leaving the old annotation is an invalid word.
    wrong = copy.deepcopy(candidate)
    role = next(p["role"] for p in pairs if p["side"] == "exit")
    sign = next(e for e in reversed(wrong["program"]) if e[0] == "sign" and e[1] == role)
    sign[3] = next(p["middle"] for p in pairs if p["role"] == role and p["side"] == "exit")
    accepted.append(expect_reject("stale sign frame", lambda: M.replay(wrong), "sign frame"))
    wrong = copy.deepcopy(candidate)
    index = next(i for i, e in enumerate(wrong["program"]) if e[0] == "sign")
    del wrong["program"][index]
    accepted.append(expect_reject("omitted sign", lambda: M.replay(wrong), "all-input boundary"))
    wrong = copy.deepcopy(candidate)
    index = next(i for i, e in enumerate(wrong["program"])
                 if e[0] == "add" and e[1] == "C")
    del wrong["program"][index]
    accepted.append(expect_reject("private cleanup", lambda: M.replay(wrong),
                                  "exact zero before private erase"))
    wrong = copy.deepcopy(candidate)
    index = next(i for i, e in enumerate(wrong["program"]) if e[0] == "add" and e[1] == "X0")
    wrong["program"][index][3] = 0
    accepted.append(expect_reject("public correction coefficient", lambda: M.replay(wrong),
                                  "all-input boundary"))
    return accepted


def verify(check_controls=True):
    M.authenticate()
    source = M.read_json(M.PACKAGE / "inputs/PR2586-WORD.json")
    candidate = M.read_json(M.PACKAGE / "WORD.json")
    native = M.read_json(M.PACKAGE / "NATIVE.json")
    rebuilt, runs, pairs = M.fuse(source)
    M.require(M.same_json(candidate, rebuilt), "complete literal word regeneration")
    baseline = M.replay(source)
    result = M.replay(candidate)
    inherited = M.read_json(M.PACKAGE / "inputs/PR2586-RESULT.json")["logical"]
    for key in ("events", "counts", "profile", "rank_mass", "boundary_coefficients"):
        M.require(M.same_json(baseline[key], inherited[key]), "source receipt binding " + key)
    independent_pairs, census = independent_run_census(source)
    M.require(independent_pairs == sorted(p["original_events"] for p in pairs),
              "independent dependency scan")
    M.require(len(runs) == 416 and len(pairs) == 128, "complete endpoint census")
    M.require(baseline["rank_mass"] == result["rank_mass"] == 3542, "unchanged rank mass")
    M.require(result["events"] == 5270 and result["counts"]["transport"] == 1942,
              "complete event invoice")
    M.require(result["zero_erasures"] == baseline["zero_erasures"] == 8, "eight zero erasures")
    for op in ("add", "sign", "zero", "erase"):
        M.require(result["counts"][op] == baseline["counts"][op], "retained scalar/private counts")
    old_signs = [e for e in source["program"] if e[0] == "sign"]
    new_signs = [e for e in candidate["program"] if e[0] == "sign"]
    M.require([e[:3] for e in old_signs] == [e[:3] for e in new_signs], "sign order and values")
    changed_signs = sum(a != b for a, b in zip(old_signs, new_signs))
    M.require(changed_signs == 26, "changed sign annotations")
    retained = lambda w: [e for e in w["program"] if e[0] in ("add", "zero", "erase")]
    M.require(retained(source) == retained(candidate), "literal ADD/private chronology")
    interpreter = M.native_module("native_verify.py")
    native_result = check_native(native, pairs, interpreter)
    blocked_ranks = []
    for run in runs:
        if len(run["transports"]) == 1:
            event = source["program"][run["transports"][0]]
            gates = M.conjugate(interpreter.adjoint(interpreter.frame(tuple(event[2]), 9))
                                + interpreter.frame(tuple(event[3]), 9))
            rank = rank_bits(x for x, _, _ in interpreter.tableau(gates)[9:])
            M.require(rank == 1, "blocked endpoint intrinsic rank")
            blocked_ranks.append(rank)
    M.require(sum(blocked_ranks) + sum(p["rank"] for p in pairs) == 928,
              "sharp endpoint-run rank mass")
    rejected = controls(source, candidate, native, pairs, interpreter) if check_controls else []
    # A basis change of presentation must be accepted, not mistaken for a new frame.
    equivalent = copy.deepcopy(candidate)
    for event in equivalent["program"]:
        if event[0] == "transport" and len(event[3]) > 1:
            event[3][0] ^= event[3][1]
            break
    M.require(M.replay(equivalent) == result, "equivalent-frame positive control")
    histogram = Counter(max(p["original_ranks"]) for p in pairs)
    return dict(schema_version=1, status="PASS", baseline=baseline, candidate=result,
                endpoint_run_census=census, fused_pairs=128, blocked_endpoints=288,
                pair_rank_histogram={str(k): v for k, v in sorted(histogram.items())},
                sign_frames_changed=changed_signs, native=native_result, controls=rejected,
                sharp_endpoint_run_rank_mass=928, intrinsic_rank_segments_checked=416,
                moment_statement="For every 0<p<1 and fixed m>0: delta = "
                "sum_r n_r*((r+1)^p-r^p-1)/m^p < 0; n_2..n_6=(16,28,39,30,15).",
                scope="Finite endpoint-run fusion of the pinned partial physical dual; no new kappa")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()
    result = verify()
    expected = M.read_json(M.PACKAGE / "RESULT.json")
    M.require(M.same_json(result, expected), "complete typed result receipt")
    if args.regenerate:
        import build
        word, native = build.construct()
        M.require(M.same_json(word, M.read_json(M.PACKAGE / "WORD.json")), "regenerated word")
        M.require(M.same_json(native, M.read_json(M.PACKAGE / "NATIVE.json")), "regenerated native payload")
    if args.out:
        M.write_json_new(args.out, result)
    print("PASS_P104_DUAL_ENDPOINT_FUSION pairs=128 blocked=288 transports=1942 "
          "rank_mass=3542 columns=358 native=128 zero_erases=8 controls=9 no_new_kappa")


if __name__ == "__main__":
    main()
