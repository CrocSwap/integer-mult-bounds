"""Verify the new selector, packed bank and relabelled paths. Apache-2.0."""

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank import (BANK_BYTES, REPRESENTATIVES, SELECTORS, STATES, TABLE_BYTES,
                  output_map, pack, pair_index, require, run, selector, transition)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAPS = ((0, 1, 2, 3), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0),
        (0, 2, 1, 3), (1, 3, 0, 2), (2, 0, 3, 1), (3, 1, 2, 0))


def source_tables() -> tuple:
    """Load authenticated source bytes, bypassing any bytecode cache.

    This fixed, hash-bound module load is the only dynamic-code exception.
    Only make() is called; the predecessor's main verifier is never called.
    """
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    source = ROOT / "research/paired-residue-sampler/verify.py"
    authenticated = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash")
            authenticated[row["path"]] = raw
    namespace = {"__file__": str(source), "__name__": "paired_source"}
    raw = authenticated["research/paired-residue-sampler/verify.py"]
    exec(compile(raw, str(source), "exec"), namespace)
    # The inherited weights, depth counts and exact means are not audit targets.
    return tuple(namespace["make"](a, b)[2] for a, b in REPRESENTATIVES)


def weights(a: int, b: int) -> tuple:
    return ((13 - a) * (13 - b), (13 - a) * b, a * (13 - b), a * b)


def validate(payload: bytes, tables: tuple) -> dict:
    require(type(payload) is bytes and len(payload) == BANK_BYTES, "bank length")
    orbits = Counter()
    edges = 0
    for a in range(1, 13):
        for b in range(1, 13):
            code = payload[pair_index(a, b)]
            require(code < 168, "selector code")
            table_id, flags = divmod(code, 8)
            representative = REPRESENTATIVES[table_id]
            mapped = [0] * 4
            for label, weight in enumerate(weights(*representative)):
                mapped[MAPS[flags][label]] = weight
                require(output_map(flags, label) == MAPS[flags][label], "output map")
            require(tuple(mapped) == weights(a, b), "selector product law")
            orbits[representative] += 1
            for state, row in enumerate(tables[table_id]):
                for coin, target in enumerate(row):
                    expected = target if target < STATES else STATES + MAPS[flags][target - STATES]
                    require(transition(payload, code, state, coin) == expected, "packed edge")
                    edges += 1
    require(len(orbits) == 21, "all canonical tables used")
    require(Counter(orbits.values()) == {4: 6, 8: 15}, "signed-exchange orbits")
    return {"selectors": SELECTORS, "canonical_tables": 21, "checked_edges": edges,
            "orbit_size_histogram": {str(k): v for k, v in sorted(Counter(orbits.values()).items())}}


def leaf_paths(table: tuple) -> tuple:
    """Shortest terminating fixtures. The queue visits at most 312 states."""
    paths = {0: ()}
    queue = deque([0])
    leaves = {}
    for _ in range(STATES):
        if not queue:
            break
        state = queue.popleft()
        for coin, target in enumerate(table[state]):
            path = paths[state] + (coin,)
            if target >= STATES:
                leaves.setdefault(target - STATES, path)
            elif target not in paths:
                paths[target] = path
                queue.append(target)
    require(not queue and len(leaves) == 4, "complete fixture traversal")
    return tuple(leaves[label] for label in range(4))


def path_checks(payload: bytes, tables: tuple) -> dict:
    fixtures = tuple(leaf_paths(table) for table in tables)
    cases = 0
    for a in range(1, 13):
        for b in range(1, 13):
            code = payload[pair_index(a, b)]
            table_id, flags = divmod(code, 8)
            for label, path in enumerate(fixtures[table_id]):
                expected = (MAPS[flags][label], len(path))
                require(run(payload, a, b, path + (0, 1, 0)) == expected, "first stop and label")
                require(run(payload, a, b, path[:-1]) == (None, len(path) - 1), "unfinished prefix")
                cases += 1
            require(run(payload, a, b, (1,) * 312) == (None, 312), "phase-wrap continuation")
    # A seven-step literal source rule illustrates the changed coin-to-label contract.
    tape = (1, 1, 1, 1, 1, 0, 0)
    residues, node, original = weights(12, 2), 0, None
    for used, coin in enumerate(tape, 1):
        node = 2 * node + coin
        for label, residue in enumerate(residues):
            node -= 2 * residue // 169
            if node < 0:
                original = label, used
                break
        if original is not None:
            break
        residues = tuple(2 * residue % 169 for residue in residues)
    require(original == (1, 7), "original label witness")
    require(run(payload, 12, 2, tape) == (2, 7), "changed label witness")
    return {"terminating_paths": cases, "unfinished_prefixes": cases,
            "two_period_continuations": 144,
            "changed_function_witness": {"pair": [12, 2], "tape": "1111100",
                                         "original_label": 1, "bank_label": 2, "stopping_depth": 7}}


def rejected(operation, reason: str) -> None:
    try:
        operation()
    except ValueError as error:
        require(str(error) == reason, "wrong rejection reason")
        return
    raise ValueError("negative control accepted")


def negative_checks(payload: bytes, tables: tuple) -> int:
    for a, b in ((0, 1), (13, 1), (True, 1), (1.0, 2)):
        reason = "integer residue pair" if type(a) is not int else "nonzero residue pair"
        rejected(lambda: selector(a, b), reason)
    for flag in (1, 2, 4):
        altered = bytearray(payload)
        altered[pair_index(1, 2)] ^= flag
        rejected(lambda: validate(bytes(altered), tables), "selector product law")
    altered = bytearray(payload)
    altered[0] = 255
    rejected(lambda: validate(bytes(altered), tables), "selector code")
    altered = bytearray(payload)
    altered[SELECTORS] ^= 1
    rejected(lambda: validate(bytes(altered), tables), "packed edge")
    rejected(lambda: validate(payload[:-1], tables), "bank length")
    rejected(lambda: transition(payload, 0, STATES, 0), "pending state")
    rejected(lambda: transition(payload, 0, 0, True), "binary coin")
    rejected(lambda: run(payload, 1, 1, (0, 2)), "binary tape")
    rejected(lambda: run(payload, 1, 1, (1,) * 4097), "finite tape limit")
    altered = bytearray(payload)
    altered[SELECTORS] = 255
    altered[SELECTORS + 1] |= 1
    rejected(lambda: transition(bytes(altered), 0, 0, 0), "packed target")
    return 15


def outside_output(path: str, data: bytes) -> None:
    target = Path(path).expanduser().resolve()
    require(not target.is_relative_to(ROOT), "output must be outside checkout")
    require(target.parent.is_dir(), "output parent exists")
    require(target.write_bytes(data) == len(data), "complete output write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-bank")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    tables = source_tables()
    payload = pack(tables)
    result = {"status": "PASS_SIGNED_SWAP_RESIDUE_BANK", **validate(payload, tables),
              **path_checks(payload, tables), "rejection_controls": negative_checks(payload, tables),
              "bank_bytes": len(payload), "transition_bytes": 21 * TABLE_BYTES,
              "bank_sha256": hashlib.sha256(payload).hexdigest(),
              "scope": "new forward logical bank; inherited DDG law and optimum; no physical tariff or kappa"}
    result["package_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir()) if path.is_file()
    }
    if args.emit_bank:
        outside_output(args.emit_bank, payload)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if args.receipt:
        outside_output(args.receipt, encoded)
    print(encoded.decode(), end="")


if __name__ == "__main__":
    main()
