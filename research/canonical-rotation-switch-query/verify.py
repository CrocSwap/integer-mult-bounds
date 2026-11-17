"""Finite corroboration of the new point-query construction. Apache-2.0.

Produced by Nick Petalas. No predecessor replay entry point is invoked.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from rotation_query import child_parameters, endpoint_bit, require, switch_bit


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REFERENCE = "research/unconditional-batched-crt/check_batched_crt.py"


def load_reference():
    """Authenticate the exact canonical definition used as the comparison oracle."""
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [row for row in pins["files"] if row["path"] == REFERENCE]
    require(len(rows) == 1 and rows[0]["usage"] == "input", "one live source pin")
    for row in pins["files"]:
        if row["usage"] == "input":
            require(row["path"] in (REFERENCE, "research/unconditional-batched-crt/NOTICE.md"),
                    "fixed canonical input paths")
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "canonical input source hash")
    path = ROOT / REFERENCE
    spec = importlib.util.spec_from_file_location("canonical_rotation_reference", path)
    require(spec is not None and spec.loader is not None, "reference loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def root_check(permutation, modulus, offset, layers):
    """Extract the actual child permutations, without using the new recurrence."""
    size = len(permutation)
    color = tuple(layers[0][1][x] ^ (x & 1) for x in range(size))
    for last in (False, True):
        row = layers[-1 if last else 0][1]
        require(tuple(endpoint_bit(modulus, offset, x, last) for x in range(size)) == row,
                "endpoint formula")
    for branch in (0, 1):
        actual = [None] * (size // 2)
        for x in range(size):
            if color[x] == branch:
                require(actual[x // 2] is None, "one child source per pair")
                actual[x // 2] = permutation[x] // 2
        child_modulus, child_offset = child_parameters(modulus, offset, branch)
        expected = tuple((x + child_offset) % child_modulus if x < child_modulus else x
                         for x in range(size // 2))
        require(tuple(actual) == expected, "padded-rotation child closure")


def finite_census(reference):
    networks, entries, routes, roots = 0, 0, 0, 0
    for h in range(1, 6):
        size = 1 << h
        for modulus in range(1, size + 1):
            for offset in range(modulus):
                permutation = reference.rotation(size, modulus, offset)
                layers = reference.benes(permutation)
                if h > 1:
                    root_check(permutation, modulus, offset, layers)
                    roots += 1
                for layer, (_, row) in enumerate(layers):
                    for address, expected in enumerate(row):
                        require(switch_bit(h, modulus, offset, layer, address) == expected,
                                "direct bit equals the canonical source bit")
                        entries += 1
                for original in range(size):
                    current = original
                    for layer in range(2 * h - 1):
                        axis = min(layer, 2 * h - 2 - layer)
                        current ^= switch_bit(h, modulus, offset, layer, current) << axis
                    require(current == permutation[original], "direct-query endpoint")
                    routes += 1
                networks += 1
    return {"networks": networks, "switch_entries": entries,
            "routed_addresses": routes, "root_decompositions": roots}


def rejection_controls():
    invalid = ((0, 1, 0, 0, 0), (4097, 1, 0, 0, 0), (2, 0, 0, 0, 0),
               (2, 5, 0, 0, 0), (2, 3, -1, 0, 0), (2, 3, 3, 0, 0),
               (2, 3, 0, -1, 0), (2, 3, 0, 3, 0), (2, 3, 0, 0, -1),
               (2, 3, 0, 0, 4), (True, 1, 0, 0, 0), (2, 3.0, 0, 0, 0))
    for parameters in invalid:
        try:
            switch_bit(*parameters)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    require(switch_bit(2, 3, 1, 0, 2) != 0, "odd boundary swap cannot be dropped")
    require(switch_bit(3, 5, 1, 4, 5) != int(5 < 5), "padded last-row switch matters")
    require(child_parameters(5, 1, 0) != (3, 0), "odd children cannot be interchanged")
    require(child_parameters(6, 5, 1) == (3, 0), "child offset needs equality reduction")
    require(child_parameters(5, 1, 1) != (3, 0), "branch carry cannot be dropped")
    require(switch_bit(3, 5, 1, 1, 5) != switch_bit(3, 5, 1, 1, 4),
            "table query follows the address's low branch bit")
    return {"domain_rejections": len(invalid), "semantic_controls": 6}


def large_width_checks():
    checked = 0
    for h in (31, 65, 127, 1024, 4096):
        modulus = (1 << h) - 1
        require(switch_bit(h, modulus, 1, 0, modulus) == 1, "large padded first row")
        require(switch_bit(h, modulus, 2, 2 * h - 2, 0) == 1, "large last row")
        require(switch_bit(h, modulus, 0, h - 1, modulus) == 0, "large identity")
        require(switch_bit(h, 1 << h, 1 << (h - 1), h - 1, 0) == 1,
                "full-depth query reaches the nonzero dyadic leaf")
        checked += 4
    return checked


def evidence():
    reference = load_reference()
    result = finite_census(reference)
    result.update(rejection_controls())
    result["large_width_queries"] = large_width_checks()
    bits = bytes(switch_bit(5, 17, a, 6, x) for a in range(17) for x in range(32))
    result["h5_s17_layer6_bits"] = len(bits)
    result["h5_s17_layer6_sha256_bit_bytes"] = hashlib.sha256(bits).hexdigest()
    files = sorted(path for path in PACKAGE.iterdir() if path.is_file())
    result["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in files}
    result["reference_sha256"] = hashlib.sha256((ROOT / REFERENCE).read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = evidence()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        target = args.receipt.expanduser().resolve()
        require(ROOT not in target.parents, "receipt must be outside the checkout")
        target.write_text(payload)
    print(payload, end="")
    print("PASS_CANONICAL_ROTATION_SWITCH_QUERY")


if __name__ == "__main__":
    main()
