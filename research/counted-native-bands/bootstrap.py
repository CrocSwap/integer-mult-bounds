"""Restore the two pinned predecessor packages and apply the reviewed local source changes."""

from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from subprocess import run
import tarfile

HERE = Path(__file__).resolve().parent


def unpack(destination):
    frozen = HERE / "predecessor"
    spec = json.loads((frozen / "SOURCES.json").read_bytes())["offline_predecessor"]
    archive = frozen / spec["archive"]
    if sha256(archive.read_bytes()).hexdigest() != spec["archive_sha256"]:
        raise ValueError("The archived predecessor differs")
    found = set()
    with tarfile.open(archive) as package:
        for entry in package:
            name = entry.name
            path = Path(name)
            if (name not in spec["files"] or not entry.isfile() or name in found
                    or path.is_absolute() or ".." in path.parts or str(path) != name):
                raise ValueError("Unexpected predecessor source")
            record = spec["files"][name]
            data = package.extractfile(entry).read()
            if len(data) != record["size"] or sha256(data).hexdigest() != record["sha256"]:
                raise ValueError(f"The source differs at {name}")
            found.add(name)
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if found != spec["files"].keys():
        raise ValueError("A predecessor source is missing")
    for name, changes in json.loads((frozen / "OVERLAY.json").read_bytes()).items():
        target = destination / name
        data = target.read_bytes()
        if sha256(data).hexdigest() != changes["old_sha256"]:
            raise ValueError(f"The base of the signed-margin extension differs at {name}")
        source = data.decode()
        for old, new in changes["edits"]:
            if source.count(old) != 1:
                raise ValueError(f"The signed-margin change has no unique site at {name}")
            source = source.replace(old, new)
        data = source.encode()
        if sha256(data).hexdigest() != changes["new_sha256"]:
            raise ValueError(f"The signed-margin extension differs at {name}")
        target.write_bytes(data)


def install(destination):
    unpack(destination)
    run(["git", "apply", "--no-index", str(HERE / "integration.patch")],
        check=True, cwd=destination)
    for name in ("counted_band", "smooth_word", "stream_epoch"):
        copyfile(HERE / f"{name}.py", destination / f"{name}.py")
