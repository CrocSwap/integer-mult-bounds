"""Restore and bind the two signed tiers from the archived research sources."""

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


def install(destination):
    dest = Path(destination).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()):
        raise ValueError("Use an empty installation directory")
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    for name, hex_digest in pins["archive_and_overlay_sha256"].items():
        if sha256((HERE / name).read_bytes()).hexdigest() != hex_digest:
            raise ValueError(f"The source differs at {name}")
    with TemporaryDirectory(prefix="tier-source-") as temp:
        folder = Path(temp)
        entries = dict(pins["installer_files"])
        with tarfile.open(HERE / "source/installer.tar.gz") as source:
            for member in source:
                name = member.name
                if name not in entries or Path(name).name != name or not member.isfile():
                    raise ValueError("Invalid fixed source entry")
                data = source.extractfile(member).read()
                if sha256(data).hexdigest() != entries.pop(name):
                    raise ValueError(f"The fixed source differs at {name}")
                (folder / name).write_bytes(data)
        if entries:
            raise ValueError("The fixed compiler is incomplete")
        run([sys.executable, "-IB", str(folder / "bootstrap.py"), str(dest)], check=True)
    for phase in ("before", "after"):
        for name, hashes in pins["runtime"].items():
            if sha256((dest / name).read_bytes()).hexdigest() != hashes[phase]:
                raise ValueError(f"The {phase} image differs at {name}")
        if phase == "before":
            run(["git", "apply", "--no-index", str(HERE / "runtime.patch")], check=True, cwd=dest)
            copyfile(HERE / "source/strong-bit-k7.json.gz", dest / "strong-bit.json.gz")
            copyfile(HERE / "installations.py", dest / "installations.py")
    copyfile(HERE / "grades.py", dest / "grades.py")


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("destination", type=Path)
    install(cli.parse_args().destination)
