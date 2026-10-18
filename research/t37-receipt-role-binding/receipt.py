#!/usr/bin/env python3
"""Compare T37 receipts after checking an explicit path-to-input-role bijection.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Paths here are receipt labels, never files to open. Bindings must come from the
invocation being checked, independently of the receipt's labels and digests.
"""
from copy import deepcopy
import json
from pathlib import PurePosixPath


INPUT_ROLES = (
    "word.json.gz",
    "local-replay.json",
    "baseline/split-centres/GLOBAL-TEMPLATE.json.gz",
    "baseline/split-centres/CANONICAL-WORD.json.gz",
    "baseline/work/complex-nine-native/DATA-PHASES.json",
)
REPOSITORY_ROLES = (
    "research/complex-t37-owners/OWNERS.json.gz",
    "research/complex-t37-owners/EDITS.json",
    "research/complex-t21-owners/independent_check.py",
)
ROLES = frozenset(INPUT_ROLES + REPOSITORY_ROLES)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def unique_pairs(items):
    value = {}
    for key, item in items:
        need(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def invalid_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs,
                      parse_constant=invalid_constant)


def runtime_paths(repository, inputs):
    """Build labels from explicit invocation roots, without reading those paths.

    Accepts pathlib Path or PurePath roots (including PureWindowsPath). The
    caller supplies the canonical absolute roots used by the producing command.
    No suffix, basename, hash-based role inference, or filesystem lookup occurs.
    """
    need(repository.is_absolute() and inputs.is_absolute(), "absolute invocation roots required")
    return {**{name: str(inputs / name) for name in INPUT_ROLES},
            **{name: str(repository / name) for name in REPOSITORY_ROLES}}


def historical_paths():
    """Literal layout recorded by the pinned PR942 producer; no path is opened."""
    repository = PurePosixPath("/private/tmp/integer-mult-queue-20261013")
    local = PurePosixPath("/private/tmp/batch952-t37-complete/replay/native/local")
    baseline = PurePosixPath("/private/tmp/batch952-baseline799/global/global/base")
    return {
        "word.json.gz": str(local / "CANONICAL-WORD.json.gz"),
        "local-replay.json": str(local / "INDEPENDENT-LOCAL-REPLAY.json"),
        **{name: str(baseline / name.removeprefix("baseline/"))
           for name in INPUT_ROLES if name.startswith("baseline/")},
        **{name: str(repository / name) for name in REPOSITORY_ROLES},
    }


def normalize(report, paths, expected_hashes):
    """Erase only a validated role's concrete path label, retaining all values."""
    need(type(report) is dict, "receipt must be an object")
    need(type(paths) is dict and set(paths) == ROLES, "binding role inventory")
    need(type(expected_hashes) is dict and set(expected_hashes) == ROLES,
         "expected hash role inventory")
    need(all(type(path) is str and path for path in paths.values()), "invalid path label")
    need(len(set(paths.values())) == len(ROLES), "ambiguous path binding")
    actual = report.get("input_sha256")
    need(type(actual) is dict and set(actual) == set(paths.values()), "receipt path inventory")
    mapped = {}
    for role in sorted(ROLES):
        got, expected = actual[paths[role]], expected_hashes[role]
        need(type(got) is str and type(expected) is str and got == expected,
             "input digest for role: " + role)
        mapped[role] = got
    result = deepcopy(report)
    result["input_sha256"] = mapped
    canonical(result)
    return result


def compare(report, paths, expected):
    result = normalize(report, paths, expected["input_sha256"])
    need(canonical(result) == canonical(expected), "complete receipt differs")
    return result
