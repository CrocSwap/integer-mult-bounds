#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the public replay on a Git-free export and reject changed evidence."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from memory import MAX_MEMORIES, insert, require, span
from verify import HERE, INPUTS, OLD, ROOT, read


def run(script, expected, marker):
    result = subprocess.run(
        [sys.executable, "-O", "-Werror", "-B", str(script)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    require(result.returncode == expected, result.stdout + result.stderr)
    require(marker in result.stdout + result.stderr, "expected CLI marker: " + marker)


def boundary_controls():
    try:
        insert(
            [span([v]) for v in range(1, MAX_MEMORIES + 1)], span([MAX_MEMORIES + 1])
        )
    except ValueError as error:
        require(
            str(error) == "memory antichain capacity", "specific resource rejection"
        )
    else:
        raise ValueError("capacity exhaustion must not return an exclusion")
    with tempfile.TemporaryDirectory(prefix="p104-json-") as temporary:
        path = Path(temporary) / "duplicate.json"
        path.write_text('{"x":1,"x":2}')
        try:
            read(path)
        except ValueError as error:
            require(str(error) == "duplicate JSON key", "duplicate-key rejection")
        else:
            raise ValueError("duplicate evidence keys accepted")


def export_controls():
    with tempfile.TemporaryDirectory(prefix="p104-memory-export-") as temporary:
        root = Path(temporary)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        files = [path for path in HERE.iterdir() if path.is_file()]
        require(len(files) <= 20, "bounded package inventory")
        for path in files:
            shutil.copyfile(path, package / path.name)
        for relative in INPUTS:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        script = package / "verify.py"
        run(script, 0, "PASS_P104_MEMORY_RELAXATION_SOUNDNESS")
        receipt = package / "RESULT.json"
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed["no_new_kappa"] = 1
        receipt.write_text(json.dumps(changed))
        run(script, 1, "typed receipt mismatch")
        receipt.write_bytes(original)
        source = root / OLD
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"\n")
        run(script, 1, "source changed:")
        source.write_bytes(original_source)
        # All replayed files and inputs can be read-only; no Git is present.
        for path in list(package.iterdir()) + [root / rel for rel in INPUTS]:
            if path.is_file():
                path.chmod(0o444)
        run(script, 0, "PASS_P104_MEMORY_RELAXATION_SOUNDNESS")
        require(not list(root.rglob("__pycache__")), "bytecode-free direct export")
        # Restore permissions for portable TemporaryDirectory cleanup.
        for path in list(package.iterdir()) + [root / rel for rel in INPUTS]:
            if path.is_file():
                path.chmod(0o644)


def main():
    boundary_controls()
    export_controls()
    print(
        "PASS_P104_MEMORY_CLI export=read_only_git_free "
        "rejection_groups=4 optimized=True"
    )


if __name__ == "__main__":
    main()
