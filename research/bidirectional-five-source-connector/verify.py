#!/usr/bin/env python3
"""Sharp six-transfer F2 connector certificate, not a supplier theorem.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import census

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SEED = "628ce1c7a4abbbac17914cb067826ef4"
BASE = "e112d71c8d7bb32435debcc54df932593dd8223a"
SOURCE_WORD = (0, 1, 2, 0, 3, 1, 4, 3, 2, 4)
LOOP = (0, 1, 0, 1, 0, 1)
CUTS = (1, 2, 3, 5, 6, 7)
DIRECTIONS = (2, 3, 2, 2, 2)
ROOTS = (36, 37)
SCRATCH = (38, 39, 40)
ROWS = 41


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def check_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(sources["base_commit"] == BASE, "wrong source base")
    checked = 0
    for entry in sources["files"]:
        if entry["usage"] != "input":
            continue
        payload = (ROOT / entry["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == entry["sha256"],
                "source binding changed: " + entry["path"])
        changed = payload + b"\ncorrupt-source-control\n"
        require(hashlib.sha256(changed).hexdigest() != entry["sha256"],
                "source corruption control")
        checked += 1
    selection = json.loads((PACKAGE / "SELECTION.json").read_text())
    require(selection["seed"] == SEED and selection["base_commit"] == BASE,
            "assignment provenance changed")
    require(any(card["task_id"] == "connector-alphabet-change"
                for card in selection["suggestions"]), "missing emitted card")
    return checked


def readout_word(skeleton):
    roots, history = census.literal_history(skeleton)
    require(roots == [32, 64], "unrestored skeleton")
    at = [[] for _ in range(len(skeleton) + 1)]
    pairs = {}
    for mask in range(1, 32):
        found = next(((a, b) for a in history for b in history if a[2] ^ b[2] == mask), None)
        require(found is not None, "missing mask " + str(mask))
        pairs[mask] = [[cut, port] for cut, port, _ in found]
        for cut, port, _ in found:
            at[cut].append(["A", mask, port])
    word = []
    for cut, calls in enumerate(at):
        word.extend(calls)
        if cut < len(skeleton):
            word.append(skeleton[cut])
    return word, pairs


def atomic_endpoint(word):
    roots = [32, 64]
    outputs = [0] * 32
    for op in word:
        if op[0] == "T":
            roots[op[1]] ^= roots[1 - op[1]]
        elif op[0] == "B":
            roots[op[2]] ^= 1 << op[1]
        elif op[0] == "A":
            outputs[op[1]] ^= roots[op[2]]
        else:
            raise ValueError("unknown root operation")
    return roots == [32, 64] and outputs == list(range(32))


def factors(kind, index):
    return (f"A{index}",) if kind == "A" else tuple(f"B{index}.{k}" for k in range(index + 1))


def compile_child(chain, source, target, scratch):
    require(source != target and source not in scratch and target not in scratch,
            "aliased child ports")
    if len(chain) == 1:
        return [("L", chain[0], source, target)]
    require(bool(scratch), "unpaid borrowed row")
    mid = len(chain) // 2
    first = compile_child(chain[:mid], source, scratch[0], scratch[1:])
    last = compile_child(chain[mid:], scratch[0], target, scratch[1:])
    return first + last + first[::-1] + last[::-1]


def lower(word):
    result = []
    for op in word:
        if op[0] == "T":
            result.append(("X", ROOTS[1 - op[1]], ROOTS[op[1]]))
        else:
            kind, index, port = op
            source, target = ((index, ROOTS[port]) if kind == "B"
                              else (ROOTS[port], index + 4))
            result.extend(compile_child(factors(kind, index), source, target, SCRATCH))
    return result


def formal_expected():
    state = [{(row,)} for row in range(ROWS)]
    for mask in range(1, 32):
        for j in range(5):
            if mask >> j & 1:
                state[mask + 4].add((f"A{mask}",) + factors("B", j)[::-1] + (j,))
    return state


def formal_replay(word):
    state = [{(row,)} for row in range(ROWS)]
    for op in word:
        if op[0] == "X":
            _, source, target = op
            state[target] ^= state[source]
        else:
            _, label, source, target = op
            state[target] ^= {(label,) + term for term in state[source]}
    return state


def apply(matrix, value):
    return sum(((row & value).bit_count() & 1) << k for k, row in enumerate(matrix))


def dense_controls(lowered):
    count = 0
    nonsymmetric = 0
    noncommuting = 0
    singular = 0
    for width in (1, 2, 3):
        rng = random.Random(18078 + width)
        names = [f for j in range(5) for f in factors("B", j)] + [f"A{m}" for m in range(1, 32)]
        matrices = {name: tuple(rng.getrandbits(width) for _ in range(width)) for name in names}
        nonsymmetric += sum(any(((matrix[i] >> j) & 1) != ((matrix[j] >> i) & 1)
                                for i in range(width) for j in range(width))
                            for matrix in matrices.values())
        singular += sum(any(apply(matrix, value) == 0 for value in range(1, 1 << width))
                        for matrix in matrices.values())
        for a, b in zip(names, names[1:]):
            noncommuting += any(apply(matrices[a], apply(matrices[b], 1 << k)) !=
                                apply(matrices[b], apply(matrices[a], 1 << k))
                                for k in range(width))
        cases = [[(1 << bit) if row == active else 0 for row in range(ROWS)]
                 for active in range(ROWS) for bit in range(width)]
        cases += [[rng.getrandbits(width) for _ in range(ROWS)] for _ in range(5)]
        for initial in cases:
            expected = initial.copy()
            for mask in range(1, 32):
                for j in range(5):
                    if mask >> j & 1:
                        value = initial[j]
                        for f in factors("B", j):
                            value = apply(matrices[f], value)
                        expected[mask + 4] ^= apply(matrices[f"A{mask}"], value)
            for oriented in (lowered, lowered[::-1]):
                state = initial.copy()
                for op in oriented:
                    if op[0] == "X":
                        state[op[2]] ^= state[op[1]]
                    else:
                        state[op[3]] ^= apply(matrices[op[1]], state[op[2]])
                require(state == expected, "dense dirty-row mismatch")
                count += 1
    require(nonsymmetric > 0 and noncommuting > 0 and singular > 0, "degenerate dense fixtures")
    return {"cases": count, "widths": [1, 2, 3], "nonsymmetric_maps": nonsymmetric,
            "noncommuting_adjacent_pairs": noncommuting, "singular_maps": singular}


def failure_controls(word, lowered):
    mutations = Counter()
    for at, op in enumerate(word):
        require(not atomic_endpoint(word[:at] + word[at + 1:]), "undetected deleted root call")
        mutations["single_call_deletions"] += 1
        changed = op.copy()
        changed[-1] = 1 - changed[-1]
        require(not atomic_endpoint(word[:at] + [changed] + word[at + 1:]),
                "undetected wrong physical port/direction")
        mutations["port_or_transfer_direction_flips"] += 1
    expected = formal_expected()
    first_b2 = next(i for i, op in enumerate(lowered) if op[0] == "L" and op[1] == "B2.0")
    mutant = lowered.copy()
    op = list(mutant[first_b2])
    op[1] = "B2.1"
    mutant[first_b2] = tuple(op)
    require(formal_replay(mutant) != expected, "undetected wrong factor")
    mutations["wrong_factor"] += 1
    require(formal_replay(lowered[:first_b2] + lowered[first_b2 + 1:]) != expected,
            "undetected unpaid child restore")
    mutations["omitted_child_leaf"] += 1
    try:
        compile_child(("f", "g"), 0, 36, (36,))
    except ValueError:
        mutations["aliased_scratch"] += 1
    else:
        raise ValueError("aliased scratch accepted")
    # A one-readout echo agrees on clean roots but leaks arbitrary incoming dirt.
    roots, history = census.literal_history([["B", 0, 0], ["B", 0, 0]])
    value = next(v for cut, port, v in history if cut == 1 and port == 0)
    require(roots == [32, 64] and value & 31 == 1 and value != 1,
            "clean-input-only negative control")
    mutations["clean_only_readout"] += 1
    require(census.literal_coverage([["B", 0, 0], ["B", 0, 1]]) is None,
            "unequal injection directions were accepted")
    mutations["unequal_injection_directions"] += 1
    require(all(any(census.dot(r, u) == 0 for u in (1, 2, 3)) for r in (1, 2, 3)),
            "three-source-direction all-ones obstruction")
    mutations["three_direction_obstruction"] += 1
    return dict(mutations)


def evidence():
    bound_sources = check_sources()
    primary = list(census.pairings())
    secondary = list(census.matchings())
    require(len(primary) == len(set(primary)) == 945 and set(primary) == set(secondary),
            "pairing domain disagreement")
    old_histogram = Counter(len({a ^ b for a in census.prefixes(w) for b in census.prefixes(w)})
                            for w in primary)
    prior = json.loads((ROOT / "research/universal-connector-boundary/CERTIFICATE.json").read_text())
    expected_old = {int(k): v for k, v in prior["censuses"][1]["histogram"].items()}
    require(old_histogram == expected_old and max(old_histogram) == 31, "inherited 945 control")
    eligible = census.eligible_pairs(primary)
    other = census.eligible_pairs_independent(secondary)
    require(len(eligible) == 175 and set(eligible) == set(other), "relaxed filter disagreement")
    loop_counts = {n: len(census.closed_loops(n)) for n in range(6)}
    require(loop_counts == {0: 1, 1: 0, 2: 2, 3: 0, 4: 6, 5: 0}, "loop closure control")
    representatives = sorted({min(census.orbit(w)) for w in census.closed_loops(4)})
    require(representatives == [(0, 0, 0, 0), (0, 0, 1, 1)], "four-transfer orbit reduction")
    lower_bound = {}
    for loop in representatives:
        first = census.segment_census(loop, eligible)
        second = census.direct_census(loop, sorted(other))
        require(first == second, "independent four-transfer census disagreement")
        require(max(first["histogram"]) == 31 and 32 not in first["histogram"],
                "four-transfer counterexample")
        first["orbit_size"] = len(census.orbit(loop))
        lower_bound["".join("CD"[p] for p in loop)] = first
    skeleton = census.skeleton(SOURCE_WORD, LOOP, CUTS, DIRECTIONS)
    require(skeleton is not None and census.literal_coverage(skeleton) == set(range(32)),
            "six-transfer witness coverage")
    symmetry_cases = 0
    for cut in range(len(skeleton)):
        rotated = skeleton[cut:] + skeleton[:cut]
        for swapped in (False, True):
            operations = [op[:-1] + [1 - op[-1]] if swapped else op for op in rotated]
            require(census.literal_coverage(operations) == set(range(32)), "cyclic/swap control")
            symmetry_cases += 1
    word, pairs = readout_word(skeleton)
    require(len(word) == 78 and atomic_endpoint(word) and atomic_endpoint(word[::-1]),
            "complete root word")
    require(Counter(op[1] for op in word if op[0] == "B") == Counter({j: 2 for j in range(5)}),
            "source incidence")
    require(Counter(op[1] for op in word if op[0] == "A") == Counter({m: 2 for m in range(1, 32)}),
            "reader incidence")
    lowered = lower(word)
    require(len(lowered) == 186 and sum(op[0] == "L" for op in lowered) == 180,
            "complete lowered invoice")
    require(formal_replay(lowered) == formal_expected() and
            formal_replay(lowered[::-1]) == formal_expected(), "free noncommutative endpoint")
    # Replay the pinned old eight-transfer construction, without claiming its invention.
    old = json.loads((ROOT / "research/two-connector-eight-transfer-threshold/EXPECTED.json").read_text())
    for fixture in old["witnesses"].values():
        operations = [["T", 0] if item == "C" else ["B", int(item[1]), int(item[-1])]
                      for item in fixture["skeleton"]]
        require(census.literal_coverage(operations) == set(range(32)), "old eight-transfer positive control")
    ports = {kind: dict(sorted(Counter(str(op[-1]) for op in word if op[0] == kind).items()))
             for kind in ("A", "B", "T")}
    return {"schema_version": 1, "seed": SEED, "base_commit": BASE,
            "old_pairings": 945, "old_histogram": dict(sorted(old_histogram.items())),
            "eligible_word_partitions": 175, "eligible_sha256": digest(sorted(eligible)),
            "closed_loop_counts": loop_counts, "four_transfer_census": lower_bound,
            "witness": {"source_word": SOURCE_WORD, "transfer_word": "CDCDCD", "cuts": CUTS,
                        "normalized_source_directions": DIRECTIONS, "skeleton": skeleton,
                        "readout_pairs": pairs, "complete_word": word, "ports": ports,
                        "root_calls": 78, "transfers": 6, "factor_calls": 180,
                        "primitive_and_transfer_records": len(lowered), "dirty_data_rows": ROWS,
                        "borrowed_child_rows": 3, "distinct_factor_maps": 46,
                        "lowered_word_sha256": digest(lowered)},
            "controls": {"source_bindings": bound_sources, "old_eight_transfer_witnesses": len(old["witnesses"]),
                         "cyclic_and_port_symmetries": symmetry_cases,
                         "dense": dense_controls(lowered), "rejected_mutations": failure_controls(word, lowered)},
            "scope": "Exact incidence-minimal F2 two-root connector threshold, not a physical supplier or kappa improvement."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="print canonical research evidence instead of comparing it")
    args = parser.parse_args()
    # JSON object keys are strings; normalize integer histogram keys before comparison.
    actual = json.loads(canonical(evidence()))
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    recorded = json.loads((PACKAGE / "EVIDENCE.json").read_text())
    require(canonical(actual) == canonical(recorded), "recorded evidence changed")
    changed = json.loads(canonical(recorded))
    changed["witness"]["transfers"] = 5
    require(canonical(actual) != canonical(changed), "wrong-count evidence control")
    print("PASS_BIDIRECTIONAL_FIVE_SOURCE minimum_transfers=6 root_calls=78 "
          "eligible=175 four_transfer_candidates=2102100 engines=agree "
          f"factor_calls=180 dense_cases={actual['controls']['dense']['cases']} no_new_kappa")


if __name__ == "__main__":
    main()
