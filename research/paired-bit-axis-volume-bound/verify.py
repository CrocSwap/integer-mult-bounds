"""Replay the scoped paired BIT address and paid-volume certificate."""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
BIT = PACKAGE.parent / "paired-query-only-bit"


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    spec = spec_from_file_location("axis_gate", PACKAGE / "axis_gate.py")
    axis = module_from_spec(spec)
    spec.loader.exec_module(axis)
    actual = json.dumps(axis.run(BIT), indent=2, sort_keys=True) + "\n"
    if actual != (PACKAGE / "AXIS.json").read_text():
        raise ValueError("regenerated axis receipt differs")

    key = "EFREE-CALLER.json.gz"
    with TemporaryDirectory() as directory:
        mutant = Path(directory)
        (mutant / key).write_bytes((BIT / key).read_bytes() + b"\n")
        try:
            axis.authenticate(mutant, key)
        except ValueError as error:
            if str(error) != "SHA-256 mismatch: bit/" + key:
                raise
        else:
            raise ValueError("accepted changed caller source")
    print("PASS_PAIRED_BIT_AXIS_VOLUME_BOUND rank_mass=112V basis_columns=230 no_new_kappa")


if __name__ == "__main__":
    main()
