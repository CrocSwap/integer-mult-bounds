"""Replay both exact mixed scalar checks on the same pinned word and caller."""
import gzip
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def read(path):
    return decode(path.read_bytes())


def authenticate(scratch):
    pins = read(HERE / "LOCAL-PINS.json")
    for key, digest in pins.items():
        path = PurePosixPath(key)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != digest:
            raise ValueError(f"changed dependency {key}")
    deps = scratch / "dependencies"
    shutil.copytree(HERE / "dependencies", deps)
    provenance = read(HERE / "PROVENANCE.json")["files"]
    assert len(provenance) == 6
    assert sum(bool(pin["uncompress"]) for pin in provenance.values()) == 2
    for key, pin in provenance.items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], key
    return deps


def run(script, *args):
    result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                            check=True, capture_output=True, timeout=25)
    return result.stdout


def contained(inner, outer):
    lower, upper = map(Fraction, inner)
    a, b = map(Fraction, outer)
    return a <= lower <= upper <= b


def compare(independent, price, support):
    assert independent["counts"] == support["counts"]
    assert independent["paid"] == price["complete_old_paid"]
    assert independent["productive"] == price["complete_targets"]
    assert contained(independent["old_margin"], price["complete_old_margin"])
    assert len(independent["rows"]) == len(support["records"]) == 44
    assert not support["survivors"] and not support["unvisited"]
    assert independent["candidates"] == independent["unresolved"] == 0
    legal = 0
    for r, s in zip(independent["rows"], support["records"], strict=True):
        assert (r["clocks"], r["status"]) == (s["clocks"], s["status"])
        if r["status"] != "no_positive_price":
            continue
        legal += 1
        assert r["paid_old_minus_new"] == s["paid_old_minus_new"]
        assert [r["old_route"][i] for i in (0, 2)] == s["exterior_old"]
        assert [r["new_route"][i] for i in (0, 2)] == s["exterior_new"]
        assert r["new_coefficient"] == next(e[3] for e in s["candidate_scalars"] if e[0] == "ADD")
        assert contained(r["signed_delta"], s["incremental_moment"])
        assert contained(r["full_margin"], s["complete_margin"])
        assert Fraction(r["full_margin"][1]) < 0
    assert legal == 7 and independent["best_clocks"] == [39791,39793]


def replay():
    with TemporaryDirectory(prefix="p104-add-scale-") as temp:
        scratch = Path(temp)
        deps = authenticate(scratch)
        out = scratch / "primary"
        run(HERE / "engines/primary.py", "--round30", deps / "round30",
            "--predecessor", deps / "7298", "--out", out)
        for name in ("PRICE.json", "SUPPORT.json"):
            assert (out / name).read_bytes() == (HERE / "receipts/primary" / name).read_bytes(), name
        raw = run(HERE / "engines/independent.py", deps)
        assert raw == (HERE / "receipts/independent/RESULT.json").read_bytes()
        compare(decode(raw), read(out / "PRICE.json"), read(out / "SUPPORT.json"))
        print("PASS_ADJACENT_ADD_SCALE slots=44 legal=7 price_negative=7 unresolved=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    replay()
