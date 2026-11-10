"""Pin the primary scan compiler and compare a separately written FIFO oracle.

This is finite semantic corroboration, not timing or a full CRT evaluator.
"""
import hashlib
from itertools import permutations
import json
from pathlib import Path
from random import Random
import sys
import types


PRIMARY_SHA256 = "e8ff7800ffa267d2825009656b78ab1613544b55301982744ec0d99f38800913"
ORACLE_SHA256 = "7a58689072b730201a6b4007f7b2524db2abff460a3116cfa42821fb2e1b63a5"


def load(path, name, expected=None):
    path = Path(path)
    data = path.read_bytes()
    if expected is not None and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("reviewed primary code changed")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def main():
    primary = load(sys.argv[1], "_pinned_primary_benes", PRIMARY_SHA256)
    independent = load(sys.argv[2], "_preimplementation_fifo_benes", ORACLE_SHA256)
    cases = []
    for n in (2, 4):
        cases.extend((tuple(p), n.bit_length() - 1) for p in permutations(range(n)))
    rng = Random(4100)
    for n, count in ((8, 8), (16, 2)):
        for _ in range(count):
            permutation = list(range(n))
            rng.shuffle(permutation)
            cases.append((tuple(permutation), n.bit_length() - 1))
    cases.append(((0, 2, 1, 3), 7))
    count = columns = queries = 0
    digest = hashlib.sha256()
    for permutation, p in cases:
        n = len(permutation)
        h = n.bit_length() - 1
        expected = independent.compile_levelwise(permutation)
        encoded = b"".join(primary.word(x, h) for x in permutation)
        network, invoice = primary.compile_stream(encoded, h, p)
        actual = tuple(primary.unpack(network, h))
        if actual != expected:
            raise ValueError("primary tables differ from separate FIFO compiler")
        if invoice["arena_records"] != n * (h * h + 3 * h + 1):
            raise ValueError("all-node storage census mismatch")
        accesses = n * n + 2 * n * h * h + (37 * n * h - 35 * n) // 2
        if invoice["logical_accesses"] != accesses:
            raise ValueError("independently derived access census mismatch")
        for x, image in enumerate(permutation):
            if independent.endpoint(actual, x) != image:
                raise ValueError("direct permutation endpoint mismatch")
            if independent.endpoint(tuple(reversed(actual)), image) != x:
                raise ValueError("reverse-layer inverse endpoint mismatch")
        for layer, (_, table) in enumerate(expected):
            for address, wanted in enumerate(table):
                answer, _ = primary.query_stream(network, h, layer, address)
                if int(bytes(answer.data), 2) != wanted:
                    raise ValueError("queried bit differs from separate oracle")
                queries += 1
        digest.update(bytes(network.data))
        count += 1
        columns += n
    print(json.dumps({"status": "PASS_PRIMARY_VS_PREIMPLEMENTATION_ORACLE",
                      "cases": count, "endpoint_columns": columns,
                      "control_queries": queries, "owned_tables_sha256": digest.hexdigest(),
                      "primary_sha256": PRIMARY_SHA256,
                      "oracle_sha256": ORACLE_SHA256,
                      "scope": "source-pinned finite compiler/query equivalence and forward/reverse endpoints; not an asymptotic timing proof"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
