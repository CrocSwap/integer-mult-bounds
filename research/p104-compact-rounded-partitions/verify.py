"""Replay the compact rounded-packet installation from its exact peer source."""

from argparse import ArgumentParser
from hashlib import sha256
import json
import runpy
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
EXPECTED_HEAD = "7b48187d99525ad59f560de3921ec7e48382484c"


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Repeated source key {name}")
        result[name] = value
    return result


def restore(work: Path) -> None:
    source = json.loads((HERE / "PEER-SOURCE.json").read_bytes(), object_pairs_hook=unique_object)
    if source["head"] != EXPECTED_HEAD:
        raise ValueError("Unexpected peer commit")
    archive = HERE / "peer8055.tar.gz"
    if sha256(archive.read_bytes()).hexdigest() != source["archive_sha256"]:
        raise ValueError("Peer archive differs")
    files = source["files_sha256"]
    seen = set()
    with tarfile.open(archive) as bundle:
        for entry in bundle:
            path = Path(entry.name)
            if path.is_absolute() or ".." in path.parts or str(path) != entry.name:
                raise ValueError("Unexpected archive path")
            if not entry.isfile() or entry.name in seen or entry.name not in files:
                raise ValueError(f"Unexpected or repeated peer file {entry.name}")
            content = bundle.extractfile(entry).read()
            if sha256(content).hexdigest() != files[entry.name]:
                raise ValueError(f"Source differs at {entry.name}")
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            seen.add(entry.name)
    if seen != files.keys():
        raise ValueError("Peer archive is missing a file")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("price", "interval", "binary", "gaussian", "product", "setup"))
    args = parser.parse_args()
    with TemporaryDirectory(prefix="compact-rounded-signed-") as directory:
        root = Path(directory)
        peer, work = root / "peer", root / "candidate"
        restore(peer)
        prepare = runpy.run_path(str(HERE / "prepare.py"))
        prepare["materialize"](peer, HERE / "COMPACT-PRICE.json", HERE / "integer-prototype.py", work)
        (work / "RESULT.json").write_bytes((HERE / "RESULT.json").read_bytes())
        subprocess.run([sys.executable, "-IB", str(work / "verify.py"), args.mode], check=True)
        print("PASS_COMPACT_ROUNDED_PARTITIONS", args.mode, flush=True)


if __name__ == "__main__":
    main()
