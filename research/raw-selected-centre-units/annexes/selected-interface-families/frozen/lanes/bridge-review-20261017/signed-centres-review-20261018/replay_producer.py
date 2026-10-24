"""Repeat the signed native producer without writes to frozen paths."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
FAMILY = HERE.parents[1]/"controller-followthrough-20261017"
PRODUCER = FAMILY/"bipartite-eight-20261018"
OUTPUT = HERE/"producer-replay"
NAMES = ["BIPARTITE-EIGHT.json", "BIPARTITE-EIGHT-PROGRAM.json.gz"]


def main():
    OUTPUT.mkdir(exist_ok=True)
    for directory in ("partial-orthogonal", "structured-centres"):
        sys.path.insert(0, str(FAMILY/directory))
    pins = {name:sha256((PRODUCER/name).read_bytes()).hexdigest() for name in NAMES}
    write_text, write_bytes = Path.write_text, Path.write_bytes

    def destination(path):
        if path.parent != PRODUCER or path.name not in NAMES:
            raise ValueError("Undeclared producer write: " + str(path))
        return OUTPUT/path.name

    def redirect_text(path, *args, **kwargs):
        return write_text(destination(path), *args, **kwargs)

    def redirect_bytes(path, *args, **kwargs):
        return write_bytes(destination(path), *args, **kwargs)

    with patch.object(Path, "write_text", redirect_text), patch.object(Path, "write_bytes", redirect_bytes):
        runpy.run_path(str(PRODUCER/"check_bipartite_eight.py"), run_name="__main__")
    receipt = []
    for name in NAMES:
        original = sha256((PRODUCER/name).read_bytes()).hexdigest()
        actual = sha256((OUTPUT/name).read_bytes()).hexdigest()
        if original != pins[name] or original != actual:
            raise ValueError("Producer output mismatch: " + name)
        receipt.append(dict(name=name, sha256=actual, source_unchanged=True, byte_equal=True))
    (HERE/"PRODUCER-REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print("SIGNED_PRODUCER_OUTPUTS_BYTE_EQUAL", flush=True)


if __name__ == "__main__":
    main()
