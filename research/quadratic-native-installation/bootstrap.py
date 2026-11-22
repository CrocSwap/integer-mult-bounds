"""Restore the pinned signed machine in a clean directory and install the new compiler."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from subprocess import run
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def install(destination, original=False):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("The installation needs an empty output directory")
    source = json.loads((HERE / "SOURCES.json").read_bytes())
    archive = HERE / "retimed-source.tar.gz"
    if sha256(archive.read_bytes()).hexdigest() != source["precursor_archive_sha256"]:
        raise ValueError("The signed source archive differs from its pin")
    with TemporaryDirectory(prefix="phase-source-") as temp:
        previous = Path(temp)
        expected = dict(source["precursor_files"])
        with tarfile.open(archive) as tape:
            for member in tape:
                name = member.name
                path = Path(name)
                if (
                    name not in expected
                    or not member.isfile()
                    or path.is_absolute()
                    or ".." in path.parts
                ):
                    raise ValueError("Unexpected frozen source entry")
                data = tape.extractfile(member).read()
                if sha256(data).hexdigest() != expected.pop(name):
                    raise ValueError(f"The frozen source differs at {name}")
                out = previous / path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
        if expected:
            raise ValueError("The frozen source archive is incomplete")
        run(
            [
                sys.executable,
                "-I",
                "-B",
                str(previous / "bootstrap.py"),
                str(destination),
            ],
            check=True,
        )
        copyfile(
            previous / "check_nonzero_eight.py", destination / "check_nonzero_eight.py"
        )
    if original:
        return
    patch = HERE / "production.patch"
    if sha256(patch.read_bytes()).hexdigest() != source["production_patch_sha256"]:
        raise ValueError("The installation delta differs")
    for phase in ("before", "after"):
        for name, pins in source["runtime_patch_sha256"].items():
            if sha256((destination / name).read_bytes()).hexdigest() != pins[phase]:
                raise ValueError(f"The {phase} image differs at {name}")
        if phase == "before":
            run(["git", "apply", "--no-index", str(patch)], cwd=destination, check=True)
    for module in (
        "gauss_phase.py",
        "phase_atlas.py",
        "sparse_helpers.py",
        "clock_ports.py",
    ):
        copyfile(HERE / module, destination / module)


if __name__ == "__main__":
    args = ArgumentParser(description=__doc__)
    args.add_argument("destination", type=Path)
    args.add_argument("--original", action="store_true")
    opts = args.parse_args()
    install(opts.destination, opts.original)
