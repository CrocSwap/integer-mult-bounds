"""Replay both fixed signed-caller exclusions and the independent endpoints."""
from argparse import ArgumentParser
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def unique(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def matches(actual, expected):
    assert decode(actual) == decode(expected.read_bytes()), expected


def subprocess_replay(script, *args):
    result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                            check=True, capture_output=True)
    return result.stdout


def authenticate(scratch):
    pins = decode((HERE / "LOCAL-PINS.json").read_bytes())
    for key, digest in pins.items():
        path = PurePosixPath(key)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != digest:
            raise ValueError(f"changed dependency {key}")
    provenance = decode((HERE / "PROVENANCE.json").read_bytes())["files"]
    assert sum(bool(pin["uncompress"]) for pin in provenance.values()) == 2
    for key, pin in provenance.items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], key


def run():
    with TemporaryDirectory(prefix="p104-relative-defect-") as temp:
        scratch = Path(temp)
        deps = scratch / "dependencies"
        shutil.copytree(HERE / "dependencies", deps)
        authenticate(scratch)
        word_root = deps / "round30"
        caller = word_root / "complex/source/inputs/CALLER.json"
        engine = HERE / "engines/screen.py"
        b = scratch / "type-b"
        a = scratch / "type-a"
        subprocess_replay(engine, word_root, b)
        subprocess_replay(HERE / "engines/screen_typea.py", word_root, engine, a)
        for path in (a, b):
            expected = HERE / "receipts" / path.name
            for name in ("PRICE.json", "SUPPORT.json"):
                matches((path / name).read_bytes(), expected / name)
            letter = path.name[-1]
            phase = subprocess_replay(HERE / f"engines/phase_{letter}.py", "--caller", caller)
            matches(phase, expected / "PHASE.json")
            support = decode((path / "SUPPORT.json").read_bytes())
            assert support["checked_subsets"] == 15 and support["unvisited_subsets"] == 0
            assert support["status"] == "all_subsets_excluded"
        print("PASS_SIGNED_CALLER_RELATIVE_DEFECT type_a=15 type_b=15 excluded=30 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    parser = ArgumentParser(description=__doc__)
    parser.parse_args()
    run()
