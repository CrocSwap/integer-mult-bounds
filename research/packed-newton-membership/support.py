"""Source authentication and the opt-in complete replay adapter.

Produced by Nick Petalas. Apache-2.0.
"""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAX_SOURCE_BYTES = 32 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked_hash(path, expected):
    need(path.is_file(), "missing source: " + str(path))
    with path.open("rb") as stream:
        payload = stream.read(MAX_SOURCE_BYTES + 1)
    need(len(payload) <= MAX_SOURCE_BYTES, "source size limit")
    need(sha256(payload).hexdigest() == expected, "source changed: " + str(path))


def authenticate():
    metadata = json.loads((HERE / "SOURCES.json").read_text())
    for row in metadata["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            checked_hash(path, row["sha256"])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "missing module loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_modules():
    authenticate()
    source = ROOT / "research/newton-bounded-residue-validator"
    # The source verifier's literal import is bound to authenticated bytes.
    reference = load("packed_reference", source / "membership.py")
    previous = sys.modules.get("membership")
    previous_path = list(sys.path)
    sys.modules["membership"] = reference
    try:
        replay = load("packed_source_replay", source / "verify.py")
    finally:
        sys.path[:] = previous_path
        if previous is None:
            sys.modules.pop("membership", None)
        else:
            sys.modules["membership"] = previous
    return reference, replay


def replay_result(replay, candidate):
    import packed
    if candidate:
        replay.member = packed.member
        replay.obstruction = packed.obstruction
    result = replay.replay()
    expected = json.loads((ROOT / "research/newton-bounded-residue-validator/RESULT.json").read_text())
    need(result == expected, "complete predecessor replay changed")
    return result
