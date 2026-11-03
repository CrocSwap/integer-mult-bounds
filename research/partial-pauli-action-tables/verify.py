"""Bounded exact conformance of the optional complete PR5342 replay adapter.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import contextlib
import hashlib
import io
from itertools import product
import json
from pathlib import Path
import struct
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay


def need(ok, message):
    if not ok:
        raise ValueError(message)


def complete_trace(original):
    module = replay.load_source()
    stats = {}
    action = module.act if original else replay.make_action(stats)
    digest = hashlib.sha256()
    calls = 0
    bit_tests = 0
    old_xors = 0

    def observed(columns, x):
        nonlocal calls, bit_tests, old_xors
        value = action(columns, x)
        row = (len(columns), *columns, *([0] * (4 - len(columns))), x, value)
        digest.update(struct.pack("7B", *row))
        calls += 1
        bit_tests += len(columns)
        old_xors += x.bit_count()
        return value

    module.act = observed
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        module.main()
    return {"stdout": output.getvalue(), "calls": calls, "old_bit_tests": bit_tests,
            "old_xors": old_xors, "action_sha256": digest.hexdigest()}, stats


def exhaustive_actions():
    source = replay.load_source()
    stats = {}
    action = replay.make_action(stats)
    calls = 0
    for length in range(5):
        for columns in product(range(16), repeat=length):
            for x in range(1 << length):
                need(action(columns, x) == source.act(columns, x), "binary action mismatch")
                calls += 1
    need(stats["tables"] == replay.MAX_TABLES, "complete column-tuple inventory")
    need(calls == sum(32**j for j in range(5)), "complete action domain")
    return stats


def controls():
    action = replay.make_action({})
    invalid = [((1,) * 5, 0), ((16,), 0), ((-1,), 0), ((True,), 0),
               ((0.5,), 0), ((1,), -1), ((1,), 2), ((1,), True), ((1,), 0.5)]
    for columns, x in invalid:
        try:
            action(columns, x)
        except ValueError:
            continue
        raise ValueError("invalid action was accepted")
    stats = {}
    fresh = replay.make_action(stats)
    need(stats == {"calls": 0, "tables": 0, "entries": 0, "xor_updates": 0},
         "tables escaped the invocation boundary")
    values = [1, 2]
    need(fresh(values, 3) == 3, "list input action")
    values[0] = 4
    need(fresh(values, 3) == 6 and stats["tables"] == 2, "mutable input key")
    with patch.object(Path, "read_bytes", return_value=b"raise RuntimeError('must not execute')"):
        try:
            replay.load_source()
        except ValueError:
            pass
        else:
            raise ValueError("corrupted source was accepted")
    return len(invalid) + 3


def main():
    pins = json.loads((replay.PACKAGE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            payload = (replay.PACKAGE.parents[1] / row["path"]).read_bytes()
            need(hashlib.sha256(payload).hexdigest() == row["sha256"], "input source drift")
    old, _ = complete_trace(True)
    new, stats = complete_trace(False)
    need(old == new, "complete ordered action trace or output differs")
    need(stats["calls"] == old["calls"], "skipped original actions")
    need(stats["xor_updates"] < old["old_xors"], "no exact XOR-work improvement")
    domain = exhaustive_actions()
    report = {"status": "PASS_PARTIAL_PAULI_ACTION_TABLES", "complete_replay": new,
              "table_work": stats, "complete_action_domain": domain,
              "new_controls": controls(),
              "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(replay.PACKAGE.iterdir()) if p.is_file()}}
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
