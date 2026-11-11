"""Reproduce all proof receipts against the canonical in-tree inputs."""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
BIT = PACKAGE.parent / "paired-query-only-bit"


def module(name):
    spec = spec_from_file_location(name, PACKAGE / (name + ".py"))
    loaded = module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def compare(result, filename):
    actual = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if actual != (PACKAGE / filename).read_text():
        raise ValueError(f"regenerated receipt differs: {filename}")


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    uniform = module("verify")
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for key in uniform.PINS:
            relative = Path(key).relative_to("bit")
            dest = root / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((BIT / relative).read_bytes())

        compare(uniform.run(root), "RESULT.json")
        compare(module("nonuniform").run(root), "NONUNIFORM.json")
        invoice = root / "bit/EFREE-RESULT.json"
        compare(module("nonuniform_audit").run(invoice), "NONUNIFORM-AUDIT.json")
        invoice.write_bytes(invoice.read_bytes() + b"\n")
        try:
            uniform.auth(root, "bit/EFREE-RESULT.json")
        except ValueError as error:
            if str(error) != "SHA-256 mismatch: bit/EFREE-RESULT.json":
                raise
        else:
            raise ValueError("accepted changed invoice")
    print("PASS_PAIRED_BIT_LANEWISE_IDLE_BOUND opposite=81 head=444+K-5e max_K=28 no_new_kappa")


if __name__ == "__main__":
    main()
