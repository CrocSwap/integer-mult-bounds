#!/usr/bin/env python3
"""Restore the pinned source and replay the optional Lean 4.36 kernel proof."""
import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
PROOF_SHA256 = "ee9ec96c4f92b2a45f6d2998db0383b43e4051b32131be09ff1c3a36d3b1bec2"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(sha256((HERE / "CappedPower.lean").read_bytes()).hexdigest() == PROOF_SHA256,
            "reviewed proof bytes changed")
    source = PACKAGE / "sources/pr8042"
    manifest = json.loads((PACKAGE / "SOURCE-BINDINGS.json").read_text())
    require(manifest["commit"] == "dfd25d553a843a946ca0b94130a5ff8943e98fdd",
            "unexpected runtime source")
    for name, pin in manifest["files"].items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts, "invalid source path")
        data = (source / path).read_bytes()
        require(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"],
                "changed pinned source: " + name)
    spec = spec_from_file_location("capped_power_bootstrap", source / "bootstrap.py")
    bootstrap = module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    with TemporaryDirectory(prefix="capped-power-kernel-") as temporary:
        runtime = Path(temporary)
        bootstrap.install(runtime)
        sys.path.insert(0, str(runtime))
        from upstream import install
        install()
        import positive
        subprocess.run([
            sys.executable, "-I", "-B", str(HERE / "verify.py"),
            "--lean", str(args.lean.resolve()), "--runtime", str(runtime),
            "--positive", str(Path(positive.__file__).resolve()),
            "--outer-stop", str(source / "lean/OuterStop.lean"),
            "--output", str(args.output.resolve()),
        ], check=True)
    print("PASS_CAPPED_POWER_KERNEL_AND_SOURCE_BINDING")


if __name__ == "__main__":
    main()
