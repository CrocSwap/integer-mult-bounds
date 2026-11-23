#!/usr/bin/env python3
"""Reproduce the exact architecture screens using Python's stdlib and C++17.

No optimizer, network access, supplier checkout or vector-code solver runs.
--deep adds the independent Python replay of the 16 prescribed-terminal
negative cases; the default already exhausts all permutations on all 87
topologies in C++ and checks its matching method against direct enumeration.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import audit
import center_basis

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "discovery"))
from fano_reuse import topologies
from balanced_fano import execute


def need(condition, message):
    if not condition:
        raise ValueError(message)


def manifest():
    paths = [p for p in HERE.rglob("*") if p.is_file() and p.name != "SOURCE.json"
             and "__pycache__" not in p.parts and p.suffix in (".py", ".cpp", ".md", ".json")]
    # The reference provenance itself is an input, not this manifest.
    paths.append(HERE / "references/SOURCE.json")
    paths.append(HERE / "NOTICE")
    return {"files": {p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
                      for p in sorted(set(paths))},
            "scope": "This self-contained package only; inherited whole-algorithm interfaces are not discharged."}


def line(identifier, width, pairs):
    values = [identifier, width, len(pairs), 0] + [v for pair in pairs for v in pair]
    return " ".join(map(str, values))


def run_binary(binary, cases):
    text = "\n".join(line(c["id"], c["W"], c["pairs"]) for c in cases) + "\n"
    done = subprocess.run([str(binary), "--all-permutations"], input=text,
                          text=True, capture_output=True, check=True)
    rows = [json.loads(s) for s in done.stdout.splitlines()]
    need([r["id"] for r in rows] == [c["id"] for c in cases], "Missing, duplicate or reordered search case")
    return rows


def brute_control(case):
    width, pairs = case["W"], case["pairs"]
    routes = {tuple(range(width))}
    for a, b in pairs:
        next_routes = set(routes)
        for permutation in routes:
            new = list(permutation)
            new[a], new[b] = new[b], new[a]
            next_routes.add(tuple(new))
        routes = next_routes
    actual = set()
    words = 0
    for choices in product(range(6), repeat=len(pairs)):
        rows = execute(width, pairs, choices)
        if sorted(rows) != [1 << j for j in range(width)]:
            continue
        words += 1
        actual.add(tuple(row.bit_length() - 1 for row in rows))
    return {"routes": len(routes), "scalar_permutations": len(actual),
            "matching_full_words": words, "outside_routing": bool(actual - routes)}


def controls(binary):
    specs = [(3, []), (3, [(0, 1)]), (4, [(0, 1), (2, 3)]),
             (4, [(0, 1), (1, 2), (2, 3)]),
             (4, [(0, 1), (1, 2), (0, 2), (2, 3)]),
             (4, [(0, 1), (1, 2), (2, 3), (0, 3), (1, 3)]),
             (5, [(0, 1), (2, 3), (1, 4), (0, 2), (3, 4)]),
             (5, [(0, 4), (1, 4), (2, 4), (3, 4), (0, 4)])]
    cases = [{"id": 1000 + i, "W": w, "pairs": pairs} for i, (w, pairs) in enumerate(specs)]
    results = run_binary(binary, cases)
    for case, observed in zip(cases, results):
        expected = brute_control(case)
        need(observed["routing_permutations"] == expected["routes"], "Routing disagrees with direct enumeration")
        need(observed["nonroutable_scalar_permutation"] == expected["outside_routing"], "Incorrect routing comparison")
        if not observed.get("all_permutations_routable"):
            need(observed["scalar_permutations"] == expected["scalar_permutations"], "Lost scalar permutations")
            need(observed["matching_full_words"] == expected["matching_full_words"], "Lost matching complete words")
    return {"direct_full_word_controls": len(cases), "all_passed": True}


def all_fano(binary):
    cases = list(topologies())
    need(len(cases) == 87, "The finite topology family changed")
    results = run_binary(binary, cases)
    for result in results:
        need(not result["nonroutable_scalar_permutation"], "A nonroutable scalar candidate needs a frame investigation")
        if not result.get("all_permutations_routable"):
            need(result["prefix_assignments"] == result["suffix_assignments"] == 6**7,
                 "An enumeration half is incomplete")
            need(result["scalar_permutations"] == result["routing_permutations"], "Unexpected permutation-set count")
    return {"status": "ALL COMPLETED SCALAR PERMUTATIONS ARE ROUTABLE IN THIS FINITE FAMILY",
            "topologies": len(cases), "width_counts": dict(sorted(Counter(c["W"] for c in cases).items())),
            "topology_specification_sha256": sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest(),
            "results": results,
            "scope": "All 87 chronological balanced-Fano stub reuses; all local GL(2,F2) gates; every full output permutation, including arbitrary auxiliary/data exchanges. This does not cover vector gates or other graphs."}


def compare(name, value, writing):
    content = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path = HERE / name
    if writing:
        path.write_text(content)
    else:
        need(path.read_text() == content, "Regenerated certificate differs: " + name)


def main():
    need(not sys.flags.optimize, "Run without -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--deep", action="store_true")
    args = parser.parse_args()
    before = manifest()
    if not args.write:
        need(before == json.loads((HERE / "SOURCE.json").read_text()), "Package source closure changed")
    compare("ceiling-certificate.json", audit.certificate(), args.write)
    compare("center-basis-certificate.json", center_basis.certificate(), args.write)
    print("PASS exact data/family ceilings and the sharp rank-minimal center controls", flush=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, "-B", str(HERE / "test_audit.py")], check=True, env=env)
    with tempfile.TemporaryDirectory(prefix="percent-exponent-check-") as directory:
        binary = Path(directory) / "balanced-search"
        subprocess.run([os.environ.get("CXX", "c++"), "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror",
                        str(HERE / "discovery/balanced_search.cpp"), "-o", str(binary)], check=True)
        compare("enumeration-controls.json", controls(binary), args.write)
        compare("fano-all-permutations.json", all_fano(binary), args.write)
    print("PASS all 87 topologies and all scalar permutations; independent full-word controls", flush=True)
    if args.deep:
        command = [sys.executable, "-B", str(HERE / "fano_reuse_verify.py")]
        if args.write:
            command.append("--write")
        subprocess.run(command, check=True, env=env)
    if args.write:
        (HERE / "SOURCE.json").write_text(json.dumps(manifest(), sort_keys=True, indent=2) + "\n")
    else:
        need(manifest() == before, "Verification changed package inputs")
    print("PASS conditional architecture audit; no new multiplication exponent", flush=True)


if __name__ == "__main__":
    main()
