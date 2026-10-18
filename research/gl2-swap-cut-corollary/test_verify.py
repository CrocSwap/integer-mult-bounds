#!/usr/bin/env python3
"""Behavioral controls for the mathematical checker; Apache-2.0."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(path), *args],
                          text=True, capture_output=True, timeout=120)


def changed(source, old, new):
    require(source.count(old) == 1, "mutation anchor is not unique")
    return source.replace(old, new)


def main():
    source = (HERE / "verify.py").read_text()
    original = run(HERE / "verify.py")
    require(original.returncode == 0, original.stderr)
    reference = json.loads(original.stdout)
    controls = []
    with tempfile.TemporaryDirectory(prefix="swap-corollary-controls-") as td:
        root = Path(td)
        mutants = [
            ("removed_endpoint_guard",
             'require(matrix == endpoint(r, t), "complete formal endpoint")',
             "return None", "control unexpectedly accepted: complete formal endpoint"),
            ("rank_undercharge", "return len(pivots)", "return min(1, len(pivots))",
             "target crossing rank"),
            ("wrong_group_action", "VECTORS = (2, 3, 1)", "VECTORS = (1, 2, 3)",
             "adjacent label binding"),
            ("aliased_dirty_endpoint", "dirty[0][2] ^= UNIT", "dirty[0][2] ^= 0",
             "control unexpectedly accepted: complete formal endpoint"),
        ]
        for name, old, new, expected in mutants:
            path = root / (name + ".py")
            path.write_text(changed(source, old, new))
            p = run(path)
            require(p.returncode != 0 and expected in p.stderr,
                    name + " did not reject through its named control: " + p.stderr)
            controls.append(name)
        equivalent = root / "reindexed.py"
        equivalent.write_text(changed(source, "INDEX = {g: i for i, g in enumerate(GROUP)}",
                                      "GROUP = tuple(reversed(GROUP))\nINDEX = {g: i for i, g in enumerate(GROUP)}"))
        p = run(equivalent)
        require(p.returncode == 0 and json.loads(p.stdout) == reference,
                "equivalent group-basis order rejected: " + p.stderr)
        controls.append("equivalent_group_basis")

        output = root / "occupied.json"
        output.write_text("preserve this evidence\n")
        p = run(HERE / "verify.py", "--output", str(output))
        require(p.returncode != 0 and "FileExistsError" in p.stderr
                and output.read_text() == "preserve this evidence\n",
                "existing evidence was not protected")
        controls.append("occupied_output")

        # Neither implementation needs Git or any undeclared repository path.
        export = root / "readonly"
        package = export / "research" / "gl2-swap-cut-corollary"
        package.mkdir(parents=True)
        paths = []
        for name in ("verify.py", "independent.py"):
            path = package / name
            path.write_bytes((HERE / name).read_bytes())
            paths.append(path)
        for relative in ("research/symmetric-adjacent-cut-bound/PROOF.md",
                         "research/four-swap-full-occupancy/README.md"):
            path = export / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((HERE.parents[1] / relative).read_bytes())
            paths.append(path)
        before = {p.relative_to(export).as_posix(): p.read_bytes() for p in paths}
        directories = [p for p in export.rglob("*") if p.is_dir()] + [export]
        independent_source = paths[1].read_text()
        mutant = package / "independent_mutant.py"
        mutant.write_text(changed(independent_source,
                                  'require(actual == expected, "complete_endpoint")',
                                  'return None'))
        p = run(mutant)
        require(p.returncode != 0 and "negative control accepted: complete_endpoint" in p.stderr,
                "independent endpoint detector removal was not detected: " + p.stderr)
        mutant.unlink()
        controls.append("independent_removed_endpoint_guard")
        # Reject missing or changed proof inputs before doing the finite replay.
        dependency = paths[2]
        saved = dependency.read_bytes()
        dependency.write_bytes(saved + b"\nchanged source\n")
        p = run(paths[1])
        require(p.returncode != 0 and "source_pin:" in p.stderr,
                "changed proof source was accepted: " + p.stderr)
        dependency.unlink()
        p = run(paths[1])
        require(p.returncode != 0 and "FileNotFoundError" in p.stderr,
                "missing proof source was accepted: " + p.stderr)
        dependency.write_bytes(saved)
        controls.append("changed_and_missing_source_inputs")
        try:
            for path in paths:
                path.chmod(0o444)
            for path in directories:
                path.chmod(0o555)
            for path in paths[:2]:
                p = run(path)
                require(p.returncode == 0, "read-only relocation failed: " + p.stderr)
            require(before == {p.relative_to(export).as_posix(): p.read_bytes() for p in paths},
                    "export changed")
            require(sorted(p.relative_to(export).as_posix() for p in export.rglob("*") if p.is_file()) == sorted(before),
                    "replay left undeclared files")
        finally:
            for path in directories:
                path.chmod(0o755)
            for path in paths:
                path.chmod(0o644)
        controls.append("git_free_readonly_relocation_both_engines")
    print(json.dumps({"status": "PASS_GL2_SWAP_PACKAGE_CONTROLS", "controls": controls,
                      "assertions_required": False}, sort_keys=True))


if __name__ == "__main__":
    main()
