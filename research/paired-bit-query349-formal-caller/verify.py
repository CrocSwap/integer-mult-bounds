"""Replay both signed caller orientations and the directed raw price."""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
BIT = PACKAGE.parent / "paired-query-only-bit"


def source_module(filename):
    spec = spec_from_file_location(filename, PACKAGE / filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_receipt(receipt, filename):
    expected = (PACKAGE / filename).read_text()
    actual = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if actual != expected:
        raise ValueError(f"regenerated receipt differs: {filename}")


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    endpoint = source_module("HEAD-REPLAY.py")
    verify_receipt(endpoint.main(BIT), "HEAD-REPLAY.json")
    verify_receipt(source_module("HEAD-REPLAY-price.py").price(BIT), "HEAD-REPLAY-price.json")

    key = "EFREE-CALLER.json.gz"
    raw = bytearray((BIT / key).read_bytes())
    raw[-1] ^= 1
    with TemporaryDirectory() as directory:
        mutated = Path(directory)
        (mutated / key).write_bytes(raw)
        try:
            endpoint.load(mutated, key)
        except ValueError as error:
            if str(error) != f"sha256 mismatch: {key}":
                raise
        else:
            raise ValueError("accepted changed caller source")

    print("PASS_PAIRED_BIT_QUERY349_FORMAL_CALLER coefficients=1444x2 stages=18 controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
