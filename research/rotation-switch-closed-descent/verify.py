"""Check the new query against the retained canonical network and recurrence.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random

from query import MAX_HEIGHT, endpoint, interval_pair, require, switch_bit

PACKAGE = Path(__file__).resolve().parent


def load_sources():
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    for row in pins:
        require(hashlib.sha256((PACKAGE / row["path"]).read_bytes()).hexdigest()
                == row["sha256"], "retained source hash")
    modules = []
    for name, path in [("canonical", "retained/pr4100/check_batched_crt.py"),
                       ("recursive", "retained/pr7504/rotation_query.py")]:
        spec = importlib.util.spec_from_file_location(name, PACKAGE / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def wrong_query(h, s, a, j, x, change):
    depth = min(j, 2 * h - 2 - j)
    mask = (1 << depth) - 1
    tail = x & mask
    left, right = interval_pair(s, a, depth, x)
    if change == "wrong complement":
        right = (s - a + tail) >> depth
    elif change == "lost carry":
        left = a >> depth
    elif change == "wrong path":
        left, right = interval_pair(s, a, depth, x >> depth)
    elif change == "unshifted wire":
        return endpoint(left, right, x, h - depth, j != depth)
    elif change == "lost identity":
        right = max(1, right)
    return endpoint(left, right, x >> depth, h - depth, j != depth)


def census(canonical, recursive):
    totals = {"networks": 0, "canonical_entries": 0, "recursive_entries": 0,
              "routed_addresses": 0, "descent_states": 0}
    changes = ("wrong complement", "lost carry", "wrong path",
               "unshifted wire", "lost identity")
    witnesses = {}
    digest = hashlib.sha256()
    for h in range(1, 7):
        size = 1 << h
        for s in range(1, size + 1):
            for a in range(s):
                permutation = canonical.rotation(size, s, a)
                layers = canonical.benes(permutation)
                for j, (_, row) in enumerate(layers):
                    for x, expected in enumerate(row):
                        args = h, s, a, j, x
                        bit = switch_bit(*args)
                        require(bit == expected, "canonical table mismatch")
                        require(bit == recursive.switch_bit(*args), "recursive query mismatch")
                        digest.update(bytes((bit,)))
                        totals["canonical_entries"] += 1
                        totals["recursive_entries"] += 1
                        for change in changes:
                            if change not in witnesses and wrong_query(*args, change) != expected:
                                witnesses[change] = {"query": list(args), "expected": expected,
                                                     "mutant": wrong_query(*args, change)}
                for original in range(size):
                    current = original
                    for j in range(2 * h - 1):
                        current ^= switch_bit(h, s, a, j, current) << min(j, 2*h-2-j)
                    require(current == permutation[original], "routed endpoint mismatch")
                    totals["routed_addresses"] += 1
                    left, right = a, s - a
                    child_s, child_a = s, a
                    for depth in range(h):
                        require(interval_pair(s, a, depth, original) == (left, right),
                                "closed interval pair mismatch")
                        if left and right:
                            require((child_s, child_a) == (left + right, left),
                                    "nonidentity child mismatch")
                        else:
                            require(child_a == 0, "identity child mismatch")
                        totals["descent_states"] += 1
                        branch = (original >> depth) & 1
                        left, right = (left + branch) // 2, (right + 1 - branch) // 2
                        child_s, child_a = recursive.child_parameters(child_s, child_a, branch)
                totals["networks"] += 1
    require(set(witnesses) == set(changes), "undetected semantic mutation")
    totals.update(table_sha256=digest.hexdigest(), semantic_mutants=witnesses)
    return totals


def domain_controls():
    cases = [(0, 1, 0, 0, 0), (MAX_HEIGHT+1, 1, 0, 0, 0),
             (2, 0, 0, 0, 0), (2, 5, 0, 0, 0), (2, 3, -1, 0, 0),
             (2, 3, 3, 0, 0), (2, 3, 0, -1, 0), (2, 3, 0, 3, 0),
             (2, 3, 0, 0, -1), (2, 3, 0, 0, 4),
             (True, 1, 0, 0, 0), (2, 3.0, 0, 0, 0)]
    for case in cases:
        try:
            switch_bit(*case)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    return len(cases)


def wide_checks(recursive):
    rng = random.Random(6107504)
    queries = 0
    for h in (7, 31, 65, 127, 511, 1024, 4096):
        for _ in range(60):
            s = rng.randrange(1, (1 << h) + 1)
            args = h, s, rng.randrange(s), rng.randrange(2*h-1), rng.getrandbits(h)
            require(switch_bit(*args) == recursive.switch_bit(*args), "wide source query")
            queries += 1
    sensitivity = 0
    for h in (2, 3, 17, 129, 4096):
        s = (1 << h) - 1
        require(switch_bit(h, s, 0, 2*h-2, 0) == 0, "lower-bound base input")
        for k in range(1, h):
            require(switch_bit(h, s, 1 << k, 2*h-2, 0) == 1,
                    "lower-bound one-bit neighbor")
            sensitivity += 1
    minimal_sensitivity = 0
    for h in (3, 17, 129, 4096):
        s, a = (1 << h) - 1, 1 << (h - 1)
        require(switch_bit(h, s, a, 2*h-2, a) == 0, "minimal-encoding base input")
        for k in range(1, h - 1):
            require(switch_bit(h, s, a + (1 << k), 2*h-2, a) == 1,
                    "minimal-encoding one-bit neighbor")
            minimal_sensitivity += 1
    for h in (8192, MAX_HEIGHT):
        require(switch_bit(h, (1 << h)-1, 1, 0, (1 << h)-1) == 1,
                "large padded boundary")
        require(switch_bit(h, 1 << h, 1 << (h-1), h-1, 0) == 1,
                "large nonidentity center")
        require(switch_bit(h, (1 << h)-1, 0, h-1, 0) == 0,
                "large identity center")
    return {"wide_recursive_queries": queries, "one_bit_sensitivity_checks": sensitivity,
            "minimal_encoding_sensitivity_checks": minimal_sensitivity,
            "queries_beyond_source_cap": 6}


def calculate():
    canonical, recursive = load_sources()
    result = census(canonical, recursive)
    result.update(wide_checks(recursive))
    result["domain_rejections"] = domain_controls()
    bits = bytes(switch_bit(5, 17, a, 6, x) for a in range(17) for x in range(32))
    result["h5_s17_layer6_entries"] = len(bits)
    result["h5_s17_layer6_sha256"] = hashlib.sha256(bits).hexdigest()
    result["scope"] = "O(h) arithmetic bit query; no physical caller or new kappa"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "result mismatch")
    print("PASS_ROTATION_SWITCH_CLOSED_DESCENT optimal O(h) bit query")


if __name__ == "__main__":
    main()
