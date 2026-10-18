#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Materialize PR3024's streaming T740 witness for the actual admission CLI.

The lift and journals are Nick Petalas's retained PR3024/3018 sources.
dcharb78 supplied PR3042's six-skip words, building on Jeremy Kothe's edit
stage. PR3021 supplies the exact journal and cleanup helpers. No search occurs.
"""

import gzip
import hashlib
import json
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAIN = ROOT / "research/rank7-joint-endframes"
PROFILE = {1: 16376940, 2: 4741920, 3: 1594737, 4: 719280,
           5: 137085, 8: 53280, 48: 281903}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    need(len(raw) <= 20_000_000, "compressed input bound")
    raw = gzip.decompress(raw) if path.suffix == ".gz" else raw
    need(len(raw) <= 150_000_000, "decoded input bound")
    return json.loads(raw)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def authenticate():
    pins = read(PACKAGE / "PINS.json")
    need(1 <= len(pins) <= 100, "input count")
    for relative, expected in pins.items():
        path = Path(relative)
        need(not path.is_absolute() and ".." not in path.parts, "input path")
        need(digest(ROOT / path) == expected, "source digest: " + relative)


def load(relative, name):
    """Compile authenticated source bytes, bypassing bytecode caches."""
    return load_path(PACKAGE / relative, name)


def load_path(path, name):
    module = types.ModuleType(name)
    pins = read(PACKAGE / "PINS.json")
    expected = pins[path.relative_to(ROOT).as_posix()]
    need(digest(path) == expected, "module source digest")
    module.__file__ = str(path)
    # Exact source compilation avoids preexisting bytecode. See ENGINEERING.md.
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)  # noqa: S102
    return module


def witness():
    authenticate()
    lift = load("vendor/pr3024/lift.py", "retained_lift740")
    check = load("vendor/pr3021/verify.py", "retained_r1_check")
    check.PACKAGE, check.ROOT, check.MAIN = PACKAGE, ROOT, MAIN
    original = read(MAIN / "allocation/FILL.json.gz")
    base = check.apply_exchange(original, read(PACKAGE / "vendor/pr3018/EXCHANGE.json"))
    edits = lift.patch(base["rows"], read(PACKAGE / "vendor/pr3024/EXCHANGE.json"))
    order = read(MAIN / "allocation/ORDER.json")
    dispatch = {(s, r): p for s, r, p in read(MAIN / "allocation/DISPATCH.json")}
    order, dispatch = lift.chronology(order, dispatch)
    need(len(order) == len(dispatch) == 6660, "complete T740 calls")
    providers = read(PACKAGE / "vendor/pr3042/allocation/PROVIDERS.json")
    import word_check
    word_check.check_providers(read(MAIN / "allocation/PROVIDERS.json"), providers,
        read(PACKAGE / "vendor/pr3042/edits/EDITS.json")["declared"])
    declared = read(PACKAGE / "vendor/pr3042/edits/EDITS.json")["edits"]
    for tag in ("base", "extra"):
        word_check.check_word(read(MAIN / f"data/WORD-{tag}.json.gz"),
                         read(PACKAGE / f"vendor/pr3042/edits/FINAL-WORD-{tag}.json.gz"),
                         declared[tag], check.cleanup)
    return lift.Rows(base["rows"], edits), order, dispatch, providers


def write_fill(path, rows):
    """Write canonical JSON through bounded streaming compression."""
    need(len(rows) == 2717280, "complete materialized role count")
    header = {"columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
              "dispatch_overrides": []}
    prefix = json.dumps(header, sort_keys=True, separators=(",", ":"))[:-1] + ',"rows":['
    count, payload = 0, hashlib.sha256()
    with path.open("wb") as raw, gzip.GzipFile(
        filename="", mode="wb", fileobj=raw, compresslevel=1, mtime=0
    ) as out:
        data = prefix.encode()
        out.write(data)
        payload.update(data)
        for count, row in enumerate(rows, 1):
            need(count <= 2717280, "materialization iteration bound")
            data = (("," if count > 1 else "") + json.dumps(row, separators=(",", ":"))).encode()
            out.write(data)
            payload.update(data)
        out.write(b"]}\n")
        payload.update(b"]}\n")
    need(count == 2717280, "no omitted materialized role")
    return {"sha256": digest(path), "payload_sha256": payload.hexdigest(), "rows": count}


def build(directory):
    rows, order, dispatch, _ = witness()
    fill = write_fill(directory / "COMPOSED-FILL.json.gz", rows)
    for name, value in (("ORDER.json", order),
                        ("DISPATCH.json", [[s, r, dispatch[s, r]] for s, r in order])):
        (directory / name).write_text(json.dumps(value, separators=(",", ":")) + "\n")
    return {**fill, "order_sha256": digest(directory / "ORDER.json"),
            "dispatch_sha256": digest(directory / "DISPATCH.json")}
