"""Load the immutable logical caller and bank codec into one module namespace."""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
CALLER = HERE / "inputs/pr2753"
PARKING = HERE / "inputs/pr2769"
_active = False

# Main's UTF-8-only HPE verifier correction changes one proof-supplement hash.
# Accept these two complete records, not an unconstrained semantic projection.
SELECTED_RECORDS = {
    "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32":
        "ae6a99f28aa468649eb66a361e764d769363bf11",
    "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129":
        "b1fea0c94436b236cc2b7d41a7be032811b94c81",
}


def selected_sources(data):
    digest = sha256(data).hexdigest()
    blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if SELECTED_RECORDS.get(digest) != blob:
        raise ValueError("unrecognized complete selected record")
    sources = json.loads((CALLER / "SOURCES.json").read_text())
    rows = [row for row in sources["files"]
            if row["path"] == "certificates/selected-result.json"]
    if len(rows) != 1 or rows[0]["sha256"] != next(iter(SELECTED_RECORDS)):
        raise ValueError("unchanged predecessor selected-record pin")
    rows[0].update(sha256=digest, git_blob=blob)
    return sources


def compatibility_controls():
    selected = json.loads((REPOSITORY / "certificates/selected-result.json").read_bytes())
    for key in ("kappa", "proof_supplements"):
        changed = dict(selected)
        changed[key] = "unrecognized mutation"
        try:
            selected_sources(json.dumps(changed).encode())
        except ValueError:
            continue
        raise ValueError("selected-record mutation accepted: " + key)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def authenticate():
    entries = json.loads((HERE / "SNAPSHOTS.json").read_text())["files"]
    expected = set()
    for entry in entries:
        path = entry["path"]
        if path in expected or not path.startswith("inputs/"):
            raise ValueError("unique frozen input inventory")
        expected.add(path)
        if sha256((HERE / path).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("frozen source changed: " + path)
    observed = {path.relative_to(HERE).as_posix() for path in (HERE / "inputs").rglob("*")
                if path.is_file() and "__pycache__" not in path.parts}
    if expected != observed:
        raise ValueError("complete frozen input inventory")
    source_verifier = module("frozen_caller_verifier", CALLER / "verify.py")
    sources = selected_sources((REPOSITORY / "certificates/selected-result.json").read_bytes())
    source_verifier.authenticate(sources=sources, here=CALLER, root=REPOSITORY)


def activate():
    global _active
    if _active:
        return sys.modules["bank_codec"]
    authenticate()
    module("bootstrap", CALLER / "bootstrap.py")
    import sources
    sources.ROOT = REPOSITORY
    sys.path.insert(0, str(HERE))
    sys.path.append(str(PARKING / "vendor"))
    import words
    if sha256(Path(words.__file__).read_bytes()).digest() != sha256((PARKING / "vendor/words.py").read_bytes()).digest():
        raise ValueError("logical caller and codec use one unchanged Word interface")
    codec = module("bank_codec", PARKING / "codec.py")
    _active = True
    return codec
