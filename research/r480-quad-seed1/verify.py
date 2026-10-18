#!/usr/bin/env python3
"""Exact local construction check; standard library, Python 3.9+.

Prepared for Hao Yan (@FanPUYen) with substantial OpenAI Codex assistance.
Apache-2.0. Source construction: DreamingOfClouds #503/#510 and eumemic #493.
No producer or predecessor checker is imported.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = "research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
SOURCE_SHA = "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def transfer(operations, n):
    """Rows are exact integer coefficients, without reduction modulo two."""
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in operations:
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def rank(lines):
    basis = {}
    for line in lines:
        row = list(map(Fraction, line))
        for pivot, old in sorted(basis.items()):
            c = row[pivot]
            row = [a - c * b for a, b in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            c = row[pivot]
            basis[pivot] = [x / c for x in row]
    return len(basis)


def validate_recipe(w, recipe):
    expected_keys = {
        "source", "source_sha256", "seed", "quad_index", "A_start", "A_end",
        "frame_id", "wires", "old_ops", "new_ops", "forward_matrix",
        "old_reverse_matrix", "new_reverse_matrix", "attempt", "coverage_before",
    }
    require(set(recipe) == expected_keys, "recipe fields")
    require(recipe["source"] == SOURCE and recipe["source_sha256"] == SOURCE_SHA,
            "recipe source binding")
    for key in ("seed", "quad_index", "A_start", "A_end", "frame_id", "attempt"):
        require(type(recipe[key]) is int, "recipe integer type: " + key)
    require((recipe["seed"], recipe["quad_index"], recipe["attempt"]) == (1, 1, 0),
            "seed/coverage binding")
    require(recipe["coverage_before"] == [], "search stopped at first quad")
    a, b, frame = recipe["A_start"], recipe["A_end"], recipe["frame_id"]
    require((a, b, frame) == (621, 639, 303), "quad location")
    wires = recipe["wires"]
    require(all(type(x) is int for x in wires), "wire integer types")
    require(wires == [487, 504, 550, 574, 598, 622], "quad wire binding")
    require(all(g[0] == frame and len(g[2]) == 1 for g in w["A"][a:b]),
            "source quad shape")
    index = {r: i for i, r in enumerate(wires)}
    original = [[index[d], index[s]] for _, d, src in w["A"][a:b] for s in src]
    for key in ("old_ops", "new_ops"):
        require(type(recipe[key]) is list, "operations list")
        for gate in recipe[key]:
            require(type(gate) is list and len(gate) == 2 and
                    all(type(i) is int and 0 <= i < 6 for i in gate) and gate[0] != gate[1],
                    "invalid XOR primitive")
    require(original == recipe["old_ops"], "source quad operations")
    replacement = recipe["new_ops"]
    require(len(replacement) == 12 < len(original) == 18, "strict gate saving")
    forward = transfer(original, 6)
    require(transfer(replacement, 6) == forward, "full integer forward transfer")
    old_reverse = transfer(original[::-1], 6)
    new_reverse = transfer(replacement[::-1], 6)
    require(all(x <= y for nr, old in zip(new_reverse, old_reverse)
                for x, y in zip(nr, old)), "reverse nonnegative majorization")
    for key, value in (("forward_matrix", forward),
                       ("old_reverse_matrix", old_reverse),
                       ("new_reverse_matrix", new_reverse)):
        require(type(recipe[key]) is list and len(recipe[key]) == 6 and
                all(type(row) is list and len(row) == 6 and
                    all(type(x) is int and x >= 0 for x in row) for row in recipe[key]),
                "matrix integer types")
        require(recipe[key] == value, "matrix certificate: " + key)
    return a, b, frame, wires


def construct(w, recipe):
    a, b, frame, wires = validate_recipe(w, recipe)
    out = copy.deepcopy(w)
    out["A"][a:b] = [[frame, wires[d], [wires[s]]] for d, s in recipe["new_ops"]]
    out["C"] = [[1, d, list(src)] for _, d, src in reversed(out["A"])]
    return out


def scalar_replay(w):
    n, v = 2 * w["v"] + w["R"], w["v"]
    state = [1 << i for i in range(n)]
    norm = [1] * n
    def gate(d, sources):
        for s in sources:
            state[d] ^= state[s]
            norm[d] += norm[s]
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for t, row in enumerate(w[phase]):
                gate(v + t, [w["ret"][k] for k in row])
        else:
            for _, d, src in w[phase]:
                gate(d, src)
    expected = [((1 << i) ^ (1 << (i - v))) if v <= i < 2 * v else 1 << i
                for i in range(n)]
    require(state == expected, "all-column endpoint / arbitrary dirt restoration")
    return {"columns": n, "unsigned_raw_peak": max(norm), "raw_norm_sha256": digest(norm)}


def paths(w):
    n, v = 2 * w["v"] + w["R"], w["v"]
    require(n == 720 and len(w["start"]) == n and len(w["final"]) == n, "dimensions")
    result = [[f] for f in w["start"]]
    frames = [set(row) for row in w["frames"]]
    def touch(r, f):
        require(type(r) is int and 0 <= r < n, "register index")
        require(type(f) is int and 0 <= f < len(frames), "frame index")
        old = result[r][-1]
        require(frames[old] <= frames[f], "frame descent")
        if old != f:
            result[r].append(f)
    for phase in ("D", "A", "B", "C"):
        for f, d, src in w[phase]:
            require(len(set([d] + src)) == 1 + len(src), "self-read / duplicate operand")
            for r in [d] + src:
                touch(r, f)
            if phase == "D":
                require(f == 0 and v <= d < 2 * v and all(s >= 2 * v for s in src),
                        "compensation interface")
            elif phase == "A":
                require(not v <= d < 2 * v and all(not v <= s < 2 * v for s in src),
                        "phase-A interface")
            elif phase == "B":
                require(v <= d < 2 * v and all(not v <= s < 2 * v for s in src),
                        "phase-B interface")
            else:
                require(f == 1 and all(not v <= r < 2 * v for r in [d] + src),
                        "cleanup interface")
    require(w["C"] == [[1, d, list(src)] for _, d, src in reversed(w["A"])],
            "literal reverse cleanup")
    require(len(w["ret"]) == 9 and len(set(w["ret"])) == 9 and
            all(2 * v <= r < n for r in w["ret"]), "retained helpers")
    require(len(w["scatter"]) == v and
            all(type(k) is int and 0 <= k < 9 for row in w["scatter"] for k in row),
            "scatter interface")
    for r, f in enumerate(w["final"]):
        touch(r, f)
    return result


def cost(w, path_list, dimensions):
    histogram = Counter({8: len(w["ret"])})  # nine copied retained totals
    for path in path_list:
        for lo, hi in zip(path, path[1:]):
            step = dimensions[hi] - dimensions[lo]
            require(step > 0, "positive climb")
            histogram[step] += 1
    xor = {p: sum(len(src) for _, _, src in w[p]) for p in ("D", "A", "B", "C")}
    xor["scatter"] = sum(map(len, w["scatter"]))
    return {"xor_by_phase": xor, "total_xors": sum(xor.values()),
            "paid_histogram": {str(k): n for k, n in sorted(histogram.items())},
            "rank_mass": sum(k * n for k, n in histogram.items())}


def rejected(action, name):
    try:
        action()
    except (ValueError, IndexError, KeyError, TypeError):
        return name
    raise ValueError("negative control unexpectedly accepted: " + name)


def controls(w, recipe, candidate):
    checks = []
    # Test the local integer transfer after each deletion. The independent
    # checker separately reflects these deletions into the literal cleanup.
    for i in range(len(recipe["new_ops"])):
        r = copy.deepcopy(recipe)
        del r["new_ops"][i]
        checks.append(rejected(lambda r=r: require(transfer(r["new_ops"], 6) ==
                         recipe["forward_matrix"], "changed matrix"), "omit_quad_gate_%d" % i))
    r = copy.deepcopy(recipe)
    r["new_ops"] = r["new_ops"][::-1]
    checks.append(rejected(lambda: validate_recipe(w, r), "reverse_gate_order"))
    r = copy.deepcopy(recipe)
    r["new_ops"][0][0] = True
    checks.append(rejected(lambda: validate_recipe(w, r), "boolean_as_integer"))
    r = copy.deepcopy(recipe)
    r["new_reverse_matrix"][0][0] += 1
    checks.append(rejected(lambda: validate_recipe(w, r), "false_reverse_certificate"))
    bad = copy.deepcopy(candidate)
    del bad["C"][0]
    checks.append(rejected(lambda: paths(bad), "missing_cleanup_structure"))
    checks.append(rejected(lambda: scalar_replay(bad), "missing_cleanup_dirt"))
    bad = copy.deepcopy(candidate)
    bad["D"][0][2].pop()
    checks.append(rejected(lambda: scalar_replay(bad), "missing_dirty_compensation"))
    bad = copy.deepcopy(candidate)
    bad["A"][recipe["A_start"]][0] = 0
    checks.append(rejected(lambda: paths(bad), "frame_zero_substitution"))
    bad = copy.deepcopy(candidate)
    bad["scatter"][0] = bad["scatter"][0][1:]
    checks.append(rejected(lambda: scalar_replay(bad), "missing_scatter_read"))
    return checks


def verify():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == "66849e1475c930fd7732b1a0067ffee7e1e95f60", "base pin")
    require(pins["files"][SOURCE] == SOURCE_SHA, "word pin")
    for name, wanted in pins["files"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == wanted,
                "source drift: " + name)
    w = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    recipe = json.loads((HERE / "recipe.json").read_text())
    candidate = construct(w, recipe)
    require(all(candidate[k] == value for k, value in w.items() if k not in ("A", "C")),
            "unrelated word fields changed")
    baseline_paths, candidate_paths = paths(w), paths(candidate)
    require(baseline_paths == candidate_paths, "all register frame paths unchanged")
    used_frames = {f for path in baseline_paths for f in path}
    dimensions = {f: rank([w["lines"][i] for i in w["frames"][f]]) for f in used_frames}
    require(dimensions[303] == 4, "quad rational rank")
    old_cost, new_cost = cost(w, baseline_paths, dimensions), cost(candidate, candidate_paths, dimensions)
    require(old_cost["paid_histogram"] == new_cost["paid_histogram"], "paid profile unchanged")
    old_scalar, new_scalar = scalar_replay(w), scalar_replay(candidate)
    require(new_scalar["unsigned_raw_peak"] <= old_scalar["unsigned_raw_peak"], "raw magnitude bound")
    require(old_cost["total_xors"] - new_cost["total_xors"] == 12, "complete saving")
    control_names = controls(w, recipe, candidate)
    evidence = {
        "status": "PASS_R480_QUAD_SEED1", "base_commit": pins["base_commit"],
        "source_word_sha256": SOURCE_SHA, "candidate_content_sha256": digest(candidate),
        "recipe_sha256": digest(recipe), "frame_paths_sha256": digest(candidate_paths),
        "quad": {"index": 1, "frame": 303, "rational_rank": dimensions[303],
                 "old_gates": 18, "new_gates": 12,
                 "reverse_strict_entries": sum(x < y for nr, old in zip(recipe["new_reverse_matrix"],
                         recipe["old_reverse_matrix"]) for x, y in zip(nr, old))},
        "baseline": {"cost": old_cost, "scalar": old_scalar},
        "candidate": {"cost": new_cost, "scalar": new_scalar},
        "negative_controls": control_names,
        "scope": "Finite circuit construction; unchanged paid profile; no new kappa or all-size proof.",
    }
    return evidence, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write deterministic candidate word and evidence here")
    parser.add_argument("--write-certificate", action="store_true", help="deliberately regenerate EXPECTED.json")
    args = parser.parse_args()
    evidence, candidate = verify()
    formatted = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.write_certificate:
        (HERE / "EXPECTED.json").write_text(formatted)
    else:
        require((HERE / "EXPECTED.json").read_text() == formatted, "exact evidence certificate")
    if args.out:
        out = args.out.resolve()
        require(not out.is_relative_to(HERE) if hasattr(out, "is_relative_to") else HERE not in out.parents,
                "output must be outside the package")
        out.mkdir(parents=True, exist_ok=True)
        (out / "word.json").write_bytes(canonical(candidate) + b"\n")
        with (out / "word.json.gz").open("wb") as stream:
            with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as zipped:
                zipped.write(canonical(candidate))
        (out / "evidence.json").write_text(formatted)
    print("PASS_R480_QUAD_SEED1 quad=1 XORs=33958->33946 saved=12 columns=720 controls=%d kappa=unchanged"
          % len(evidence["negative_controls"]))


if __name__ == "__main__":
    main()
