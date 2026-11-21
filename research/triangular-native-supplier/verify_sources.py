"""Compare each retained source with its original Git object."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
sys.path.insert(0, str(base))
from retained import install


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    _, parent, _, older = install()
    receipts = json.loads((base / "inputs/retained.json").read_text())
    history = json.loads((parent / "inputs/origins.json").read_text())
    proofs = json.loads((base / "lean/retained/sources.json").read_text())
    checked = 0

    def compare(file, commit, path, digest):
        nonlocal checked
        blob = subprocess.check_output(
            ["git", "-C", str(args.checkout), "show", commit + ":" + path]
        )
        if sha256(blob).hexdigest() != digest or file.read_bytes() != blob:
            raise ValueError("Source differs from the pinned file " + path)
        checked += 1

    for name, pin in receipts["members"].items():
        compare(parent / name, receipts["commit"], pin["path"], pin["sha256"])
    for name, pin in history["members"].items():
        compare(older / name, pin["commit"], name, pin["sha256"])
    for name, pin in proofs.items():
        compare(base / "lean/retained" / name, pin["commit"], pin["path"], pin["sha256"])
    print(
        "PASS_TRIANGULAR_SOURCES",
        checked,
        "source bindings",
        len(receipts["members"]),
        "direct",
        len(history["members"]),
        "nested",
        len(proofs),
        "Lean",
    )


if __name__ == "__main__":
    main()
