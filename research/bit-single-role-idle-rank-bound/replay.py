"""Reconstruct the two idle-pair rank certificates from pinned BIT inputs."""
from argparse import ArgumentParser
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
from shutil import copyfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
BIT = "research/paired-query-only-bit/"


def unique(raw):
    def keyed(items):
        result = dict(items)
        assert len(result) == len(items), "duplicate JSON key"
        return result
    return json.loads(raw, object_pairs_hook=keyed)


def index_sources(records):
    paths = {record["path"]: record for record in records}
    assert len(paths) == len(records), "duplicate source path"
    return paths


def reject(fn, value):
    try:
        fn(value)
    except AssertionError:
        return
    raise AssertionError("duplicate control accepted")


def run(root):
    manifest = unique((HERE / "SOURCES.json").read_bytes())
    pins = index_sources(manifest["files"])
    reject(unique, b'{"a":1,"a":2}')
    reject(index_sources, [{"path": "same"}, {"path": "same"}])
    files = {
        BIT + "EFREE-CALLER.json.gz": "preflight/EFREE-CALLER.json.gz",
        BIT + "retained/inputs/BIT-NATIVE-WORD.json.gz": "native/inputs/WORD.json.gz",
        BIT + "EFREE-RESULT.json": "native/inputs/INVOICE.json",
    }
    assert set(files) == {name for name, pin in pins.items() if pin["usage"] == "input"}
    with TemporaryDirectory(prefix="idle-rank-replay-") as scratch:
        temp = Path(scratch)
        for source, dest in files.items():
            data = (root / source).read_bytes()
            pin = pins[source]
            assert sha256(data).hexdigest() == pin["sha256"], source
            assert sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == pin["git_blob"], source
            unique(gzip.decompress(data) if source.endswith(".gz") else data)
            target = temp / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        copyfile(HERE / "rank_gate.py", temp / "preflight/rank_gate.py")
        primary = runpy.run_path(str(temp / "preflight/rank_gate.py"))["run"]()
        assert unique(json.dumps(primary)) == unique((HERE / "PRIMARY.json").read_bytes())
        result = runpy.run_path(str(HERE / "verify.py"))["audit"](temp / "preflight", temp / "native", None)
        assert unique(json.dumps(result)) == unique(gzip.decompress((HERE / "RESULT.json.gz").read_bytes()))
        return {
            "primary_rank_two": primary["rank_counts"][2],
            "independent_rank_two": result["rank"]["disjoint_pair_rank_two"],
            "whole_realizable_upper": result["whole_realizable_upper"],
            "shortfall": result["shortfall_lower"],
        }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    print(json.dumps(run(parser.parse_args().root), sort_keys=True))
