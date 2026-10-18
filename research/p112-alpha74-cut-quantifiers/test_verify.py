"""Mathematical and source-bound failure controls. Apache-2.0."""

import copy
import json
import stat
import subprocess
import sys
import tempfile
from itertools import islice
from pathlib import Path

from verify import PACKAGE, ROOT, authenticate, certificate, read_json, require


def rejects(action, fragment):
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), "unexpected rejection: " + str(error))
    else:
        raise ValueError("accepted mutant: " + fragment)


def private_copy(destination):
    paths = list(islice(PACKAGE.rglob("*"), 33))
    require(len(paths) <= 32, "private inventory bound")
    paths.append(ROOT / "research/p112-root-simplex-exclusion/geometry.py")
    for source in paths:
        info = source.lstat()
        require(not stat.S_ISLNK(info.st_mode), "source symlink")
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "regular source")
        target = destination / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def source_controls():
    with tempfile.TemporaryDirectory(prefix="alpha74-controls-") as directory:
        root = Path(directory)
        private_copy(root)
        authenticate(root)
        package = root / PACKAGE.relative_to(ROOT)
        manifest = package / "SOURCES.json"
        original = manifest.read_bytes()
        for change in ("type", "usage", "inventory"):
            value = json.loads(original)
            if change == "type":
                value["schema_version"] = True
            elif change == "usage":
                value["files"][-1]["usage"] = "provenance"
            else:
                value["files"].append(copy.deepcopy(value["files"][-1]))
            manifest.write_text(json.dumps(value))
            rejects(lambda: authenticate(root), "manifest pin")
        manifest.write_bytes(original)
        source = root / "research/p112-root-simplex-exclusion/geometry.py"
        source.write_bytes(source.read_bytes() + b"\n# private corruption\n")
        rejects(lambda: authenticate(root), "source SHA256")
        for name in ("verify.py", "independent.py"):
            result = subprocess.run(
                [sys.executable, "-O", "-W", "error", "-B", str(package / name)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            require(
                result.returncode != 0 and "source SHA256" in result.stderr,
                "actual process accepted corrupt source",
            )


def main():
    witness = read_json(PACKAGE / "WITNESS.json")
    require(
        certificate(witness)["direction_dependent_one_cut_span"] == 8,
        "positive witness",
    )
    for change, message in (
        ("cut", "direction root"),
        ("normal", "orthogonal direction basis"),
        ("type", "witness schema type"),
        ("index", "root index"),
        ("cover", "cover"),
    ):
        mutant = copy.deepcopy(witness)
        if change == "cut":
            mutant["individual_cuts"][0] = [8]
        elif change == "normal":
            mutant["directions"][0] = mutant["directions"][1][:]
        elif change == "type":
            mutant["schema_version"] = True
        elif change == "index":
            mutant["U_roots"][0] = True
        else:
            mutant["V_roots"][0] = 8
        rejects(lambda mutant=mutant: certificate(mutant), message)
    source_controls()
    print(
        "PASS_ALPHA74_CONTROLS: cut, normal, type, index, cover, "
        "source, process, manifests"
    )


if __name__ == "__main__":
    main()
