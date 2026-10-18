"""Behavioral boundary and private source controls. Nick Petalas, Apache-2.0."""

import copy
import json
import stat
import subprocess
import sys
import tempfile
from itertools import islice
from pathlib import Path

from verify import (
    PACKAGE,
    ROOT,
    authenticate,
    canonical,
    certificate,
    read_json,
    require,
)


def rejects(action, fragment):
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), "unexpected failure: " + str(error))
    else:
        raise ValueError("control was accepted: " + fragment)


def private_copy(destination):
    paths = list(islice(PACKAGE.rglob("*"), 33))
    paths.append(ROOT / "research/p112-root-simplex-exclusion/geometry.py")
    require(len(paths) <= 32, "private-copy inventory bound")
    for path in paths:
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), "source symlink")
        if stat.S_ISDIR(info.st_mode):
            continue
        require(
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "regular private source"
        )
        target = destination / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Writing new bytes deliberately avoids copying read-only export modes.
        target.write_bytes(path.read_bytes())


def source_controls():
    with tempfile.TemporaryDirectory(prefix="mixed566-controls-") as work:
        root = Path(work)
        private_copy(root)
        authenticate(root)
        source = root / "research/p112-root-simplex-exclusion/geometry.py"
        source.write_bytes(source.read_bytes() + b"\n# private corruption\n")
        rejects(lambda: authenticate(root), "source SHA256")
        run = subprocess.run(
            [
                sys.executable,
                "-W",
                "error",
                "-B",
                str(root / "research/p112-mixed566-cut32/verify.py"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        require(
            run.returncode != 0 and "source SHA256" in run.stderr,
            "actual verifier process accepted corrupt source",
        )
        source.write_bytes((ROOT / source.relative_to(root)).read_bytes())
        manifest = root / "research/p112-mixed566-cut32/SOURCES.json"
        original = manifest.read_bytes()
        for change in ("version", "usage", "inventory"):
            data = json.loads(original)
            if change == "version":
                data["schema_version"] = True
            elif change == "usage":
                data["files"][-1]["usage"] = "provenance"
            else:
                data["files"].append(copy.deepcopy(data["files"][-1]))
            manifest.write_text(json.dumps(data))
            rejects(lambda: authenticate(root), "manifest pin")
        manifest.write_bytes(original)
        prior = root / "research/p112-mixed566-cut32/vendor/pr3295-PROOF.md"
        prior.write_bytes(prior.read_bytes() + b"corruption")
        rejects(lambda: authenticate(root), "source SHA256")


def main():
    require(certificate()["D6"][0]["gap"] == 1, "positive fixture")
    rejects(lambda: certificate(33), "concentration not forced")
    rejects(lambda: certificate(True), "bounded common cut")
    require(
        canonical({"schema_version": True}) != canonical({"schema_version": 1}),
        "typed JSON equality",
    )
    receipt = read_json(PACKAGE / "RESULT.json")
    mutant = copy.deepcopy(receipt)
    mutant["D6"][0]["coverage_at_most"] += 1
    require(canonical(mutant) != canonical(certificate()), "arithmetic receipt mutant")
    source_controls()
    print(
        "PASS_MIXED566_CONTROLS: cut33, bool, receipt, geometry, "
        "process, manifest, source"
    )


if __name__ == "__main__":
    main()
