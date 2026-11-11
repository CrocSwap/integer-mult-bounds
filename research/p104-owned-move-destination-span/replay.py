"""Replay exact donor exclusion, complete invoice and controls on a sealed word."""
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
WORD = "round30/complex/source/inputs/WORD.json.gz"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def unique(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def matches(actual, expected):
    assert decode(actual) == decode(expected.read_bytes()), expected.name


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
    assert set(provenance) == {
        "dependencies/" + WORD,
        "dependencies/round30/complex/source/inputs/CALLER.json.gz",
        "dependencies/round30/complex/source/inputs/EARLY-RESULT.json.gz",
    }
    for key, pin in provenance.items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], key
    assert provenance["dependencies/" + WORD]["commit"] == HEAD


def run():
    with TemporaryDirectory(prefix="p104-destination-span-") as temp:
        scratch = Path(temp)
        deps = scratch / "dependencies"
        shutil.copytree(HERE / "dependencies", deps)
        authenticate(scratch)
        indep = deps / "round41/independent"
        word = deps / WORD
        matches(subprocess_replay(indep / "donor_replay.py", "--word", word), indep / "RESULT.json")
        pair = scratch / "pair"
        subprocess_replay(HERE / "engines/pairs.py", deps / "round30", deps / "round41", pair)
        matches(subprocess_replay(indep / "replay_pairs.py", "--word", word),
                HERE / "receipts/independent/PAIRS.json")
        full = scratch / "full"
        subprocess_replay(HERE / "engines/fullbank.py", deps, full)
        matches(subprocess_replay(indep / "replay_bank.py", "--word", word),
                HERE / "receipts/independent/BANK.json")
        for path, scope in ((pair, "pairs"), (full, "fullbank")):
            for name in ("PRICE.json", "SUPPORT.json"):
                matches((path / name).read_bytes(), HERE / "receipts" / scope / name)
        pair_result = decode((pair / "SUPPORT.json").read_bytes())
        report = decode((full / "SUPPORT.json").read_bytes())
        rows = report["rows"]
        assert len(rows) == 47 and sum(len(r["donors"]) for r in rows) == 424
        assert all(r["kind"] == "separating_dual" for r in rows)
        assert not report["matches"] and not report["unvisited_moves"]
        assert pair_result["visited_pairs"] == 2767 and pair_result["unvisited_pairs"] == 0
        assert report["optimistic_saving_upper_after_support"] == "0"
        print("PASS_OWNED_MOVE_DESTINATION_SPAN moves=47 donors=424 pairs=2767 duals=47 independent_large_ranks=39 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    parser = ArgumentParser(description=__doc__)
    parser.parse_args()
    run()
