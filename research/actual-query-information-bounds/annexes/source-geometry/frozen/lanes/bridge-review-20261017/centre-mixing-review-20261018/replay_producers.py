"""Repeat the producer checks without writing to their frozen paths."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
OUTPUT = HERE / "producer-replay"
JOBS = [
    ("oblique-native-20261017/interior-cut/inventory_new_edges.py", ["ALL-CUT-EDGES.json", "ALL-CUT-EDGES.json.gz"]),
    ("oblique-native-20261017/interior-cut/check_frame_support.py", ["FRAME-SUPPORT.json"]),
    ("coherent-port/centre-mixing-20261018/check_support.py", ["SUPPORT.json"]),
    ("coherent-port/centre-mixing-20261018/check_mixing.py", ["MIXING.json"]),
]


def main():
    OUTPUT.mkdir(exist_ok=True)
    sys.path.insert(0, str(LANES / "oblique-native-20261017/interior-cut"))
    receipts = []
    write_text, write_bytes = Path.write_text, Path.write_bytes
    for name, outputs in JOBS:
        source = LANES / name
        pins = {output: sha256((source.parent/output).read_bytes()).hexdigest() for output in outputs}

        def destination(path):
            if path.parent != source.parent or path.name not in outputs:
                raise ValueError("Undeclared producer write: " + str(path))
            return OUTPUT / path.name

        def redirect_text(path, *args, **kwargs):
            return write_text(destination(path), *args, **kwargs)

        def redirect_bytes(path, *args, **kwargs):
            return write_bytes(destination(path), *args, **kwargs)

        with patch.object(Path, "write_text", redirect_text), patch.object(Path, "write_bytes", redirect_bytes):
            runpy.run_path(str(source), run_name="__main__")
        for output in outputs:
            original = sha256((source.parent/output).read_bytes()).hexdigest()
            actual = sha256((OUTPUT/output).read_bytes()).hexdigest()
            if original != pins[output] or actual != original:
                raise ValueError("Producer output mismatch: " + output)
            receipts.append(dict(source=name, output=output, sha256=actual,
                                 source_unchanged=True, output_equal=True))
    (HERE/"PRODUCER-REPLAY.json").write_text(json.dumps(receipts, indent=2, sort_keys=True)+"\n")
    print("ALL_PRODUCER_OUTPUTS_BYTE_EQUAL", flush=True)


if __name__ == "__main__":
    main()
