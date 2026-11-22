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
    run(["git", "apply", "--no-index", str(HERE / "machine.patch")],
        check=True, cwd=destination)
    run(["git", "apply", "--no-index", str(HERE / "receiver.patch")],
        check=True, cwd=destination)
    for name in ("five_exchange", "installations", "raw_binary_stage", "retimed_supplier", "transport", "unpowered_price", "fiscal_scans"):
        copyfile(HERE / f"{name}.py", destination / f"{name}.py")
    target_k7 = destination / "strong-bit.json.gz"
    k7_source = HERE / "strong-bit-k7.json.gz"
    if sha256(k7_source.read_bytes()).hexdigest() != "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362":
        raise ValueError("seed_k7 binary source archive digest differs")
    copyfile(k7_source, target_k7)
    strong_binary_file = destination / "strong_binary.py"
    sb_text = strong_binary_file.read_text(encoding="utf-8")
    if "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326" not in sb_text:
        raise ValueError("Expected predecessor binary digest in strong_binary.py")
    strong_binary_file.write_text(sb_text.replace("74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326", "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362", 1), encoding="utf-8")
    ind_price_file = destination / "independent_binary_price.py"
    ibp_text = ind_price_file.read_text(encoding="utf-8")
    if "104_904" not in ibp_text:
        raise ValueError("Expected predecessor paid port count in independent_binary_price.py")
    ind_price_file.write_text(ibp_text.replace("104_904", "104_652", 1), encoding="utf-8")


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser(description=__doc__)
    cli.add_argument("destination", type=Path)
    target = cli.parse_args().destination.resolve()
    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()):
        cli.error("Select an empty destination for this installation")
    install(target)
