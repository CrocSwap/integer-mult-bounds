#!/usr/bin/env python3
"""Exercise the authenticated caller with synthetic subprocess receipts, not censuses."""

import copy
import io
import json
import runpy
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

LOCAL = runpy.run_path(str(Path(__file__).with_name("verify.py")))
CALLER, ROOT = LOCAL["CALLER"], LOCAL["ROOT"]
authenticated_sources, need = LOCAL["authenticated_sources"], LOCAL["need"]


def load_caller(source):
    path = ROOT / CALLER
    need(path.read_text() == source, "caller changed after source authentication")
    namespace = runpy.run_path(str(path))
    return namespace["main"].__globals__


def fixtures():
    premises = [
        {
            "premise": "PASS",
            "dimension": d,
            "length": n,
            "canonical_words": w,
            "maximum_coverage": c,
        }
        for d, n, w, c in [(5, 10, 945, 31), (6, 12, 10395, 49), (6, 14, 945945, 59)]
    ]
    controls = []
    for pattern, count, coverage in [("A", 5, 116), ("B", 77, 126)]:
        controls.append(
            {
                "controls": "PASS",
                "pattern": pattern,
                "normalized_paths": 106,
                "translated_candidates": 848,
                "universal_low_dihedral_orbits": count,
                "positive_simple24_coverage": 128,
                "negative_simple22_coverage": coverage,
                "repeated_origin_rejected": True,
                "wrong_count_rejected": True,
                "wrong_join_rejected": True,
                "full_enumeration_rediscovered": True,
                "full_enumeration_nodes": 3,
                "full_enumeration_capacity_survivors": 2,
                "full_enumeration_compositions": 2,
            }
        )
    cycles = [
        {
            "pattern": p,
            "template": i,
            "conditional_cover": True,
            "exhausted": True,
            "found": False,
        }
        for p, count in [("A", 5), ("B", 77)]
        for i in range(1, count + 1)
    ]
    summary = {"all_requested_exhausted": True, "completed_orbits": 82}
    return premises, controls + cycles + [summary]


def invoke(source, premises, records, controls_only=False):
    namespace = load_caller(source)
    calls = []

    def fake_run(command, directory, timeout):
        calls.append(command[1:])
        need(Path(directory).is_dir() and timeout > 0, "bounded private invocation")
        return copy.deepcopy(
            premises if command[1:] == ["--premises-only"] else records
        )

    # Compile and native-process boundaries only are replaced. The actual
    # parser, selected mode, receipt checks, exceptions and final PASS execute.
    namespace["run_json"] = fake_run
    namespace["subprocess"] = types.SimpleNamespace(
        run=lambda *_args, **_kwargs: types.SimpleNamespace(returncode=0)
    )
    argv = [str(ROOT / CALLER)] + (["--controls-only"] if controls_only else [])
    with (
        patch.object(sys, "argv", argv),
        patch.dict("os.environ", {"CXX": sys.executable}),
        redirect_stdout(io.StringIO()) as printed,
    ):
        namespace["main"]()
    return calls, printed.getvalue()


def rejection_controls(source):
    mutations = [
        ("missing orbit", lambda p, r: r.pop(2)),
        ("duplicate orbit", lambda p, r: r.__setitem__(3, copy.deepcopy(r[2]))),
        ("extra orbit", lambda p, r: r.insert(2, copy.deepcopy(r[2]))),
        ("wrong orbit", lambda p, r: r[2].__setitem__("template", 6)),
        ("found word", lambda p, r: r[2].__setitem__("found", True)),
        ("incomplete orbit", lambda p, r: r[2].__setitem__("exhausted", False)),
        (
            "incomplete final flag",
            lambda p, r: r[-1].__setitem__("all_requested_exhausted", False),
        ),
        (
            "incomplete final count",
            lambda p, r: r[-1].__setitem__("completed_orbits", 81),
        ),
        ("missing path controls", lambda p, r: r.pop(0)),
        (
            "no recursive positive",
            lambda p, r: r[0].__setitem__("full_enumeration_nodes", 2),
        ),
        ("wrong premise", lambda p, r: p[2].__setitem__("maximum_coverage", 60)),
        ("duplicate premise", lambda p, r: p.__setitem__(2, copy.deepcopy(p[1]))),
    ]
    for name, mutate in mutations:
        premises, records = fixtures()
        mutate(premises, records)
        try:
            invoke(source, premises, records)
        except ValueError:
            continue
        raise ValueError(f"caller accepted {name}")
    return len(mutations)


def process_controls(source):
    namespace = load_caller(source)
    with tempfile.TemporaryDirectory(prefix="caller-process-controls-") as directory:
        good = [sys.executable, "-I", "-B", "-c", "print('{\"ok\":true}')"]
        with redirect_stdout(io.StringIO()):
            need(
                namespace["run_json"](good, directory, 5) == [{"ok": True}],
                "real JSON process",
            )
        failures = [
            ("print('{}'); raise SystemExit(3)", 5, ValueError),
            ("print('not JSON')", 5, json.JSONDecodeError),
            ("import time; time.sleep(5)", 0.05, subprocess.TimeoutExpired),
        ]
        for program, timeout, expected in failures:
            try:
                with redirect_stdout(io.StringIO()):
                    namespace["run_json"](
                        [sys.executable, "-I", "-B", "-c", program], directory, timeout
                    )
            except expected:
                continue
            raise ValueError("actual process failure accepted")
    return len(failures)


def main():
    source = authenticated_sources()[CALLER]
    premises, records = fixtures()
    calls, output = invoke(source, premises, records)
    need(
        calls == [["--premises-only"], ["--seconds", "300"]],
        "full caller selected a subset or mode",
    )
    need(json.loads(output)["complete_orbits"] == 82, "full caller receipt")
    calls, output = invoke(source, premises, records[:2], controls_only=True)
    need(calls == [["--controls-only"]], "controls-only invocation")
    need(json.loads(output)["complete_orbits"] == 0, "controls promoted to exclusion")
    result = {
        "synthetic_complete_orbits": 82,
        "caller_rejections": rejection_controls(source),
        "real_process_rejections": process_controls(source),
        "caller_modes": 2,
    }
    expected = json.loads((LOCAL["PACKAGE"] / "RESULT.json").read_text())["caller"]
    need(result == expected, "complete caller receipt changed")
    print(json.dumps(result, sort_keys=True))
    print("PASS_CONNECTOR_CALLER_CONTRACT")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(f"FAIL {error}") from error
