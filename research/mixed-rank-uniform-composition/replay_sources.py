"""Replay the pinned native packages and the two mixed-price verifiers."""

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bind_compiler import MIXED, MP, NATIVE, NP

BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
HERE = Path(__file__).resolve().parent


def extract(head, paths, destination):
    with TemporaryDirectory() as staging:
        archive = Path(staging) / "source.tar"
        with archive.open("wb") as output:
            subprocess.run(["git", "archive", head, "--", *paths], stdout=output, check=True)
        with tarfile.open(archive) as source:
            source.extractall(destination, filter="data")


def execute(script, *arguments):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, arguments)], check=True)


def main(cache, fetch):
    if not cache.is_dir() and not fetch:
        raise ValueError("Provide a populated mixed-source cache or use --fetch.")
    for script in ["bind_compiler.py", "check_binding.py", "check_ordinary.py"]:
        execute(HERE / script)
    execute(HERE / "lean/generate_moments.py", "--check")
    with TemporaryDirectory() as temporary:
        work = Path(temporary)
        extract(NATIVE, [NP], work)
        native = work / NP
        manifest = json.loads((native / "VERIFY.json").read_text())
        extract(BASE, manifest["inputs"], work)
        for name in ["check_complex.py", "check_binary.py", "check_leaves.py"]:
            execute(native / name)
        execute(native / "charts.py", "--check-build")
        execute(HERE / "check_weighted.py", native)
        extract(MIXED, [MP], work)
        source = work / MP
        producer, review = work / "producer", work / "review"
        network = ["--fetch"] if fetch else []
        execute(source / "verify.py", "--work", cache, "--out", producer, *network)
        execute(source / "review/independent.py", "--work", cache, "--out", review,
                "--producer", producer, *network)
        for name in ["RESULT.json", "BIT.json", "AUDIT.json"]:
            if (source / name).read_bytes() != (producer / name).read_bytes():
                raise ValueError(f"Producer changed {name}.")
        for name in ["APPLICATION.json", "AUDIT.json"]:
            result = (producer / name).read_bytes()
            if result != (review / name).read_bytes():
                raise ValueError(f"Review changed {name}.")
            print(name, hashlib.sha256(result).hexdigest(), flush=True)
    print("PASS_PINNED_COMPLETE_APPLICATION_AND_NATIVE_REPLAYS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True, help="Mixed-source cache directory")
    parser.add_argument("--fetch", action="store_true", help="Fetch missing source inputs")
    args = parser.parse_args()
    main(args.cache.resolve(), args.fetch)
