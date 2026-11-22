"""Replay a fixed-carrier price edit by restoring the exact registered peer package."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
EXPECTED_HEAD = "baaec65bf8e4c7e92be110a00d5b06522177931f"
REPLACEMENTS = {
    "installations.py": (
        ("Q(2092819, 2**29)", "Q(1071523491, 2**38)"),
        ('Q(".003898171")', 'Q(".0038981721342")'),
    ),
    "check_complete.py": (
        ('"gaussian_c_decimal": "0.003898179158568382"', '"gaussian_c_decimal": "0.003898179751558928"'),
        ('"extended_kappa": "0.003898171"', '"extended_kappa": "0.0038981721342"'),
    ),
    "check_extended_stop.py": (
        ("F(2092819,2**29)", "F(1071523491,2**38)"),
    ),
}
MODES = ("binary", "cost", "schedule", "install", "physical", "receiver", "slabs", "product")


def restore(work: Path) -> None:
    source = json.loads((HERE / "PEER-SOURCE.json").read_bytes())
    if source["head"] != EXPECTED_HEAD:
        raise ValueError("Unexpected peer commit")
    archive = HERE / "peer8052.tar.gz"
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


def edit_installation(work: Path) -> None:
    for name, replacements in REPLACEMENTS.items():
        path = work / name
        text = path.read_text()
        for old, new in replacements:
            if text.count(old) != 1:
                raise ValueError(f"Expected one change point in {name}")
            text = text.replace(old, new)
        path.write_text(text)
    (work / "RESULT.json").write_bytes((HERE / "RESULT.json").read_bytes())


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=MODES)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="p104-fixed-carrier-") as temporary:
        work = Path(temporary)
        restore(work)
        edit_installation(work)
        subprocess.run([sys.executable, "-IB", str(work / "verify.py"), args.mode], check=True)
        print("PASS_GAUSSIAN_FIXED_CARRIER", args.mode, flush=True)


if __name__ == "__main__":
    main()
