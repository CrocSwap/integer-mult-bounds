#!/usr/bin/env python3
"""Audit one pinned capacity filter, not the complete f(7) exclusion.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/connector-covering-code/cycle_search.cpp"
POSITIVE = (0, 1, 0, 2, 0, 1, 0, 5, 2, 3, 4, 3,
            6, 3, 4, 3, 5, 3, 4, 3, 6, 3, 4, 3)
MUTANTS = (
    ((0, 0, 0, 1, 0, 2, 1, 3, 2, 3), (0, 1, 0, 1, 2, 0, 2, 2, 2, 2), "reset"),
    ((0, 0, 0, 1, 2, 0, 3, 2, 3, 1), (1, 1, 1, 1, 1, 1, 1, 1, 2, 2), "omit"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def live_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    checked = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        actual = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        require(actual == row["sha256"], "source digest mismatch: " + row["path"])
        checked[row["path"]] = actual
    require(str(SOURCE.relative_to(ROOT)) in checked, "native source is not pinned")
    return checked


def run(command, *, input_text=None, timeout=120):
    result = subprocess.run(command, input=input_text, text=True, capture_output=True,
                            timeout=timeout, check=False)
    require(result.returncode == 0,
            "command failed: " + " ".join(map(str, command)) + "\n" + result.stderr[-3000:])
    require(not result.stderr, "unexpected native diagnostics: " + result.stderr[-3000:])
    return result.stdout


def prefix_points(word):
    state = 0
    points = []
    for label in word:
        points.append(state)
        state ^= 1 << label
    return points, state


def historical_control():
    points, final = prefix_points((0, 1, 0, 2, 1, 3, 2, 3))
    require(points == [0, 1, 3, 2, 6, 4, 12, 8] and final == 0, "tiny walk differs")
    require(len({a ^ b for a in points for b in points}) == 16, "tiny cover fails")
    results = {}
    for name, functional in (("bit0", lambda x: x & 1),
                             ("weight", lambda x: x.bit_count() % 2)):
        sides = [[p for p in points if functional(p) == side] for side in (0, 1)]
        excess = sum(len(side) * (len(side) - 1) // 2
                     - len({a ^ b for a, b in itertools.combinations(side, 2)})
                     for side in sides)
        actual_budget = sum(len(side) * (len(side) - 1) // 2 for side in sides) - 7
        results[name] = {"sizes": list(map(len, sides)), "excess": excess,
                         "actual_budget": actual_budget}
    require(results == {"bit0": {"sizes": [6, 2], "excess": 8, "actual_budget": 9},
                        "weight": {"sizes": [4, 4], "excess": 0, "actual_budget": 5}},
            "historical parity calibration differs")
    return {"word": "01021323", "prefixes": points, "coverage": 16,
            "balanced_budget": 5, "partitions": results}


def source_impact():
    old = (ROOT / "research/universal-f7-singleton-seedb859517b/engine.py").read_bytes()
    vendor = (ROOT / "research/universal-f7-singleton-l20-seed06704c39/engine.py").read_bytes()
    require(old == vendor and b"elif nq & 1:" in old, "old Python partition binding differs")
    call18 = (ROOT / "research/universal-f7-singleton-seedb859517b/search.py").read_text()
    call20 = (ROOT / "research/universal-f7-singleton-l20-seed06704c39/census20.py").read_text()
    old_c = (ROOT / "research/universal-f7-singleton-l20-census-complete-seedfd938f30/f7_census.c").read_text()
    corrected = (ROOT / "research/f7-weight-parity-census-correction/engine/corrected_census.c").read_text()
    require("cyclic_census(7, 18, budget=9, simple=True" in call18, "length18 caller differs")
    require("cyclic_census(7, 20, budget=27, simple=True" in call20, "length20 caller differs")
    require("if (nq & 1)" in old_c and "#define BUDGET 27" in old_c, "old C rule differs")
    require("int p=parity(nq)" in corrected and "__builtin_popcount((unsigned)x)&1" in corrected,
            "corrected partition binding differs")
    return {"old_python_engines_identical": True,
            "old_calls": [{"pr": 2542, "length": 18, "budget": 9},
                          {"pr": 2634, "length": 20, "budget": 27},
                          {"pr": 2691, "length": 20, "budget": 27}],
            "corrected_partition": "Hamming-weight parity",
            "scope": "Exact source locators and historical calibration, not fresh seven-label censuses."}


def slot_profile(low, gaps, *, gauge=0, mutant=None):
    """Literal time positions and unordered pairs; no aggregate formula."""
    require(len(low) == len(gaps), "slot length mismatch")
    points, final = prefix_points(low)
    require(final == 0, "unrestored low word")
    slots = []
    elapsed_high = 0
    for block, (point, gap) in enumerate(zip(points, gaps)):
        require(0 <= gap <= 8, "gap outside audit domain")
        start = 0 if mutant == "reset" else elapsed_high
        slots.extend((point, ((start + offset) % 2) ^ ((point & gauge).bit_count() % 2), block)
                     for offset in range(gap + 1))
        elapsed_high += gap
    profile = [[0, 0] for _ in range(16)]
    for a, b in itertools.combinations(slots, 2):
        if mutant == "omit" and a[0] == b[0] and a[2] != b[2]:
            continue
        profile[a[0] ^ b[0]][a[1] ^ b[1]] += 1
    counts = [sum(slot[0] == point for slot in slots) for point in range(16)]
    accepted = (max(gaps) <= 7 and elapsed_high % 2 == 0 and max(counts) <= 8
                and all(value >= (3 if (d, side) == (0, 0) else 4)
                        for d, row in enumerate(profile) for side, value in enumerate(row)))
    return accepted, profile


def projection(word, high):
    low_coordinates = [label for label in range(7) if label not in high]
    low, gaps, gap = [], [], 0
    for label in word:
        if label in high:
            gap += 1
        else:
            low.append(low_coordinates.index(label))
            gaps.append(gap)
            gap = 0
    require(gap == 0, "projection must end in a low step")
    return tuple(low), tuple(gaps)


def query(executable, cases):
    data = "".join("".join(map(str, low)) + " " + "".join(map(str, gaps)) + "\n"
                   for low, gaps in cases)
    lines = run([str(executable), "--query"], input_text=data).splitlines()
    require(len(lines) == len(cases) and all(x in ("0", "1") for x in lines),
            "malformed or incomplete query response")
    return [line == "1" for line in lines]


def positive_and_gauge_controls(executable):
    points, final = prefix_points(POSITIVE)
    require(final == 0 and len(set(points)) == 24, "positive is not a simple restored24")
    require(len({x ^ y for x in points for y in points}) == 128, "positive is not universal")
    cases = []
    gauge_checks = repeated = 0
    for high in itertools.combinations(range(7), 3):
        if sum(label not in high for label in POSITIVE) > 10:
            continue
        for base in (POSITIVE, POSITIVE[::-1]):
            for rotation in range(24):
                word = base[rotation:] + base[:rotation]
                if word[-1] in high:
                    continue
                low, gaps = projection(word, high)
                baseline, profile = slot_profile(low, gaps)
                require(baseline, "capacity oracle rejects universal positive")
                for gauge in range(16):
                    accepted, changed = slot_profile(low, gaps, gauge=gauge)
                    require(accepted == baseline, "gauge changed capacity verdict")
                    for d in range(16):
                        flip = (d & gauge).bit_count() % 2
                        require(changed[d] == [profile[d][flip], profile[d][1 ^ flip]],
                                "gauge bucket permutation failed")
                    gauge_checks += 1
                cases.append((low, gaps))
                repeated += len(set(prefix_points(low)[0])) < len(low)
    require(len(cases) == 176 and all(query(executable, cases)), "source rejects positive projection")
    return {"simple24_word": list(POSITIVE), "coverage": 128, "projections": len(cases),
            "repeated_low_projections": repeated, "gauge_checks": gauge_checks}


def bounded_python_controls(executable):
    # Two declared complete 0/1-gap cubes, unrelated to the source traversal.
    lows = ((0, 1, 0, 2, 1, 3, 2, 3), MUTANTS[0][0])
    cases = [(low, gap) for low in lows for gap in itertools.product(range(2), repeat=len(low))]
    cases += [(low, gaps) for low, gaps, _ in MUTANTS]
    expected = [slot_profile(low, gaps)[0] for low, gaps in cases]
    require(query(executable, cases) == expected, "Python/source differential mismatch")
    witness_receipts = []
    for low, gaps, mutation in MUTANTS:
        good, profile = slot_profile(low, gaps)
        bad, changed = slot_profile(low, gaps, mutant=mutation)
        require(good and not bad, "semantic mutation witness stopped discriminating")
        witness_receipts.append({"mutation": mutation, "low": list(low), "gaps": list(gaps),
                                 "correct_profile": profile, "mutant_profile": changed,
                                 "correct_accepts": good, "mutant_accepts": bad})
    return {"source_queries": len(cases), "mutant_witnesses": witness_receipts}


def repeated_prefix_boundary(executable):
    # PR1185's retained upper witness: a real universal word outside the
    # simple-cycle contract. Position counts are not distinct-state counts.
    word = tuple(map(int, "010201030102010345464546"))
    points, final = prefix_points(word)
    require(final == 0 and len(set(points)) == 23, "repeated-prefix witness differs")
    require(len({x ^ y for x in points for y in points}) == 128, "repeated word not universal")
    low, gaps = projection(word, (0, 1, 2))
    low_points, _ = prefix_points(low)
    positions_at_zero = sum(gaps[i] + 1 for i, point in enumerate(low_points) if point == 0)
    distinct_at_zero = len({p & 7 for p in points if p >> 3 == 0})
    require((positions_at_zero, distinct_at_zero) == (9, 8), "fiber multiplicity control differs")
    require(not slot_profile(low, gaps)[0] and query(executable, [(low, gaps)]) == [False],
            "simple-only guard no longer rejects the repeated-prefix control")
    return {"word": "".join(map(str, word)), "coverage": 128, "distinct_prefixes": 23,
            "low": list(low), "gaps": list(gaps), "positions_at_low_zero": positions_at_zero,
            "distinct_high_states_at_low_zero": distinct_at_zero, "source_accepts": False,
            "interpretation": "Outside the source simple-cycle contract; not a source bug."}


def expected_cases(blocks, cap, total):
    # Generating-function coefficients, independent of the native recursion.
    coefficients = [1]
    for _ in range(blocks):
        coefficients = [sum(coefficients[i - j] for j in range(cap + 1)
                            if 0 <= i - j < len(coefficients))
                        for i in range(len(coefficients) + cap)]
    return coefficients[total]


def native_checks(executable):
    rows = [json.loads(line) for line in run([str(executable)]).splitlines()]
    require([row["domain"] for row in rows] == ["A-core", "A-boundary", "B-core", "B-boundary"],
            "native domain inventory mismatch")
    core = {"A": 5 * expected_cases(8, 3, 14), "B": 77 * expected_cases(10, 2, 12)}
    for row in rows:
        family, kind = row["domain"].split("-")
        blocks, orbits = (8, 5) if family == "A" else (10, 77)
        expected = (core[family] if kind == "core" else
                    orbits * (1 + 8 * blocks + 64 * blocks * (blocks - 1) // 2))
        require(row["cases"] == expected, "incomplete native domain")
        require(sum(row["reasons"]) == expected and row["accepted"] == row["reasons"][0],
                "native reason counts disagree")
    require(all(rows[2]["mutant_disagreements"]), "B mutation controls are vacuous")
    require(rows[2]["accepted"] > 0 and rows[2]["repeated_low_cases"] > 0, "vacuous B domain")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true", help="explicitly regenerate RESULT.json")
    args = parser.parse_args()
    sources = live_sources()
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    require(compiler is not None, "C++17 compiler required")
    with tempfile.TemporaryDirectory(prefix="connector-capacity-audit-") as temp:
        executable = Path(temp) / "audit"
        run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
             str(HERE / "audit.cpp"), "-o", str(executable)], timeout=60)
        receipt = {"schema": "connector-capacity-parity-audit/v1", "sources": sources,
                   "historical_control": historical_control(),
                   "source_impact": source_impact(),
                   "native_domains": native_checks(executable),
                   "positive_controls": positive_and_gauge_controls(executable),
                   "python_controls": bounded_python_controls(executable),
                   "repeated_prefix_boundary": repeated_prefix_boundary(executable)}
    destination = HERE / "RESULT.json"
    if args.write_receipt:
        destination.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        require(receipt == json.loads(destination.read_text()), "receipt differs from fresh checks")
    cases = sum(row["cases"] for row in receipt["native_domains"])
    accepted = sum(row["accepted"] for row in receipt["native_domains"])
    print(f"PASS_CONNECTOR_CAPACITY_PARITY cases={cases} accepted={accepted} "
          "positive_projections=176 gauges=2816 python_queries=1282 repeated_prefix_control=1 no_full_census")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        raise SystemExit("FAIL_CONNECTOR_CAPACITY_PARITY " + str(error)) from error
