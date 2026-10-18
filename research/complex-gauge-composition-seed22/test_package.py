#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Focused positive and deliberate-failure checks; standard library only."""
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("seed22_compose_tests", HERE / "compose.py")
compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose)


def rejects(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + label)


def main():
    result = compose.compute()
    need = compose.need
    saved = json.loads((HERE / "RESULT.json").read_bytes())
    need(compose.canonical(result) == compose.canonical(saved), "saved result")

    pr1263 = compose.load_pr1263()
    word, programs = pr1263.source()
    gauges_by_orientation = json.loads((HERE / "vendor/pr1263/GAUGES.json").read_bytes())
    for orientation in ("forward", "backward"):
        row = result["orientations"][orientation]
        gauges = {int(h): int(k) for h, k in gauges_by_orientation[orientation].items()}
        schedule = row["schedule"]
        candidate = compose.mixed_word(programs[orientation], word, gauges, schedule)
        compose.need(compose.exact_columns(candidate, orientation)["formal_columns"] == 712,
                     "positive all-column control " + orientation)

        previous = 0
        changed_index = None
        for event_index, exponent in schedule:
            if exponent != previous:
                changed_index = event_index
                break
            previous = exponent
        compose.need(changed_index is not None, "a paid dynamic transition exists")
        omitted = compose.mixed_word(programs[orientation], word, gauges, schedule,
                                     omit_transition=changed_index)
        rejects(lambda: compose.exact_columns(omitted, orientation), "omitted dynamic SCALE")

        corrupted = copy.deepcopy(candidate)
        for event in corrupted:
            if (event[0] == "scalar" and event[1][0] == "add"
                    and (event[1][1] == ["L", compose.HELPER]
                         or event[1][2] == ["L", compose.HELPER])):
                q = compose.fraction_from_gate(event[1]) * 2
                event[1][3:5] = [q.numerator, q.denominator]
                break
        rejects(lambda: compose.exact_columns(corrupted, orientation), "incorrect ADD coefficient")

        missing_exit = candidate[:-2] + candidate[-1:]
        rejects(lambda: compose.exact_columns(missing_exit, orientation), "missing static-helper restoration")

    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    first_path, record = next(iter(manifest["files"].items()))
    root = HERE if record["location"] == "package" else compose.ROOT
    original = (root / first_path).read_bytes()
    rejects(lambda: compose.verify_file_record(original + b"corrupt", record, first_path),
            "corrupt source pin")

    print("PASS_COMPLEX_K8_MIXED_GAUGE_CONTROLS positive=2 orientations negative=7 checks in 4 classes")


if __name__ == "__main__":
    main()
