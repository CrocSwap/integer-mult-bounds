"""Read exact source objects for the involutive Walsh lift.

New code uses the repository Apache-2.0 license. Research and verification
used OpenAI Codex assistance. No source archive is changed or copied.
"""

from functools import lru_cache
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import gzip
import json
import subprocess
import tarfile


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
LOCAL_ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
LOCAL_ARCHIVE_SHA256 = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
LOCAL_PINS = {
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "CLIFFORD-RECIPES.json": "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "RESIDUAL-ADAPTERS.json": "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
    "DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}
LOCAL_MEMBERS = {
    name: ("t16/global/base/work/complex-nine-native/" if name == "DATA-PHASES.json"
           else "slots/local/") + name
    for name in LOCAL_PINS
}
SELECTED_ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
SELECTED_ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
INVOICE_MEMBERS = {
    "candidate/strict/global/audit/PREFIX-AND-INVOICE.json":
        "212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12",
    "candidate/strict/global/audit/OWNERS-AND-PROFILE.json":
        "30bafff060afcfb3644e951214d66cfaffe58242881c652e28003958b42127cc",
}
ENGINE_ROOT = "research/complex-k492-owner-repair/vendor/multicold/engines/"
ENGINE_PINS = {
    "moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "base_two_moment.py": "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=8)
def read_git(repo, path, expected_sha256):
    """Read one immutable Git object and check its complete byte string."""
    result = subprocess.run(
        ["git", "show", BASE + ":" + path], cwd=Path(repo),
        check=True, capture_output=True,
    )
    raw = result.stdout
    require(sha256(raw).hexdigest() == expected_sha256, "Source pin changed: " + path)
    return raw


def archive_members(repo, path, archive_sha256, pins):
    """Read named archive members in memory after the archive pin passes."""
    raw = read_git(repo, path, archive_sha256)
    result = {}
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        for name, expected in pins.items():
            member = archive.getmember(name)
            require(member.isfile(), "The source member is not a file: " + name)
            payload = archive.extractfile(member).read()
            require(sha256(payload).hexdigest() == expected, "Member pin changed: " + name)
            result[name] = payload
    return result


def decode_json(raw, name):
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def load_local(repo):
    pins = {LOCAL_MEMBERS[name]: pin for name, pin in LOCAL_PINS.items()}
    raw = archive_members(repo, LOCAL_ARCHIVE, LOCAL_ARCHIVE_SHA256, pins)
    return {name: decode_json(raw[member], name) for name, member in LOCAL_MEMBERS.items()}


def load_invoice(repo):
    raw = archive_members(repo, SELECTED_ARCHIVE, SELECTED_ARCHIVE_SHA256, INVOICE_MEMBERS)
    invoice = json.loads(raw["candidate/strict/global/audit/PREFIX-AND-INVOICE.json"])
    owners = json.loads(raw["candidate/strict/global/audit/OWNERS-AND-PROFILE.json"])
    return invoice, owners


def engine_bytes(repo, name):
    return read_git(repo, ENGINE_ROOT + name, ENGINE_PINS[name])
