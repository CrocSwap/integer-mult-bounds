"""Restore authenticated public inputs, apply one retune and replay a signed mode."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import runpy
from subprocess import run
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "cbe847a953b971f9c6c5a0a6661e2008acd29086"
SOURCE_SHA = "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51"


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"Repeated source key {name}")
        result[name] = value
    return result


def restore(tree):
    source = (HERE / "PEER-SOURCE.json").read_bytes()
    if sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError("Peer source manifest differs")
    pins = json.loads(source, object_pairs_hook=unique_object)
    archive = HERE / "peer8057.tar.gz"
    if pins["head"] != HEAD or sha256(archive.read_bytes()).hexdigest() != pins["archive_sha256"]:
        raise ValueError("Unexpected source archive")
    seen = set()
    with tarfile.open(archive) as bundle:
        for item in bundle:
            path = Path(item.name)
            if path.is_absolute() or ".." in path.parts or str(path) != item.name:
                raise ValueError(f"Invalid source path {item.name}")
            if item.isdir():
                continue
            if not item.isfile() or item.name in seen or item.name not in pins["files_sha256"]:
                raise ValueError(f"Unexpected or repeated peer file {item.name}")
            data = bundle.extractfile(item).read()
            if sha256(data).hexdigest() != pins["files_sha256"][item.name]:
                raise ValueError(f"Source differs at {item.name}")
            destination = tree / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            seen.add(item.name)
    if seen != pins["files_sha256"].keys():
        raise ValueError("Source archive is missing a file")
    return tree / "research" / "frequency-weighted-native-multiplier"


def main():
    modes = ("price", "calendar", "raw", "exterior", "nested", "product", "setup", "regenerate")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=modes)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="k7-shortcut-lift-") as temporary:
        tree = Path(temporary)
        peer = restore(tree)
        runpy.run_path(str(HERE / "prepare.py"))["materialize"](peer)
        for name in ("check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py"):
            (peer / name).write_bytes((HERE / name).read_bytes())
        if args.mode == "regenerate":
            runtime = tree / "runtime"
            run([sys.executable, "-IB", str(peer / "bootstrap.py"), str(runtime)], check=True)
            result = run([sys.executable, "-IB", str(peer / "receipt.py"), str(runtime)], check=True, capture_output=True, text=True)
            print(json.dumps(json.loads(result.stdout), indent=2))
            return
        if args.mode == "setup":
            serial = peer.parent / "tiered-native-multiplier" / "check_serial_setup.py"
            run([sys.executable, "-IB", str(serial)], check=True)
        else:
            (peer / "RESULT.json").write_bytes((HERE / "RESULT.json").read_bytes())
            run([sys.executable, "-IB", str(peer / "verify.py"), args.mode], check=True)
        print("PASS_SHORTCUT_WORD_LIFT_20BIT", args.mode, flush=True)


if __name__ == "__main__":
    main()
