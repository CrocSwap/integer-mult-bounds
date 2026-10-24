"""Repeat the producer checks without writes to their frozen paths."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
OUTPUT = HERE / "producer-replay"
FAMILY = "controller-followthrough-20261017/"
JOBS = [
    (FAMILY+"partial-orthogonal/check_partial_orthogonal.py",
     ["PARTIAL-ORTHOGONAL.json", "PARTIAL-ORTHOGONAL-PROGRAM.json.gz"]),
    (FAMILY+"partial-orthogonal/check_symmetric_family.py", ["SYMMETRIC-FAMILY.json"]),
    (FAMILY+"structured-centres/check_structured_centres.py",
     ["STRUCTURED-CENTRES.json", "STRUCTURED-CENTRES-PROGRAM.json.gz"]),
    (FAMILY+"structured-centres/check_rank8_gauges.py", ["RANK8-GAUGES.json"]),
    (FAMILY+"structured-centres/check_rank8_gauges_v2.py", ["RANK8-GAUGES-V2.json"]),
]


def main():
    OUTPUT.mkdir(exist_ok=True)
    for directory in ("partial-orthogonal", "structured-centres"):
        sys.path.insert(0, str(LANES / FAMILY / directory))
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
