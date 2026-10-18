# SPDX-License-Identifier: Apache-2.0
"""Authenticate and freshly bind one forward SCALE/ADD pair in both providers.

This runs the pinned native compiler and its full algebra/frame checks. It does
not rerun the inherited coefficient-capacity or Boolean-circuit suites.
"""

import hashlib
import importlib
import json
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PAIRED = ROOT / "research/rank7-paired-scale"
CALLER = ROOT / "research/rank7-boolean-scalar-caller"
NATIVE = CALLER / "source/vendor/native"
PARENT = NATIVE / "vendor/parent"
EVENT_INDEX = 6872
SCALE = ["scalar", ["scale", ["L", 292], 1, -1], 0]
NEXT_READ = ["scalar", ["add", ["L", 333], ["L", 292], -1, 1], 0]
PAIRED_INPUTS = {
    "RESULT.json", "SOURCES.json", "UPSTREAM.json", "bindings.py",
    "pairscale.py", "vendor/RESULT.json", "vendor/scalars.py",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    require(__debug__, "assertions must remain enabled for inherited compilers")
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    records = [r for r in records if r["usage"] == "input"]
    paths = {r["path"] for r in records}
    require(1 <= len(records) <= 96 and len(paths) == len(records),
            "bounded unique input inventory")
    required = {f"research/rank7-paired-scale/{p}" for p in PAIRED_INPUTS}
    require(required <= paths, "paired-scale input inventory")
    for record in records:
        path = ROOT / record["path"]
        require(path.is_file() and not path.is_symlink()
                and path.resolve().is_relative_to(ROOT)
                and path.stat().st_size <= 8_000_000,
                "bounded contained source: " + record["path"])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                "source hash: " + record["path"])
    inherited = json.loads((PAIRED / "SOURCES.json").read_text())["files"]
    require({r["path"] for r in inherited if r["usage"] == "input"} <= paths,
            "complete transitive paired-scale input inventory")
    return len(records)


@contextmanager
def fresh_imports(directory):
    # -B suppresses writes, but only a fresh cache prefix also excludes stale reads.
    old_path, old_prefix, old_write = sys.path[:], sys.pycache_prefix, sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix="paired-routing-import-") as cache:
        sys.path.insert(0, str(directory))
        sys.pycache_prefix, sys.dont_write_bytecode = cache, True
        try:
            yield
        finally:
            sys.path[:], sys.pycache_prefix, sys.dont_write_bytecode = old_path, old_prefix, old_write


def imported(name, expected):
    module = importlib.import_module(name)
    require(Path(module.__file__).resolve() == expected.resolve(),
            "import origin: " + name)
    return module


def load_pairscale():
    """Return the authenticated predecessor circuit module."""
    authenticate()
    with fresh_imports(PAIRED):
        imported("bindings", PAIRED / "bindings.py")
        module = imported("pairscale", PAIRED / "pairscale.py")
        require(Path(module.s.__file__).resolve() == PAIRED / "vendor/scalars.py",
                "paired scalar import origin")
    return module


def frame_bindings(events, word):
    """Track literal frame changes through the selected pair, without row replay."""
    current, phase = word["start"][:], None
    require(word["frames"][0] == [], "frame zero is the empty frame")
    for index, event in enumerate(events[: EVENT_INDEX + 2]):
        kind = event[0]
        if kind == "phase":
            phase = event[1]
        elif kind == "climb":
            _, _, role, old, new, rank = event
            require(current[role] == old, "climb source frame")
            require(len(word["frames"][new]) - len(word["frames"][old]) == rank,
                    "climb rank")
            current[role] = new
        elif kind == "warp":
            _, role, _, old, new = event
            require(role[0] == "L" and current[role[1]] == old, "warp source frame")
            current[role[1]] = new
        elif kind == "scalar":
            operation, frame = event[1:]
            roles = operation[1:3] if operation[0] == "add" else operation[1:2]
            require(all(r[0] == "L" and current[r[1]] == frame for r in roles),
                    "scalar operand frames")
        if index in (EVENT_INDEX, EVENT_INDEX + 1):
            require(phase == "A" and current[292] == current[333] == 0,
                    "literal pair in the common empty A frame")
    return {"label": 0, "axes": [], "rank": 0, "phase": "A"}


def event_bindings(work):
    """Compile both providers into fresh children of work and bind 6872/6873.

    The caller owns and removes work. Admission at width 84 and grid 7 is the
    inherited capacity premise; no new signed-precision theorem is checked here.
    """
    authenticate()
    with fresh_imports(PARENT):
        parent = imported("replay_parent", PARENT / "replay_parent.py")
        contractions = imported("contractions", PARENT / "contractions.py")
        tariff = imported("tariff", PARENT / "tariff.py")
        imported("frames", PARENT / "frames.py")
        imported("contract", PARENT / "contract.py")
    parent.check_pins()
    inherited = parent.read(NATIVE / "RESULT.json")
    paired = parent.read(PAIRED / "RESULT.json")
    caller_receipt = parent.read(CALLER / "RESULT.json")
    require(paired["data_width"] == caller_receipt["data_width"] == 84
            and caller_receipt["fractional_bits"] == 7, "inherited width/grid")
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    result = {}
    for provider in ("base", "extra"):
        source = PARENT / f"vendor/WORD-{provider}.json.gz"
        raw = parent.read(source)
        candidate = contractions.produce(tariff.produce(raw), parent.read(PARENT / "EDITS.json"))
        require(parent.digest(candidate) == inherited["providers"][provider]["word_sha256"],
                "exact inherited provider word")
        programs, checks = parent.compile_word(candidate, work / provider)
        require(checks == inherited["providers"][provider]["native_checks"],
                "complete fresh native compiler receipt")
        word = parent.read(work / provider / "native/CANONICAL-WORD.json.gz")
        events = programs["forward"]
        require(events[EVENT_INDEX: EVENT_INDEX + 2] == [SCALE, NEXT_READ],
                "fresh literal SCALE and next read")
        example = paired["literal_examples"][provider]
        require(example["event_index"] == EVENT_INDEX and example["event"] == SCALE
                and example["next_event"] == NEXT_READ, "paired-scale published example")
        require(word["v"] == 112 and word["R"] == 408 and word["h"] == 9,
                "native role dimensions")
        roles = {}
        for role in (292, 333):
            offset = role - 2 * word["v"]
            original = word["helper_origin"][offset]
            require(original == role and word["start"][role] == 0,
                    "literal helper origin and entrance frame")
            roles[f"L{role}"] = {"original_register": original, "helper_offset": offset}
        result[provider] = {
            "source_word_compressed_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "candidate_word_sha256": parent.digest(candidate),
            "canonical_word_sha256": parent.digest(word),
            "native_checks": checks,
            "event_index": EVENT_INDEX,
            "event": events[EVENT_INDEX],
            "next_event_index": EVENT_INDEX + 1,
            "next_event": events[EVENT_INDEX + 1],
            "frame": frame_bindings(events, word),
            "roles": roles,
            "coordinate_scope": "one supplied Gaussian coordinate; whole-role cardinality unclaimed",
            "capacity_premise": {"data_width": 84, "fractional_bits": 7,
                                 "source": "inherited conditional capacity; not rerun here"},
        }
    require(result["base"]["native_checks"] == result["extra"]["native_checks"],
            "identical emitted native programs across providers")
    return result
