#!/usr/bin/env python3
"""Defer the retained Jensen entry's POSIX import until its guarded child.

Produced by Nick Petalas. Apache-2.0. The retained entry is Chris R's PR5614.
"""

import hashlib
from pathlib import Path
from types import ModuleType


SOURCE = Path(__file__).resolve().parent.parent / "p104-jensen-compiler-benchmark"
PINS = (
    ("verify.py", "e4ea0ea30f715115d5054c317af81ec814ebc4270b2bff4aa3acb83bced9a5e2"),
    ("PAYLOAD-INVENTORY.json", "ed12d58b9a3889a2656c2d21475dd2c230c8e376e0eda0ba8e23560bd12c396a"),
)


def adapt(raw: bytes) -> str:
    """Accept only the frozen entry, then move exactly one import."""
    if hashlib.sha256(raw).hexdigest() != PINS[0][1]:
        raise ValueError("retained source hash: verify.py")
    original = raw.decode("utf-8")
    before_import = "\nimport resource\n"
    before_function = "\ndef child_limits():\n"
    if original.count(before_import) != 1 or original.count(before_function) != 1:
        raise ValueError("retained import/function anchors")
    return original.replace(before_import, "\n", 1).replace(
        before_function, before_function + "    import resource\n", 1
    )


def load(source: Path = SOURCE) -> ModuleType:
    """Load the pinned entry; its original main still selects the operation."""
    for name, expected in PINS:
        path = source / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 262144:
            raise ValueError("invalid retained source: " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("retained source hash: " + name)
    module = ModuleType("retained_jensen_lazy_resource")
    module.__file__ = str(source / "verify.py")
    compiled = compile(adapt((source / "verify.py").read_bytes()), module.__file__, "exec")
    exec(compiled, module.__dict__)
    return module


def main() -> None:
    load().main()


if __name__ == "__main__":
    main()
