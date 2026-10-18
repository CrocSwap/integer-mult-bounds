"""Authenticate the fixed QQ16 producer inputs. Apache-2.0."""

import gzip
import hashlib
import json
import stat
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST_SHA256 = "39d9ede88b11412f007a2c5dd8641dd6c238d8252f97039b31161ade1f4a0bdb"
CERT = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBERS = {
    "slots/local/CLIFFORD-RECIPES.json": "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json": "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path, capacity):
    require(stat.S_ISREG(path.lstat().st_mode), "regular file required")
    with path.open("rb") as stream:
        raw = stream.read(capacity + 1)
    require(len(raw) <= capacity, "file capacity")
    return raw


def authenticate():
    raw = read(HERE / "SOURCES.json", 32768)
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, "fixed source manifest")
    inventory = json.loads(raw)
    require(type(inventory["schema_version"]) is int, "integer schema version")
    require(inventory["schema_version"] == 1, "source schema")
    for row in inventory["files"]:
        require(row["usage"] in ("input", "provenance"), "source usage")
        if row["usage"] == "input":
            raw = read(ROOT / row["path"], 24_000_000)
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input hash")
    for row in inventory["retained_predecessor"]["files"]:
        raw = read(HERE / row["local_path"], 65536)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained hash")


def load():
    authenticate()
    with gzip.open(ROOT / CERT, "rb") as stream:
        raw = stream.read(12_000_001)
    require(len(raw) <= 12_000_000, "decoded certificate capacity")
    packet = json.loads(raw)
    require(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "schema")
    objects = []
    with tarfile.open(ROOT / ARCHIVE) as archive:
        items = archive.getmembers()
        require(len(items) <= 1000, "archive member capacity")
        require(not any(x.issym() or x.islnk() for x in items), "no archive links")
        for name, expected in MEMBERS.items():
            matches = [item for item in items if item.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique regular member")
            require(matches[0].size <= 12_000_000, "member capacity")
            with archive.extractfile(matches[0]) as stream:
                raw = stream.read(12_000_001)
            require(hashlib.sha256(raw).hexdigest() == expected, "member hash")
            objects.append(json.loads(raw))
    return packet, objects[0], objects[1]


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


def reg(token):
    require(type(token) is list and len(token) == 2, "register token")
    kind, index = token
    require(kind in ("L", "C") and type(index) is int, "register type")
    require(0 <= index < (704 if kind == "L" else 8), "register range")
    return index + (704 if kind == "C" else 0)


def rank(rows, width):
    basis = [0] * width
    for value in rows:
        require(type(value) is int and 0 <= value < 1 << width, "binary row")
        for pivot in range(width - 1, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(x != 0 for x in basis)


def monomial(m):
    require(
        set(m) == {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"},
        "monomial fields",
    )
    a, q, z = (m[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4"))
    require(len(a) == len(q) == len(z) == 9, "nine active axes")
    require(
        rank(a, 9) == 9 and all(type(x) is int and 0 <= x < 512 for x in q),
        "invertible binary monomial",
    )
    require(all(type(x) is int and 0 <= x < 4 for x in z), "quarter turns")
    require(type(m["offset"]) is int and 0 <= m["offset"] < 512, "offset")
    require(type(m["phase"]) is int and 0 <= m["phase"] < 4, "phase")


def cover_maps(packet):
    used = {e[2] for e in expand(packet, "B_1_2") if e[0] == "cover_map"}
    require(len(used) == 512, "used cover inventory")
    for name in used:
        row = packet["map_registry"][name]
        columns = row["owner_right_matrix_columns"]
        require(len(columns) == 73 and rank(columns, 73) == 73, "invertible owner map")
        delta = row["payload_translation_at_identity_owner"]
        require(type(delta) is int and 0 <= delta < 1 << 73, "cover translation")
        require(
            row["action"] == "out(d,z_1,...,z_lambda)=in(d*g,"
            "z_1 XOR d*delta,...,z_lambda XOR d*delta)",
            "all-depth cover action",
        )
    return len(used)
