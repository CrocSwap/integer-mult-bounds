"""Exact finite routing, serialization and failure-mode certificate.

Produced by Nick Petalas. Apache-2.0. No predecessor verifier is executed.
"""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("compact_router", HERE / "router.py")
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def topology(height):
    """Independent recursive-topology expansion, with an explicit worklist."""
    n = 1 << height
    layers = [[] for _ in range(2 * height - 1)]
    stack = [(0, tuple(range(n)))]
    for _ in range(n - 1):
        depth, wires = stack.pop()
        pairs = list(zip(wires[::2], wires[1::2]))
        layers[depth].extend((a, b, True) for a, b in pairs)
        if len(wires) > 2:
            last = len(layers) - 1 - depth
            layers[last].extend((a, b, i != len(pairs) - 1)
                                for i, (a, b) in enumerate(pairs))
            stack.append((depth + 1, wires[1::2]))
            stack.append((depth + 1, wires[::2]))
    require(not stack, "oracle node exhaustion")
    return tuple(tuple(sorted(row)) for row in layers)


def check_addresses(height, network):
    n = 1 << height
    cursor, forced = 0, 0
    _, _, size = router.dimensions(height)
    pattern = tuple(i % 2 for i in range(size))
    for layer, row in enumerate(network):
        for a, b, stored in row:
            expected = cursor if stored else None
            require(router.address(height, layer, a) == expected,
                    "first wire compact address")
            require(router.address(height, layer, b) == expected,
                    "second wire compact address")
            if stored:
                cursor += 1
            else:
                forced += 1
        for wire in (0, n - 1):
            a, b, stored = next(record for record in row if wire in record[:2])
            index = router.address(height, layer, a)
            expected_bit = 0 if not stored else pattern[index]
            require(router.query(height, pattern, layer, wire) == expected_bit,
                    "validated query returns the dense control")
    require(cursor == n * height - n + 1, "compact size")
    require(forced == n // 2 - 1, "deleted distinct-switch records")
    return cursor, forced


def explicit_endpoint(network, rom):
    """Use enumerated records, independently of the address formula."""
    n = 2 * len(network[0])
    values = list(range(n))
    cursor = 0
    for row in network:
        for a, b, stored in row:
            if stored:
                if rom[cursor]:
                    values[a], values[b] = values[b], values[a]
                cursor += 1
    require(cursor == len(rom), "oracle reads all stored bits")
    return tuple(values)


def check_packed(height, network, rom):
    data = router.pack_rom(height, rom)
    require(len(data) == (len(rom) + 7) // 8, "canonical byte payload length")
    cursor, queries = 0, 0
    for layer, row in enumerate(network):
        for a, b, stored in row:
            expected = rom[cursor] if stored else 0
            for wire in (a, b):
                require(router.query_packed(height, data, layer, wire) == expected,
                        "packed query equals the explicit dense control")
                queries += 1
            cursor += int(stored)
    require(cursor == len(rom), "packed oracle reads all controls")
    return queries


def check_permutation(permutation, network, digest):
    original = tuple(permutation)
    rom = router.compile_rom(permutation)
    require(tuple(permutation) == original, "borrowed permutation unchanged")
    endpoint = explicit_endpoint(network, rom)
    expected = [None] * len(permutation)
    for source, target in enumerate(permutation):
        expected[target] = source
    require(endpoint == tuple(expected), "all labeled endpoint columns")
    height = len(permutation).bit_length() - 1
    dirty = tuple(((-1) ** i * (i + 3), i % 3) for i in range(len(permutation)))
    routed = router.apply_rom(height, rom, dirty)
    require(routed == tuple(dirty[source] for source in endpoint),
            "arbitrary dirty payload permutation")
    inverse_rom = router.compile_rom(expected)
    require(router.apply_rom(height, inverse_rom, routed) == dirty,
            "inverse permutation restores every dirty wire")
    digest.update(bytes(permutation) if len(permutation) <= 256
                  else json.dumps(permutation).encode())
    digest.update(bytes(rom))
    return check_packed(height, network, rom)


def rejection_controls():
    bad = [(), (0,), (0, 1, 2), (0, 0), (0, 2), (False, 1)]
    rejected = 0
    for permutation in bad:
        try:
            router.compile_rom(permutation)
        except ValueError:
            rejected += 1
    for height, rom, layer, wire in [
        (0, (), 0, 0), (13, (), 0, 0), (1, (), 0, 0),
        (1, (2,), 0, 0), (1, (True,), 0, 0),
        (1, (0,), 1, 0), (1, (0,), 0, 2), (1, (0,), -1, 0),
    ]:
        try:
            router.query(height, rom, layer, wire)
        except ValueError:
            rejected += 1
    require(rejected == len(bad) + 8, "all malformed inputs rejected")
    for data in (b"", b"\x02", bytearray(b"\x00")):
        try:
            router.query_packed(1, data, 0, 0)
        except ValueError:
            rejected += 1
    require(rejected == len(bad) + 11, "invalid packed controls rejected")
    network = topology(3)
    rom = router.compile_rom(tuple(range(8)))
    mutants = 0
    for i in range(len(rom)):
        changed = list(rom)
        changed[i] ^= 1
        require(explicit_endpoint(network, changed) != tuple(range(8)),
                "control-bit mutation changes an observed endpoint")
        mutants += 1
    return {"invalid_inputs": rejected, "single_bit_mutants": mutants}


def run():
    digest = hashlib.sha256()
    cases = []
    for n in (2, 4, 8):
        height = n.bit_length() - 1
        network = topology(height)
        size, forced = check_addresses(height, network)
        count, queries = 0, 0
        for permutation in itertools.permutations(range(n)):
            queries += check_permutation(permutation, network, digest)
            count += 1
        cases.append({"wires": n, "permutations": count,
                      "stored_bits": size, "deleted_switches": forced,
                      "packed_dense_queries": queries})
    larger = []
    for height in range(4, 13):
        n = 1 << height
        network = topology(height)
        size, forced = check_addresses(height, network)
        samples = [tuple(range(n)), tuple(reversed(range(n))),
                   tuple((i + 1) % n for i in range(n)),
                   tuple((3 * i + 5) % n for i in range(n))]
        queries = 0
        for permutation in samples:
            queries += check_permutation(permutation, network, digest)
        larger.append({"height": height, "wires": n, "permutations": len(samples),
                       "stored_bits": size, "deleted_switches": forced,
                       "packed_dense_queries": queries})
    controls = rejection_controls()
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "router.py", "verify.py")
    hashes = {}
    for name in names:
        path = HERE / name
        require(path.stat().st_size <= 1 << 20, "package file size bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"status": "PASS_COMPACT_WAKSMAN_ROW_ROM", "small_cases": cases,
            "larger_cases": larger, "controls": controls,
            "ordered_census_sha256": digest.hexdigest(), "package_sha256": hashes,
            "claim_type": "constructive implementation and scoped proof",
            "selected_frontier_changed": False}


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "only --emit is supported")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print(json.dumps(result, sort_keys=True, indent=2))
        small = sum(case["permutations"] for case in result["small_cases"])
        large = sum(case["permutations"] for case in result["larger_cases"])
        controls = sum(result["controls"].values())
        print(result["status"], f"permutations={small} larger={large}",
              f"controls={controls} no_new_kappa")


if __name__ == "__main__":
    main()
