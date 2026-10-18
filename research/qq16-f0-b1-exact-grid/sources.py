"""Bounded source loading for the complete QQ16 reference. Apache-2.0."""

import gzip
import hashlib
import json
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBERS = {
    "slots/local/CLIFFORD-RECIPES.json": (
        "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731"
    ),
    "slots/local/RESIDUAL-ADAPTERS.json": (
        "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c"
    ),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, capacity):
    require(path.is_file() and not path.is_symlink(), "regular source file")
    with path.open("rb") as stream:
        raw = stream.read(capacity + 1)
    require(len(raw) <= capacity, "source capacity")
    return raw


def authenticate():
    inventory = json.loads(read(HERE / "SOURCES.json", 32768))
    require(inventory["schema_version"] == 1, "source inventory schema")
    rows = inventory["files"]
    require(type(rows) is list and len(rows) == 4, "four fixed source pins")
    expected = {
        (CERT, "input"),
        (ARCHIVE, "input"),
        ("certificates/selected-result.json", "provenance"),
        ("docs/research/agent-task-catalog.json", "provenance"),
    }
    require(
        {(row["path"], row["usage"]) for row in rows} == expected,
        "fixed source inventory",
    )
    for row in rows:
        if row["usage"] == "input":
            raw = read(ROOT / row["path"], 24_000_000)
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input hash")
    retained = inventory["retained_predecessor"]["files"]
    names = {"verify.py", "independent.py", "README.md", "RESULT.json"}
    require(
        len(retained) == 4 and {r["name"] for r in retained} == names,
        "fixed retained-source inventory",
    )
    for row in retained:
        raw = read(HERE / "vendor/pr3226" / row["name"], 32768)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained hash")


def expand(packet, name):
    result = []
    program = packet["programs"][name]
    require(len(program) <= 1000, "wrapper capacity")
    for event in program:
        if event[0] == "retained_core":
            result.extend(packet["core_words"][event[1]])
        elif event[0] in ("private_sweep", "cover_sweep"):
            result.extend(event[2])
        else:
            result.append(event)
    require(len(result) == (26099 if name == "F_0" else 27019), "event inventory")
    return result


def load():
    authenticate()
    with gzip.open(ROOT / CERT, "rb") as stream:
        raw = stream.read(12_000_001)
    require(len(raw) <= 12_000_000, "decoded certificate capacity")
    packet = json.loads(raw)
    require(
        packet["schema"] == "conserved-qq16-full-cover-native-words-v1",
        "certificate schema",
    )
    objects = []
    with tarfile.open(ROOT / ARCHIVE) as archive:
        require(len(archive.getmembers()) <= 1000, "archive inventory capacity")
        for name, expected in MEMBERS.items():
            matches = [item for item in archive.getmembers() if item.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique member")
            require(matches[0].size <= 12_000_000, "member capacity")
            stream = archive.extractfile(matches[0])
            require(stream is not None, "member stream")
            raw = stream.read(12_000_001)
            require(hashlib.sha256(raw).hexdigest() == expected, "member hash")
            objects.append(json.loads(raw))
    return packet, objects[0], objects[1]
